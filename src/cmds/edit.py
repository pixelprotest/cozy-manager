import os
import json
from src.utils.generic import get_edit_args, print_db_entry, get_user_choice, get_absolute_model_filepath
from dotenv import load_dotenv
load_dotenv()

storage_root_dir = os.getenv("MODEL_STORAGE_DIR")
db_filepath = os.getenv("MODEL_INFO_FILE")


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
               "Remove model from collection",
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
            
    elif choice == "3":
        # Check if the model ID exists in the database
        if args.id not in db:
            print(f"Error: Model with ID '{args.id}' not found in the database.")
            return

        # Confirm deletion
        confirm = input(f"Are you sure you want to delete model '{args.id}'? This action cannot be undone. (y/N): ")
        if confirm.lower() != 'y':
            print("Deletion cancelled.")
            return

        # If confirmed, proceed with deletion
        del db[args.id]

    else:
        print("Invalid choice. No changes made.")
        return

    # Save the updated json db file
    with open(db_filepath, "w") as f:
        json.dump(db, f, indent=4)

    print("Database updated successfully.")
