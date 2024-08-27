import os
import json
from src.download import (download_file_from_hf, 
                          download_file_from_civitai, 
                          download_file)
from src.info import (create_download_info, 
                      save_download_info)
from src.utils import get_absolute_model_filepath
from dotenv import load_dotenv
load_dotenv()

db_filepath = os.getenv("MODEL_INFO_FILE")

def purge_model_from_db(model_id, force=False):
    """ Main entry point for purging a model """
    # Load the JSON file
    with open(db_filepath, "r") as f:
        db = json.load(f)

    # Check if the ID exists in the download_info
    if model_id not in db:
        print(f"Error: Model with ID '{model_id}' not found.")
        return

    # Get the model information
    model_info = db[model_id]
    local_filename = model_info.get('local_filename')
    model_type = model_info.get('model_type')
    model_base = model_info.get('model_base')

    # Confirm deletion if force is False
    if not force:
        confirm = input(f"Are you sure you want to purge model '{model_id}'? This action cannot be undone. (y/N): ")
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
    del db[model_id]

    # Save the updated JSON file
    with open(db_filepath, "w") as f:
        json.dump(db, f, indent=4)

    print(f"Model '{model_id}' has been purged from the database.")


def check_and_download_file(url, 
                            download_dir, 
                            model_info_filepath, 
                            model_type,
                            model_base,
                            filename=None):
    if not os.path.exists(model_info_filepath):
        with open(model_info_filepath, "w") as json_file:
            json.dump({}, json_file)

    with open(model_info_filepath, "r") as json_file:
        download_info = json.load(json_file)
    
    should_add_info = True ## init to true
    ## here we check if the file already exists, so we can bypass the download
    for entry in download_info.values():
        if entry["url"] == url:
            local_filename = entry["local_filename"]
            local_filepath = get_absolute_model_filepath(local_filename, model_type, model_base)
            if os.path.exists(local_filepath):
                print(f"File already exists: {local_filepath}")
                return local_filepath
            else:
                print(f"File info found, but file missing. Re-downloading: {url}")
                should_add_info = False
                break
    
    # If we get here, either the URL wasn't found or the file was missing
    if 'huggingface.co' in url:
        filename = download_file_from_hf(url, filename=filename, download_dir=download_dir)
    elif 'civitai.com' in url:
        filename = download_file_from_civitai(url, filename=filename, download_dir=download_dir) 
    else:
        filename = download_file(url, filename=filename, download_dir=download_dir)

    if should_add_info:
        # Create and save download information
        download_info = create_download_info(url, 
                                             filename, 
                                             model_type,
                                             model_base,
                                             model_info_filepath)
        save_download_info(download_info, model_info_filepath)
    
    return filename
