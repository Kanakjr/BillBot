# %%
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore',category=Warning)
from utils import (
    convert_tables_to_df,
    get_or_generate_analyze_json,
    generate_transaction_df
)
load_dotenv("./app/.env")

DATA_FOLDER = "./app/data"
pdf_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".pdf")]
pdf_files = sorted(pdf_files)

# %%
transaction_df_list = []
for pdf_path in pdf_files:
    pdf_path = os.path.join(DATA_FOLDER,pdf_path)
    print(f'File: {pdf_path}')
    json_data = get_or_generate_analyze_json(pdf_path)
    # pdf_text = extract_text_from_pdf(json_data)
    # key_value_pairs = convert_keyvalues_to_dict(json_data)
    df_list = convert_tables_to_df(json_data)
    final_transaction_df_list = generate_transaction_df(df_list=df_list)
    for transaction_df in final_transaction_df_list:
        # print(f'Table Columns:{list(transaction_df.columns)}')
        print(transaction_df[:3].to_csv())
        transaction_df_list.append(transaction_df)
    print('\n')
# %%

def process_credit_card_data(df_list):
    # Define a dictionary to map input column names to output column names
    column_mapping = {
        'Date': 'Date',
        'Transaction Details': 'Transaction Description',
        'Transaction Description': 'Transaction Description',
        'Amount (in₹)': 'Amount',
        'Amount (in Rs.)': 'Amount',
        'Amount': 'Amount',
        'Particulars': 'Transaction Description',
        # 'Intl.# amount': 'Amount',
        # 'Intl. amount': 'Amount',
    }

    # Initialize an empty list to store the consolidated dataframes
    consolidated_dfs = []

    # Iterate through each dataframe in the input list
    for df in df_list:
        # Find relevant columns present in the dataframe
        relevant_columns = [col for col in column_mapping.keys() if col in df.columns]

        # Check if any relevant columns are present
        print(list(df.columns))
        print(relevant_columns)
        print('')
        if len(relevant_columns) == 3:
            # Map columns to the output format
            mapped_df = df[relevant_columns].rename(columns=column_mapping)

            # Append the mapped dataframe to the list
            consolidated_dfs.append(mapped_df)

    # Concatenate all the dataframes in the list
    consolidated_df = pd.concat(consolidated_dfs, ignore_index=True)

    consolidated_df = consolidated_df.dropna()
    consolidated_df['Credit/Debit'] = np.where(consolidated_df['Amount'].str.contains('Cr'), 'Credit', 'Debit')

    # Convert Amount column to numeric and handle commas in numeric values
    # consolidated_df['Amount'] = pd.to_numeric(consolidated_df['Amount'].replace('[\$,]', '', regex=True), errors='coerce')
    # consolidated_df['Amount'] = pd.to_numeric(consolidated_df['Amount'].replace('[^\d.]', '', regex=True), errors='coerce')

    return consolidated_df,consolidated_dfs

consolidated_df,consolidated_dfs = process_credit_card_data(transaction_df_list)


# %%
consolidated_df.head()
# %%
