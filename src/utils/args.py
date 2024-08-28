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

def get_unload_args():
    parser = argparse.ArgumentParser(description="Unload locally stored data")
    parser.add_argument("_cmd")
    parser.add_argument("--tag", type=str, default=None, help="Unloads all files with this tag")
    parser.add_argument("--model_type", type=str, default=None, help="Unloads all files with this model type")
    parser.add_argument("--model_base", type=str, default=None, help="Unloads all files with this model base")
    return parser.parse_args()

def get_list_args():
    parser = argparse.ArgumentParser(description="List models.")
    parser.add_argument("_cmd")
    parser.add_argument("--all", action="store_true", help="List all models")
    parser.add_argument("--local", action="store_true", help="List local models")
    parser.add_argument("--virtual", action="store_true", help="List virtual models")
    parser.add_argument("--model-type", type=str, help="Filter models by model type")
    parser.add_argument("--model-base", type=str, help="Filter models by model base")
    parser.add_argument("--data", action="store_true", help="Show the size of the models stored locally")
    return parser.parse_args()

def get_edit_args():
    parser = argparse.ArgumentParser(description="Edit collection entry.")
    parser.add_argument("_cmd")
    parser.add_argument("id", type=str, help="ID of the model entry to edit")
    return parser.parse_args()

def get_reload_args():
    parser = argparse.ArgumentParser(description="Reload models.")
    parser.add_argument("_cmd")
    parser.add_argument("--model-type", type=str, help="Only reload the models of this type, e.g. controlnet, unet, checkpoint")
    parser.add_argument("--model-base", type=str, help="Only reload the models of this base, e.g. flux1, sdxl, sd15")
    return parser.parse_args()
