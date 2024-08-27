import sys
import os
from dotenv import load_dotenv
from src.cmds.download import download_model
from src.cmds.unload import clearup_space
from src.cmds.reload import redownload_models
from src.cmds.list import list_models
from src.cmds.edit import edit_db

# Load environment variables from .env file
load_dotenv()
hf_token = os.getenv("HF_TOKEN")
civitai_api_key = os.getenv("CIVITAI_API_KEY")
db_filepath = os.getenv("MODEL_INFO_FILE")
storage_root_dir = os.environ.get("MODEL_STORAGE_DIR")

## map of the commands available to cozy manager
cmd_map = {
    "download": download_model,
    "clear": clearup_space,
    "reload": redownload_models,
    "list": list_models,
    "edit": edit_db
}

def get_cozy_command():
    if len(sys.argv) < 2:
        print("--- Missing an actionable command" )
        print("--- Usage:")
        print(f"--- > cozy < {' | '.join(cmd_map.keys())} > ... etc")
        sys.exit(1)
    ## now we should have _a_ command
    cmd = sys.argv[1]

    ## check to make sure it's a valid command
    if cmd not in cmd_map:
        print(f"--- Unknown command: {cmd}")
        print(f"--- currently available commands: ")
        print(f"--- {', '.join(cmd_map.keys())}")
        sys.exit(1)

    cmd_handle = cmd_map[cmd]

    ## now return the actual command handle
    return cmd_handle

def main():
    get_cozy_command()()