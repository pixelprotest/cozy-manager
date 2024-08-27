# Cozy AI Model Manager

Cozy AI Model Manager is a command line tool for managing your AI Model Collection.

Key features:
- Keep track of your entire model collection, never having to manually download the same model twice.
- Simple command to deploy your model collection on new machines.
- Automatically renames ambiguous model names to descriptive names based on repo:

   e.g. `https://huggingface.co/pixelprotest/monkey-island-flux-lora/resolve/main/diffusion_pytorch_model.safetensors`

   e.g. `diffusion_pytorch_model.safetensors` becomes `monkey-island-flux-lora.safetensors`
- Organizes your models in sub directories based on `model type` and `model base`:

   e.g. `model_store/lora/flux1/monkey-island-flux-lora.safetensors`

- Free up diskspace and save money on paying for GBs of persistent cloud storage.
- Download from multiple sources, including Hugging Face and Civitai.

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


## Quick Start
Follow the installation instructions above, then to download your first model:

`cozy download <url> <type> <base> <optional local filename>`
- url: could be a huggingface url to a .safetensors file or a generic civitai model page url
- type: can be a model type like `lora`, `vae`, `controlnet`, etc
- base: can be a model base like `sdxl`, `sd1.5`, `sd1.0`, etc
- optional local filename: if you want to store the model with a different name than the original filename

to clear out disk space and remove all locally stored models: 

`cozy unload`

to reload all previously downloaded models: 

`cozy reload`

to list all the models in your collection:

`cozy list`

to list data size of currently local / loaded models:

`cozy list --data`



other commands:

- to list all the models in the db: 

   `cozy list`

   - you can list the ones that are currently downloaded:

      `cozy list --loaded`

   - you can list the ones that are not downloaded:

      `cozy list --unloaded`

   - you can list the size of the models stored locally:

      `cozy list --data`

- to edit the db entry for a model, this will open a command line prompt asking you what you want to edit, it will walk you through some options

   `cozy edit <id>`

   - you can change the filename
   - you can add / remove / clear tags


### 1. Download a model

To download a model, the basic command is:

`cozy download <url> <model-type> <model-base-type> <optional filename>` 

For example lets say we want to download a `sdxl` `lora` from civitai, 
we can copy the url and download it on the cli like this:

`cozy download https://civitai/path/to/lora/here lora sdxl`

Or lets say we want to download the `flux1-dev` `ae.safetensors` file from huggingface.
The original `ae.safetensors` filename is a bit ambiguous, so we can pass in a new name
to store it like `flux1-dev-ae.safetensors`

`pp-manager-dl https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/ae.safetensors vae flux1 flux1-dev-ae.safetensors`

The `model-type` and the `model-base-type` will create subdirectories in the `MODEL_STORAGE_DIR`


### 2. Unload Models 

You can clear up disk space by unloading models from your drive. If you run the unload command it will remove all the locally stored models from your drive. e.g.

`cozy unload`

To remove all the models with a specific tag:

#### TBD:

`cozy unload --tag <tag>`

`cozy unload --model-type <model-type>`

`cozy unload --model-base <model-base>`

### 3. Reload Models

Since all the information of our previously downloaded models are stored in a json file, 
we can redownload all the models by running:

`cozy reload`

#### TBD:

`cozy reload --tag <tag>` ## reloads all the models with a specific tag

`cozy reload --model-type <model-type>` ## reloads all the models with a specific model type

`cozy reload --model-base <model-base>` ## reloads all the models with a specific model base

### 5. List Models

`cozy list --all`

`cozy list --loaded` ## shows the models that are currently stored locally

`cozy list --unloaded` ## show shte models that are not stored locally and only available 'virtually' in the json file

`cozy list --data` ## shows the size of the models stored locally


### 6. Edit Mode..

`cozy edit <id>`

this will open a command line prompt asking you what you want to edit, it will walk you through some options