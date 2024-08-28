import os
import huggingface_hub
import yaml
from src.utils.db import get_entry_data
from dotenv import load_dotenv
load_dotenv()

config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), os.path.pardir, 'config.yaml')

def log_into_huggingface():
    huggingface_hub.login(hf_token)

def get_absolute_model_filepath(filename, model_type, model_base):
    model_store_directory = os.getenv("MODEL_STORAGE_DIR")

    if model_type:
        model_type = sanitize_and_validate_arg_input(model_type, 'model_type_names')
    if model_base:
        model_base = sanitize_and_validate_arg_input(model_base, 'model_base_names')

    return os.path.join(model_store_directory, model_type, model_base, filename)

def is_model_local(filename, model_type, model_base):
    filepath = get_absolute_model_filepath(filename, model_type, model_base) 
    return os.path.exists(filepath)


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

def print_db_entry(id, 
                   header_str=None, 
                   line_len=80, 
                   clear=False, 
                   divider_start=True, 
                   divider_end=True, 
                   mode='detailed'):
    
    if clear: ## if True, we clear the screen
        clear_terminal()

    if header_str:
        print('-' * line_len)
        header_len = len(header_str)
        dash_count = max(0, line_len - 5 - header_len) ## 5 for '--- ' and ' '
        print(f'--- {header_str} {"-" * dash_count}')

    ## ------------------------------------------------------------------
    if divider_start:
        print("-" * line_len)
    ## ------------------------------------------------------------------

    url = get_entry_data(id, 'url', 'N/A')
    local_filename = get_entry_data(id, 'local_filename', 'N/A')
    model_type = get_entry_data(id, 'model_type', 'N/A')
    model_base = get_entry_data(id, 'model_base', 'N/A')
    if mode=='detailed':
        ## load some extra data
        download_date = get_entry_data(id, 'download_date', 'N/A')
        tags = get_entry_data(id, 'tags', [])
        print(f"ID: {id}")
        print(f"URL: {url}")
        print(f"Local Filename: {local_filename}")
        print(f"Model Type: {model_type}")
        print(f"Model Base: {model_base}")
        print(f"Download Date: {download_date}")
        print(f"Tags: {', '.join(tags) if tags else 'None'}")
    elif mode=='minimal':
        print(f"[{id}] :: {model_type} / {model_base} / {local_filename}")

    ## ------------------------------------------------------------------
    if divider_end:
        print("-" * line_len)
    ## ------------------------------------------------------------------

def print_db_entries(id_list, line_len=80):
    ## print the first entry with the divider start
    print_db_entry(id_list[0], line_len=line_len, 
                   mode='minimal', divider_start=True, divider_end=False)

    ## now print the rest without the divider start
    for id in id_list[1:-1]:
        print_db_entry(id, line_len=line_len,
                       mode='minimal', divider_start=False, divider_end=False)

    ## now print the last entry with the divider end
    print_db_entry(id_list[-1], line_len=line_len,
                   mode='minimal', divider_start=False, divider_end=True)

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