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