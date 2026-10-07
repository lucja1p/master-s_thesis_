import streamlit as st

from utils.state import go_to
from utils.database import save_participant

def show_demographics():

    with st.form("demographics"):

        gender = st.radio("Płeć", ["Mężczyzna", "Kobieta", "Inna"], index = None)
        year_of_birth = st.selectbox("Rok urodzenia", options = list(range(2008, 1926, -1)), index = None, placeholder = "Wybierz rok")
        education = st.radio("Najwyższe ukończone wykształcenie", ["Podstawowe", "Zasadnicze zawodowe", "Średnie", "Wyższe"], index = None)
        experience = st.radio("Jak często korzystasz z chatbotów AI?, to trzeba jeszcze sprawdzić", ["Nigdy", "Rzadko", "Czasami", "Często", "Codziennie"], index = None)

        submitted = st.form_submit_button("Dalej")
        
        if submitted:

            if gender is None or year_of_birth is None or education is None or experience is None:
                st.error("Uzupełnij wszystkie pola.")

            else:
                
                st.session_state.answers["gender"] = gender
                st.session_state.answers["year_of_birth"] = year_of_birth
                st.session_state.answers["education"] = education
                st.session_state.answers["ai_experience"] = experience

                save_participant()

                go_to("chatbot_03")