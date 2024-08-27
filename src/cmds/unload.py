import os
import json
from urllib.parse import urlparse
from src.utils import (get_download_args, 
                       get_clearup_args, 
                       get_list_args, 
                       get_edit_args,
                       get_reload_args,
                       sanitize_and_validate_arg_input, 
                       get_absolute_model_filepath, 
                       get_user_choice,
                       print_db_entry,
                       clear_terminal,
                       get_size_of_path) 
from src.main import check_and_download_file
from dotenv import load_dotenv
load_dotenv()

storage_root_dir = os.getenv("MODEL_STORAGE_DIR")
db_filepath = os.getenv("MODEL_INFO_FILE")

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
