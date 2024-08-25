import json
import os

def create_download_info(url, filename, json_filepath):
    """Create a dictionary with download information.
        imagine the url is https://huggingface.co/xinsir/controlnet-tile-sdxl-1.0/
                                    resolve/main/diffusion_pytorch_model.safetensors
    """
    # Read existing download_info.json to get the next available ID
    try:
        with open(json_filepath, "r") as json_file:
            existing_info = json.load(json_file)
        next_id = max(map(int, existing_info.keys())) + 1
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        existing_info = {}
        next_id = 1

    if 'civitai.com' in url:
        source_name = "civitai"
        # For Civitai downloads, we need to check the directory size
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(filename):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        file_size_mb = total_size / (1024 * 1024)
    else:
        source_name = "huggingface"
        # Get file size in megabytes
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)

    new_info = {
        "url": url,
        "local_filename": filename,
        "source_name": source_name,
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

    ## now add the new info with a new id 
    existing_info[str(next_id)] = new_info

    return existing_info

def save_download_info(info, json_filepath):
    """Save download information to a JSON file."""
    with open(json_filepath, "r+") as json_file:
        try:
            existing_info = json.load(json_file)
        except json.JSONDecodeError:
            existing_info = {}
        
        existing_info.update(info)
        
        json_file.seek(0)
        json.dump(existing_info, json_file, indent=4)
        json_file.truncate()