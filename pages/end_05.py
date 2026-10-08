import streamlit as st

from utils.access import mark_completed


def show_end():

    # Zamyka link jednorazowy – po tym nie da się go użyć ponownie.
    mark_completed()

    st.title("Dziękuję za udział!")

    st.write(
        "Badanie zostało zakończone."
    )

