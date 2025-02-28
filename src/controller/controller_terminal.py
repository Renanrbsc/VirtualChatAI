from src.models.chat_base import ChatBase
from src.models.tts_converter import TextToSpeechConverter
from src.models.mic_converter import MicConverter
from src.models.translate_phrase import PhraseTranslator
from src.view.view_terminal import TerminalView
import keyboard
import time


class TerminalChatController:
    """
    Controller for handling terminal-based chat interactions.

    This class facilitates a conversation between the user and the chat character,
    managing input methods, language translation, character switching, and speech synthesis.
    """

    def __init__(self):
        """
        Initialize the TerminalChatController by setting up the chat model,
        view interface, language translators, text-to-speech converter, and microphone input.

        It also prompts the user to select input and output languages, input method,
        and character configuration.
        """
        self.chat = ChatBase()
        self.view = TerminalView()

        # Select input language
        self.input_language = self.view.select_input_language()
        self.translator = PhraseTranslator(user_lang=self.input_language)
        self.tts_converter = TextToSpeechConverter(self.input_language)
        self.mic_converter = MicConverter(self.input_language)

        # Select the user input method
        self.input_method = self.view.select_input_method()

        # Select chat character and display associated information
        self.select_chat_character()

    def select_chat_character(self):
        """
        Prompts the user to select a chat character from the available list.

        It displays the available characters, retrieves the user's choice,
        loads the selected character's configuration, and shows detailed character information.
        """
        available_characters = self.chat.get_character_names()
        self.view.display_message("\nPersonagens disponíveis:")
        for character in available_characters:
            self.view.display_message(f"- {character}")

        selected_character = self.view.get_input("Selecione um personagem: ")
        character_info = self.chat.get_character_info(selected_character)
        self.chat.load_chat_config(selected_character, self.input_language)

        self.chat.setup_conversation()
        if self.input_language != 'en':
            self.chat.memory = self.translator.translate_user_to_en(self.chat.memory)

        self.view.display_character_info(character_info)

    def get_input_user(self):
        """
        Retrieves user input based on the specified input method.

        If the input method is keyboard, it prompts for text input.
        If the input method is microphone, it waits for the user to hold SPACE while speaking.

        Returns:
            str: The user input message or None if the input method is unsupported.
        """
        if self.input_method == "keyboard":
            return self.view.get_input(f"{self.chat.user}: ")
        elif self.input_method == "mic":
            self.view.display_message("Please press and hold SPACE while speaking and release to finish.")
            while not keyboard.is_pressed("SPACE"):
                time.sleep(1)
            user_msg = self.mic_converter.record_audio()
            print(f"{self.chat.user}:", user_msg)
            return user_msg
        else:
            return None

    def switch_response_attempt(self, prompt):
        """
        Provides the user with an option to request additional responses.

        The user is prompted up to three times to request a new response for the given prompt.
        If the user inputs 'y', a new character response is generated and processed. If 'n' is entered,
        the switching attempt stops.

        Args:
            prompt (str): The prompt used to generate the character's response.

        Returns:
            str or None: The final character response if a switch is made; otherwise, None.
        """
        count_switch = 1
        if self.input_method == "keyboard":
            user_msg_switch = self.view.get_input(f"{count_switch}/3 Switch: ")
            if user_msg_switch.lower() == "y":
                while True:
                    character_response = self.chat.get_response(prompt)
                    self.view.display_message(f"{self.chat.char_name}: {character_response}")

                    if self.input_language != 'en':
                        character_response_translated = self.translator.translate_en_to_user(character_response)
                        self.view.display_message(f"{self.chat.char_name}: {character_response_translated}")
                        self.tts_converter.text_to_speech(character_response_translated)
                    else:
                        self.tts_converter.text_to_speech(character_response)

                    count_switch += 1
                    if count_switch > 3:
                        self.view.display_message("Too many requests: limit 3")
                        break
                    user_msg_switch = self.view.get_input(f"{count_switch}/3 Switch: ")
                    if user_msg_switch.lower() == "n":
                        break
                return character_response
            elif user_msg_switch.lower() == "n":
                return None
            else:
                self.view.display_message("Invalid input. Please enter 'y' or 'n'.")
                return self.switch_response_attempt(prompt)
        else:
            return None

    def run(self):
        """
        Starts the interactive chat session.

        The method continuously retrieves user input, processes translation,
        appends conversation history, generates responses from the chat character,
        and applies text-to-speech conversion. The conversation continues until the user
        enters 'exit'.
        """
        self.view.display_message(f"Chat com {self.chat.char_name} iniciado! Digite 'exit' para sair.")
        while True:
            user_msg = self.get_input_user()
            if user_msg.lower() == "exit":
                self.view.display_message("Exiting...")
                break

            if user_msg and user_msg[-1] not in ['?', '!', "."]:
                user_msg += "."

            if self.input_language != 'en':
                user_msg_translated = self.translator.translate_user_to_en(user_msg)
                self.view.display_message(f"{self.chat.user}: {user_msg_translated}")
                user_msg = user_msg_translated

            self.chat.conversation.append({'role': self.chat.user, 'content': user_msg})
            prompt = self.chat.update_memory()

            character_response = self.chat.get_response(prompt)
            self.view.display_message(f"{self.chat.char_name}: {character_response}")

            if self.input_language != 'en':
                character_response_translated = self.translator.translate_en_to_user(character_response)
                self.view.display_message(f"{self.chat.char_name}: {character_response_translated}")
                self.tts_converter.text_to_speech(character_response_translated)
            else:
                self.tts_converter.text_to_speech(character_response)

            character_response_switch = self.switch_response_attempt(prompt)
            if character_response_switch:
                character_response = character_response_switch

            self.chat.conversation.append({'role': self.chat.char_name, 'content': character_response})

            time.sleep(1)