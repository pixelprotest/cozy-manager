import sys
import os
import json
from urllib.parse import urlparse
from dotenv import load_dotenv
from src.utils import (get_download_args, 
                       get_clearup_args, 
                       sanitize_and_validate_arg_input,
                       get_absolute_model_filepath)
from src.main import check_and_download_file

# Load environment variables from .env file
load_dotenv()
hf_token = os.getenv("HF_TOKEN")
civitai_api_key = os.getenv("CIVITAI_API_KEY")
db_filepath = os.getenv("MODEL_INFO_FILE")
storage_root_dir = os.environ.get("MODEL_STORAGE_DIR")


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

def get_cozy_command():
    if len(sys.argv) < 2:
        print("--- Missing an actionable command" )
        print("--- Usage:")
        print("--- > cozy <download|clear|reload> ... etc")
        sys.exit(1)

    cmd = sys.argv[1]
    return cmd

def main():
    cmd = get_cozy_command()

    if cmd=="download":
        download_model()
    elif cmd=="clear":
        clearup_space()
    elif cmd=="reload":
        redownload_models()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)