# aidb-rag
An application to demonstrate how can you make a RAG using EDB's aidb and PostgreSQL

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

