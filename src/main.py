import os
import json
from src.download import (download_file_from_hf, 
                          download_file_from_civitai, 
                          download_file)
from src.info import (create_download_info, 
                      save_download_info)

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
