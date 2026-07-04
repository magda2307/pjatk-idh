import streamlit as st


def main():
    st.set_page_config(
        page_title="Hurtownia Iowa Liquor Sales",
        layout="wide",
    )
    st.title("Hurtownia danych Iowa Liquor Sales")
    st.info(
        "Główny dashboard projektu jest w pliku `app/streamlit_app.py` "
        "i to on jest uruchamiany przez Docker Compose."
    )
    st.page_link("app/streamlit_app.py", label="Otwórz właściwy dashboard")


if __name__ == "__main__":
    main()
