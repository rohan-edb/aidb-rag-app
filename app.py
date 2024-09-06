import argparse
# import streamlit as st
from enum import Enum
from dotenv import load_dotenv
import os
import torch

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

from commands.chat import chat
from commands.create_db import create_db
from commands.import_data import import_data_s3, import_data_pg, update_s3_data

load_dotenv()


class Command(Enum):
    CREATE_DB = "create-db"
    UPDATE_DATA_S3 = "update-data-s3"
    IMPORT_DATA_S3 = "import-data-s3"
    IMPORT_DATA_PG = "import-data-pg"
    CHAT = "chat"


def main():
    parser = argparse.ArgumentParser(description="Application Description")

    subparsers = parser.add_subparsers(
        title="Subcommands",
        dest="command",
        help="Display available subcommands",
    )

    # create-db command
    subparsers.add_parser(
        Command.CREATE_DB.value, help="Create a database"
    ).set_defaults(func=create_db)

    # import-data-s3 command
    import_data_s3_parser = subparsers.add_parser(
        Command.IMPORT_DATA_S3.value, help="Import data from S3 bucket"
    )
    import_data_s3_parser.add_argument(
        "bucket_name", type=str, help="Specify the s3 bucket"
    )
    import_data_s3_parser.set_defaults(func=import_data_s3)

    # update_s3_data command
    import_data_s3_parser = subparsers.add_parser(
        Command.UPDATE_DATA_S3.value, help="Update retriever from S3 bucket"
    )
    import_data_s3_parser.add_argument(
        "bucket_name", type=str, help="Specify the s3 bucket"
    )
    import_data_s3_parser.add_argument(
        "retriever_name", type=str, help="Specify the retriever name"
    )
    import_data_s3_parser.set_defaults(func=update_s3_data)
    

    # import-data-pg command
    import_data_pg_parser = subparsers.add_parser(
        Command.IMPORT_DATA_PG.value, help="Import data from PG table with auto_enable=on"
    )
    import_data_pg_parser.add_argument(
        "data_dir", type=str, help="Specify the data directory where PDFs stored"
    )
    import_data_pg_parser.set_defaults(func=import_data_pg)

    # chat command
    chat_parser = subparsers.add_parser(Command.CHAT.value, help="Use chat feature")
    chat_parser.add_argument("retriever_name", type=str, help="Specify the retriever name")
    chat_parser.set_defaults(func=chat)

    args = parser.parse_args()

    if args.command == Command.CHAT.value:
        if hasattr(args, "func"):
            if torch.cuda.is_available():
                device = "cuda"
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.bfloat16,
                )
                dtype = torch.float16
            elif torch.backends.mps.is_available():
                device = "mps"
                bnb_config = None
                dtype = torch.float16  # MPS supports float16å

            else:
                device = "cpu"
                bnb_config = None
            tokenizer = AutoTokenizer.from_pretrained(
                os.getenv("TOKENIZER_NAME"),
                token=os.getenv("HUGGING_FACE_ACCESS_TOKEN"),
            )
            model = AutoModelForCausalLM.from_pretrained(
                os.getenv("MODEL_NAME"),
                token=os.getenv("HUGGING_FACE_ACCESS_TOKEN"),
                quantization_config=bnb_config,
                device_map=device,
                torch_dtype=torch.float16,
            )

            args.func(args, model, device, tokenizer)
    elif (
        (args.command == Command.IMPORT_DATA_S3.value)
        or (args.command == Command.UPDATE_DATA_S3.value)
        or (args.command == Command.IMPORT_DATA_PG.value)
        or (args.command == Command.CREATE_DB.value)
    ):
        args.func(args)
    else:
        print("Invalid command. Use '--help' for assistance.")


if __name__ == "__main__":
    main()
