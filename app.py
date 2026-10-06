import streamlit as st

from pages.instruction_01 import show_instruction
from pages.demographics_02 import show_demographics
from pages.chatbot_03 import show_experiment
from pages.questionnaire_04 import show_questionnaire
from pages.end_05 import show_end

from utils.state import initialize_state


initialize_state()

if st.session_state.page == "instruction_01":
    show_instruction()

elif st.session_state.page == "demographics_02":
    show_demographics()

elif st.session_state.page == "chatbot_03":
    show_experiment()

elif st.session_state.page == "questionnaire_04":
    show_questionnaire()

elif st.session_state.page == "end_05":
    show_end()