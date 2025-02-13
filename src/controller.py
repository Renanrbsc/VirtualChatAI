from src.modules.chat import Chat
from src.modules.tts_converter import TextToSpeechConverter
from src.modules.mic_converter import MicConverter
from src.modules.translate_phrase import PhraseTranslator
import keyboard
import time


class Controller:
    def __init__(self, config_path="chat_config.json"):
        """
        Initializes the Controller with a Chat instance and a MicConverter.

        Args:
            config_path (str): Path to the configuration file for the chat.
        """
        self.chat = Chat(config_path)
        self.mic = MicConverter()
        self.tts_converter = TextToSpeechConverter()
        self.input_method = self.select_input_method()
        self.input_language = self.select_input_language()
        self.translator_user = PhraseTranslator(source_lang=self.input_language, target_lang="en")
        self.translator_char = PhraseTranslator(source_lang="en", target_lang=self.input_language)

    def select_input_method(self) -> str:
        """
        Prompt the user once at the start of the project to choose an input method.

        Returns:
            str: "mic" if the user chooses microphone input, "keyboard" otherwise.
        """
        print("Select your input method (only once at the beginning):")
        print("1) Keyboard input")
        print("2) Microphone input")
        choice = ""
        while choice not in ["1", "2"]:
            choice = input("Enter 1 or 2: ").strip()
        if choice == "2":
            print("Microphone input selected.")
            return "mic"
        else:
            print("Keyboard input selected.")
            return "keyboard"
        
    def select_input_language(self) -> str:
        """
        Prompt the user to select the language for the user input.
        Returns:
            str: The selected language code.
        """
        print("\nSelect your input language:")
        print("1) Portuguese")
        print("2) English")
        choice = ""
        while choice not in ["1", "2"]:
            choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return "pt"
        else:
            return "en"
        
    def get_input(self, input_type="user", count_switch=1) -> str:
        """
        Get input based on the selected input method.

        Args:
            input_type (str): The type of input to get ("user" or "switch").
            count_switch (int): The current switch count for the user input.

        Returns:
            str: The message based on the input type parameter.
        """
        if input_type == "user":
            if self.input_method == "mic":
                print("Please press and hold SPACE while speaking and release to finish.")
                while not keyboard.is_pressed("SPACE"):
                    time.sleep(1)
                user_msg = self.mic.record_audio()
                print(f"{self.chat.user}:", user_msg)
            elif self.input_method == "keyboard":
                user_msg = input(f"{self.chat.user}: ").strip()
        elif input_type == "switch":
            if self.input_method == "keyboard":
                print(f"{count_switch}/3. Do you want to switch the message? (y/n)")
                user_msg = input("Switch? ").strip()
            elif self.input_method == "mic":
                user_msg = "n"
        return user_msg

    def run(self):
        """
        Starts the chat session, allowing user interaction and response generation.
        """
        print(f"Chat with {self.chat.char_name} started! Type 'exit' to quit.")

        while True:
            count_switch = 1
            user_msg = self.get_input(input_type="user")
            user_msg_translated = self.translator_user.translate(user_msg)
            if user_msg_translated:
                print(f"{self.chat.user}:", user_msg_translated)
                user_msg = user_msg_translated

            if user_msg.lower() == "exit":
                print("Exiting...")
                break
            
            if user_msg and user_msg[-1] not in ['?', '!', "."]:
                user_msg += "."

            self.chat.conversation.append({'role': self.chat.user, 'content': user_msg})
            prompt = self.chat.update_memory()
            
            character_response = self.chat.get_response(prompt, self.chat.chat_options)
            print(f"{self.chat.char_name}:", character_response)

            character_response_translated = self.translator_char.translate(character_response)
            if character_response_translated:
                print(f"{self.chat.char_name}:", character_response_translated)

            self.tts_converter.text_to_speech(character_response)

            user_msg_reset = self.get_input(input_type="switch", count_switch=count_switch)
            if user_msg_reset.lower() == "y":  
                while True:
                    character_response = self.chat.get_response(prompt, self.chat.chat_options)
                    print(f"{self.chat.char_name}:", character_response)

                    character_response_translated = self.translator_char.translate(character_response)
                    if character_response_translated:
                        print(f"{self.chat.char_name}:", character_response_translated)

                    self.tts_converter.text_to_speech(character_response)

                    count_switch += 1
                    if count_switch > 3:
                        print("Too many requests: limit 3")
                        break
                    user_msg_reset = self.get_input(input_type="switch", count_switch=count_switch)
                    if user_msg_reset.lower() == "n":
                        break
                    
            self.chat.conversation.append({'role': self.chat.char_name, 'content': character_response})
            
            time.sleep(1)
