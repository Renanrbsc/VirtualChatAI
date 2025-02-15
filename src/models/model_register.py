import subprocess
import time
import requests
import configparser


class RegisterModel:
    """
    A class to register a model with Ollama and manage its server.

    Attributes:
        config (configparser.ConfigParser): Parser for configuration file.
        model (dict): Contains 'name' and 'path' of the model from config file.
    """
    def __init__(self, config_path="config.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.model = {
            "name": self.config.get("ModelLLM", "name_model"),
            "path": self.config.get("ModelLLM", "path_model")
        }

    def register_model(self):
        """
        Register the model with Ollama if it is not already registered.

        It uses the subprocess.run to execute the 'ollama create' command with the model's
        name and file path.

        Raises:
            subprocess.CalledProcessError: If the subprocess command fails.
        """
        print(f"Registering model '{self.model['name']}' with Ollama...")
        try:
            subprocess.run(
                ["ollama", "create", self.model["name"], "--file", self.model["path"]],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            print("Model registered successfully!")
        except subprocess.CalledProcessError as e:
            print("Error registering the model:")
            print(e.stderr)
            raise

    def is_ollama_running(self):
        """
        Check if the Ollama server is running.

        Returns:
            bool: True if the server responds with a 200 HTTP status code, False otherwise.
        """
        try:
            response = requests.get("http://localhost:11434/api/tags")
            return response.status_code == 200
        except requests.ConnectionError:
            return False

    def start_ollama(self):
        """
        Start the Ollama server if it is not already running.

        This method starts the Ollama server with the model and specific parameters:
            --model: sets the model name.
            --gpu: number of GPUs to use (set to 1).
            --threads: number of threads (set to 4).
            --ctx: context size (set to 4096).
            -b: batch size (set to 2048).
            -ub: un-batched size (set to 512).
            --num_gpu_layers: number of GPU layers (set to 32).

        It waits up to 30 seconds for the server to start and verifies its status.
        """
        if self.is_ollama_running():
            print(f"Ollama server is already running.\n")
            return

        print("Starting the Ollama server with adjusted parameters...")
        try:
            subprocess.Popen(
                [
                    "ollama", "serve",
                    "--model", self.MODEL["name"],
                    "--gpu", "1",         # Use 1 GPU
                    "--threads", "4",     # Use 4 threads
                    "--ctx", "4096",      # Set context to 4096 token limit
                    "-b", "1024",         # Set batch size to 1024
                    "-ub", "256",         # Set un-batched size to 512
                    "--num_gpu_layers", "25"  # Allocate 25 GPU layers
                    "--tensor_split", "2"  # Equilibrate between CPU, GPU (60% RAM / CPU, 40% GPU)
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            timeout = 30
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.is_ollama_running():
                    print(f"Ollama server started successfully!\n")
                    return
                time.sleep(1)
            print("Error: Unable to confirm that the Ollama server started correctly.")
        except Exception as e:
            print(f"Error starting the Ollama server: {e}")

    def is_model_ready(self):
        """
        Check if the model is ready for use by querying the server.

        It sends a GET request to the server and verifies if the model is listed in the response.

        Returns:
            bool: True if the model is present in the server's model list, False otherwise.
        """
        try:
            response = requests.get("http://localhost:11434/api/tags")
            models = response.json().get("models", [])
            return any(m["name"] == self.model["name"] for m in models)
        except requests.ConnectionError:
            return False

    def run(self):
        """
        Execute the process of ensuring the model is registered and the Ollama server is running.

        If the model is not ready, it attempts to register the model and waits a maximum of 30 seconds.
        After verifying the model is ready, it starts the Ollama server if not already running.
        """
        if not self.is_model_ready():
            self.register_model()
            timeout = 30
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.is_model_ready():
                    print("Model is ready for use!")
                    break
                time.sleep(1)
            else:
                print("Error: Model was not registered after waiting.")
                return
        else:
            print("Model is already registered!")

        self.start_ollama()