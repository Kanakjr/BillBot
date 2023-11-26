Listing: .
  [D] .
  [F] ./.DS_Store
  [D] ./app
  [F] ./app/.DS_Store
  [F] ./app/formrecognizer.py
  [F] ./app/requirements.txt
  [D] ./app/.streamlit
  [F] ./app/.streamlit/config.toml
  [D] ./app/__pycache__
  [F] ./app/__pycache__/llm_utils.cpython-38.pyc
  [F] ./app/__pycache__/utils.cpython-38.pyc
  [F] ./app/__pycache__/formrecognizer.cpython-38.pyc
  [D] ./app/docs
  [F] ./app/docs/bot.txt
  [F] ./app/llm_utils.py
  [F] ./app/utils.py
  [F] ./app/.env
  [F] ./app/main.py
  [D] ./app/data
  [F] ./Dockerfile
  [F] ./build_readme_prompt.sh
  [F] ./rundocker.sh
  [F] ./README.md
  [F] ./.gitignore
  [D] ./.github
  [D] ./.github/workflows
  [F] ./.github/workflows/docker-image.yml
  [D] ./.git
  [F] ./readme_prompt.txt



Listing: ./app
  [D] ./app
  [F] ./app/.DS_Store
  [F] ./app/formrecognizer.py
  [F] ./app/requirements.txt
  [D] ./app/.streamlit
  [F] ./app/.streamlit/config.toml
  [D] ./app/__pycache__
  [F] ./app/__pycache__/llm_utils.cpython-38.pyc
  [F] ./app/__pycache__/utils.cpython-38.pyc
  [F] ./app/__pycache__/formrecognizer.cpython-38.pyc
  [D] ./app/docs
  [F] ./app/docs/bot.txt
  [F] ./app/llm_utils.py
  [F] ./app/utils.py
  [F] ./app/.env
  [F] ./app/main.py
  [D] ./app/data



Listing: ./app/__pycache__
  [D] ./app/__pycache__
  [F] ./app/__pycache__/llm_utils.cpython-38.pyc
  [F] ./app/__pycache__/utils.cpython-38.pyc
  [F] ./app/__pycache__/formrecognizer.cpython-38.pyc



Listing: ./app/docs
  [D] ./app/docs
  [F] ./app/docs/bot.txt



### ./app/docs/bot.txt
# Role: Billing Document Bot

## Profile

- Description: The Billing Document Bot is an AI-powered bot designed to answer questions based on any billing document. It utilizes the document summary and the data in the document, which are presented in the form of key-value pairs, to provide accurate and relevant answers. The bot strictly relies on the information contained within the document and does not make any assumptions or provide answers not supported by the document. If the bot is unable to find the answer to a question, it will inform the user that it does not have the required information. 

## Functionality

- The bot can answer questions related to billing documents.
- It relies solely on the document summary and the data within the document.
- The document data is provided in the form of key-value pairs.
- If the bot cannot find the answer to a question, it will inform the user accordingly.


### ./app/formrecognizer.py
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import os

def analyze_pdf_document(pdf_file_path):
    # Replace with your actual Azure Form Recognizer service endpoint and key
    SERVICE_ENDPOINT = os.environ.get("SERVICE_ENDPOINT")
    SERVICE_KEY = os.environ.get("SERVICE_KEY")
    # Initialize DocumentAnalysisClient
    document_analysis_client = DocumentAnalysisClient(
        endpoint=SERVICE_ENDPOINT, credential=AzureKeyCredential(SERVICE_KEY)
    )
    # Open the PDF file and begin document analysis
    with open(pdf_file_path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-document", document=f
        )
    # Wait for the analysis to complete and get the result
    result = poller.result()
    return result.to_dict()


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    import warnings

    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        module="streamlit.runtime.caching.cache_data_api",
    )
    load_dotenv("./app/.env")

    filepath = "app/data/LT E-BillPDF_231119_145147.pdf"
    result = analyze_pdf_document(filepath)
    result


### ./app/llm_utils.py
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain.schema.document import Document
import streamlit as st
import os
import json


def get_llm(OPENAI_MODEL=None, max_tokens=1000):
    if not OPENAI_MODEL:
        OPENAI_MODEL = os.environ.get("OPENAI_MODEL")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    llm = ChatOpenAI(
        temperature=0,
        model_name=OPENAI_MODEL,
        openai_api_key=OPENAI_API_KEY,
        max_tokens=max_tokens,
    )
    return llm


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)  # Cache data for 12 hours
def get_openAPI_response(text, task, OPENAI_MODEL=None, max_tokens=1000, llm=None):
    messages = [HumanMessage(content=text)]
    llm = get_llm(OPENAI_MODEL=OPENAI_MODEL, max_tokens=max_tokens)
    response = llm.invoke(messages, config={"run_name": task})
    response = str(response.content)
    return response


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)  # Cache data for 12 hours
def summarize_bill(text, task="Summarize", chain_type="stuff"):
    docs = [Document(page_content=text)]
    llm = get_llm()
    prompt_template = """## Summarise the given document:
## Doucment Text:
{text}

## Document Summary:"""
    prompt = PromptTemplate.from_template(prompt_template)
    chain = load_summarize_chain(llm, prompt=prompt, chain_type=chain_type)
    result = chain.invoke(docs, config={"run_name": task})
    return result["output_text"]


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)  # Cache data for 12 hours
def get_recommended_question(document_summary, key_values=[]):
    key_values = format_dict_as_string(key_values)
    prompt = PromptTemplate(
        input_variables=["document_summary", "key_values"],
        template="""## You are given a document summary and some of the key value data from the document. 
## Document Summary: 
{document_summary} 

## Document Data: 
{key_values}

## Generate a list of 10 recommended questions on the given document. Format it as markdown text.
""",
    )
    llm = get_llm()
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.invoke(
        input={
            "document_summary": document_summary,
            "key_values": key_values,
        },
        config={"run_name": "RecommenedQBill"},
    )
    response = response["text"]
    return response


def get_bill_metadata(document_content, key_values=[]):
    # Assuming format_dict_as_string is a function that formats key_values into a string
    key_values_str = format_dict_as_string(key_values)
    prompt = PromptTemplate(
        input_variables=["document_content", "key_values"],
        template="""## You are given a document summary and some of the key value data from the document. 
## Document Content: 
{document_content} 

## Document Data: 
{key_values}

## Based on the document summary and data provided, please output the following in JSON format:
- recommended_questions: A list of 10 recommended questions about the document.
- keywords: A list of keywords or key phrases that represent the main topics or themes of the document.
- named_entities: A list of named entities from the document, with each named entity being a list of the extracted name and its type (PERSON,Organization,Location,Date,Time,etc) (e.g., [["Steve Jobs", "PERSON"], ["India", "COUNTRY"]]).
- document_type: Identify and categorize the type of document (e.g., "bill", "invoice", "ID card", "invoice", "contract", "report", "legal document" etc.).
- language: Determine the language in which the document is written
- currency: Determine the currency used in the document. Output the currency code, such as USD, EUR, GBP, INR etc. Consider variations in formatting and placement of currency symbols, as well as potential textual references to currencies. 

## JSON Output:
""",
    )
    # Get the language model response
    llm = get_llm(max_tokens=2000)
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.invoke(
        input={
            "document_content": document_content,
            "key_values": key_values_str,
        },
        config={"run_name": "BillMetadata"},
    )

    # Parse the response, assuming the model returns a properly formatted JSON string
    response_data = json.loads(response["text"])

    # Output the combined dictionary
    return response_data


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)  # Cache data for 12 hours
def get_billbot_response(question, document_summary, key_values=[]):
    key_values = format_dict_as_string(key_values)
    prompt = PromptTemplate(
        input_variables=["question", "document_summary", "key_values"],
        template="""## You are given a document summary and some of the key value data from the document. 
## Document Summary:
{document_summary} 

## Document Data:
{key_values}

## You have to answer the given user question stricty from the document. 
Do not assume any values or answer on your own. 
If you don't know the answer respond with "I don't know the answer"

## Question: {question}
""",
    )
    llm = get_llm()
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.invoke(
        input={
            "question": question,
            "document_summary": document_summary,
            "key_values": key_values,
        },
        config={"run_name": "BillBot"},
    )
    response = response["text"]
    return response


def format_dict_as_string(input_dict):
    formatted_string = ""
    for key, value in input_dict.items():
        formatted_string += f"{key} : {value}\n"
    return formatted_string.strip()


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    import warnings
    from utils import get_or_generate_analyze_json,convert_keyvalues_to_dict,extract_text_from_pdf

    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        module="streamlit.runtime.caching.cache_data_api",
    )
    load_dotenv("./app/.env")

    pdf_path = "./app/data/LT E-BillPDF_231119_145147.pdf"
    json_data = get_or_generate_analyze_json(pdf_path)
    document_content = extract_text_from_pdf(json_data)
    key_values = convert_keyvalues_to_dict(json_data)
    get_bill_metadata(document_content, key_values)



### ./app/main.py
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
            selected_pdf = st.selectbox(
                "Select PDF file", pdf_files, index=pdf_files.index(st.session_state["selected_pdf"]) if st.session_state["selected_pdf"] else 0
            )

            if selected_pdf != st.session_state["selected_pdf"]:
                st.session_state["selected_pdf"] = selected_pdf
                st.rerun()

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
            st.markdown(f"""**Filename:** {st.session_state["selected_pdf"]}

**Type:** {json_data["document_type"]} | **Language:** {json_data["language"]} |  **Currency:** {json_data["currency"]}
                        
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



### ./app/requirements.txt
langchain==0.0.316
openai==0.28.1
streamlit==1.28.0
streamlit-feedback==0.1.2
requests==2.31.0
requests-file==1.5.1
python-dotenv==1.0.0
beautifulsoup4==4.12.2
tiktoken==0.5.1
azure-ai-formrecognizer==3.3.2


### ./app/utils.py
import json, os
import pandas as pd
from llm_utils import summarize_bill, get_recommended_question,get_bill_metadata
import base64
from formrecognizer import analyze_pdf_document

# Function to extract text from a PDF file
def extract_text_from_pdf(json_data):
    text = json_data["content"]
    return text


# # Function to load JSON data from a file
# def load_json_data(json_path):
#     with open(json_path, "r") as json_file:
#         data = json.load(json_file)
#     return data


def convert_keyvalues_to_dict(json_data, confidence_threshold=0.5):
    result_dict = {}
    for pair in json_data["key_value_pairs"]:
        confidence = pair.get("confidence", 1.0)
        if confidence >= confidence_threshold:
            key_content = pair["key"]["content"]
            value_content = ""
            if "value" in pair:
                if pair["value"]:
                    value_content = pair["value"]["content"]
            result_dict[key_content] = value_content
    return result_dict


def convert_tables_to_df(json_data):
    tables = json_data["tables"]
    dataframes = []
    for table in tables:
        rows = table["row_count"]
        columns = table["column_count"]
        cells = table["cells"]
        # Initialize an empty DataFrame for the current table
        df = pd.DataFrame(index=range(rows), columns=range(columns))
        # Fill the DataFrame with cell content
        for cell in cells:
            row_idx = cell["row_index"]
            col_idx = cell["column_index"]
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


def get_or_generate_recommended_questions(pdf_path, document_summary, key_values):
    recommended_questions_file_path = pdf_path + "_questions.txt"
    # Check if the summary file exists
    if os.path.exists(recommended_questions_file_path):
        with open(recommended_questions_file_path, "r") as recommended_questions_file:
            recommended_questions = recommended_questions_file.read()
    else:
        recommended_questions = get_recommended_question(document_summary, key_values)
        # Save the summary to the file
        with open(recommended_questions_file_path, "w") as recommended_questions_file:
            recommended_questions_file.write(recommended_questions)
    return recommended_questions

def get_or_generate_analyze_json(pdf_path):
    analyze_json_file_path = pdf_path + ".json"
    if os.path.exists(analyze_json_file_path):
        with open(analyze_json_file_path, "r") as analyze_json_file:
            analyze_json = analyze_json_file.read()
        return json.loads(analyze_json)
    else:
        analyze_results = analyze_pdf_document(pdf_path)
        analyze_json = json.dumps(analyze_results, indent=2)
        with open(analyze_json_file_path, "w") as analyze_json_file:
            analyze_json_file.write(analyze_json)
        return analyze_results
    
def get_or_generate_metadata_json(pdf_path,document_content, key_values):
    metadata_json_file_path = pdf_path + "_metadata.json"
    if os.path.exists(metadata_json_file_path):
        with open(metadata_json_file_path, "r") as metadata_json_file:
            metadata_json = metadata_json_file.read()
        return json.loads(metadata_json)
    else:
        metadata_results = get_bill_metadata(document_content, key_values)
        metadata_json = json.dumps(metadata_results, indent=2)
        with open(metadata_json_file_path, "w") as metadata_json_file:
            metadata_json_file.write(metadata_json)
        return metadata_results

def displayPDF(file):
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_md = F'<embed src="data:application/pdf;base64,{base64_pdf}" width=100% height="500" type="application/pdf">'
    return pdf_md



### ./build_readme_prompt.sh
#!/bin/bash

# Function to process a file
process_file() {
  file="$1"
  if [ "$file" != "./readme_prompt.txt" ]; then
    echo "Processing: $file"
    echo "### $file" >> readme_prompt.txt
    cat "$file" >> readme_prompt.txt
    echo -e "\n\n" >> readme_prompt.txt
  else
    echo "Skipped: $file (readme_prompt.txt)"
  fi
}

# Function to list all folders and files in the current directory recursively, excluding specified directories
list_files() {
  directory="$1"
  echo "Listing: $directory" >> readme_prompt.txt
  find "$directory" -type d ! -path "./app/data/*" ! -path "./.git/*" -exec echo "  [D] {}" \; -o -type f -exec echo "  [F] {}" \; | grep -v -e './\.git/' -e './app/data/' >> readme_prompt.txt
  echo -e "\n\n" >> readme_prompt.txt
}

# Function to crawl through directories
crawl_directory() {
  directory="$1"
  if [ "$directory" != "./app/data" ]; then
    list_files "$directory"
    for file in "$directory"/*; do
      if [ -d "$file" ]; then
        crawl_directory "$file"
      elif [ -f "$file" ]; then
        case "$file" in
          *.py|Dockerfile|*.sh|.github/workflows/docker-image.yml|.env|*.txt)
            process_file "$file"
            ;;
        esac
      fi
    done
  fi
}

# Clear existing readme_prompt.txt
> readme_prompt.txt

# Start crawling from the current directory
crawl_directory "."

echo "Crawling completed. Results are saved in readme_prompt.txt"



### ./rundocker.sh
docker system prune -f
docker build -f "Dockerfile" -t billbot:latest "."
docker ps -q --filter "name=billbot" | xargs -I {} docker stop {}
sleep 5
docker run --rm -d -p 8504:8504/tcp --name billbot billbot


