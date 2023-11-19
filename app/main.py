import streamlit as st
import os
import json
import pandas as pd
from utils import get_billbot_response, summarize_bill
from dotenv import load_dotenv

load_dotenv("./.env")
data_folder = "data"


# Function to extract text from a PDF file
def extract_text_from_pdf(json_data):
    text = json_data["analyzeResult"]["content"]
    return text


# Function to load JSON data from a file
def load_json_data(json_path):
    with open(json_path, "r") as json_file:
        data = json.load(json_file)
    return data


def convert_keyvalues_to_dict(json_data, confidence_threshold=0.5):
    result_dict = {}
    for pair in json_data["analyzeResult"]["keyValuePairs"]:
        confidence = pair.get("confidence", 1.0)

        if confidence >= confidence_threshold:
            key_content = pair["key"]["content"]
            value_content = ""
            if "value" in pair:
                value_content = pair["value"]["content"]
            result_dict[key_content] = value_content
    return result_dict


def convert_tables_to_df(json_data):
    tables = json_data["analyzeResult"]["tables"]
    dataframes = []
    for table in tables:
        rows = table["rowCount"]
        columns = table["columnCount"]
        cells = table["cells"]
        # Initialize an empty DataFrame for the current table
        df = pd.DataFrame(index=range(rows), columns=range(columns))
        # Fill the DataFrame with cell content
        for cell in cells:
            row_idx = cell["rowIndex"]
            col_idx = cell["columnIndex"]
            content = cell.get("content", "")
            df.at[row_idx, col_idx] = content
        # Append the DataFrame to the list
        dataframes.append(df)
    return dataframes


def get_or_generate_summary(pdf_path, pdf_text):
    summary_file_path = pdf_path + "_summary.txt"
    # Check if the summary file exists
    if os.path.exists(summary_file_path):
        with open(summary_file_path, "r") as summary_file:
            bill_summary = summary_file.read()
    else:
        bill_summary = summarize_bill(text=pdf_text)
        # Save the summary to the file
        with open(summary_file_path, "w") as summary_file:
            summary_file.write(bill_summary)
    return bill_summary


def setup_sidebar():
    with st.sidebar:
        st.markdown("""# Welcome, Kanak Dahake""")
        st.markdown("---")
        pdf_files = [f for f in os.listdir(data_folder) if f.endswith(".pdf")]
        st.session_state["selected_pdf"] = st.sidebar.selectbox(
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


def setup_sidebar_about():
    with st.sidebar:
        st.markdown("---")
        with st.expander("Developer: **Kanak Dahake**", expanded=True):
            st.markdown(
                """📧 ksdusa4@gmail.com \\
🌐 [Website](https://kanakjr.in) 
👔 [LinkedIn](https://www.linkedin.com/in/kanak-dahake)
🐙 [GitHub](https://github.com/Kanakjr)"""
            )


def main():
    pdf_path = os.path.join(data_folder, st.session_state["selected_pdf"])
    json_path = pdf_path + ".json"

    content_tab, bot_tab = st.tabs(["Content", "Bot"])

    with content_tab:
        json_data = load_json_data(json_path)
        pdf_text = extract_text_from_pdf(json_data)
        st.text_area(label="PDF Text:", value=pdf_text)

        bill_summary = get_or_generate_summary(pdf_path, pdf_text)
        st.text_area(label="Summary:", value=bill_summary, height=120)

        with st.expander("Extracted keyValuePairs:"):
            key_value_pairs = convert_keyvalues_to_dict(json_data)
            st.table(key_value_pairs)
        with st.expander("Extracted Tables:"):
            df_list = convert_tables_to_df(json_data)
            for df in df_list:
                st.write(df)

    with bot_tab:
        question = st.text_input("Question on bill document")
        if st.button("Get Answer"):
            st.session_state["bot_response"] = get_billbot_response(
                question=question,
                document_summary=bill_summary,
                key_values=key_value_pairs,
            )
        if st.session_state["bot_response"]:
            st.write(st.session_state["bot_response"])


def initialize_session_state():
    if "bot_response" not in st.session_state:
        st.session_state["bot_response"] = None
    if "selected_pdf" not in st.session_state:
        st.session_state["selected_pdf"] = None


# Load ENV Variables
load_dotenv("./.env")
# Set API keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Set Streamlit page config
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

# Streamlit app title and description
st.title("🤖 Bill Bot")

# Call the function to initialize session state
initialize_session_state()

setup_sidebar()
setup_sidebar_about()
main()
