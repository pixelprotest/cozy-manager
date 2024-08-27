import os
import huggingface_hub
import wget
import subprocess
from src.utils import get_filenames_to_auto_rename


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
        ## now check against the filenames to auto rename
        for filename_to_auto_rename in get_filenames_to_auto_rename():
            if filename_to_auto_rename in filename:
                filename = filename_to_auto_rename
                break
    
    # Construct the full path for the downloaded file
    full_path = os.path.join(download_dir, filename)

    repo_id = "/".join(url.split("/")[3:5]) ## extract repo_id from URL
    filename_in_repo = url.split("/")[-1] ## extract filename from URL
    print(f'repo id: {repo_id}, filename: {filename_in_repo}')
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

    return filename   

def download_file_from_civitai(url, filename=None, download_dir="downloads"):
    # Create the download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)

    full_path = download_dir ## should be the download dir + the name of the dir thats created

    # Get all directory names in the download_dir
    existing_dirs_before = get_existing_dirs(download_dir)

    # Use civitdl as a command-line process to download the file
    try:
        command = [
            "civitdl",
            url,
            download_dir,
        ]
        
        # Run the command and capture the output in real-time
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        # Print the output (including progress bar) in real-time
        for line in process.stdout:
            print(line, end='')  # end='' to avoid double line breaks
        
        # Wait for the process to complete and get the return code
        return_code = process.wait()
        
        if return_code == 0:
            try:
                # Check for new directories after download
                existing_dirs_after = get_existing_dirs(download_dir)
                new_model_dirname = list(set(existing_dirs_after) - set(existing_dirs_before))
                
                if new_model_dirname:
                    # If a new directory was created, update the full_path
                    full_path = os.path.join(download_dir, new_model_dirname[0])
                    dirname = new_model_dirname[0]
                    print(f"New directory created: {full_path}")
                    return dirname 
                else:
                    print("No new directory was created during download.")
            except Exception as e:
                print(f"Error occurred while checking for new directories: {str(e)}")
                return None
        else:
            print(f"Error downloading file from Civitai. Return code: {return_code}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running civitdl: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error downloading file from Civitai: {e}")
        return None
    

def get_existing_dirs(dir):
    return [d for d in os.listdir(dir) if os.path.isdir(os.path.join(dir, d))]