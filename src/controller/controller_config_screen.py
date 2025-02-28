from src.models.chat_base import ChatBase
from src.view.view_config_screen import ViewScreen
from src.view.view_chat_screen import ChatView
from src.controller.controller_chat_screen import ScreenChatController

class ScreenConfigController:
    def __init__(self):
        self.chat = ChatBase()
        self.view = ViewScreen()
    
        # Set the callback for character details retrieval
        self.view.set_character_details_callback(self.retrieve_character_details)
        
        # Set OK callback to launch chat screen
        self.view.set_ok_callback(self.launch_chat_screen)
    
        self.populate_character_selection()
        self.view.run()

    def populate_character_selection(self):
        """Populate the character selection dropdown with available characters."""
        available_characters = self.chat.get_character_names()
        self.view.update_character_options(available_characters)

    def retrieve_character_details(self, selected_character):
        """
        Retrieve and display character details.
    
        Args:
            selected_character (str): Name of the selected character
        """
        try:
            # Get full character information
            character_info = self.chat.get_character_info(selected_character)
        
            # Display character information through the view
            self.view.display_character_info(character_info)
        except Exception as e:
            print(f"Error retrieving character details: {e}")

    def launch_chat_screen(self, config_data):
        """
        Launch the chat screen with selected configuration.
        
        Args:
            config_data (dict): Configuration data from the config screen
        """
        # Validate configuration data
        if not config_data or not config_data.get('selected_character'):
            print("Please select a character before proceeding.")
            return

        # Close the configuration window
        self.view.root.destroy()
        
        # Initialize chat controller with view and configuration
        chat_controller = ScreenChatController(
            chat_model=self.chat,
            selected_character=config_data['selected_character'],
            input_language=config_data['input_language'],
        )
