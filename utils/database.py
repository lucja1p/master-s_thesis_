import streamlit as st
import psycopg


def get_connection():
    return psycopg.connect(
        st.secrets["DATABASE_URL"]
    )


def save_participant():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO participants (
                    participant_id,
                    gender,
                    year_of_birth,
                    education,
                    ai_experience
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    st.session_state.participant_id,
                    st.session_state.answers["gender"],
                    st.session_state.answers["year_of_birth"],
                    st.session_state.answers["education"],
                    st.session_state.answers["ai_experience"],
                )
            )

        conn.commit()


def save_trial(trial_number, trial_data):

    with get_connection() as conn:
        with conn.cursor() as cur:

            # 1. Zapis trialu
            cur.execute(
                """
                INSERT INTO trials (
                    participant_id,
                    trial_number,
                    task,
                    condition,
                    final_answer
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING trial_id
                """,
                (
                    st.session_state.participant_id,
                    trial_number,
                    trial_data["task"],
                    trial_data["condition"],
                    trial_data["answer"],
                )
            )

            trial_id = cur.fetchone()[0]

            # 2. Zapis wiadomości
            for order, message in enumerate(trial_data["messages"], start=1):
                cur.execute(
                    """
                    INSERT INTO messages (
                        trial_id,
                        message_order,
                        role,
                        content
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        trial_id,
                        order,
                        message["role"],
                        message["content"],
                    )
                )

            # 3. Zapis kwestionariusza
            questionnaire = trial_data["questionnaire"]

            cur.execute(
                """
                INSERT INTO questionnaire (
                    trial_id,
                    first_item,
                    second_item,
                    third_item,
                    fourth_item,
                    fifth_item
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    trial_id,
                    questionnaire["first_item"],
                    questionnaire["second_item"],
                    questionnaire["third_item"],
                    questionnaire["fourth_item"],
                    questionnaire["fifth_item"],
                )
            )

        conn.commit()