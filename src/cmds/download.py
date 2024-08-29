import os
from src.utils.args import get_download_args
from src.utils.generic import sanitize_and_validate_arg_input
from src.main import check_and_download_file
from src.utils.metadata import get_model_info
from dotenv import load_dotenv
load_dotenv()

storage_root_dir = os.getenv("MODEL_STORAGE_DIR")
db_filepath = os.getenv("MODEL_INFO_FILE")

def run_download():
    """ Main entry point for downloading a model """
    args = get_download_args()
    # Set up download directory
    if args.model_type and args.model_base:
        model_type = sanitize_and_validate_arg_input(args.model_type, 'model_type_names')
        model_base = sanitize_and_validate_arg_input(args.model_base, 'model_base_names')
    else:
        model_type, model_base = get_model_info(args.url)
    download_dir = os.path.join(storage_root_dir, model_type, model_base)

    # Check if file exists, and download if necessary
    filename = check_and_download_file(args.url, 
                                       download_dir, 
                                       model_type=model_type, 
                                       model_base=model_base,
                                       filename=args.filename)
    print(f"\nFile processed: {filename}")