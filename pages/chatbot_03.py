import streamlit as st
from openai import OpenAI
import time
from utils.state import go_to


def stream_text(text, condition, total_time=5):
    if condition == "letter":
        units = list(text)

    elif condition == "word":
        units = text.split(" ")

    elif condition == "sentence":
        units = text.split(". ")

    delay = total_time / len(units)

    for i, unit in enumerate(units):
        if condition == "letter":
            yield unit

        elif condition == "word":
            yield unit + " "

        elif condition == "sentence":
            if i < len(units) - 1:
                yield unit + ". "
            else:
                yield unit

        time.sleep(delay)


def show_experiment():
    current_trial = st.session_state.current_trial

    condition = st.session_state.trials[current_trial]["condition"]
    task = st.session_state.trials[current_trial]["task"]

    # Inicjalizacja stanu
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "task_finished" not in st.session_state:
        st.session_state.task_finished = False

    if "answers" not in st.session_state:
        st.session_state.answers = {}


    if not st.session_state.task_finished:

        st.markdown(
            f"""
            Razem z chatbotem opracuj 3 argumenty za tym, że:

            **{task}**

            Jeśli masz już gotowe argumenty, wciśnij przycisk KOŃCZĘ ZADANIE. <br>**UWAGA:** po wciśnięciu przycisku, nie ma możliwości prowadzenia dalszej konwersacji z chatbotem.
            """, unsafe_allow_html=True
        )

    else:

        st.info(
            "Zadanie zakończone. Zjedź na dół strony i uzupełnij pole z odpowiedzią."
        )

    # Przycisk zakończenia rozmowy
    if not st.session_state.task_finished:

        if st.button("KOŃCZĘ ZADANIE"):
            st.session_state.task_finished = True
            st.rerun()

    SYSTEM_PROMPT = f"""
        Musisz pomóc użytkownikowi wymyślić 3 argumenty przemawiające
        za następującym stwierdzeniem:

        "{task}"

        Odpowiadaj po polsku.
        Pomagaj użytkownikowi rozwijać i dopracowywać argumenty.
        Odpowiedź formułuj w kilku, maksymalnie kilkunastu zdaniach.
        Nie zmieniaj tematu rozmowy.
    """

    client = OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
    )

    # Historia rozmowy
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat działa tylko dopóki zadanie nie zostało zakończone
    if not st.session_state.task_finished:

        if prompt := st.chat_input("Napisz wiadomość"):

            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })

            with st.chat_message("user"):
                st.write(prompt)

            response = client.responses.create(
                model="gpt-5.6-luna",
                instructions=SYSTEM_PROMPT,
                input=st.session_state.messages
            )

            # Odpowiedź chatbota ze streamingiem
            with st.chat_message("assistant"):
                placeholder = st.empty()
                displayed_text = ""

                for chunk in stream_text(
                    response.output_text,
                    condition
                ):
                    displayed_text += chunk
                    placeholder.markdown(displayed_text)

            answer = response.output_text

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

    else:

        st.markdown("---")

        st.subheader("Twoja odpowiedź")

        st.write(
            "Wpisz poniżej 3 argumenty przemawiające za podanym stwierdzeniem."
        )

        final_answer = st.text_area(
            "Podaj swoje 3 argumenty:",
            height=180,
            placeholder="1. ...\n\n2. ...\n\n3. ..."
        )

        if st.button("PRZEJDŹ DALEJ"):

            if final_answer.strip():

                st.session_state.current_trial_data = {
                    "task": task,
                    "condition": condition,
                    "messages": st.session_state.messages.copy(),
                    "answer": final_answer
                }
                st.session_state.task_finished = False

                go_to("questionnaire_04")

            else:
                st.warning("Najpierw wpisz swoją odpowiedź.")

