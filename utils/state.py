import streamlit as st
import random

from config import CONDITIONS, TASKS


def initialize_state():

    if "page" not in st.session_state:
        st.session_state.page = "instruction_01"

    if "trials" not in st.session_state:
        tasks = list(TASKS)
        conditions = list(CONDITIONS)

        random.shuffle(tasks)
        random.shuffle(conditions)

        st.session_state.trials = [
            {
                "task": task,
                "condition": condition
            }
            for task, condition in zip(tasks, conditions)
        ]


    if "current_trial" not in st.session_state:
        st.session_state.current_trial = 0

    if "answers" not in st.session_state: # do poprawy
        st.session_state.answers = {}


def go_to(page):
    st.session_state.page = page
    st.rerun()