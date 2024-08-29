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
Follow the installation instructions, then to download your first model:

`cozy download <url>` 

`cozy list` list all the models in your collection

`cozy unload` clear out disk space and remove all locally stored models:

`cozy reload` reload all previously downloaded models

`cozy edit <id>` edit the db entry for a model this will open a command line prompt asking you what you want to edit, it will walk you through some options:

See more detailed command explainations below to get more granular control on each command.




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






### 1. Download a model

To download a model, the basic command is:

`cozy download <url> <model-type> <model-base-type> <optional filename>` 

For example lets say we want to download a `sdxl` `lora` from civitai, 
we can copy the url and download it on the cli like this:

`cozy download https://civitai/path/to/lora/here lora sdxl`

Or lets say we want to download the `flux1-dev` `ae.safetensors` file from huggingface.
The original `ae.safetensors` filename is a bit ambiguous, so we can pass in a new name
to store it like `flux1-dev-ae.safetensors`

`cozy https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/ae.safetensors vae flux1 flux1-dev-ae.safetensors`

The `model-type` and the `model-base-type` will create subdirectories in the `MODEL_STORAGE_DIR`

if no `--model-type` and no `--model-base` are passed int, it will automatically try to distill 
the type and base for you.


### 2. Unload Models 

You can clear up disk space by unloading models from your drive. If you run the unload command it will remove all the locally stored models from your drive. e.g.

`cozy unload`

`cozy unload --tag <tag>` unload all the models with a specific tag

`cozy unload --model-type <model-type>` unload all the models with a specific model type

`cozy unload --model-base <model-base>` unload all the models with a specific model base


### 3. Reload Models

Since all the information of our previously downloaded models are stored in a json file, 
we can redownload all the models by running:

`cozy reload`

`cozy reload type lora` reloads all the loras in your collection

`cozy reload base flux` reloads all the flux models in your collection

`cozy reload tag based` reloads all the models with a specific tag

### 5. List Models

To list the items in your collection you can simply list all of them by doing:

`cozy list` 

`cozy list loaded` to list all the models that _are_ stored locally

`cozy list unloaded` to list all the models that are _not_ stored locally

`cozy list type lora` to list all the loras in your collection

`cozy list base flux` to list all the flux models in your collection

You can be even more granular by passing in the `--model-type` and `--model-base` flags, like here listing only the flux loras in your collection:

`cozy list --model-type lora --model-base flux`

to list all the models that are tagged `based` in your collection

`cozy list tag based` 

finally you can check how much data is stored locally by doing:

`cozy list data`

### 6. Edit Mode

To edit the items in your collection, you can find the `id` using the `cozy list` command, and then by doing:

`cozy edit <id>`

this will open a command line prompt asking you what you want to edit, it will walk you through some options
- add / remove / clear tags
- change the local filename
- change the model type
- change the model base
- remove the model from the collection
