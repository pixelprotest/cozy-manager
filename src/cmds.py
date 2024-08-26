import os
import json
from urllib.parse import urlparse
from src.utils import (get_download_args, 
                       get_clearup_args, 
                       get_list_args, 
                       get_purge_args,
                       sanitize_and_validate_arg_input, 
                       get_absolute_model_filepath) 
from src.main import check_and_download_file
from dotenv import load_dotenv
load_dotenv()

storage_root_dir = os.getenv("MODEL_STORAGE_DIR")
db_filepath = os.getenv("MODEL_INFO_FILE")

def download_model():
    """ Main entry point for downloading a model """
    args = get_download_args()
    # Set up download directory
    model_type = sanitize_and_validate_arg_input(args.model_type, 'model_type_names')
    model_base = sanitize_and_validate_arg_input(args.model_base, 'model_base_names')
    download_dir = os.path.join(storage_root_dir, model_type, model_base)

    # Check if file exists, and download if necessary
    filename = check_and_download_file(args.url, 
                                       download_dir, 
                                       db_filepath, 
                                       model_type=model_type, 
                                       model_base=model_base,
                                       filename=args.filename)
    print(f"\nFile processed: {filename}")
    print("Download information saved to download_info.json")

def clearup_space():
    """ Main entry point for cleaning up space """
    args = get_clearup_args()

    clear_model_type = None
    clear_model_base = None
    if args.model_type:
        clear_model_type = sanitize_and_validate_arg_input(args.model_type, 'model_type_names')
    if args.model_base:
        clear_model_base = sanitize_and_validate_arg_input(args.model_base, 'model_base_names')

    # Read the download_info.json file
    with open(db_filepath, "r") as json_file:
        download_info = json.load(json_file)

    # Iterate through each entry in the download_info
    for entry in download_info.values():
        local_filename = entry.get("local_filename")
        force_keep = entry.get("force_keep", False)
        tags = entry.get("tags", [])
        model_type = entry.get("model_type", None)
        model_base = entry.get("model_base", None)
        local_filepath = get_absolute_model_filepath(local_filename, model_type, model_base)

        ## if we passed in a specific tag, and the entry has a tag
        if args.tag:
            if args.tag not in tags:
                ## then we can skip this file
                continue

        if clear_model_type:
            if clear_model_type!= model_type:
                continue ## then we bypass this file

        if clear_model_base:
            if clear_model_base!= model_base:
                continue
        
        ## if we passed in a force_keep flag, and the entry has a force_keep flag
        if force_keep:
            ## then we can skip this file
            print(f"Skipping {local_filename} due to force_keep flag")
            continue
        
        if local_filename and os.path.exists(local_filepath):
            try:
                if os.path.isfile(local_filepath):
                    os.remove(local_filepath)
                    print(f"Removed file: {local_filename}")
                elif os.path.isdir(local_filepath):
                    import shutil
                    shutil.rmtree(local_filepath)
                    print(f"Removed directory: {local_filename}")
                else:
                    print(f"Unknown file type: {local_filename}")
            except OSError as e:
                print(f"Error removing {local_filename}: {e}")
        elif local_filename:
            print(f"File not found: {local_filepath}")
        else:
            print("Local filename not found in entry")

    print("Cleanup process completed.")

def redownload_models():
    """ Main entry point for redownloading models """
    # Read the download_info.json file
    with open(db_filepath, "r") as json_file:
        download_info = json.load(json_file)

    # Iterate through each entry in the download_info
    for entry in download_info.values():
        url = entry.get("url")
        local_filename = entry.get("local_filename")
        model_type = entry.get("model_type")
        model_base = entry.get("model_base")
        local_filepath = get_absolute_model_filepath(local_filename, model_type, model_base)
        
        if url and local_filename:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(local_filepath), exist_ok=True)
            
            # Extract the filename from the URL if not present in local_filename
            if os.path.basename(local_filename) == "":
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                local_filename = os.path.join(local_filepath, filename)
            
            # Download the file
            filename = check_and_download_file(url, 
                                               os.path.dirname(local_filepath), 
                                               db_filepath,
                                               model_type=model_type,
                                               model_base=model_base,
                                               filename=os.path.basename(local_filepath))
        else:
            print(f"Skipping entry due to missing URL or local filename: {entry}")

    print("Redownload process completed.")

def purge_model():
    """ Main entry point for purging a model """
    args = get_purge_args()
    # Load the JSON file
    with open(db_filepath, "r") as f:
        download_info = json.load(f)

    # Check if the ID exists in the download_info
    if args.id not in download_info:
        print(f"Error: Model with ID '{args.id}' not found.")
        return

    # Get the model information
    model_info = download_info[args.id]
    local_filename = model_info.get('local_filename')
    model_type = model_info.get('model_type')
    model_base = model_info.get('model_base')

    # Confirm deletion if --force is not used
    if not args.force:
        confirm = input(f"Are you sure you want to purge model '{args.id}'? This action cannot be undone. (y/N): ")
        if confirm.lower() != 'y':
            print("Purge cancelled.")
            return

    # Remove the file if it exists
    if local_filename:
        local_filepath = get_absolute_model_filepath(local_filename, model_type, model_base)
        if os.path.exists(local_filepath):
            try:
                os.remove(local_filepath)
                print(f"File '{local_filepath}' has been removed.")
            except OSError as e:
                print(f"Error removing file: {e}")
        else:
            print(f"File '{local_filepath}' not found.")

    # Remove the entry from the JSON file
    del download_info[args.id]

    # Save the updated JSON file
    with open(db_filepath, "w") as f:
        json.dump(download_info, f, indent=4)

    print(f"Model '{args.id}' has been purged from the database.")

def list_models():
    """ Main entry point for listing models """
    args = get_list_args()
    # Load the JSON file
    with open(db_filepath, "r") as f:
        download_info = json.load(f)

    if args.all:
        for id, entry in download_info.items():
            print(f"ID: {id}")
            print(f"URL: {entry.get('url', 'N/A')}")
            print(f"Local Filename: {entry.get('local_filename', 'N/A')}")
            print(f"Model Type: {entry.get('model_type', 'N/A')}")
            print(f"Model Base: {entry.get('model_base', 'N/A')}")
            print(f"Download Date: {entry.get('download_date', 'N/A')}")
            print("-" * 40)
    elif args.local:
        for id, entry in download_info.items():
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
        matching_models = [entry for entry in download_info.values() if entry.get('model_type') == model_type]
        print("-" * 40)
        print(f"Found {len(matching_models)} models for model type '{model_type}':")
        print("-" * 40)
        for entry in matching_models:
            print(f"ID: {entry.get('id', 'N/A')}")
            print(f"URL: {entry.get('url', 'N/A')}")
            print(f"Local Filename: {entry.get('local_filename', 'N/A')}")
            print(f"Model Base: {entry.get('model_base', 'N/A')}")
            print(f"Download Date: {entry.get('download_date', 'N/A')}")
            print("-" * 40)
    elif args.model_base:
        model_base = sanitize_and_validate_arg_input(args.model_base, 'model_base_names')
        matching_models = [entry for entry in download_info.values() if entry.get('model_base') == model_base]
        print("-" * 40)
        print(f"Found {len(matching_models)} models for model base '{model_base}':")
        print("-" * 40)
        for entry in matching_models:
            print(f"ID: {entry.get('id', 'N/A')}")
            print(f"URL: {entry.get('url', 'N/A')}")
            print(f"Local Filename: {entry.get('local_filename', 'N/A')}")
            print(f"Model Type: {entry.get('model_type', 'N/A')}")
            print(f"Download Date: {entry.get('download_date', 'N/A')}")
            print("-" * 40)
    else:
        print("Please specify --all to list all models.")