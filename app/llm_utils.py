from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain.schema.document import Document
import streamlit as st
import os


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
    with st.spinner(task):
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
    with st.spinner(task):
        result = chain.invoke(docs, config={"run_name": task})
    return result["output_text"]


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)  # Cache data for 12 hours
def get_recommended_question(document_summary, key_values=[]):
    key_values = format_dict_as_string(key_values)
    prompt = PromptTemplate(
        input_variables=["document_summary", "key_values"],
        template="""## You are given a document summary and some of the key value data from the document. 
## Document Summary{document_summary} 
## Document Data:{key_values}

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


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)  # Cache data for 12 hours
def get_billbot_response(question, document_summary, key_values=[]):
    key_values = format_dict_as_string(key_values)
    prompt = PromptTemplate(
        input_variables=["question", "document_summary", "key_values"],
        template="""## You are given a document summary and some of the key value data from the document. 
## Document Summary{document_summary} 
## Document Data:{key_values}

## You have to answer the given user question stricty from the document. 
Do not assume any values or answer on your own. 
If you don't know the answer resppnd with "I don't know the answer"

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

    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        module="streamlit.runtime.caching.cache_data_api",
    )
    load_dotenv("./app/.env")
