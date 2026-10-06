import streamlit as st
from utils.state import go_to


def show_instruction():

    st.title("Instrukcja")

    st.info(
        """
            W tym badaniu będziesz wykonywać 3 zadania z wykorzystaniem chatbota opartego na sztucznej inteligencji. 

            W każdym zadaniu otrzymasz jedno stwierdzenie. Twoim zadaniem będzie **opracowanie 3 argumentów popierających dane stwierdzenie** razem z chatbotem dostępnym w aplikacji.
            

            Najpierw porozmawiasz z chatbotem, z którym wspólnie opracujecie argumenty. Możesz zadawać pytania, prosić o rozwinięcie odpowiedzi lub poprosić o przedstawienie innych argumentów.
            **NIE WPISUJ W ROZMOWIE IMIENIA, ADRESU ANI INNYCH DANYCH POZWALAJĄCYCH CIĘ ZIDENTYFIKOWAĆ.**

            Na każde zadanie możesz wysłać maksymalnie 10 wiadomości do chatbota.

            Po zakończeniu rozmowy z chatbotem, pojawi się pole tekstowe na Twoje argumenty oraz kwestionariusz dotyczący Twoich wrażeń z interakcji z chatbotem.

            Ten sam schemat będzie powtarzany przy każdym z trzech zadań.

            Link do badania jest dostępny przez 40 minut, natomiast całe badanie powinno zająć około 20 minut.

        """
    )

    agreement = st.checkbox("Oświadczam, że zapoznałem/am się z instrukcją i wyrażam zgodę na przeprowadzenie badania.")

    if st.button("Rozpocznij badanie"):
        if agreement:
            go_to("demographics_02")
        else:
            st.error("Wyraź zgodę na badanie.")
