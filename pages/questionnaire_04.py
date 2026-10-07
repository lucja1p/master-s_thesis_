import streamlit as st
from utils.state import go_to
from utils.database import save_trial


def semantic_row(text1, text2, key):
    col1, col2, col3 = st.columns([2, 5, 2], vertical_alignment="center")

    with col1:
        st.markdown(
            f"<div style='text-align: right;'>{text1}</div>",
            unsafe_allow_html=True
        )

    with col2:
        answer = st.slider(
            "",
            min_value=1,
            max_value=5,
            value=3, step = 1,
            key=key
        )

    with col3:
        st.markdown(
            f"<div style='text-align: left;'>{text2}</div>",
            unsafe_allow_html=True
        )

    return answer


def show_questionnaire():
    current_trial = st.session_state.current_trial

    st.subheader(
        "Proszę ocenić swoje odczucia na temat robota, w skali od 1 do 5"
    )

    with st.form("questionnaire"):
        first_item = semantic_row(
            "nieprawdziwy",
            "naturalny",
            f"trial_{current_trial}_first_item"
        )

        second_item = semantic_row(
            "przypomina maszynę",
            "przypomina człowieka",
            f"trial_{current_trial}_second_item"
        )

        third_item = semantic_row(
            "pozbawiony świadomości",
            "świadomy",
            f"trial_{current_trial}_third_item"
        )

        fourth_item = semantic_row(
            "sztuczny",
            "jak żywy",
            f"trial_{current_trial}_fourth_item"
        )

        fifth_item = semantic_row(
            "komunikuje się sztywno",
            "komunikuje się płynnie",
            f"trial_{current_trial}_fifth_item"
        )

        submitted = st.form_submit_button("Dalej")

        if submitted:
            questionnaire = {
                "first_item": first_item,
                "second_item": second_item,
                "third_item": third_item,
                "fourth_item": fourth_item,
                "fifth_item": fifth_item
            }

            # Dodajemy kwestionariusz do aktualnego trialu
            st.session_state.current_trial_data["questionnaire"] = questionnaire

            # Zapisujemy cały ukończony trial
            st.session_state.trial_results.append(
                st.session_state.current_trial_data
            )

            trial_data = st.session_state.current_trial_data
            save_trial(
                trial_number=st.session_state.current_trial + 1,
                trial_data=trial_data
                )
            # Czyścimy dane aktualnego trialu
            st.session_state.current_trial_data = None
            st.session_state.messages = []

            # Przechodzimy do kolejnego trialu
            st.session_state.current_trial += 1

            if st.session_state.current_trial < 3:
                go_to("chatbot_03")
            else:
                go_to("end_05")



