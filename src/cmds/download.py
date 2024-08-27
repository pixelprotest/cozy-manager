import os
from src.utils.generic import (get_download_args, 
                               sanitize_and_validate_arg_input)
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