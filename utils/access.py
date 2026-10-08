"""
Kontrola dostępu przez linki jednorazowe.

Jak to działa w Streamlit:
  Streamlit nie ma własnych "endpointów" (np. /invite/abc). Przy każdym
  kliknięciu cały app.py wykonuje się od góry. Dlatego link to po prostu
  adres aplikacji z parametrem ?t=<token>, a require_token() wywołujemy
  na samej górze app.py. Jeśli link jest zły, st.stop() przerywa skrypt
  i uczestnik widzi tylko komunikat błędu.

Cykl życia linku (tabela access_tokens):
  utworzony      -> first_opened_at = NULL
  otwarty        -> first_opened_at = czas pierwszego wejścia (start 40 min)
  zakończony     -> completed_at ustawiane na stronie końcowej
  wygasły        -> minęło LINK_TTL_MINUTES od first_opened_at
  unieważniony   -> revoked_at ustawione ręcznie przez badacza

Konfiguracja (.streamlit/secrets.toml lub Secrets w Streamlit Cloud):
  REQUIRE_TOKEN    = true/false  (false = tryb testowy, wejście bez linku)
  LINK_TTL_MINUTES = 40
"""

import datetime as dt
import hashlib

import streamlit as st

from utils.database import get_connection


# Atomowe "sprawdź i oznacz": jedno zapytanie, więc dwie karty otwarte
# w tej samej chwili nie obejdą reguł. COALESCE sprawia, że czas
# pierwszego otwarcia ustawia się tylko raz.
#
# Odświeżenie strony (F5) kasuje stan sesji Streamlit. Warunek NOT EXISTS
# blokuje wtedy link, jeśli uczestnik zapisał już dane demograficzne –
# badacz może unieważnić taki link i wysłać nowy. F5 na stronie
# instrukcji (przed zapisem danych) jest nieszkodliwe.
CLAIM_TOKEN_SQL = """
    UPDATE access_tokens
       SET first_opened_at = COALESCE(first_opened_at, now())
     WHERE token_hash = %s
       AND completed_at IS NULL
       AND revoked_at IS NULL
       AND (first_opened_at IS NULL
            OR first_opened_at > now() - make_interval(mins => %s))
       AND NOT EXISTS (SELECT 1 FROM participants p
                        WHERE p.participant_id = access_tokens.participant_id)
 RETURNING participant_id, first_opened_at
"""


def _deny(message):
    st.error(message)
    st.stop()


def require_token():
    if not st.secrets.get("REQUIRE_TOKEN", False):
        return

    ttl_minutes = int(st.secrets.get("LINK_TTL_MINUTES", 40))

    # Link sprawdzony już w tej sesji -> tylko lokalna kontrola czasu,
    # bez odpytywania bazy przy każdym kliknięciu.
    expires_at = st.session_state.get("access_expires_at")
    if expires_at is not None:
        if dt.datetime.now(dt.timezone.utc) > expires_at:
            _deny("Czas na wykonanie badania minął. Link wygasł.")
        return

    token = st.query_params.get("t")
    if not token:
        _deny("Do badania można wejść wyłącznie przez otrzymany link.")

    # Musi być liczone tak samo jak w scripts/generate_links.py.
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    with get_connection() as conn:
        row = conn.execute(CLAIM_TOKEN_SQL, (token_hash, ttl_minutes)).fetchone()

    if row is None:
        # Celowo jeden komunikat dla wszystkich przypadków – nie zdradzamy,
        # czy token istnieje.
        _deny(
            "Link jest nieprawidłowy, wygasł lub został już wykorzystany. "
            "Jeśli badanie zostało przerwane, skontaktuj się z badaczem."
        )

    participant_id, first_opened_at = row

    # Ustawiamy PRZED initialize_state(), która nadaje uuid4() tylko
    # wtedy, gdy participant_id jeszcze nie istnieje.
    st.session_state.participant_id = str(participant_id)
    st.session_state.token_hash = token_hash
    st.session_state.access_expires_at = first_opened_at + dt.timedelta(minutes=ttl_minutes)


def mark_completed():
    # Wywoływane na stronie końcowej. Po tym link przestaje działać.
    token_hash = st.session_state.get("token_hash")
    if token_hash is None or st.session_state.get("access_completed"):
        return

    with get_connection() as conn:
        conn.execute(
            "UPDATE access_tokens SET completed_at = now() "
            "WHERE token_hash = %s AND completed_at IS NULL",
            (token_hash,),
        )

    st.session_state.access_completed = True
