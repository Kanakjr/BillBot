import streamlit as st
import os
from dotenv import load_dotenv

from utils import (
    extract_text_from_pdf,
    convert_keyvalues_to_dict,
    convert_tables_to_df,
    get_or_generate_metadata_json,
    get_or_generate_summary,
    get_or_generate_analyze_json,
    get_or_generate_recommended_questions,
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

            uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
            if uploaded_file is not None:
                # Save the uploaded file to the data folder
                with open(os.path.join(DATA_FOLDER, uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Auto-select the uploaded file in the selectbox
                st.session_state["selected_pdf"] = uploaded_file.name

            pdf_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".pdf")]
            # Selectbox to choose a PDF file
            st.session_state["selected_pdf"] = st.selectbox(
                "Select PDF file", pdf_files, index=pdf_files.index(st.session_state["selected_pdf"]) if st.session_state["selected_pdf"] else 0
            )

            st.markdown("---")
            st.markdown("#### My Settings")
            OPENAI_MODEL = st.radio(
                "Choose OpenAI Model",
                (
                    "gpt-4-1106-preview",
                    "gpt-3.5-turbo-1106",
                ),
                index=1,
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

    def get_bot_response(self):
        st.session_state["bot_response"] = get_billbot_response(
            question=st.session_state["bot_question"],
            document_summary=st.session_state["bill_summary"],
            key_values=st.session_state["key_value_pairs"],
        )

    def named_entities_to_str(self,input_data):
        organized_data = {}
        for item in input_data:
            value = item[1]
            key = item[0]
            if value not in organized_data:
                organized_data[value] = [key]
            else:
                organized_data[value].append(key)

        result_string = ""
        for key, values in organized_data.items():
            result_string += f"- **{key}** : {' | '.join(values)}\n"
        return result_string

    def display_bill_info(self,json_data,recommended_questions=None):
        with st.expander("Metadata"):
            named_entities = self.named_entities_to_str(json_data["named_entities"])
            st.markdown(f"""**Type:** {json_data["document_type"]} **Language:** {json_data["language"]}  **Currency:** {json_data["currency"]}
                        
**Keywords:**  {" | ".join(json_data["keywords"])}

**Named Entities:**
{named_entities}
    """)
        if not recommended_questions:
            recommended_questions = ""
            for idx,question in enumerate(json_data["recommended_questions"]):
                recommended_questions += f"{idx+1}. {question}\n"
        with st.expander("Recommended Questions:",expanded=True):
            st.markdown(f"""{recommended_questions}""")

    def main(self):
        pdf_path = os.path.join(DATA_FOLDER, st.session_state["selected_pdf"])

        with st.spinner("Analysing the document Layout and Data..."):
            json_data = get_or_generate_analyze_json(pdf_path)
            pdf_text = extract_text_from_pdf(json_data)
            key_value_pairs = convert_keyvalues_to_dict(json_data)
            df_list = convert_tables_to_df(json_data)
        with st.spinner("Summarising the Document..."):
            bill_summary = get_or_generate_summary(pdf_path, pdf_text)
        with st.spinner("Generating Bill Metadata..."):
            bill_medata = get_or_generate_metadata_json(pdf_path,pdf_text,key_value_pairs)
        with st.spinner("Generating Recommended Questions..."):
            recommended_questions = get_or_generate_recommended_questions(pdf_path, bill_summary, key_value_pairs)
        
        st.session_state["bill_summary"] = bill_summary
        st.session_state["key_value_pairs"] = key_value_pairs

        bot_tab, content_tab = st.tabs(["Bot", "Content"])
        with bot_tab:
            col1, col2 = st.columns([1, 1], gap="medium")
            col1.text_area("Question on bill document", key="bot_question")
            col1.button("Get Answer", on_click=self.get_bot_response,use_container_width=True)
            if st.session_state["bot_response"]:
                col1.write(st.session_state["bot_response"])
            #col2.markdown("**Recommended Questions:**")
            #col2.markdown(recommended_questions)
            with col2:
                self.display_bill_info(bill_medata,recommended_questions)

        with content_tab:
            col1, col2 = st.columns(2)
            # col1.markdown(f"{pdf_path}")
            col1.markdown(displayPDF(pdf_path), unsafe_allow_html=True)
            col2.text_area(label="PDF Text:", value=pdf_text, height=200)
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
        .block-container {padding-top: .7rem; padding-bottom: 0rem; }
    </style>""",
    unsafe_allow_html=True,
)
st.title("🤖 Bill Bot")

# Initialize and run the Bill Bot Streamlit application
app = BillBotApp()
app.run()
