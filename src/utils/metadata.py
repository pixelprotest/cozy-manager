import os
import re
import yaml
import requests
from bs4 import BeautifulSoup
from src.utils.generic import (sanitize_and_validate_arg_input, 
                               sanitize_huggingface_file_to_repo_url)

config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), os.path.pardir, 'config.yaml')

def get_model_info(url, verbose=False):
    """ gets the model_type and the base_model from a url, works for both huggingface and civitai
    """
    if verbose:
        print('--- the url is: ', url)

    if 'civitai' in url:
        return get_civitai_model_info(url, verbose)
    elif 'huggingface' in url:
        url = sanitize_huggingface_file_to_repo_url(url)
        return distill_model_metadata_from_webpage(url, verbose)
    else:
        print('url not supported')
        return None, None

def get_civitai_model_info(url, verbose=False):
    model_ids = get_civitai_model_ids(url)
    model_id = model_ids['model_id']
    version_id = model_ids['version_id']
    is_versioned = True if version_id else False

    if is_versioned:
        api_url = f"https://civitai.com/api/v1/model-versions/{version_id}"
    else:
        api_url = f"https://civitai.com/api/v1/models/{model_id}"
    
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        if is_versioned:
            model_type = data['model']['type']
            base_model = data['baseModel']
            pass
        else:
            model_type = data.get('type')
            base_model = None
            if data.get('modelVersions'):
                latest_version = data['modelVersions'][0]  # Assuming the first version is the latest
                base_model = latest_version.get('baseModel')

        ## now sanitize the model type and base model
        model_type = sanitize_and_validate_arg_input(model_type, 'model_type_names')
        base_model = sanitize_and_validate_arg_input(base_model, 'model_base_names')

        if verbose:    
            print('api base:', base_model)
            print('api type:', model_type)

        return model_type, base_model
    else:
        print(f"Error: Unable to fetch model info. Status code: {response.status_code}")
        return None, None
    
def get_civitai_model_ids(url):
    # Pattern to match model ID and model version ID separately
    model_pattern = r"models/(\d+)"
    version_pattern = r"modelVersionId=(\d+)"
    
    model_match = re.search(model_pattern, url)
    version_match = re.search(version_pattern, url)
    
    model_id = model_match.group(1) if model_match else None
    version_id = version_match.group(1) if version_match else None
    
    return {
        "model_id": model_id,
        "version_id": version_id
    }

def distill_model_metadata_from_webpage(url, verbose=False):
    """ mainly used for huggingface, as base and type 
    categories are not always clearly defined
    """
    content = parse_url_to_text(url)

    ## first grab all the aliases for the types and the bases
    base_name_list = get_model_aliases('model_base_names')
    model_type_list = get_model_aliases('model_type_names')

    ## count he occurances on the page and assign a confidence value to each 
    base_model_confidences = calculate_model_confidences(content, base_name_list)
    model_type_confidences = calculate_model_confidences(content, model_type_list)

    ## distill the highest confidence base and model type
    highest_base_model = get_highest_confidence(base_model_confidences)
    highest_model_type = get_highest_confidence(model_type_confidences)

    if verbose:
        print('distilled base:', highest_base_model)
        print('distilled type:', highest_model_type)

    return highest_model_type, highest_base_model 
    
def parse_url_to_text(url):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all text from the parsed HTML
        text = soup.get_text(separator=' ', strip=True)
        
        return text
    else:
        print(f"Error: Unable to fetch the webpage. Status code: {response.status_code}")
        return None

def get_model_aliases(config_key_name):
    """ takes a config_key_name like 'model_base_names' or 'model_type_names' 
    and returns a nested list of model names and their aliases
    """
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)

    model_names= []
    for name, aliases in data[config_key_name].items():
        aliases = data[config_key_name].get(name, []) ## get all the aliases for the model base name
        combined_list = [name] + aliases ## combine the main name with its aliases
        combined_list = [x.lower() for x in combined_list] ## lowercase all
        combined_list = list(set(combined_list)) ## remove duplicates
        ## make sure to move the base_name to the front
        combined_list.remove(name.lower())
        combined_list.insert(0, name.lower())
        model_names.append(combined_list)

    return model_names 

def count_word_occurences_in_text(text, word_list):
    word_counts = {}
    # Convert text to lowercase for case-insensitive matching
    text = text.lower()
    
    for word in word_list:
        # Convert each word to lowercase
        word = word.lower()
        # Count occurrences of the word in the text
        count = text.count(word)
        word_counts[word] = count
    
    return word_counts

def calculate_model_confidences(content, name_list):
    confidences = {}
    total_occurrences = 0
    
    for base_list in name_list:
        key = base_list[0]  # Assume the first item is the key name
        occurrences = sum(count_word_occurences_in_text(content, base_list).values())
        confidences[key] = occurrences
        total_occurrences += occurrences
    
    # Calculate confidence levels
    for key in confidences:
        confidences[key] = confidences[key] / total_occurrences if total_occurrences > 0 else 0
    
    return confidences

def get_highest_confidence(confidence_dict, threshold=0.5):
    if not confidence_dict:
        return None
    
    highest_key = max(confidence_dict, key=confidence_dict.get)
    highest_confidence = confidence_dict[highest_key]
    
    if highest_confidence >= threshold:
        return highest_key
    else:
        return None
    



if __name__ == "__main__":
    url_list = [
        "https://huggingface.co/XLabs-AI/flux-lora-collection",
        "https://huggingface.co/black-forest-labs/FLUX.1-dev",
        "https://huggingface.co/xinsir/controlnet-tile-sdxl-1.0",
        "https://civitai.com/models/118025/360redmond-a-360-view-panorama-lora-for-sd-xl-10",
    ]

    for url in url_list:
        get_model_info(url, verbose=True)