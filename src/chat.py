"""
chat.py

This module implements the Chat class which manages an interactive conversation
with a character using a registered backend model.
"""

import json
import requests
from src.model_register import RegisterModel


class Chat:
    """
    A chat bot that interacts with a user by sending prompts to a backend model.

    Attributes:
        OLLAMA_SERVER_URL (str): The URL for the backend model API.
    """
    OLLAMA_SERVER_URL = "http://localhost:11434/api/generate"

    def __init__(self, config_path="chat_config.json"):
        """
        Initialize the Chat instance.

        Args:
            config_path (str): Path to the JSON configuration file. Defaults to "chat_config.json".
        """
        self.register_model = RegisterModel()
        self.register_model.run()
        self.model_name = self.register_model.model['name']
        self.load_chat_config(config_path)
        self.setup_conversation()
        self.chat_options = self.get_chat_options()

    def load_chat_config(self, config_path: str) -> None:
        """
        Load conversation configuration from a JSON file.

        The configuration file should contain a list of characters. The user is prompted
        to pick one of the characters, and the corresponding conversation settings are loaded.

        Args:
            config_path (str): Path to the JSON configuration file.
        """
        try:
            with open(config_path, "r") as f:
                chat_configs = json.load(f)

            print("Choose a character to chat:")
            for index, config in enumerate(chat_configs, start=1):
                print(f"{index}. {config['character']['name']}")

            while True:
                try:
                    choice = int(input("Enter the number of the desired character: "))
                    if 1 <= choice <= len(chat_configs):
                        selected_config = chat_configs[choice - 1]
                        print(f"You chose: {selected_config['character']['name']}")
                        break
                    else:
                        print("Invalid choice. Try again!")
                except ValueError:
                    print("Invalid input. Please enter a number.")

            self.user = selected_config["user"]
            self.character = selected_config["character"]
            self.character_name = self.character["name"]
            self.context = selected_config["context"]
            self.scenario = selected_config["scenario"]

        except Exception as e:
            print(f"Error loading chat configuration: {e}")
            # Set default values in case of error.
            self.user = "User"
            self.character_name = "Assistant"
            self.context = "[You are an assistant. Engage in a friendly conversation.]"
            self.character = "The assistant is very knowledgeable and helpful."
            self.scenario = f"{self.character_name} is conversing with {self.user}."

        print(f"\nLoaded chat configuration for {self.character_name}.")
        print(f"User: {self.user}")
        print("Character:")
        for key, value in self.character.items():
            print(f"  {key.capitalize()}: {value}")
        print(f"Scenario: {self.scenario}")
        print(f"Context: {self.context}\n")

    def setup_conversation(self):
        """
        Set up initial conversation parameters.

        Initializes the stop sequence used to indicate the termination of a conversation segment,
        the conversation message list, and the conversation memory string.
        """
        self.stop_sequence = [
            f"{self.user}:",
            f"\n{self.user} ",
            f"\n{self.character_name}: ",
            "\n",
            ". "
        ]
        self.conversation = []
        self.memory = (
            f"Character: {self.character}\n"
            f"Context: {self.context}\n"
            f"[Scenario: {self.scenario}]\n"
        )

    def get_chat_options(self) -> dict:
        """
        Return the options for generating the chatbot response.

        These options include parameters like temperature, top_p, maximum tokens, and a stop sequence.

        Returns:
            dict: A dictionary containing options for the model.
        """
        return {
            "temperature": 0.8,
            "top_p": 0.9,
            "max_tokens": 240,
            "num_predict": 50,
            "repeat_penalty": 1.1,
            "stop": self.stop_sequence
        }

    def update_memory(self) -> str:
        """
        Update the conversation memory with a truncated history if necessary.

        If the total character count of the conversation exceeds 4000,
        older messages (except the initial context) are removed until the limit is met.
        Returns a concatenated string of the fixed memory and formatted conversation.

        Returns:
            str: The conversation memory string.
        """
        total_characters = sum(len(item['content']) for item in self.conversation)
        while total_characters > 4000:
            try:
                self.conversation.pop(1)
                total_characters = sum(len(item['content']) for item in self.conversation)
            except Exception as e:
                print(f"Error removing old messages: {e}")
                break

        formatted_conversation = (
            "\n".join(
                f"{msg['role']}: {msg['content']}" for msg in self.conversation
            )
            + f"\n{self.character_name}: "
        )
        return self.memory + formatted_conversation

    def get_response(self, prompt: str, chat_options: dict) -> str:
        """
        Query the backend model and return the character's response.

        Args:
            prompt (str): The prompt combining memory and conversation history.
            chat_options (dict): Options for generating the response (e.g., temperature and max_tokens).

        Returns:
            str: The generated response text or an empty string if an error occurred.
        """
        response = requests.post(
            self.OLLAMA_SERVER_URL,
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": chat_options
            }
        )

        if response.status_code == 200:
            res_text = response.json().get("response", "").strip()
            if res_text and res_text[-1] not in ['?', '!', "."]:
                res_text += "."
            if f"{self.character_name}: " in res_text:
                res_text = res_text.replace(f"{self.character_name}: ", "")
            return res_text
        else:
            print("Error retrieving response:", response.text)
            return ""

    def run(self):
        """
        Start an interactive chat session with the character.

        The session can be exited by typing 'exit'.
        """
        print(f"Chat with {self.character_name} started! Type 'exit' to quit.")

        while True:
            user_msg = input("You: ").strip()
            if user_msg.lower() == "exit":
                print("Closing...")
                break
            if user_msg and user_msg[-1] not in ['?', '!', "."]:
                user_msg += "."

            self.conversation.append({'role': self.user, 'content': user_msg})
            prompt = self.update_memory()
            character_response = self.get_response(prompt, self.chat_options)

            if character_response:
                print(f"{self.character_name}:", character_response)
                self.conversation.append({'role': self.character_name, 'content': character_response})
