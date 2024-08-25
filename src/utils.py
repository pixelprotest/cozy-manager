import os
import huggingface_hub
import yaml

def log_into_huggingface():
    huggingface_hub.login(hf_token)

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

def sanitize_and_validate_model_type(model_type):
    return sanitize_and_validate_arg_input(model_type, 'model_type_names')

def sanitize_and_validate_model_base(model_base):
    return sanitize_and_validate_arg_input(model_base, 'model_base_names')
