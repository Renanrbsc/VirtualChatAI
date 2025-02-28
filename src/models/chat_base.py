import json
import requests
from src.models.model_register import RegisterModel

class ChatBase:
    """
    Base class for managing the conversation with the backend model.
    
    This class abstracts the conversation logic including configuration,
    memory management, and querying the backend model.
    """
    OLLAMA_SERVER_URL = "http://localhost:11434/api/generate"

    def __init__(self):
        self.register_model = RegisterModel()
        self.register_model.run()
        self.model_name = self.register_model.model['name']

    def load_chat_config(self, character_name, output_language) -> None:
        """
        Load conversation configuration from a JSON file.
        
        The configuration file should list characters. The user selection
        should be handled by the UI controller to choose which configuration
        to use. For now, we load the selected configuration.
        """
        try:
            selected_config = self.get_character_info(character_name)

            if output_language == "pt":
                output_language = "Portuguese"
            else:
                output_language = "English"

            self.user = selected_config["user"]
            self.char_name = selected_config["character"]["name"]
            self.char_personality = selected_config["character"]["personality"]
            self.char_greeting = selected_config["character"]["greeting"]
            self.char_scenario = selected_config["character"]["scenario"]
            self.char_language = output_language
            self.char_voice = selected_config["character"]["voice"]
            self.context = selected_config["context"]
            self.first_person = selected_config["first_person"]
        except Exception as e:
            print(f"Error loading chat configuration: {e}")
            # Provide default values if configuration fails.
            self.user = "User"
            self.char_name = "Assistant"
            self.char_personality = "The assistant is knowledgeable and helpful."
            self.char_greeting = "Hello! I'm here to assist you."
            self.char_scenario = f"{self.char_name} is conversing with {self.user}."
            self.char_language = "English"
            self.char_voice = "Soft"
            self.context = "You are an assistant. Engage in a friendly conversation."
            self.first_person = True

    def setup_conversation(self) -> None:
        """
        Set up the initial conversation parameters and memory.
        """
        self.stop_sequence = [
            f"{self.user}:",
            f"\n{self.user} ",
            f"\n{self.char_name}: ",
            "\n",
            ". "
        ]
        self.conversation = []

        if self.first_person:
            self.person_instruction = "Always answer in the first person.\n"
        else:
            self.person_instruction = "Always answer in the third person and describe scenario.\n"

        self.memory = (
            f"Character: {self.char_name}\n"
            f"Personality: {self.char_personality}\n"
            f"Greeting: {self.char_greeting}\n"
            f"Scenario: {self.char_scenario}\n"
            f"Language: {self.char_language}\n"
            f"Voice: {self.char_voice}\n"
            f"Context: {self.context}\n"
            f"Instruction: {self.person_instruction}\n"
        )

        self.chat_options = {
            "temperature": 0.8,
            "top_p": 0.9,
            "max_tokens": 240,
            "num_predict": 50,
            "repeat_penalty": 1.1,
            "stop": self.stop_sequence
        }

    def update_memory(self) -> str:
        """
        Build and return the current conversation prompt using the conversation history.
        """
        total_characters = sum(len(item['content']) for item in self.conversation)
        while total_characters > 4000 and len(self.conversation) > 1:
            try:
                removed = self.conversation.pop(0)
                total_characters -= len(removed['content'])
            except Exception as e:
                print(f"Error removing old messages: {e}")
                break

        formatted_conversation = (
            self.memory
            + "\n".join(
                f"{msg['role']}: {msg['content']}" for msg in self.conversation
            )
            + f"\n{self.char_name}: "
        )
        return formatted_conversation

    def get_response(self, prompt: str) -> str:
        """
        Query the backend model and return the generated response.
        """
        response = requests.post(
            self.OLLAMA_SERVER_URL,
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": self.chat_options
            }
        )

        if response.status_code == 200:
            res_text = response.json().get("response", "").strip()
            # Append punctuation if missing.
            if res_text and res_text[-1] not in ['?', '!', "."]:
                res_text += "."
            if f"{self.char_name}: " in res_text:
                res_text = res_text.replace(f"{self.char_name}: ", "")
            return res_text
        else:
            print("Error retrieving response:", response.text)
            return ""

    def get_all_characters(self, config_path: str = "chat_config.json") -> list:
        try:
            with open(config_path, "r") as f:
                chat_configs = json.load(f)
            return chat_configs
        except Exception as e:
            print(f"Error loading chat configurations: {e}")
            return []

    def get_character_names(self) -> list:
        """
        Return the names of all available characters.
        """
        return [char["character"]["name"] for char in self.get_all_characters()]
    
    def get_character_info(self, character_name: str) -> dict:
        """
        Retrieve the character information for the given character name.
        """
        for char in self.get_all_characters():
            if char["character"]["name"] == character_name:
                return char
        return {}
