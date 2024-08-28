import os
from src.utils.download import (download_file_from_hf, 
                          download_file_from_civitai, 
                          download_file)
from src.utils.info import (create_download_info)
from src.utils.db import read_db
from src.utils.generic import get_absolute_model_filepath
from dotenv import load_dotenv
load_dotenv()

db_filepath = os.getenv("MODEL_INFO_FILE")



def check_and_download_file(url, 
                            download_dir, 
                            model_type,
                            model_base,
                            filename=None):
    db = read_db()
    
    should_add_info = True ## init to true
    ## here we check if the file already exists, so we can bypass the download
    for entry in db.values():
        if entry["url"] == url:
            local_filename = entry["local_filename"]
            local_filepath = get_absolute_model_filepath(local_filename, model_type, model_base)
            if os.path.exists(local_filepath):
                print(f"File already exists: {local_filepath}")
                return local_filepath
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
        db = create_download_info(url, 
                                  filename, 
                                  model_type,
                                  model_base)
    
    return filename
