import os
import json
from urllib.parse import urlparse
from src.utils import (get_download_args, 
                       get_clearup_args, 
                       get_list_args, 
                       get_purge_args,
                       get_tag_args,
                       get_edit_args,
                       sanitize_and_validate_arg_input, 
                       get_absolute_model_filepath, 
                       get_user_choice,
                       print_db_entry,
                       clear_terminal) 
from src.main import check_and_download_file
from dotenv import load_dotenv
load_dotenv()

storage_root_dir = os.getenv("MODEL_STORAGE_DIR")
db_filepath = os.getenv("MODEL_INFO_FILE")

def download_model():
    """ Main entry point for downloading a model """
    args = get_download_args()
    # Set up download directory
    model_type = sanitize_and_validate_arg_input(args.model_type, 'model_type_names')
    model_base = sanitize_and_validate_arg_input(args.model_base, 'model_base_names')
    download_dir = os.path.join(storage_root_dir, model_type, model_base)

    # Check if file exists, and download if necessary
    filename = check_and_download_file(args.url, 
                                       download_dir, 
                                       db_filepath, 
                                       model_type=model_type, 
                                       model_base=model_base,
                                       filename=args.filename)
    print(f"\nFile processed: {filename}")
    print("Download information saved to download_info.json")

def clearup_space():
    """ Main entry point for cleaning up space """
    args = get_clearup_args()

    clear_model_type = None
    clear_model_base = None
    if args.model_type:
        clear_model_type = sanitize_and_validate_arg_input(args.model_type, 'model_type_names')
    if args.model_base:
        clear_model_base = sanitize_and_validate_arg_input(args.model_base, 'model_base_names')

    # Read the download_info.json file
    with open(db_filepath, "r") as json_file:
        download_info = json.load(json_file)

    # Iterate through each entry in the download_info
    for entry in download_info.values():
        local_filename = entry.get("local_filename")
        force_keep = entry.get("force_keep", False)
        tags = entry.get("tags", [])
        model_type = entry.get("model_type", None)
        model_base = entry.get("model_base", None)
        local_filepath = get_absolute_model_filepath(local_filename, model_type, model_base)

        ## if we passed in a specific tag, and the entry has a tag
        if args.tag:
            if args.tag not in tags:
                ## then we can skip this file
                continue

        if clear_model_type:
            if clear_model_type!= model_type:
                continue ## then we bypass this file

        if clear_model_base:
            if clear_model_base!= model_base:
                continue
        
        ## if we passed in a force_keep flag, and the entry has a force_keep flag
        if force_keep:
            ## then we can skip this file
            print(f"Skipping {local_filename} due to force_keep flag")
            continue
        
        if local_filename and os.path.exists(local_filepath):
            try:
                if os.path.isfile(local_filepath):
                    os.remove(local_filepath)
                    print(f"Removed file: {local_filename}")
                elif os.path.isdir(local_filepath):
                    import shutil
                    shutil.rmtree(local_filepath)
                    print(f"Removed directory: {local_filename}")
                else:
                    print(f"Unknown file type: {local_filename}")
            except OSError as e:
                print(f"Error removing {local_filename}: {e}")
        elif local_filename:
            print(f"File not found: {local_filepath}")
        else:
            print("Local filename not found in entry")

    print("Cleanup process completed.")

def redownload_models():
    """ Main entry point for redownloading models """
    # Read the download_info.json file
    with open(db_filepath, "r") as json_file:
        download_info = json.load(json_file)

    # Iterate through each entry in the download_info
    for entry in download_info.values():
        url = entry.get("url")
        local_filename = entry.get("local_filename")
        model_type = entry.get("model_type")
        model_base = entry.get("model_base")
        local_filepath = get_absolute_model_filepath(local_filename, model_type, model_base)
        
        if url and local_filename:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(local_filepath), exist_ok=True)
            
            # Extract the filename from the URL if not present in local_filename
            if os.path.basename(local_filename) == "":
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                local_filename = os.path.join(local_filepath, filename)
            
            # Download the file
            filename = check_and_download_file(url, 
                                               os.path.dirname(local_filepath), 
                                               db_filepath,
                                               model_type=model_type,
                                               model_base=model_base,
                                               filename=os.path.basename(local_filepath))
        else:
            print(f"Skipping entry due to missing URL or local filename: {entry}")

    print("Redownload process completed.")

def purge_model():
    """ Main entry point for purging a model """
    args = get_purge_args()
    # Load the JSON file
    with open(db_filepath, "r") as f:
        download_info = json.load(f)

    # Check if the ID exists in the download_info
    if args.id not in download_info:
        print(f"Error: Model with ID '{args.id}' not found.")
        return

    # Get the model information
    model_info = download_info[args.id]
    local_filename = model_info.get('local_filename')
    model_type = model_info.get('model_type')
    model_base = model_info.get('model_base')

    # Confirm deletion if --force is not used
    if not args.force:
        confirm = input(f"Are you sure you want to purge model '{args.id}'? This action cannot be undone. (y/N): ")
        if confirm.lower() != 'y':
            print("Purge cancelled.")
            return

    # Remove the file if it exists
    if local_filename:
        local_filepath = get_absolute_model_filepath(local_filename, model_type, model_base)
        if os.path.exists(local_filepath):
            try:
                os.remove(local_filepath)
                print(f"File '{local_filepath}' has been removed.")
            except OSError as e:
                print(f"Error removing file: {e}")
        else:
            print(f"File '{local_filepath}' not found.")

    # Remove the entry from the JSON file
    del download_info[args.id]

    # Save the updated JSON file
    with open(db_filepath, "w") as f:
        json.dump(download_info, f, indent=4)

    print(f"Model '{args.id}' has been purged from the database.")

def list_models():
    """ Main entry point for listing models """
    args = get_list_args()
    # Load the JSON file
    with open(db_filepath, "r") as f:
        download_info = json.load(f)

    if args.all or (not args.local and not args.virtual and not args.model_type and not args.model_base and not args.data_size):
        clear_terminal()
        for id, entry in download_info.items():
            print_db_entry(id, entry)

    elif args.local:
        for id, entry in download_info.items():
            local_filename = entry.get('local_filename', 'N/A')
            model_type = entry.get('model_type', 'N/A')
            model_base = entry.get('model_base', 'N/A')
            local_filepath = get_absolute_model_filepath(local_filename, model_type, model_base)
            
            if os.path.exists(local_filepath):
                print(f"ID: {id}")
                print(f"Local Filename: {local_filename}")
                print(f"Model Type: {model_type}")
                print(f"Model Base: {model_base}")
                print(f"File Size: {os.path.getsize(local_filepath) / (1024 * 1024):.2f} MB")
                print("-" * 40)

    elif args.model_type:
        model_type = sanitize_and_validate_arg_input(args.model_type, 'model_type_names')
        matching_models = [entry for entry in download_info.values() if entry.get('model_type') == model_type]
        print("-" * 40)
        print(f"Found {len(matching_models)} models for model type '{model_type}':")
        print("-" * 40)
        for entry in matching_models:
            print(f"ID: {entry.get('id', 'N/A')}")
            print(f"URL: {entry.get('url', 'N/A')}")
            print(f"Local Filename: {entry.get('local_filename', 'N/A')}")
            print(f"Model Base: {entry.get('model_base', 'N/A')}")
            print(f"Download Date: {entry.get('download_date', 'N/A')}")
            print("-" * 40)
    elif args.model_base:
        model_base = sanitize_and_validate_arg_input(args.model_base, 'model_base_names')
        matching_models = [entry for entry in download_info.values() if entry.get('model_base') == model_base]
        print("-" * 40)
        print(f"Found {len(matching_models)} models for model base '{model_base}':")
        print("-" * 40)
        for entry in matching_models:
            print(f"ID: {entry.get('id', 'N/A')}")
            print(f"URL: {entry.get('url', 'N/A')}")
            print(f"Local Filename: {entry.get('local_filename', 'N/A')}")
            print(f"Model Type: {entry.get('model_type', 'N/A')}")
            print(f"Download Date: {entry.get('download_date', 'N/A')}")
            print("-" * 40)
    elif args.data_size:
        print("Calculating the size of the models stored locally...")
        total_size = 0
        for entry in download_info.values():
            local_filename = entry.get('local_filename', 'N/A')
            model_type = entry.get('model_type', 'N/A')
            model_base = entry.get('model_base', 'N/A')
            local_filepath = get_absolute_model_filepath(local_filename, model_type, model_base)
            if os.path.exists(local_filepath):
                total_size += os.path.getsize(local_filepath)
        print(f"Total size of models stored locally: {total_size / (1024 * 1024):.2f} MB")
    else:
        print("Please specify --all to list all models.")

def tag_model():
    """ Main entry point for tagging a model """
    args = get_tag_args()
    # Read the download_info.json file
    with open(db_filepath, "r") as f:
        download_info = json.load(f)

    # Check if the model ID exists
    if args.id not in download_info:
        print(f"Error: Model with ID {args.id} not found.")
        return

    # Get the model entry
    model_entry = download_info[args.id]

    # Ensure the tags list exists
    if 'tags' not in model_entry:
        model_entry['tags'] = []

    if args.remove:
        # Remove the tag if it exists
        if args.tag in model_entry['tags']:
            model_entry['tags'].remove(args.tag)
            print(f"Tag '{args.tag}' removed from model {args.id}.")
        else:
            print(f"Tag '{args.tag}' does not exist for model {args.id}.")
    else:
        # Add the tag if it doesn't exist
        if args.tag not in model_entry['tags']:
            model_entry['tags'].append(args.tag)
            print(f"Tag '{args.tag}' added to model {args.id}.")
        else:
            print(f"Tag '{args.tag}' already exists for model {args.id}.")

    # Write the updated information back to the file
    with open(db_filepath, "w") as json_file:
        json.dump(download_info, json_file, indent=4)

    print(f"Model {args.id} tags: {', '.join(model_entry['tags'])}")


def edit_db():
    """ Main entry point for editing the db """
    args = get_edit_args()

    # Load the json database file
    with open(db_filepath, "r") as f:
        db = json.load(f)

    # Check if the provided id exists
    if args.id not in db:
        print(f"Error: Model with ID {args.id} not found.")
        return

    
    print_db_entry(args.id, db[args.id], header_str='Editing this db entry')

    model_entry = db[args.id]

    question = "What would you like to edit?"
    options = ["Edit tags", 
               "Edit local filename",
               "Cancel"]
    choice = get_user_choice(question, options)

    if choice == "1":
        # Edit tags
        print_db_entry(args.id, db[args.id], header_str='Editing this db entry')
        current_tags = model_entry.get('tags', [])
        print(f"Current tags: {', '.join(current_tags)}")
        
        question = "What would you like to do with the tags?"
        options = ["Add a tag", "Remove a tag", "Clear all tags", "Cancel"]
        choice = get_user_choice(question, options)

        if choice == "1": ## add a tag
            new_tag = input("Enter the tag to add: ").strip()
            if new_tag and new_tag not in current_tags:
                current_tags.append(new_tag)
                print(f"Tag '{new_tag}' added.")
            elif new_tag in current_tags:
                print(f"Tag '{new_tag}' already exists.")
            else:
                print("No valid tag entered.")
                return
        elif choice == "2": ## remove a tag
            if current_tags:
                while True:
                    tag_to_remove = input("Enter the tag to remove: ").strip()
                    if tag_to_remove == 'q':
                        break
                    elif tag_to_remove in current_tags:
                        current_tags.remove(tag_to_remove)
                        print(f"Tag '{tag_to_remove}' removed.")
                        break
                    else:
                        print(f"Tag '{tag_to_remove}' not found. (q to quit)")
            else:
                print("No tags to remove.")
                return
        elif choice == "3": ## clear all tags
            current_tags.clear()
            print("All tags cleared.")
        else:
            print("No changes made to tags.")

        model_entry['tags'] = current_tags
        print_db_entry(args.id, db[args.id], header_str='Finished editing tags')

    elif choice == "2":
        # Edit local filename
        current_filename = model_entry.get('local_filename', '')
        print(f"Current filename: {current_filename}")
        new_filename = input("Enter new filename: ").strip()
        
        if new_filename and new_filename != current_filename:
            # Rename the file on disk
            old_path = get_absolute_model_filepath(current_filename, model_entry.get('model_type'), model_entry.get('model_base'))
            new_path = get_absolute_model_filepath(new_filename, model_entry.get('model_type'), model_entry.get('model_base'))
            
            try:
                os.rename(old_path, new_path)
                model_entry['local_filename'] = new_filename
                print("Filename updated.")
            except OSError as e:
                print(f"Error renaming file: {e}")
                return

    else:
        print("Invalid choice. No changes made.")
        return

    # Save the updated json db file
    with open(db_filepath, "w") as f:
        json.dump(db, f, indent=4)

    print("Database updated successfully.")
