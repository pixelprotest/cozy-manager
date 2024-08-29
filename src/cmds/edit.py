import os
from src.utils.args import get_edit_args
from src.utils.generic import (get_user_choice, 
                               get_absolute_model_filepath,
                               is_model_local)
from src.utils.db import (get_entry,   
                          get_entry_data, 
                          delete_entry,
                          update_entry,
                          print_db_entry)
from src.utils.metadata import get_model_list
from dotenv import load_dotenv
load_dotenv()

storage_root_dir = os.getenv("MODEL_STORAGE_DIR")
db_filepath = os.getenv("MODEL_INFO_FILE")


def run_edit():
    """ Main entry point for editing the db """
    args = get_edit_args()
    id = args.id
    model_entry = get_entry(id)
    if not model_entry:
        return

    # db = read_db()
    print_db_entry(id, header_str='Editing this model entry')

    question = "What would you like to edit?"
    options = ["Edit tags", 
               "Edit local filename",
               "Edit model type",
               "Edit model base",
               "Remove model from collection",
               "Cancel"]
    choice = get_user_choice(question, options)

    if choice == "1": ## edit tags
        updated_tags = menu_edit_tags_main(id)
        update_entry(id, 'tags', updated_tags)
        print_db_entry(args.id, header_str='Finished editing tags')
    elif choice == "2": ## rename local filename
        ## first get the current and the new filename
        current_filename = get_entry_data(id, 'local_filename', '')
        new_filename = input("Enter new filename: ").strip()

        if new_filename and new_filename != current_filename:
            model_type = model_entry.get('model_type')
            model_base = model_entry.get('model_base')
            old_path = get_absolute_model_filepath(current_filename, model_type, model_base)
            new_path = get_absolute_model_filepath(new_filename, model_type, model_base)

            ## now try to rename the file
            if is_model_local(current_filename, model_type, model_base):
                try:
                    os.rename(old_path, new_path)
                except OSError as e:
                    print(f"Error renaming file: {e}")
                    return
            ## and now update the db
            update_entry(id, 'local_filename', new_filename)
            print("Filename updated.")
    elif choice == "3": ## edit model type
        current_filename = get_entry_data(id, 'local_filename', '')
        model_type = model_entry.get('model_type')
        model_base = model_entry.get('model_base')
        new_model_type = menu_edit_model_type(id)
        ## now lets get the paths.
        old_path = get_absolute_model_filepath(current_filename, model_type, model_base)
        new_path = get_absolute_model_filepath(current_filename, new_model_type, model_base)


        ## now lets rename the file## now try to rename the file
        if is_model_local(current_filename, model_type, model_base):
            ## make sure the new path directory exists.
            new_path_dir = os.path.dirname(new_path)
            os.makedirs(new_path_dir, exist_ok=True)

            try:
                os.rename(old_path, new_path)
            except OSError as e:
                print(f"Error renaming file: {e}")
                return
        ## and now update the db
        update_entry(id, 'model_type', new_model_type)
        print_db_entry(args.id, header_str='Finished editing model type')
    elif choice == "4": ## edit model type
        current_filename = get_entry_data(id, 'local_filename', '')
        model_type = model_entry.get('model_type')
        model_base = model_entry.get('model_base')
        new_model_base = menu_edit_model_base(id)
        ## now lets get the paths.
        old_path = get_absolute_model_filepath(current_filename, model_type, model_base)
        new_path = get_absolute_model_filepath(current_filename, model_type, new_model_base)


        ## now lets rename the file## now try to rename the file
        if is_model_local(current_filename, model_type, model_base):
            ## make sure the new path directory exists.
            new_path_dir = os.path.dirname(new_path)
            os.makedirs(new_path_dir, exist_ok=True)

            try:
                os.rename(old_path, new_path)
            except OSError as e:
                print(f"Error renaming file: {e}")
                return
        ## and now update the db
        update_entry(id, 'model_base', new_model_base)
        print_db_entry(args.id, header_str='Finished editing model base')
    elif choice == "5": ## remove model from collection
        ## by not forcing, the user will be prompted to confirm the deletion
        delete_entry(id, force=False)
        print(f"Model '{id}' has been removed from the collection.")
    else:
        print("Invalid choice. No changes made.")
        return
    print("Database updated successfully.")


def menu_edit_tags_main(id):
    print_db_entry(id, header_str='Editing this model entry')
    current_tags = get_entry_data(id, 'tags', [])
    print(f"Current tags: {', '.join(current_tags)}")
    
    question = "What would you like to do with the tags?"
    options = ["Add a tag", "Remove a tag", "Clear all tags", "Cancel"]
    choice = get_user_choice(question, options)

    if choice == "1": ## add a tag
        updated_tags = menu_edit_tags_add_tag(current_tags)
    elif choice == "2": ## remove a tag
        updated_tags = menu_edit_tags_remove_tag(current_tags)
    elif choice == "3": ## clear all tags
        updated_tags = menu_edit_tags_clear_all_tags()
    else:
        updated_tags = current_tags
        print("No changes made to tags.")

    return updated_tags

def menu_edit_tags_add_tag(tags):
    new_tag = input("Enter the tag to add: ").strip()
    if new_tag and new_tag not in tags:
        tags.append(new_tag)
        print(f"Tag '{new_tag}' added.")
    elif new_tag in tags:
        print(f"Tag '{new_tag}' already exists.")
    else:
        print("No valid tag entered.")
    return tags

def menu_edit_tags_remove_tag(tags):
    if not tags:
        print("No tags to remove.")
        return []
    
    while True:
        tag_to_remove = input("Enter the tag to remove: ").strip()
        if tag_to_remove == 'q':
            break
        elif tag_to_remove in tags:
            tags.remove(tag_to_remove)
            print(f"Tag '{tag_to_remove}' removed.")
            break
        else:
            print(f"Tag '{tag_to_remove}' not found. (q to quit)")
    return tags
 
def menu_edit_tags_clear_all_tags():
    print("All tags cleared.")
    return []

def menu_edit_model_type(id):
    print_db_entry(id, header_str='Editing this model entry')
    current_model_type = get_entry_data(id, 'model_type', '')
    print(f"Current model type: {current_model_type}")

    question = f"Currently the model type is: {current_model_type}. What would you like to change it to?"
    model_type_list = get_model_list('model_type_names')
    options = model_type_list
    choice = get_user_choice(question, options)

    try:
        choice_index = int(choice) - 1
        if 0 <= choice_index < len(options):
            new_model_type = options[choice_index]
            print(f"You've selected: {new_model_type}")
            return new_model_type
        else:
            print("Invalid choice. No changes made to model type.")
    except ValueError:
        print("Invalid input. No changes made to model type.")
    return current_model_type

def menu_edit_model_base(id):
    print_db_entry(id, header_str='Editing this model entry')
    current_model_base = get_entry_data(id, 'model_base', '')
    print(f"Current model base: {current_model_base}")

    question = f"Currently the model base is: {current_model_base}. What would you like to change it to?"
    model_base_list = get_model_list('model_base_names')
    options = model_base_list
    choice = get_user_choice(question, options)

    try:
        choice_index = int(choice) - 1
        if 0 <= choice_index < len(options):
            new_model_base = options[choice_index]
            print(f"You've selected: {new_model_base}")
            return new_model_base 
        else:
            print("Invalid choice. No changes made to model type.")
    except ValueError:
        print("Invalid input. No changes made to model type.")
    return current_model_base 
