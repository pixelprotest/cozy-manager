import os
import json 
from src.utils.generic import get_absolute_model_filepath 

db_filepath = os.getenv("MODEL_INFO_FILE")
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), os.path.pardir, 'config.yaml')

def read_db():
    validate_db_filepath()
    with open(db_filepath, "r") as f:
        db = json.load(f)
    return db

def write_db(db):
    validate_db_filepath()
    # Save the updated json db file
    with open(db_filepath, "w") as f:
        json.dump(db, f, indent=4)

def validate_db_filepath():
    if not os.path.exists(db_filepath):
        with open(db_filepath, "w") as f:
            json.dump({}, f)

def get_next_available_id():
    try:
        db = read_db()
        next_id = max(map(int, db.keys())) + 1
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        next_id = 1
    
    return next_id

def get_entry(id):
    db = read_db()
    if str(id) not in db:
        raise KeyError(f"Entry with id '{id}' not found in the database.")
    return db[str(id)]


def create_entry(entry):
    db = read_db()
    id = get_next_available_id()

    ## now add the new info with a new id 
    db[str(id)] = entry 

    with open(db_filepath, "r+") as f:
        try:
            db = json.load(f)
        except json.JSONDecodeError:
            db = {}
        
        db.update(entry)
        
        db.seek(0)
        json.dump(db, f, indent=4)
        db.truncate()


def delete_entry(id, force=False):
    """ Main entry point for purging a model """
    db = read_db()

    # Check if the ID exists in the download_info
    if id not in db:
        print(f"Error: Model with ID '{id}' not found.")
        return

    # Get the model information
    entry = db[id]
    local_filename = entry.get('local_filename')
    model_type = entry.get('model_type')
    model_base = entry.get('model_base')

    # Confirm deletion if force is False
    if not force:
        confirm = input(f"Are you sure you want to purge model '{id}'? This action cannot be undone. (y/N): ")
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
    del db[id]
    write_db(db)

def update_entry(id, field, value):
    db = read_db()

    # Check if the ID exists in the download_info
    if id not in db:
        print(f"Error: Model with ID '{id}' not found.")
        return

    # Update the specified field with the new value
    db[id][field] = value

    # Write the updated database back to the file
    write_db(db)

    print(f"Successfully updated {field} for model '{id}'.")

    
def get_entry_data(id, field, default=None):
    db = read_db()
    if id not in db:
        return default
    return db[id].get(field, default)

def print_db_entry(id, 
                   header_str=None, 
                   line_len=80, 
                   clear=False, 
                   divider_start=True, 
                   divider_end=True, 
                   mode='detailed'):
    
    if clear: ## if True, we clear the screen
        clear_terminal()

    if header_str:
        print('-' * line_len)
        header_len = len(header_str)
        dash_count = max(0, line_len - 5 - header_len) ## 5 for '--- ' and ' '
        print(f'--- {header_str} {"-" * dash_count}')

    ## ------------------------------------------------------------------
    if divider_start:
        print("-" * line_len)
    ## ------------------------------------------------------------------

    url = get_entry_data(id, 'url', 'N/A')
    local_filename = get_entry_data(id, 'local_filename', 'N/A')
    model_type = get_entry_data(id, 'model_type', 'N/A')
    model_base = get_entry_data(id, 'model_base', 'N/A')
    if mode=='detailed':
        ## load some extra data
        download_date = get_entry_data(id, 'download_date', 'N/A')
        tags = get_entry_data(id, 'tags', [])
        print(f"ID: {id}")
        print(f"URL: {url}")
        print(f"Local Filename: {local_filename}")
        print(f"Model Type: {model_type}")
        print(f"Model Base: {model_base}")
        print(f"Download Date: {download_date}")
        print(f"Tags: {', '.join(tags) if tags else 'None'}")
    elif mode=='minimal':
        print(f"[{id}] :: {model_type} / {model_base} / {local_filename}")

    ## ------------------------------------------------------------------
    if divider_end:
        print("-" * line_len)
    ## ------------------------------------------------------------------

def print_db_entries(id_list, line_len=80):
    if len(id_list)==0:
        print("No models found.")
    elif len(id_list)==1:
        print_db_entry(id_list[0], line_len=line_len, mode='minimal',
                       divider_start=True, divider_end=True)
    elif len(id_list)==2:
        print_db_entry(id_list[0], line_len=line_len, mode='minimal',
                       divider_start=True, divider_end=False)
        print_db_entry(id_list[1], line_len=line_len, mode='minimal',
                       divider_start=False, divider_end=True)
    else:
        ## print the first entry with the divider start
        print_db_entry(id_list[0], line_len=line_len, 
                    mode='minimal', divider_start=True, divider_end=False)

        ## now print the rest without the divider start
        for id in id_list[1:-1]:
            print_db_entry(id, line_len=line_len,
                        mode='minimal', divider_start=False, divider_end=False)

        ## now print the last entry with the divider end
        print_db_entry(id_list[-1], line_len=line_len,
                    mode='minimal', divider_start=False, divider_end=True)