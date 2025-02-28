import tkinter as tk
from tkinter import scrolledtext, Entry, Button, PhotoImage, filedialog, messagebox, font
import threading
import os
import datetime


class ChatView:
    def __init__(self, selected_character, user_name):
        """
        Initialize the chat view for a specific character.
        
        Args:
            selected_character (str): The name of the selected character
        """

        # set arguments
        self.selected_character = selected_character
        self.user_name = user_name

        # Flag to track microphone input mode
        self.mic_input_active = False
        
        # Callback for message processing
        self.message_callback = None

        # Add a flag to track processing state
        self.is_processing = False

        # GUI Setup
        self.window = tk.Tk()
        self.window.title(f"Chat with {self.selected_character}")
        self.window.geometry("600x650")

        # Top section: AI Message Display
        self.ai_message_font = font.Font(family="Arial", size=18, weight="bold")
        self.ai_message_display = scrolledtext.ScrolledText(
            self.window, 
            wrap=tk.WORD, 
            width=70, 
            height=5, 
            state='disabled',
            font=self.ai_message_font
        )
        self.ai_message_display.pack(padx=10, pady=10, fill=tk.X)

        # Middle: chat history section to include a save button
        self.history_frame = tk.Frame(self.window)
        self.history_frame.pack(padx=10, pady=10, fill=tk.X)

        # Chat History Label
        self.history_label = tk.Label(self.history_frame, text="Chat History")
        self.history_label.pack(side=tk.LEFT)

        # Save History Button
        self.save_history_button = Button(
            self.history_frame, 
            text="💾 Save", 
            command=self.save_chat_history
        )
        self.save_history_button.pack(side=tk.RIGHT)

        # Chat History ScrolledText (moved inside frame)
        self.chat_history = scrolledtext.ScrolledText(
            self.window, 
            wrap=tk.WORD, 
            width=70, 
            height=20, 
            state='disabled'
        )
        self.chat_history.pack(padx=10, pady=(0,10), fill=tk.X)

        # Bottom section: User Message Input
        self.input_frame = tk.Frame(self.window)
        self.input_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.user_input_font = font.Font(family="Arial", size=14)
        self.user_input = Entry(
            self.input_frame, 
            width=70,
            font=self.user_input_font 
        )
        self.user_input.pack(expand=True, fill=tk.X)
        
        # New frame for buttons
        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack(padx=10, pady=(0,10), fill=tk.X)
        
        # Mic Button
        self.mic_button = Button(
            self.button_frame, 
            text="🎤", 
            command=self.toggle_mic_input,
            width=10
        )
        self.mic_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Send Button
        self.send_button = Button(
            self.button_frame, 
            text="Send", 
            command=self.send_message,
            width=10
        )
        self.send_button.pack(side=tk.RIGHT)

        # Bind Enter key to send message
        self.user_input.bind('<Return>', lambda event: self.send_message())
        
    
    def set_message_callback(self, callback):
        """
        Set the callback method for processing user messages.
        
        Args:
            callback (callable): Method to process user messages
        """
        self.message_callback = callback
    
    def toggle_mic_input(self):
        """
        Toggle microphone input mode
        """
        self.mic_input_active = not self.mic_input_active
        
        if self.mic_input_active:
            # Change button appearance to indicate active mic mode
            self.mic_button.config(relief=tk.SUNKEN, bg='light green')
            self.update_chat_history("Microphone input mode activated. Press and hold SPACE to record.")
        else:
            # Reset button appearance
            self.mic_button.config(relief=tk.RAISED, bg='SystemButtonFace')
            self.update_chat_history("Microphone input mode deactivated.")
    
    def save_chat_history(self):
        """
        Save the chat history to a text file.
        Allows user to choose save location and filename.
        """
        # Get current chat history content
        chat_content = self.chat_history.get(1.0, tk.END).strip()
        
        if not chat_content:
            tk.messagebox.showinfo("Save History", "No chat history to save.")
            return

        # Generate default filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"chat_history_{self.selected_character}_{timestamp}.txt"

        # Open file save dialog
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=default_filename
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(chat_content)
                messagebox.showinfo("Save History", f"Chat history saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file: {str(e)}")
    
    def send_message(self):
        """
        Modified send_message to handle both keyboard and mic input
        """
        if self.mic_input_active:
            # If mic input is active, do nothing (mic input will be handled separately)
            return
        
        # Existing keyboard input logic
        user_message = self.user_input.get().strip()
        if user_message and self.message_callback:
            if not self.is_processing:
                self.is_processing = True
                self.user_input.config(state='disabled')
                self.send_button.config(state='disabled')
                
                self.update_chat_history(f"{self.user_name}: {user_message}")
                self.user_input.delete(0, tk.END)
                
                threading.Thread(target=self.process_message, args=(user_message,), daemon=True).start()

    def process_message(self, user_message):
        """
        Process message in a separate thread and re-enable UI
        """
        try:
            # Call message processing callback
            self.message_callback(user_message)
        except Exception as e:
            print(f"Error processing message: {e}")
        finally:
            # Use after method to update UI on main thread
            self.window.after(0, self.reset_ui)
    
    def reset_ui(self):
        """
        Reset UI state after processing
        """
        self.user_input.config(state='normal')
        self.user_input.delete(0, tk.END)
        self.send_button.config(state='normal')
        self.is_processing = False

    def display_ai_message(self, ai_message):
        """
        Display AI message in the top section
        
        Args:
            ai_message (list): Message from the AI
        """
        self.ai_message_display.config(state='normal')
        self.ai_message_display.delete(1.0, tk.END)
        self.ai_message_display.insert(tk.END, ai_message)
        self.ai_message_display.config(state='disabled')
        
        # Also add to chat history
        self.update_chat_history(f"{self.selected_character}: {ai_message}")
    
    def update_chat_history(self, message):
        """
        Update the chat history with a new message
        
        Args:
            message (str): Message to add to chat history
        """
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, message + "\n")
        self.chat_history.config(state='disabled')
        self.chat_history.see(tk.END)
    
    def show(self):
        """
        Show the chat window
        """
        self.window.mainloop()