import os
import json
from urllib.parse import urlparse
from dotenv import load_dotenv
from src.download import (download_file, 
                         download_file_from_hf, 
                         download_file_from_civitai)
from src.info import (create_download_info,
                      save_download_info)
from src.utils import (get_args, 
                       sanitize_and_validate_arg_input)
from src.main import (check_and_download_file)

# Load environment variables from .env file
load_dotenv()
hf_token = os.getenv("HF_TOKEN")
civitai_api_key = os.getenv("CIVITAI_API_KEY")
model_info_filepath = os.getenv("MODEL_INFO_FILE")
storage_root_dir = os.environ.get("MODEL_STORAGE_DIR")


def download_model():
    """ Main entry point for downloading a model """
    args = get_args()
    # Set up download directory
    model_type = sanitize_and_validate_arg_input(args.model_type, 'model_type_names')
    model_base = sanitize_and_validate_arg_input(args.model_base, 'model_base_names')
    download_dir = os.path.join(storage_root_dir, model_type, model_base)

    # Check if file exists, and download if necessary
    filename = check_and_download_file(args.url, download_dir, model_info_filepath, filename=args.filename)

    print(f"\nFile processed: {filename}")
    print("Download information saved to download_info.json")

def clearup_space():
    """ Main entry point for cleaning up space """
    # Read the download_info.json file
    with open(model_info_filepath, "r") as json_file:
        download_info = json.load(json_file)

    # Iterate through each entry in the download_info
    for entry in download_info.values():
        local_filename = entry.get("local_filename")
        force_keep = entry.get("force_keep", False)
        
        if force_keep:
            print(f"Skipping {local_filename} due to force_keep flag")
            continue
        
        if local_filename and os.path.exists(local_filename):
            try:
                if os.path.isfile(local_filename):
                    os.remove(local_filename)
                    print(f"Removed file: {local_filename}")
                elif os.path.isdir(local_filename):
                    import shutil
                    shutil.rmtree(local_filename)
                    print(f"Removed directory: {local_filename}")
                else:
                    print(f"Unknown file type: {local_filename}")
            except OSError as e:
                print(f"Error removing {local_filename}: {e}")
        elif local_filename:
            print(f"File not found: {local_filename}")
        else:
            print("Local filename not found in entry")

    print("Cleanup process completed.")

def redownload_models():
    """ Main entry point for redownloading models """
    # Read the download_info.json file
    with open(model_info_filepath, "r") as json_file:
        download_info = json.load(json_file)

    # Iterate through each entry in the download_info
    for entry in download_info.values():
        url = entry.get("url")
        local_filename = entry.get("local_filename")
        
        if url and local_filename:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(local_filename), exist_ok=True)
            
            # Extract the filename from the URL if not present in local_filename
            if os.path.basename(local_filename) == "":
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                local_filename = os.path.join(local_filename, filename)
            
            # Download the file
            filename = check_and_download_file(url, 
                                               os.path.dirname(local_filename), 
                                               model_info_filepath,
                                               filename=os.path.basename(local_filename))
            print(f"Redownloaded: {filename}")
        else:
            print(f"Skipping entry due to missing URL or local filename: {entry}")

    print("Redownload process completed.")