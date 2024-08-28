import os
import json 

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

def update_entry(id, entry):
    pass

    