import huggingface_hub
import os
import wget
import json
import civitdl
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
hf_token = os.getenv("HF_TOKEN")
civitai_api_key = os.getenv("CIVITAI_API_KEY")

def log_into_huggingface():
    huggingface_hub.login(hf_token)

def download_file(url, filename=None , download_dir="downloads"):
    """Download a file from the given URL into a specific directory with a specific filename."""
    if filename is None:
        filename = os.path.basename(url)
    
    # Create the download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)
    
    # Construct the full path for the downloaded file
    full_path = os.path.join(download_dir, filename)
    
    # Download the file to the specified directory with the given filename
    return wget.download(url, out=full_path)

def download_file_from_hf(url, filename=None, download_dir="downloads"):
    # Create the download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)
    
    # If filename is not provided, use the last part of the URL
    if filename is None:
        filename = os.path.basename(url)
    
    # Construct the full path for the downloaded file
    full_path = os.path.join(download_dir, filename)

    repo_id = "/".join(url.split("/")[3:5]) ## extract repo_id from URL
    filename_in_repo = "/".join(url.split("/")[7:]) ## extract filename from URL
    # Download the file using huggingface_hub
    huggingface_hub.hf_hub_download(
        repo_id=repo_id,
        filename=filename_in_repo,
        local_dir=download_dir,
        local_dir_use_symlinks=False
    )
    
    ## now check fi the filename_in_repo is the same as the filename we wanted..
    if filename!=filename_in_repo:
        os.rename(os.path.join(download_dir, filename_in_repo), full_path)
    
    return full_path

def download_file_from_civitai(url, filename=None, download_dir="downloads"):
    # Create the download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)


    full_path = download_dir

    # Use civitdl as a command-line process to download the file
    try:
        command = [
            "civitdl",
            url,
            full_path,
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return full_path
        else:
            print(f"Error downloading file from Civitai: {result.stderr}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running civitdl: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error downloading file from Civitai: {e}")
        return None


def create_download_info(url, filename):
    """Create a dictionary with download information.
        imagine the url is https://huggingface.co/xinsir/controlnet-tile-sdxl-1.0/
                                    resolve/main/diffusion_pytorch_model.safetensors
    """
    # Read existing download_info.json to get the next available ID
    try:
        with open("download_info.json", "r") as json_file:
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

    ## now add the new info with a new id 
    existing_info[str(next_id)] = new_info

    return existing_info

def save_download_info(info, filename="download_info.json"):
    """Save download information to a JSON file."""
    with open(filename, "r+") as json_file:
        try:
            existing_info = json.load(json_file)
        except json.JSONDecodeError:
            existing_info = {}
        
        existing_info.update(info)
        
        json_file.seek(0)
        json.dump(existing_info, json_file, indent=4)
        json_file.truncate()

def check_and_download_file(url, download_dir, filename=None):
    if not os.path.exists("download_info.json"):
        with open("download_info.json", "w") as json_file:
            json.dump({}, json_file)

    with open("download_info.json", "r") as json_file:
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
        download_info = create_download_info(url, filename)
        save_download_info(download_info)
    
    return filename

def main():
    # URL of the file to download
    # url = "https://huggingface.co/xinsir/controlnet-tile-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors"
    # url = "https://huggingface.co/xinsir/controlnet-tile-sdxl-1.0/resolve/main/.gitattributes"
    url = "https://civitai.com/models/118025/360redmond-a-360-view-panorama-lora-for-sd-xl-10"
    # url = "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors"

    # Set up download directory
    this_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(this_dir, "my_downloads", "controlnet")

    # Check if file exists, and download if necessary
    filename = check_and_download_file(url, download_dir, filename=None)

    print(f"\nFile processed: {filename}")
    print("Download information saved to download_info.json")

def main_clearspace():
    import json
    import os

    # Read the download_info.json file
    with open("download_info.json", "r") as json_file:
        download_info = json.load(json_file)

    # Iterate through each entry in the download_info
    for entry in download_info.values():
        local_filename = entry.get("local_filename")
        if local_filename and os.path.exists(local_filename):
            try:
                os.remove(local_filename)
                print(f"Removed file: {local_filename}")
            except OSError as e:
                print(f"Error removing file {local_filename}: {e}")
        elif local_filename:
            print(f"File not found: {local_filename}")
        else:
            print("Local filename not found in entry")

    print("Cleanup process completed.")

def main_redownload():
    import json
    import os
    from urllib.parse import urlparse

    # Read the download_info.json file
    with open("download_info.json", "r") as json_file:
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
            filename = check_and_download_file(url, os.path.dirname(local_filename), filename=os.path.basename(local_filename))
            print(f"Redownloaded: {filename}")
        else:
            print(f"Skipping entry due to missing URL or local filename: {entry}")

    print("Redownload process completed.")

if __name__ == "__main__":
    main()
    # main_clearspace()
    # main_redownload()
