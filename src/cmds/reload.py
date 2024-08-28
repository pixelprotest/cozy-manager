import os
import json
from urllib.parse import urlparse
from src.utils.args import get_reload_args
from src.utils.generic import get_absolute_model_filepath
from src.utils.db import read_db, update_entry
from src.main import check_and_download_file
from dotenv import load_dotenv
load_dotenv()

storage_root_dir = os.getenv("MODEL_STORAGE_DIR")
db_filepath = os.getenv("MODEL_INFO_FILE")

def run_reload():
    """ Main entry point for redownloading models """
    args = get_reload_args()

    db = read_db()

    # Iterate through each entry in the db
    for entry in db.values():
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
                                               model_type=model_type,
                                               model_base=model_base,
                                               filename=os.path.basename(local_filepath))
        else:
            print(f"Skipping entry due to missing URL or local filename: {entry}")

    print("Redownload process completed.")
