import os
import huggingface_hub
import yaml
import argparse
from dotenv import load_dotenv
load_dotenv()

config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), os.path.pardir, 'config.yaml')

def get_download_args():
    parser = argparse.ArgumentParser(description="Download AI models from various sources.")
    parser.add_argument("_cmd", help="entry command into the download function of the cozy manager")
    parser.add_argument("url", nargs='?', type=str, help="URL of the file to download")
    parser.add_argument("model_type", nargs='?', type=str, help="e.g. controlnet, unet, checkpoint")
    parser.add_argument("model_base", nargs='?', type=str, help="e.g. flux1, sdxl, sd15")
    parser.add_argument("filename", nargs='?', type=str, help="Custom filename incase repo naming not clear enough")
    parser.add_argument("--url", type=str, dest='url', help="URL of the file to download")
    parser.add_argument("--model-type", dest='model_type', type=str, help="e.g. controlnet, unet, checkpoint")
    parser.add_argument("--model-base", dest='model_base', type=str, default="flux1", help="e.g., flux1, sdxl, sd15")
    parser.add_argument("--filename", dest='filename', type=str, default=None, help="Custom filename incase repo naming not clear enough")
    return parser.parse_args()

def get_clearup_args():
    parser = argparse.ArgumentParser(description="Clear up space.")
    parser.add_argument("_cmd", help="entry command into the clearup function of the cozy manager")
    parser.add_argument("--tag", type=str, default=None, help="Clear all files with this tag")
    parser.add_argument("--model_type", type=str, default=None, help="Clear all files with this model type")
    parser.add_argument("--model_base", type=str, default=None, help="Clear all files with this model base")
    return parser.parse_args()

def get_list_args():
    parser = argparse.ArgumentParser(description="List models.")
    parser.add_argument("_cmd", help="entry command into the list function of the cozy manager")
    parser.add_argument("--all", action="store_true", help="List all models")
    parser.add_argument("--local", action="store_true", help="List local models")
    parser.add_argument("--virtual", action="store_true", help="List virtual models")
    parser.add_argument("--model-type", type=str, help="Filter models by model type")
    parser.add_argument("--model-base", type=str, help="Filter models by model base")
    parser.add_argument("--data", action="store_true", help="Show the size of the models stored locally")
    return parser.parse_args()

def get_purge_args():
    parser = argparse.ArgumentParser(description="Purge a model from storage and database.")
    parser.add_argument("_cmd", help="entry command into the purge function of the cozy manager")
    parser.add_argument("id", type=str, help="ID of the model to purge")
    parser.add_argument("--force", action="store_true", help="Force purge without confirmation")
    return parser.parse_args()

def get_edit_args():
    parser = argparse.ArgumentParser(description="Edit db entry.")
    parser.add_argument("_cmd", help="entry command into the edit function of the cozy manager")
    parser.add_argument("id", type=str, help="ID of the model entry to edit")
    return parser.parse_args()

def get_reload_args():
    parser = argparse.ArgumentParser(description="Reload models.")
    parser.add_argument("_cmd", help="entry command into the reload function of the cozy manager")
    parser.add_argument("--model-type", type=str, help="Only reload the models of this type, e.g. controlnet, unet, checkpoint")
    parser.add_argument("--model-base", type=str, help="Only reload the models of this base, e.g. flux1, sdxl, sd15")
    return parser.parse_args()

def log_into_huggingface():
    huggingface_hub.login(hf_token)

def get_absolute_model_filepath(filename, model_type, model_base):
    model_store_directory = os.getenv("MODEL_STORAGE_DIR")

    if model_type:
        model_type = sanitize_and_validate_arg_input(model_type, 'model_type_names')
    if model_base:
        model_base = sanitize_and_validate_arg_input(model_base, 'model_base_names')

    return os.path.join(model_store_directory, model_type, model_base, filename)


def sanitize_and_validate_arg_input(arg_input, mapping_type):
    arg_input = arg_input.lower().strip()
    
    # Load mappings from YAML file
    with open(config_path, 'r') as config_file:
        data = yaml.safe_load(config_file)
        mappings = data[mapping_type]
    
    for correct_value, variations in mappings.items():
        if arg_input in variations:
            return correct_value
    
    error_type = "model_type" if mapping_type == 'model_type_names' else "model_base"
    raise ValueError(f"Invalid {error_type}: {model_input}. "
                     f"Please use one of the supported {error_type}s: {', '.join(mappings.keys())}, "
                     f"or add new ones to the config.yaml")


def get_user_choice(question, options, line_len=80):
    print('-' * line_len)
    print(f'--- {question}')
    for i, o in enumerate(options):
        print(f'--- {i+1}. {o}')
    print('-' * line_len)
    return input(f"Enter your choice (1-{len(options)}): ")

def print_db_entry(id, entry, header_str=None, line_len=80):
    if header_str:
        clear_terminal()
        print('-' * line_len)
        header_len = len(header_str)
        dash_count = max(0, line_len - 5 - header_len) ## 5 for '--- ' and ' '
        print(f'--- {header_str} {"-" * dash_count}')

    print("-" * line_len)
    print(f"ID: {id}")
    print(f"URL: {entry.get('url', 'N/A')}")
    print(f"Local Filename: {entry.get('local_filename', 'N/A')}")
    print(f"Model Type: {entry.get('model_type', 'N/A')}")
    print(f"Model Base: {entry.get('model_base', 'N/A')}")
    print(f"Download Date: {entry.get('download_date', 'N/A')}")
    tags = entry.get('tags', [])
    print(f"Tags: {', '.join(tags) if tags else 'None'}")
    print("-" * line_len)

def clear_terminal():
    print("\033c", end="")

def get_filenames_to_auto_rename():
    """Read the config.yaml file and return the filenames_to_auto_rename list."""
    with open(config_path, 'r') as config_file:
        config_data = yaml.safe_load(config_file)
    
    return config_data.get('filenames_to_auto_rename', [])

def get_size_of_path(path):
    """ returns the size of the path in megabytes
    provided path can be either 
        - a file OR
        - a directory
    """
    if not os.path.exists(path):
        return 0

    total_size = 0
    if os.path.isfile(path):
        total_size = os.path.getsize(path)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)

    ## convert to MB
    total_size = round(total_size / (1024 * 1024), 2)
    return total_size

def get_huggingface_repo_id(url):
    return "/".join(url.split("/")[3:5])

def get_huggingface_repo_author(url):
    return "/".join(url.split("/")[3:4])

def get_huggingface_repo_name(url):
    return "/".join(url.split("/")[4:5])

def get_huggingface_filename(url):
    return url.split("/")[-1]   

def validate_filename(url):
    print('validating filename:')
    auto_rename_filenames = get_filenames_to_auto_rename()
    print(f'auto_rename_filenames: {auto_rename_filenames}')
    filename = os.path.basename(url)
    print(f'filename: {filename}')

    # Split the filename and extension
    filename_base, ext = os.path.splitext(filename)
    print(f'name: {filename_base}, ext: {ext}')

    ## now check if the filename should be renamed..
    if filename_base in auto_rename_filenames:
        repo_name = get_huggingface_repo_name(url)
        filename = f"{repo_name}{ext}"
        print(f'filename: {filename}')

    print('returning filename: ', filename)

    return filename