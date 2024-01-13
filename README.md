# BillBot

## Overview

The **BillBot** project is a cutting-edge application designed to revolutionize the way individuals manage and extract information from bills, receipts, and various financial documents. In today's digital world, people often find themselves overwhelmed by the abundance of such documents, typically stored in complex PDF formats with non-standardized structures.

The primary objective of BillBot is to simplify the management and retrieval of crucial information from these documents. The app provides a user-friendly, natural language interface, allowing users to interact with their bills effortlessly. By harnessing advanced technologies, BillBot overcomes the challenges posed by the unstructured nature of documents and the semantic diversity found in bills.

## Features

### 1. **Billing Document Bot**

#### Profile

- **Description:** The Billing Document Bot is an AI-powered bot specifically designed to answer questions based on any billing document.
- **Functionality:**
  - The bot can answer questions related to billing documents.
  - It relies solely on the document summary and the data within the document.
  - The document data is presented in the form of key-value pairs.
  - If the bot cannot find the answer to a question, it informs the user accordingly.

#### Usage

To interact with the Billing Document Bot, users can ask questions about their billing documents, and the bot will provide accurate and relevant answers based on the document's information.

### 2. **Document Analysis**

The app includes a powerful document analysis module that utilizes Azure Form Recognizer to analyze PDF documents. The `formrecognizer.py` script demonstrates how to extract information from a PDF document, providing a structured output.

### 3. **Language Model Utility**

The `llm_utils.py` script integrates with the LangChain library, offering various utility functions. These functions include:

- Summarizing document content.
- Generating recommended questions based on document content and key-value pairs.
- Extracting metadata such as document type, language, currency, etc.

### 4. **Streamlit Interface**

The `main.py` script orchestrates the Streamlit interface, offering users an interactive and visually appealing environment to upload PDF files, ask questions to the Billing Document Bot, and view document content, summaries, and key information.

## Usage

1. **Upload PDF:** Users can upload their PDF documents through the Streamlit interface.
2. **Ask Questions:** Utilize the Billing Document Bot by entering questions related to the uploaded document.
3. **View Information:** Explore document content, summaries, key information, and recommended questions within the Streamlit interface.

## Installation

Ensure you have the required dependencies by installing them using the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Running the App

Execute the following command to run the BillBot app:

```bash
streamlit run main.py
```

## Project Structure

The project follows a modular structure with key components in the `app` directory:

- `app/`: Contains the main application files.
- `app/docs/bot.txt`: Provides information about the Billing Document Bot.
- `app/formrecognizer.py`: Handles PDF document analysis using Azure Form Recognizer.
- `app/llm_utils.py`: Integrates language model utilities for summarization and metadata extraction.
- `app/main.py`: Orchestrates the Streamlit interface.
- `app/utils.py`: Contains utility functions for data extraction and processing.
- `app/requirements.txt`: Lists project dependencies.
- `build_readme_prompt.sh`: Script to generate a `readme_prompt.txt` file based on the project structure.
- `rundocker.sh`: Script for building and running the app using Docker.

## Acknowledgments

- The project utilizes Azure Form Recognizer for document analysis.
- LangChain provides essential language model utilities.
- Streamlit simplifies the creation of interactive web applications.

## Developer

**Kanak Dahake**
- Email: ksdusa4@gmail.com
- Website: [kanakjr.in](https://kanakjr.in)
- LinkedIn: [Kanak Dahake](https://www.linkedin.com/in/kanak-dahake)
- GitHub: [Kanakjr](https://github.com/Kanakjr)

---

*This project is designed to enhance the accessibility and understanding of billing documents, making life simpler in the digital era using the power of AI.*