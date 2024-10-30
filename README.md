# aidb-rag
An application to demonstrate how can you make a RAG using `EDB's aidb` and `PostgreSQL`.
The chat console below illustrates the features of a RAG system designed to answer questions specifically about EDB Bloggers. 
The biographies have been collected from EDB’s website. The system can work with either a local folder containing text files or an S3 bucket, and aidb will manage the content from these sources seamlessly. Once a new file is added, aidb automates the process by integrating the new information into the pipeline, enabling the RAG to respond with up-to-date answers. If no relevant data is available, it will respond with: "I'm sorry, I couldn't find any information about this person."



![Sample Chat Console Output](/imgs/gui.png)

## Requirements
- Python3
- PostgreSQL
- aidb

## Install

Clone the repository

```
git clone git@github.com:gulcin/aidb-rag-app.git
cd aidb-rag-app
```

Install Dependencies

```
virtualenv env -p `which python`
source env/bin/activate
pip install -r requirements.txt
```

Add your .env variable

```
cp .env-example .env
```

## Run

First run your `aidb` extension by following the step by step installation guide: https://www.enterprisedb.com/docs/edb-postgres-ai/ai-ml/install-tech-preview/

Make sure your aidb extension is ready to accept connections. 

Then running subcommands is divided into two phase. The first phase to prepare database and creating retriever and embeddings then next is using the chat functionality:

```
# Initialization phase
python app.py --help

usage: python app.py [-h] {create-db, import-data, import-data-s3, update-data-s3, chat} {data_source}

e.g: python app.py import-data-pg data/

# Chat phase
streamlit run app_x.py --help

usage with HF Generative Models: streamlit run app.py chat {retriever_name}
usage with OpenAI: streamlit run app_openai.py chat {retriever_name}
```
```
Application Description

options:
  -h, --help            show this help message and exit

Subcommands:
  {create-db, import-data, import-data-s3, update-data-s3, chat}
                        Display available subcommands
    create-db           Create a database
    import-data-pg      Use PG table as a source for aidb retriever
    import-data-s3      Use S3 bucket as a source for aidb retriever
    update-data-s3      Update embeddings using new data in S3 source
    chat                Use chat feature
```

