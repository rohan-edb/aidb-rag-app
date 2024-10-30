import json
import ast
import boto3
import os
from db import get_connection
from botocore.handlers import disable_signing

template = """<s>[INST]
You are a friendly documentation search bot.
Use following piece of context to answer the question.
If the context is empty, try your best to answer without it.
Never mention the context.
Try to keep your answers concise unless asked to provide details.

Context: {context}
Question: {question}
[/INST]</s>
Answer:
"""

def connect_to_s3():
    s3 = boto3.resource(
        service_name="s3",
        endpoint_url='http://s3.eu-central-1.amazonaws.com',
    )
    s3.meta.client.meta.events.register("choose-signer.s3.*", disable_signing)
    return s3

def retrieve_s3_data(file_names):
    s3 = connect_to_s3()
    bucket = s3.Bucket('aidb-rag-app')

    return [f for name in file_names for f in bucket.objects.filter(Prefix=name)]

def retrieve_augmentation(query, topk, retriever_name):
    # clean punctuations and extra spaces 
    query_str = ''.join(e for e in query if e.isalnum() or e.isspace())
    rag_query = ""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"SELECT data_sources FROM aidb.retrievers WHERE name=%s;", (retriever_name,)
            )
            results = cursor.fetchone()
            if results[0] == "pg":
                cursor.execute(
                    f"SELECT data FROM aidb.retrieve(%s, %s, %s);", (query_str, topk, retriever_name)
                )
                rag_query = ' '.join(row[0] for row in cursor.fetchall())
            else:
                cursor.execute(
                    f"SELECT data FROM aidb.retrieve(%s, %s, %s);", (query_str, topk, retriever_name)
                )
                topk_filename = []
                for result in cursor.fetchall():
                    try:
                        data = json.loads(result[0])
                    except json.JSONDecodeError:
                        data = ast.literal_eval(result[0])
                    topk_filename.append(data['text_id'])
                file_list = retrieve_s3_data(topk_filename)
                for file in file_list:
                    file_context = file.get()["Body"].read()
                    text_content = file_context.decode(encoding="utf-8", errors="ignore")
                    rag_query += text_content
            conn.commit()
    return rag_query

def rag_query(tokenizer, model, device, query, topk, retriever_name):
    client = tokenizer
    rag_query = retrieve_augmentation(query, topk, retriever_name)
    query_template = template.format(context=rag_query, question=query)
    if model.startswith("gpt"):
        completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": query_template,
            }
        ]
    )
        return completion.choices[0].message.content
    else:
        input_ids = tokenizer.encode(query_template, return_tensors="pt")

        model.generation_config.pad_token_id = tokenizer.pad_token_id
        generated_response = model.generate(input_ids.to(device), max_new_tokens=100)
        return tokenizer.decode(generated_response[0][input_ids.shape[-1]:], skip_special_tokens=True)