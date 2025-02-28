from src.models.chat_base import ChatBase
from src.models.tts_converter import TextToSpeechConverter
from src.models.mic_converter import MicConverter
from src.models.translate_phrase import PhraseTranslator
from src.view.view_chat_screen import ChatView
import threading
import keyboard
import time


class ScreenChatController:
    def __init__(self,
                 chat_model: ChatBase,
                 selected_character: str, 
                 input_language: str = 'en'):
        """
        Initialize the ChatController with configuration and dependencies.
        
        Args:
            chat_view (ChatView): The chat interface view
            selected_character (str): Name of the selected character
            input_language (str, optional): Language for input. Defaults to 'en'.
        """
        # Model and View Setup
        self.chat = chat_model
        
        # Configuration
        self.selected_character = selected_character
        self.input_language = input_language
        
        # Additional Components
        self.tts_converter = TextToSpeechConverter(input_language)
        self.mic_converter = MicConverter(input_language)
        self.translator = PhraseTranslator(
            user_lang=input_language, 
        )
        # Load character configuration
        self.chat.load_chat_config(self.selected_character, self.input_language)
        self.chat.setup_conversation()
        if self.input_language != 'en':
            self.chat.memory = self.translator.translate_user_to_en(self.chat.memory)

        self.view = ChatView(selected_character, 
                             self.chat.user)

        # Start a thread to monitor mic input
        self.mic_input_thread = threading.Thread(target=self.monitor_mic_input, daemon=True)
        self.mic_input_thread.start()

        # Set up message callback
        self.view.set_message_callback(self.process_user_message)

        # Show the chat window
        self.view.show()
    
    def monitor_mic_input(self):
        """
        Monitor microphone input when mic mode is active
        """
        while True:
            # Check if mic input is active
            if self.view.mic_input_active:
                # Wait for SPACE to be pressed
                keyboard.wait('SPACE')
                
                try:
                    # Record audio
                    user_message = self.mic_converter.record_audio()
                    
                    if user_message:
                        # Update chat history with the transcribed message
                        self.view.window.after(0, self.view.update_chat_history, f"{self.chat.user}: {user_message}")
                    
                        # Process the transcribed message
                        self.view.window.after(0, self.view.send_message)
                        self.process_user_message(user_message)
                except Exception as e:
                    print(f"Error in mic input: {e}")
            
            # Small delay to prevent high CPU usage
            time.sleep(0.1)

    def process_user_message(self, user_message: str):
        """
        Process the user's message, translate if needed, get AI response, and display.
        
        Args:
            user_message (str): Message from the user
        """
        try:
            if self.input_language != 'en':
                user_message = self.translator.translate_user_to_en(user_message)

            if user_message and user_message[-1] not in ['?', '!', "."]:
                user_message += "."

            # Update conversation and get AI response
            self.chat.conversation.append({'role': self.chat.user, 'content': user_message})
            prompt = self.chat.update_memory()
            print(f"Prompt: {prompt}")

            character_response = self.chat.get_response(prompt)
            
            if self.input_language != 'en':
                translated_char_response = self.translator.translate_en_to_user(character_response)
            else:
                translated_char_response = character_response

            # Display AI message (thread-safe)
            self.view.window.after(0, self.view.display_ai_message, translated_char_response)
            
            # Text-to-Speech if enabled
            self.tts_converter.text_to_speech(translated_char_response)

            # Update conversation with AI response
            self.chat.conversation.append({'role': self.chat.char_name, 'content': character_response})
        
        except Exception as e:
            error_message = f"Error processing message: {str(e)}"
            self.view.window.after(0, self.view.display_ai_message, character_response)
            print(error_message)
