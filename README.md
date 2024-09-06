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

Make sure your aidb extension is ready to accept connections. Then you can continue as follows:

```
python app.py --help

usage: app.py [-h] {create-db,import-data,chat} {data_source}

e.g: python app.py import-data sample.pdf

Application Description

options:
  -h, --help            show this help message and exit

Subcommands:
  {create-db,import-data,chat}
                        Display available subcommands
    create-db           Create a database
    import-data         Import data
    chat                Use chat feature
```

