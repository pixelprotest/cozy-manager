import os
import wget
import json

def download_file(url, download_dir="downloads"):
    """Download a file from the given URL into a specific directory."""
    
    # Create the download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)
    
    # Get the filename from the URL
    filename = os.path.basename(url)
    
    # Construct the full path for the downloaded file
    full_path = os.path.join(download_dir, filename)
    
    # Download the file to the specified directory
    return wget.download(url, out=full_path)


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

    new_info = {
        "url": url,
        "local_filename": filename,
        "source_name": "huggingface"
    }
    
    if "huggingface.co" in url:
        parts = url.split("/")
        new_info["author"] = parts[3]
        new_info["repo"] = parts[4]
        new_info["filename_in_repo"] = parts[-1]
    
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

def check_and_download_file(url, download_dir):
    # Check if the URL has already been downloaded
    with open("download_info.json", "r") as json_file:
        download_info = json.load(json_file)
    
    for entry in download_info.values():
        if entry["url"] == url:
            local_filename = entry["local_filename"]
            if os.path.exists(local_filename):
                print(f"File already exists: {local_filename}")
                return local_filename
            else:
                print(f"File info found, but file missing. Re-downloading: {url}")
                break
    
    # If we get here, either the URL wasn't found or the file was missing
    filename = download_file(url, download_dir=download_dir)
    
    # Create and save download information
    download_info = create_download_info(url, filename)
    save_download_info(download_info)
    
    return filename

def main():
    # URL of the file to download
    # url = "https://huggingface.co/xinsir/controlnet-tile-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors"
    url = "https://huggingface.co/xinsir/controlnet-tile-sdxl-1.0/resolve/main/.gitattributes"

    # Set up download directory
    this_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(this_dir, "my_downloads")

    # Check if file exists, and download if necessary
    filename = check_and_download_file(url, download_dir)

    print(f"\nFile processed: {filename}")
    print("Download information saved to download_info.json")

if __name__ == "__main__":
    main()
