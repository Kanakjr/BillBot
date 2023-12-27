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

def df_to_csv_string(df):
        csv_string = df.to_csv(index=False)
        lines = csv_string.split('\n')
        lines = lines[1:]
        prefixed_lines = [f"{line}" for line in lines]
        return '\n'.join(prefixed_lines)

def combine_dataframes_to_csv_string(df_list):
    combined_csv_string = ""
    for i, df in enumerate(df_list, start=1):
        combined_csv_string += f'### table{i}:\n'
        combined_csv_string += df_to_csv_string(df)
        combined_csv_string += '\n\n'
    return combined_csv_string