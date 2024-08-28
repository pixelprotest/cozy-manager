import sys
import os
from src.cmds.download import run_download
from src.cmds.unload import run_unload 
from src.cmds.reload import run_reload 
from src.cmds.list import run_list
from src.cmds.edit import run_edit 
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
hf_token = os.getenv("HF_TOKEN")
civitai_api_key = os.getenv("CIVITAI_API_KEY")
db_filepath = os.getenv("MODEL_INFO_FILE")
storage_root_dir = os.environ.get("MODEL_STORAGE_DIR")

## map of the commands available to cozy manager
cmd_map = {
    "download": run_download,
    "unload": run_unload,
    "reload": run_reload,
    "list": run_list,
    "edit": run_edit
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