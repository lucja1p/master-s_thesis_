import streamlit as st
import random
import uuid

from config import CONDITIONS, TASKS


def initialize_state():

    if "participant_id" not in st.session_state:
       st.session_state.participant_id = str(uuid.uuid4())

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

    if "trial_results" not in st.session_state:
        st.session_state.trial_results = []

    if "current_trial_data" not in st.session_state:
        st.session_state.current_trial_data = None

    if "answers" not in st.session_state: # do poprawy
        st.session_state.answers = {}


def go_to(page):
    st.session_state.page = page
    st.rerun()