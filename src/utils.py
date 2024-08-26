import os
import huggingface_hub
import yaml
import argparse
from dotenv import load_dotenv
load_dotenv()

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
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
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

