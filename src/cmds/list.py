import os
import json
from src.utils.args import get_list_args
from src.utils.generic import (sanitize_and_validate_arg_input, 
                               get_absolute_model_filepath, 
                               get_size_of_path)
from src.utils.db import (read_db, print_db_entries) 
from dotenv import load_dotenv
load_dotenv()

storage_root_dir = os.getenv("MODEL_STORAGE_DIR")
db_filepath = os.getenv("MODEL_INFO_FILE")

def run_list():
    """ Main entry point for listing models """
    args = get_list_args()

    db = read_db()

    if args.all or (not args.local and not args.virtual and not args.model_type and not args.model_base and not args.data):
        print_db_entries(list(db.keys()))

    elif args.local:
        for id, entry in db.items():
            local_filename = entry.get('local_filename', 'N/A')
            model_type = entry.get('model_type', 'N/A')
            model_base = entry.get('model_base', 'N/A')
            local_filepath = get_absolute_model_filepath(local_filename, model_type, model_base)
            
            if os.path.exists(local_filepath):
                print(f"ID: {id}")
                print(f"Local Filename: {local_filename}")
                print(f"Model Type: {model_type}")
                print(f"Model Base: {model_base}")
                print(f"File Size: {os.path.getsize(local_filepath) / (1024 * 1024):.2f} MB")
                print("-" * 40)

    elif args.model_type:
        model_type = sanitize_and_validate_arg_input(args.model_type, 'model_type_names')
        matching_models = [[id, entry] for id, entry in db.items() if entry.get('model_type') == model_type]
        id_list = [id for id, entry in matching_models]
        print("-" * 80)
        print(f"Found {len(matching_models)} models for model type '{model_type}':")
        print_db_entries(id_list)
    elif args.model_base:
        model_base = sanitize_and_validate_arg_input(args.model_base, 'model_base_names')
        matching_models = [[id, entry] for id, entry in db.items() if entry.get('model_base') == model_base]
        id_list = [id for id, entry in matching_models]
        print("-" * 80)
        print(f"Found {len(matching_models)} models for model base '{model_base}':")
        print_db_entries(id_list)
    elif args.data:
        print("Calculating the size of the models stored locally...")
        total_size = 0
        for entry in db.values():
            local_filename = entry.get('local_filename', 'N/A')
            model_type = entry.get('model_type', 'N/A')
            model_base = entry.get('model_base', 'N/A')
            local_filepath = get_absolute_model_filepath(local_filename, model_type, model_base)
            total_size += get_size_of_path(local_filepath)
        print(f"Total size of models stored locally: {total_size} MB")
    elif args.virtual:
        print("Listing the models that are not stored locally...")
        for entry in db.values():
            if not entry.get('local_filename'):
                print(f"ID: {entry.get('id', 'N/A')}")
                print(f"URL: {entry.get('url', 'N/A')}")
                print(f"Model Base: {entry.get('model_base', 'N/A')}")
                print("-" * 40)
    else:
        print("Please specify --all to list all models.")