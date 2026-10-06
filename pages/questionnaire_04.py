import streamlit as st
from utils.state import go_to


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
    st.subheader("Proszę ocenić swoje odczucia na temat robota, w skali od 1 do 5")

    with st.form("questionnaire"):
        first_item = semantic_row("nieprawdziwy", "naturalny", "first_item")
        second_item = semantic_row("przypomina maszynę", "przypomina człowieka", "second_item")
        third_item = semantic_row("pozbawiony świadomości", "świadomy", "third_item")
        fourth_item = semantic_row("sztuczny", "jak żywy", "fourth_item")
        fifth_item = semantic_row("komunikuje się sztywno", "komunikuje się płynnie", "fifth_item")

        submitted = st.form_submit_button("Dalej")

        if submitted:
            st.session_state.answers["first_item"] = first_item
            st.session_state.answers["second_item"] = second_item
            st.session_state.answers["third_item"] = third_item
            st.session_state.answers["fourth_item"] = fourth_item
            st.session_state.answers["fifth_item"] = fifth_item


            st.session_state.current_trial += 1

            if st.session_state.current_trial < 3:
                go_to("chatbot_03")

            else:
                go_to("end_05")




