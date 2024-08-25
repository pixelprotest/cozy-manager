# AI Model Manager

AI Model Manager is a tool for downloading and managing AI models from various sources, including Hugging Face and Civitai.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/pixelprotest/ai-model-manager.git
   cd ai-model-manager
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

### 1. Download a model

To download a model, use the `pp-manager-dl` command followed by the required arguments:

