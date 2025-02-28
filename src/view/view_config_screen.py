import tkinter as tk

class ViewScreen:
    def __init__(self):

        self.root = tk.Tk()
        self.root.title("VirtualChatAI")
        self.root.geometry("500x450")
        
        self.selected_character = None

        # Welcome text
        tk.Label(self.root, text="Bem-vindo ao VirtualChatAI!", font=("Arial", 16)).pack(pady=20)

        # Frame for language selection
        self.language_frame = tk.Frame(self.root)
        self.language_frame.pack(pady=10)

        tk.Label(self.language_frame, text="Selecione o Idioma de Entrada:").pack()
        self.input_language_var = tk.StringVar(value="en")
        tk.Radiobutton(self.language_frame, text="Inglês", variable=self.input_language_var, value="en").pack()
        tk.Radiobutton(self.language_frame, text="Português", variable=self.input_language_var, value="pt").pack()

        # Divider
        tk.Frame(self.root, height=2, bg="grey").pack(fill=tk.X, padx=10, pady=10)

        # Frame for character selection
        self.character_frame = tk.Frame(self.root)
        self.character_frame.pack(pady=10)

        tk.Label(self.character_frame, text="Selecione o Personagem:").pack()
        self.character_var = tk.StringVar(value="")  # Inicia vazio
        self.character_dropdown = tk.OptionMenu(self.character_frame, self.character_var, "")
        self.character_dropdown.pack()

        # Add a button to show character details
        tk.Button(self.root, text="Show Character Details", command=self.request_character_details).pack(pady=10)

        # OK button
        tk.Button(self.root, text="OK", command=self.on_ok).pack(pady=20)

    def update_character_options(self, characters):
        """Update the dropdown menu with available characters."""
        self.character_var.set("")  # Set default value to empty
        menu = self.character_dropdown["menu"]
        menu.delete(0, "end")
        for character in characters:
            menu.add_command(label=character, command=lambda value=character: self.character_var.set(value))

    def request_character_details(self):
        """
        Request character details through the controller callback.
        This method follows MVC by delegating the details retrieval to the controller.
        """
        selected_character = self.character_var.get()
        if selected_character and hasattr(self, 'character_details_callback'):
            self.character_details_callback(selected_character)

    def set_character_details_callback(self, callback):
        """
        Set the callback method for retrieving character details.

        Args:
            callback (callable): A method to be called with the selected character.
        """
        self.character_details_callback = callback

    def display_character_info(self, character_info):
        """
        Display character information in a new window.

        Args:
            character_info (dict): Dictionary containing character details
        """
        if not character_info:
            tk.messagebox.showinfo("Character Info", "No character information available.")
            return

        info_window = tk.Toplevel(self.root)
        info_window.title(f"Details for {character_info.get('character', {}).get('name', 'Unknown Character')}")
        info_window.geometry("400x500")

        # Create a frame with scrollbar for detailed information
        frame = tk.Frame(info_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(frame)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Populate character details
        character = character_info.get('character', {})
        details = [
            ("Name", character.get('name', 'N/A')),
            ("Personality", character.get('personality', 'N/A')),
            ("Greeting", character.get('greeting', 'N/A')),
            ("Scenario", character.get('scenario', 'N/A'))
        ]

        for label, value in details:
            tk.Label(scrollable_frame, text=f"{label}:", font=("Arial", 12, "bold")).pack(anchor='w')
            tk.Label(scrollable_frame, text=value, wraplength=350, justify=tk.LEFT).pack(anchor='w', pady=(0, 10))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Button(info_window, text="Close", command=info_window.destroy).pack(pady=10)

    def on_ok(self):
        """
        Prepare configuration data and trigger OK callback.
        """
        # Validate character selection
        if not self.character_var.get():
            tk.messagebox.showwarning("Warning", "Please select a character.")
            return

        # Prepare configuration dictionary
        config_data = {
            'input_language': self.input_language_var.get(),
            'selected_character': self.character_var.get()
        }

        # If a callback is set, call it with configuration data
        if hasattr(self, 'ok_callback'):
            self.ok_callback(config_data)
        else:
            print("No OK callback set.")

    def set_ok_callback(self, callback):
        """
        Set the callback method for the OK button.

        Args:
            callback (callable): Method to be called when OK is pressed
        """
        self.ok_callback = callback
        
    def on_character_selected(self, event=None):
        """
        Trigger when a character is selected in the dropdown.

        This method notifies the controller about the character selection
        by calling a callback method if provided.
        """
        self.selected_character = self.character_var.get()
        if self.selected_character and hasattr(self, 'character_selected_callback'):
            self.character_selected_callback(self.selected_character)
            print(f"Character selected: {self.selected_character}")

    def set_character_selected_callback(self, callback):
        """
        Set the callback method to be called when a character is selected.

        Args:
            callback (callable): A method to be called with the selected character.
        """
        self.character_selected_callback = callback

    def run(self):
        self.root.mainloop()
