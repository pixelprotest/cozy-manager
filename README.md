# Cozy Manager

AI Model Manager is a tool for downloading and managing AI models from various sources, including Hugging Face and Civitai.

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

## Usage

The AI Model Manager provides three main commands:

to download a model from a url: `cozy download`

to remove all downloaded models: `cozy unload`

to reload all previously downloaded models: `cozy reload`

other commands:

to list all the models in the db: `cozy list`
- you can list the ones that are currently downloaded:

   `cozy list --local`
- you can list the ones that are not downloaded:

   `cozy list --virtual`

edit the db entry for a model, this will open a command line prompt asking you what you want to edit, it will walk you through some options
   `cozy edit <id>`
- you can change the filename
- you can add / remove / clear tags

to remove a model from the db: `cozy purge`


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


### 2. Clear Up Space

To remove all the downloaded models, we can run:
`cozy clear`

To remove all the models with a specific tag, we can run:

`cozy clear --tag <tag>`

### 3. Reload Models

Since all the information of our previously downloaded models are stored in a json file, 
we can redownload all the models by running:
`cozy reload`

### 4. Purge Models

If you want to fully remove a model from both the storage and the json file, you can run:
`cozy purge <id>`

### 5. List Models

`cozy list --all`

`cozy list --local` ## shows the models that are currently stored locally

`cozy list --virtual` ## show shte models that are not stored locally and only available 'virtually' in the json file

`cozy list --data` ## shows the size of the models stored locally


### 6. Edit Mode..

`cozy edit <id>`

this will open a command line prompt asking you what you want to edit, it will walk you through some options