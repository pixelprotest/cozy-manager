# Cozy Manager

Cozy Manager is an AI Model Manager command line tool.

## Key features:
- 📁 Automatically organizes your models in sub directories e.g. `/root/lora/flux1`
- 🏷️ Automatically renames ambiguous model names to more descriptive names. e.g. `diffusion_pytorch_model.safetensors`..
- 📚 Keep track of your entire model collection, never having to manually download the same model twice.
- 🚀 Simple command to deploy your model collection on new machines.
- 💰 Save money on rented cloud storage, by easily loading and unloading diskspace.
- 🌐 Download from multiple sources, including Hugging Face and Civitai.

## Quick Start
Follow the installationinstructions and download your first model:

`cozy download <url>` 



Basic commands are as follows:

`cozy list` list the models in your collection

`cozy unload` remove all locally stored models, to clear disk space

`cozy reload` reload / redownload all models in your collection

`cozy edit <id>` edit a model entry in your collection

See more detailed command explainations below to get more granular control on each command.




## Migrating and Deploying on New Machines
Cozy manager makes it easy to migrate and deploy your collection onto a new machine.

Just install this repo on the new machine, then copy the existing `config.yaml`, `collection.json` and `.env` files onto the new machine and run `cozy reload` and it will download all the models onto the new machine.





## Installation

1. Clone this repository:
   ```
   git clone https://github.com/pixelprotest/cozy-manager.git
   cd cozy-manager 
   ```

2. Install the package:
   ```
   pip install -e .
   ```

3. Create a `.env` file in the root directory with the following content:
   ```
   HF_TOKEN=your_huggingface_token
   CIVITAI_API_KEY=your_civitai_api_key
   MODEL_INFO_FILE=/path/to/model_info.json
   MODEL_STORAGE_DIR=/path/to/model/storage/directory
   ```



## Command Docs

#### Download

To download a model you can simply run this command:

`cozy download <url>` 

the `<url>` can either be:
- huggingface direct link to a file e.g. `https://huggingface.co/.../.../checkpoint.safetensors`
- civitai url of general model page or model-version page.

When you run the command it will automatically discover the `model-type` e.g. lora, controlnet, vae 
and the `model-base` e.g. `sd15`, `sdxl`, `flux` or `pony`

When you run the command it will automatically check against the `filenames_to_auto_rename` list in the `config.yaml` file at the root of this repo.
In case it comes across ambiguous filenames like `diffusion_pytorch_model.safetensors` or `lora.safetensors` it will rename the downloaded file to a more descriptive name based on the huggingface repo name.

Generally the automated discovery should work well, but incase it did not you can use the `cozy edit` command to easily fix it.

To skip all the automation and have full manual control:

`cozy download <url> <model-type> <model-base-type> <optional filename>` 

#### Unload

You can clear up disk space by unloading models from your drive. If you run the unload command it will remove all the locally stored models from your drive. e.g.

`cozy unload`

`cozy unload type lora` unloads all the loras in your collection

`cozy unload base flux` unloads all the flux models in your collection

`cozy unload tag based` unloads all the models tagged `based`


#### Reload

Since all the information of our previously downloaded models are stored in a json file, 
we can redownload all the models by running:

`cozy reload`

`cozy reload type lora` reloads all the loras in your collection

`cozy reload base flux` reloads all the flux models in your collection

`cozy reload tag based` reloads all the models with a specific tag

#### List

To list the items in your collection you can simply list all of them by doing:

`cozy list` 

`cozy list loaded` to list all the models that _are_ stored locally

`cozy list unloaded` to list all the models that are _not_ stored locally

`cozy list type lora` to list all the loras in your collection

`cozy list base flux` to list all the flux models in your collection

`cozy list tag based` to list all the models that are tagged `based` in your collection

`cozy list data` finally you can check how much data is stored locally by doing:

#### Edit

To edit the items in your collection, you can find the `id` using the `cozy list` command, and then by doing:

`cozy edit <id>`

this will open a command line prompt asking you what you want to edit, it will walk you through some options
- add / remove / clear tags
- change the local filename
- change the model type
- change the model base
- remove the model from the collection

### More Control with Multiple Flags
Some of the commands accept passing in both `--model-type` and `--model-base` to get more granular control e.g.

`cozy list loaded --model-type lora --model-base flux` to list all the local flux loras

`cozy unload --model-type lora --model-base flux` to unload all the flux loras in your collection

`cozy reload --model-type lora --model-base flux` to reload all the flux loras



