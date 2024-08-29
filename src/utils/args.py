import argparse

def get_download_args():
    parser = argparse.ArgumentParser(description="Download AI models from various sources.")
    parser.add_argument("_cmd")
    parser.add_argument("url", nargs='?', type=str, help="URL of the file to download")
    parser.add_argument("model_type", nargs='?', type=str, help="e.g. controlnet, unet, checkpoint")
    parser.add_argument("model_base", nargs='?', type=str, help="e.g. flux1, sdxl, sd15")
    parser.add_argument("filename", nargs='?', type=str, help="Custom filename incase repo naming not clear enough")
    parser.add_argument("--url", type=str, dest='url', help="URL of the file to download")
    parser.add_argument("--model-type", dest='model_type', type=str, help="e.g. controlnet, unet, checkpoint")
    parser.add_argument("--model-base", dest='model_base', type=str, default="flux1", help="e.g., flux1, sdxl, sd15")
    parser.add_argument("--filename", dest='filename', type=str, default=None, help="Custom filename incase repo naming not clear enough")
    return parser.parse_args()

def get_list_args():
    parser = argparse.ArgumentParser(description="List models.")
    parser.add_argument("_cmd", help="The main command (should be 'list')")
    parser.add_argument("subcmd", nargs='?', default=None, choices=['loaded', 'unloaded', 'all', 'type', 'base', 'data'],
                        help="Subcommand to specify what sort of thing you want to list")
    parser.add_argument("subarg", nargs='?', default=None, help="Argument for the subcmd")
    parser.add_argument("--all", action="store_true", help="List all models")
    parser.add_argument("--loaded", action="store_true", help="List local models")
    parser.add_argument("--unloaded", action="store_true", help="List virtual models")
    parser.add_argument("--model-type", type=str, help="Filter models by model type")
    parser.add_argument("--model-base", type=str, help="Filter models by model base")
    parser.add_argument("--data", action="store_true", help="Show the size of the models stored locally")
    
    args = parser.parse_args()
    
    # Handle the case where subcommand is used
    if args.subcmd:
        if args.subcmd == 'loaded':
            args.loaded = True
        elif args.subcmd == 'unloaded':
            args.unloaded = True
        elif args.subcmd == 'all':
            args.all = True
        elif args.subcmd == 'type' and args.subarg:
            args.model_type = args.subarg
        elif args.subcmd == 'base' and args.subarg:
            args.model_base = args.subarg
        elif args.subcmd == 'data':
            args.data = True
    
    return args

def get_edit_args():
    parser = argparse.ArgumentParser(description="Edit collection entry.")
    parser.add_argument("_cmd")
    parser.add_argument("id", type=str, help="ID of the model entry to edit")
    return parser.parse_args()

def get_unload_args():
    parser = argparse.ArgumentParser(description="Unload locally stored data")
    parser.add_argument("_cmd")
    parser.add_argument("--tag", type=str, default=None, help="Unloads all files with this tag")
    parser.add_argument("--model-type", type=str, default=None, help="Unloads all files with this model type")
    parser.add_argument("--model-base", type=str, default=None, help="Unloads all files with this model base")
    return parser.parse_args()

def get_reload_args():
    parser = argparse.ArgumentParser(description="Reload models.")
    parser.add_argument("_cmd")
    parser.add_argument("subcmd", nargs='?', default=None, choices=['tag', 'type', 'base'],
                        help="Subcommand to specify what sort of thing you want to reload")
    parser.add_argument("subarg", nargs='?', default=None, help="Argument for the subcmd")
    parser.add_argument("--tag", type=str, default=None, help="Only reload the models with this tag")
    parser.add_argument("--model-type", type=str, help="Only reload the models of this type, e.g. controlnet, unet, checkpoint")
    parser.add_argument("--model-base", type=str, help="Only reload the models of this base, e.g. flux1, sdxl, sd15")

    args = parser.parse_args()

    if args.subcmd:
        if args.subcmd == 'tag':
            args.tag = args.subarg
        elif args.subcmd == 'type':
            args.model_type = args.subarg
        elif args.subcmd == 'base':
            args.model_base = args.subarg

    return args
