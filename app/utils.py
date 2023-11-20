import json, os
import pandas as pd
from llm_utils import summarize_bill, get_recommended_question
import base64

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

def displayPDF(file):
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_md = F'<embed src="data:application/pdf;base64,{base64_pdf}" width=100% height="500" type="application/pdf">'
    return pdf_md
