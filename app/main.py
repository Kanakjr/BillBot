import streamlit as st
import os
from dotenv import load_dotenv

from utils import (
    extract_text_from_pdf,
    load_json_data,
    convert_keyvalues_to_dict,
    convert_tables_to_df,
    get_or_generate_recommended_questions,
    get_or_generate_summary,
    displayPDF,
)
from llm_utils import get_billbot_response

# Load environment variables from .env file
load_dotenv("./.env")

# Define constants for data folder and API key
DATA_FOLDER = "data"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class BillBotApp:
    """
    BillBotApp encapsulates all the methods and state necessary to run the Bill Bot Streamlit application.
    """

    def __init__(self):
        # Initialize session state variables
        self.initialize_session_state()

    def initialize_session_state(self):
        """
        Initialize Streamlit session state variables.
        """
        if "bot_response" not in st.session_state:
            st.session_state["bot_response"] = None
        if "selected_pdf" not in st.session_state:
            st.session_state["selected_pdf"] = None

    def setup_sidebar(self):
        """
        Set up the sidebar for the Streamlit application.
        """
        with st.sidebar:
            # st.markdown("""# Welcome, Kanak Dahake""")
            # st.markdown("---")
            pdf_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".pdf")]
            st.session_state["selected_pdf"] = st.selectbox(
                "Select PDF file", pdf_files
            )
            st.markdown("---")
            st.markdown("#### My Settings")
            OPENAI_MODEL = st.radio(
                "Choose OpenAI Model",
                (
                    "gpt-4-1106-preview",
                    "gpt-4",
                    "gpt-4-32k",
                    "gpt-3.5-turbo-1106",
                    "gpt-3.5-turbo-16k",
                    "gpt-3.5-turbo",
                    "text-davinci-003",
                ),
                index=3,
            )
            os.environ["OPENAI_MODEL"] = OPENAI_MODEL

    def setup_sidebar_about(self):
        with st.sidebar:
            st.markdown("---")
            with st.expander("Developer: **Kanak Dahake**", expanded=True):
                st.markdown(
                    """📧 ksdusa4@gmail.com \\
    🌐 [Website](https://kanakjr.in) 
    👔 [LinkedIn](https://www.linkedin.com/in/kanak-dahake)
    🐙 [GitHub](https://github.com/Kanakjr)"""
                )

    def run(self):
        """
        Run the Streamlit application.
        """
        self.setup_sidebar()
        self.setup_sidebar_about()
        self.main()

    def main(self):
        pdf_path = os.path.join(DATA_FOLDER, st.session_state["selected_pdf"])
        json_path = pdf_path + ".json"

        json_data = load_json_data(json_path)
        pdf_text = extract_text_from_pdf(json_data)
        key_value_pairs = convert_keyvalues_to_dict(json_data)
        df_list = convert_tables_to_df(json_data)
        bill_summary = get_or_generate_summary(pdf_path, pdf_text)
        recommended_questions = get_or_generate_recommended_questions(
            pdf_path, bill_summary, key_value_pairs
        )

        bot_tab, content_tab = st.tabs(["Bot", "Content"])
        with bot_tab:
            col1, col2 = st.columns([1, 1], gap="medium")
            question = col1.text_area("Question on bill document")
            if col1.button("Get Answer"):
                st.session_state["bot_response"] = get_billbot_response(
                    question=question,
                    document_summary=bill_summary,
                    key_values=key_value_pairs,
                )
            if st.session_state["bot_response"]:
                col1.write(st.session_state["bot_response"])
            col2.markdown("**Recommended Questions:**")
            col2.markdown(recommended_questions)

        with content_tab:
            col1,col2 = st.columns(2)
            # col1.markdown(f"{pdf_path}")
            col1.markdown(displayPDF(pdf_path), unsafe_allow_html=True)
            col2.text_area(label="PDF Text:", value=pdf_text,height=200)
            col2.text_area(label="Summary:", value=bill_summary, height=250)
            with st.expander("Extracted keyValuePairs:"):
                st.table(key_value_pairs)
            with st.expander("Extracted Tables:"):
                for df in df_list:
                    st.write(df)


# Main entry point for the application

# Set Streamlit page configuration
st.set_page_config(
    page_title="Bill-Bot",
    layout="wide",
    page_icon="https://kanakjr.in/wp-content/uploads/2017/04/logokanakjr.png",
)
st.markdown(
    """<style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {visibility: hidden;}
        .block-container {padding-top: 1.2rem; padding-bottom: 0rem; }
    </style>""",
    unsafe_allow_html=True,
)

# Initialize and run the Bill Bot Streamlit application
app = BillBotApp()
app.run()
