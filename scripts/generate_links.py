"""
Generator linków jednorazowych do badania.

Uruchamia go badacz NA SWOIM KOMPUTERZE (nie jest częścią aplikacji).
Czyta DATABASE_URL i PUBLIC_BASE_URL z .streamlit/secrets.toml.

Użycie (w katalogu projektu, z aktywnym .venv):
    python scripts/generate_links.py 20           # 20 linków do aplikacji w sieci
    python scripts/generate_links.py 2 --local    # linki na localhost (do testów)

Wynik trafia do pliku data/links_<data>.csv (folder data/ jest w .gitignore).
To jedyne miejsce, w którym zapisane są działające linki, więc traktuj go
jak hasła i każdemu uczestnikowi wyślij tylko jego link.

Podgląd i unieważnianie linków: Neon -> SQL Editor, np.
    SELECT * FROM access_tokens ORDER BY created_at;
    UPDATE access_tokens SET revoked_at = now() WHERE participant_id = '...';
"""

import csv
import datetime
import hashlib
import secrets
import sys
import tomllib
from pathlib import Path

import psycopg


ROOT = Path(__file__).resolve().parents[1]
config = tomllib.loads((ROOT / ".streamlit" / "secrets.toml").read_text("utf-8"))

count = int(sys.argv[1])
if "--local" in sys.argv:
    base_url = "http://localhost:8501"
else:
    base_url = config["PUBLIC_BASE_URL"].rstrip("/")

rows = []
with psycopg.connect(config["DATABASE_URL"]) as conn:
    for _ in range(count):
        # Losowy, praktycznie niemożliwy do odgadnięcia token (~22 znaki).
        token = secrets.token_urlsafe(16)

        # W bazie zapisujemy tylko skrót tokenu, więc wyciek bazy nie ujawnia
        # linków. Skrót MUSI być liczony tak samo jak w utils/access.py.
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Baza sama nadaje participant_id (patrz db/schema.sql).
        participant_id = conn.execute(
            "INSERT INTO access_tokens (token_hash) VALUES (%s) RETURNING participant_id",
            (token_hash,),
        ).fetchone()[0]

        rows.append([participant_id, f"{base_url}/?t={token}"])
    # Koniec bloku "with" = zapis w bazie wszystkich linków naraz.

out_file = ROOT / "data" / f"links_{datetime.datetime.now():%Y%m%d_%H%M%S}.csv"
out_file.parent.mkdir(exist_ok=True)
with out_file.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["participant_id", "link"])
    writer.writerows(rows)

print(f"Utworzono {count} linków -> {out_file}")
