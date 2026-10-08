-- =====================================================================
-- Schemat bazy danych badania.
--
-- Gdzie to uruchomić:
--   Neon Console -> projekt -> (wybierz gałąź, np. "dev") -> SQL Editor
--   -> wklej całość -> Run.
--
-- Skrypt jest idempotentny (IF NOT EXISTS), więc można go uruchomić
-- ponownie bez utraty danych. Nie zmienia jednak istniejących tabel –
-- zmiany kolumn wymagają osobnego ALTER TABLE.
-- =====================================================================


-- ---------------------------------------------------------------------
-- Linki jednorazowe.
-- Każdy wiersz = jeden link wysłany jednemu uczestnikowi.
-- Przechowujemy WYŁĄCZNIE skrót SHA-256 tokenu: wyciek bazy nie ujawnia
-- działających linków. Sam token istnieje tylko w linku (i w CSV badacza).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS access_tokens (
    token_hash      TEXT PRIMARY KEY,
    -- ID uczestnika nadawane razem z linkiem. Aplikacja używa go zamiast
    -- losowego uuid4(), więc odświeżenie strony nie tworzy "nowej osoby".
    participant_id  UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    label           TEXT,                              -- np. 'pilotaz', 'grupa_A'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    first_opened_at TIMESTAMPTZ,                       -- start odliczania 40 min
    completed_at    TIMESTAMPTZ,                       -- ustawiane na stronie końcowej
    revoked_at      TIMESTAMPTZ                        -- ręczne unieważnienie linku
);


-- ---------------------------------------------------------------------
-- Dane demograficzne (1 wiersz na uczestnika).
-- Celowo bez FK do access_tokens, żeby aplikacja działała też w trybie
-- testowym bez linków (REQUIRE_TOKEN = false). Powiązanie: participant_id.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS participants (
    participant_id UUID PRIMARY KEY,
    gender         TEXT NOT NULL,
    year_of_birth  SMALLINT NOT NULL,
    education      TEXT NOT NULL,
    ai_experience  TEXT NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- ---------------------------------------------------------------------
-- Rundy (3 na uczestnika): zadanie + wylosowany warunek strumieniowania.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS trials (
    trial_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    participant_id UUID NOT NULL REFERENCES participants,
    trial_number   SMALLINT NOT NULL CHECK (trial_number BETWEEN 1 AND 3),
    task           TEXT NOT NULL,
    condition      TEXT NOT NULL CHECK (condition IN ('letter', 'word', 'sentence')),
    final_answer   TEXT,
    started_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at    TIMESTAMPTZ,
    UNIQUE (participant_id, trial_number)              -- blokuje duplikaty
);


-- ---------------------------------------------------------------------
-- Pełna historia rozmowy z chatbotem w danej rundzie.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
    trial_id      BIGINT NOT NULL REFERENCES trials ON DELETE CASCADE,
    message_order SMALLINT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content       TEXT NOT NULL,
    model         TEXT,                                -- TODO: zapisywać z kodu
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (trial_id, message_order)
);


-- ---------------------------------------------------------------------
-- Kwestionariusz po każdej rundzie (5 skal 1–5).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS questionnaire (
    trial_id    BIGINT PRIMARY KEY REFERENCES trials ON DELETE CASCADE,
    first_item  SMALLINT NOT NULL CHECK (first_item  BETWEEN 1 AND 5),
    second_item SMALLINT NOT NULL CHECK (second_item BETWEEN 1 AND 5),
    third_item  SMALLINT NOT NULL CHECK (third_item  BETWEEN 1 AND 5),
    fourth_item SMALLINT NOT NULL CHECK (fourth_item BETWEEN 1 AND 5),
    fifth_item  SMALLINT NOT NULL CHECK (fifth_item  BETWEEN 1 AND 5)
);
