import os
import huggingface_hub
import yaml

def log_into_huggingface():
    huggingface_hub.login(hf_token)

def sanitize_and_validate_model_type(model_type):
    model_type = model_type.lower().strip()
    
    # Load model type mappings from YAML file
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    with open(config_path, 'r') as config_file:
        data = yaml.safe_load(config_file)
        model_type_mappings = data['model_type_names']
    
    for correct_type, variations in model_type_mappings.items():
        if model_type in variations:
            return correct_type
        
    raise ValueError(f"Invalid model type: {model_type}. \
                     Please use one of the supported types: {', '.join(model_type_mappings.keys())}, \
                     or add new ones to the model_type_config.yaml")

