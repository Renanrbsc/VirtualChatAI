# VirtualChatAI

VirtualChatAI is an interactive chatbot project that uses a registered backend model through the Ollama server. 
The project consists of two main modules:

- **model_register.py**: Handles model registration and launching of the Ollama server.
- **chat.py**: Implements the interactive chat session with a character using the registered model.

## Prerequisites

- Python 3.7+
- Ollama installed and available in your system PATH.
- Basic knowledge of command line operations.

## Setup

### 1. Clone the repository

Clone the project repository to your local machine:

```sh
git clone https://github.com/Renanrbsc/VirtualChatAI.git
cd VirtualChatAI
```

### 2. Create a Virtual Environment

Create a virtual environment to manage Python dependencies:

```sh
python3 -m venv venv
```

Activate the virtual environment:

- On Linux/Mac:
  
  ```sh
  source venv/bin/activate
  ```

- On Windows:
  
  ```sh
  venv\Scripts\activate
  ```

### 3. Install Dependencies

Install required packages using the provided `requirements.txt` file:

```sh
pip install -r requirements.txt
```

## Configuration

### 1. Model Registration Configuration (`config.ini`)

Create a file named `config.ini` in the project’s root directory with the following structure:

```ini
[ModelLLM]
name_model = <YOUR_MODEL_NAME>
path_model = <PATH_TO_YOUR_MODEL_FILE>
```

Replace `<YOUR_MODEL_NAME>` and `<PATH_TO_YOUR_MODEL_FILE>` with your model’s actual name and file path.

The file format must be `.txt` and contain the string `FROM`.

**Example:**

- **File**: `Mistral-7B-Instruct-v0.2-GGUF/Modelfile.txt`
- **Data**:
  
  ```txt
  FROM ./mistral-7b-instruct-v0.2.Q4_0.gguf
  ```

### 2. Chat Configuration (`chat_config.json`)

Create a `chat_config.json` file to define conversation settings and available characters.

**Example structure:**

```json
[
  {
    "user": "User",
    "character": {
      "name": "Assistant",
      "description": "A knowledgeable assistant ready to help."
    },
    "context": "[You are a helpful assistant. Engage in a friendly conversation.]",
    "scenario": "Assistant is conversing with User."
  }
]
```

Feel free to customize the character, context, and scenario as needed.

## Running the Chatbot

After setting up the configurations and installing dependencies, start the interactive chat session by running:

```sh
python src/main.py
```

During the session, you will be prompted to choose a character from the chat configuration. Then, type your messages to interact with the character. Type `exit` at any time to close the chat session.

### 1. Model Registration and Server Start

When the chat session starts, the chatbot uses `model_register.py` to:

- Register the model with Ollama (if not already registered).
- Verify if the Ollama server is running.
- Start the server with defined parameters if needed.

### 2. Chat Session

The `chat.py` module handles user interaction:

- Loads conversation configuration from `chat_config.json`.
- Sets up conversation context and history.
- Sends user input to the backend model for generating responses.
- Displays the character's response in the terminal.

---
