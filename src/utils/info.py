import json
import os
from src.utils.generic import get_absolute_model_filepath

def create_download_info(url, 
                         filename, 
                         model_type,
                         model_base):
    """
    """
    filepath = get_absolute_model_filepath(filename, model_type, model_base)

    if 'civitai.com' in url:
        source_name = "civitai"
        # For Civitai downloads, we need to check the directory size
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(filepath):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        file_size_mb = total_size / (1024 * 1024)
    else:
        source_name = "huggingface"
        # Get file size in megabytes
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)

    new_info = {
        "url": url,
        "local_filename": filename,
        "source_name": source_name,
        "model_type": model_type,
        "model_base": model_base,
        "file_size_mb": round(file_size_mb, 2)  # Round to 2 decimal places
    }
    
    if "huggingface.co" in url:
        parts = url.split("/")
        new_info["author"] = parts[3]
        new_info["repo"] = parts[4]
        new_info["filename_in_repo"] = parts[-1]
    elif 'civitai.com' in url:
        parts = url.split("/")
        new_info["author"] = "unknown"
        new_info["repo"] = "unknown"
        new_info["filename_in_repo"] = "unknown"    

    new_info['tags'] = []
    new_info['force_keep'] = False ## if true the file will not be deleted when running the cleanup script