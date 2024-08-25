import huggingface_hub
import os
import wget
import json
import civitdl
import subprocess
import argparse
from dotenv import load_dotenv
from src.download import (download_file, 
                         download_file_from_hf, 
                         download_file_from_civitai)
from src.info import (create_download_info,
                      save_download_info)

# Load environment variables from .env file
load_dotenv()
hf_token = os.getenv("HF_TOKEN")
civitai_api_key = os.getenv("CIVITAI_API_KEY")
model_info_filepath = os.getenv("MODEL_INFO_FILE")
storage_root_dir = os.environ.get("MODEL_STORAGE_DIR")

def check_and_download_file(url, download_dir, model_info_filepath, filename=None):
    if not os.path.exists(model_info_filepath):
        with open(model_info_filepath, "w") as json_file:
            json.dump({}, json_file)

    with open(model_info_filepath, "r") as json_file:
        download_info = json.load(json_file)

    
    should_add_info = True ## init to true

    for entry in download_info.values():
        if entry["url"] == url:
            local_filename = entry["local_filename"]
            if os.path.exists(local_filename):
                print(f"File already exists: {local_filename}")
                return local_filename
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
        download_info = create_download_info(url, filename, model_info_filepath)
        save_download_info(download_info, model_info_filepath)
    
    return filename

def get_args():
    parser = argparse.ArgumentParser(description="Download AI models from various sources.")
    parser.add_argument("url", nargs='?', type=str, help="URL of the file to download")
    parser.add_argument("model_type", nargs='?', type=str, help="e.g. controlnet, unet, checkpoint")
    parser.add_argument("model_base", nargs='?', type=str, help="e.g. flux1, sdxl, sd15")
    parser.add_argument("filename", nargs='?', type=str, help="Custom filename incase repo naming not clear enough")
    parser.add_argument("--url", type=str, dest='url', help="URL of the file to download")
    parser.add_argument("--model-type", dest='model_type', type=str, help="e.g. controlnet, unet, checkpoint")
    parser.add_argument("--model-base", dest='model_base', type=str, default="flux1", help="e.g., flux1, sdxl, sd15")
    parser.add_argument("--filename", dest='filename', type=str, default=None, help="Custom filename incase repo naming not clear enough")
    args = parser.parse_args()
    
    return args

def download_model():
    # URL of the file to download
    # url = "https://huggingface.co/xinsir/controlnet-tile-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors"
    # url = "https://huggingface.co/xinsir/controlnet-tile-sdxl-1.0/resolve/main/.gitattributes"
    # url = "https://civitai.com/models/118025/360redmond-a-360-view-panorama-lora-for-sd-xl-10"
    # url = "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors"

    args = get_args()
    # Set up download directory
    download_dir = os.path.join(storage_root_dir, args.model_type, args.model_base)

    # Check if file exists, and download if necessary
    filename = check_and_download_file(args.url, download_dir, model_info_filepath, filename=args.filename)

    print(f"\nFile processed: {filename}")
    print("Download information saved to download_info.json")

def clearup_space():
    import json
    import os

    # Read the download_info.json file
    with open(model_info_filepath, "r") as json_file:
        download_info = json.load(json_file)

    # Iterate through each entry in the download_info
    for entry in download_info.values():
        local_filename = entry.get("local_filename")
        if local_filename and os.path.exists(local_filename):
            try:
                if os.path.isfile(local_filename):
                    os.remove(local_filename)
                    print(f"Removed file: {local_filename}")
                elif os.path.isdir(local_filename):
                    import shutil
                    shutil.rmtree(local_filename)
                    print(f"Removed directory: {local_filename}")
                else:
                    print(f"Unknown file type: {local_filename}")
            except OSError as e:
                print(f"Error removing {local_filename}: {e}")
        elif local_filename:
            print(f"File not found: {local_filename}")
        else:
            print("Local filename not found in entry")

    print("Cleanup process completed.")

def redownload_models():
    import json
    import os
    from urllib.parse import urlparse

    # Read the download_info.json file
    with open(model_info_filepath, "r") as json_file:
        download_info = json.load(json_file)

    # Iterate through each entry in the download_info
    for entry in download_info.values():
        url = entry.get("url")
        local_filename = entry.get("local_filename")
        
        if url and local_filename:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(local_filename), exist_ok=True)
            
            # Extract the filename from the URL if not present in local_filename
            if os.path.basename(local_filename) == "":
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                local_filename = os.path.join(local_filename, filename)
            
            # Download the file
            filename = check_and_download_file(url, 
                                               os.path.dirname(local_filename), 
                                               model_info_filepath,
                                               filename=os.path.basename(local_filename))
            print(f"Redownloaded: {filename}")
        else:
            print(f"Skipping entry due to missing URL or local filename: {entry}")

    print("Redownload process completed.")