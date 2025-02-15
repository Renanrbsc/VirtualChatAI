class TerminalView:
    """
    A class used to interact with the user via the terminal.

    This class provides methods to display messages, get user inputs, and allow
    the user to select input/output languages and input methods.
    """

    def display_message(self, message: str) -> None:
        """
        Display a message in the terminal.

        Args:
            message (str): The message to be displayed.
        """
        print(message)

    def get_input(self, prompt: str) -> str:
        """
        Get input from the user based on the provided prompt.

        Args:
            prompt (str): The prompt that will be displayed to the user.

        Returns:
            str: The user's input as a stripped string.
        """
        return input(prompt).strip()

    def select_input_language(self) -> str:
        """
        Ask the user to select the input language.

        The user can choose between Portuguese and English.

        Returns:
            str: "pt" for Portuguese or "en" for English.
        """
        print("Select your input language:")
        print("1) Portuguese")
        print("2) English")
        choice = ""
        while choice not in ["1", "2"]:
            choice = self.get_input("Enter 1 or 2: ")
        return "pt" if choice == "1" else "en"

    def select_output_language(self) -> str:
        """
        Ask the user to select the output language.

        The user can choose between Portuguese and English.

        Returns:
            str: "pt" for Portuguese or "en" for English.
        """
        print("\nSelect output language:")
        print("1) Portuguese")
        print("2) English")
        choice = ""
        while choice not in ["1", "2"]:
            choice = self.get_input("Enter 1 or 2: ")
        return "pt" if choice == "1" else "en"

    def select_input_method(self) -> str:
        """
        Ask the user to select the input method.

        The user can choose between keyboard input and microphone input.

        Returns:
            str: "keyboard" if the user selects keyboard input or "mic" if
                 the user selects microphone input.
        """
        print("\nSelect your input method:")
        print("1) Keyboard input")
        print("2) Microphone input")
        choice = ""
        while choice not in ["1", "2"]:
            choice = self.get_input("Enter 1 or 2: ")
        return "mic" if choice == "2" else "keyboard"

    def display_character_info(self, character_info: dict) -> None:
        """
        Display formatted character information in the terminal.

        Args:
            character_info (dict): A dictionary containing character details.
        """

        def format_info(info: dict, indent: int = 0) -> str:
            """
            Format the character information recursively for display.

            Args:
                info (dict): The dictionary containing character information.
                indent (int): The current indentation level.

            Returns:
                str: The formatted information as a string.
            """
            info_text = ""
            for key, value in info.items():
                if isinstance(value, dict):
                    info_text += " " * indent + f"{key.capitalize()}:\n"
                    info_text += format_info(value, indent + 2)
                else:
                    info_text += " " * indent + f"{key.capitalize()}: {value}\n"
            return info_text

        formatted_text = format_info(character_info)
        print("\n" + formatted_text)