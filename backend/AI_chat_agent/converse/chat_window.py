import tkinter as tk
from tkinter import scrolledtext
import json

class ChatWindow:
    def __init__(self, root, conversation_manager):
        self.root = root
        self.conversation_manager = conversation_manager
        self.conversation_log = ""

        # Create a new scrolled text field to display the conversation log
        self.conversation_log_field = scrolledtext.ScrolledText(root, height=20, width=40)
        self.conversation_log_field.pack(fill="both", expand=True)

        # Load conversation history
        if self.conversation_manager.conversation_id:
            self.load_conversation_history()

        # Create a new label for the message input
        self.message_label = tk.Label(root, text="Message:")
        self.message_label.pack()

        # Create a new text entry field for the message
        self.message_entry = tk.Text(root, height=5, width=40)
        self.message_entry.pack()

        # Create a new button to add the message to the conversation log
        self.send_button = tk.Button(root, text="Send", command=self.send_and_receive_message)
        self.send_button.pack()

        # Bind Ctrl+Enter to send_and_receive_message
        self.root.bind("<Control-Return>", self.send_and_receive_message)

    def send_and_receive_message(self, event=None):
        # Get the current message
        message = self.message_entry.get("1.0", tk.END)
        self.conversation_log += "-------------------------\nUser: " + message + "\n"
        response = self.conversation_manager.send_message(message)

        # Clear the message field
        self.message_entry.delete('1.0', tk.END)

        # Update conversation log with a delimiter
        self.update_conversation_log("\n-------------------------\nAssistant: " + response + "\n")

        self.conversation_log_field.see(tk.END)

    def load_conversation_history(self):
        with open(self.conversation_manager.conversation_history_path, 'r') as file:
            history = json.load(file)

        for i, entry in enumerate(history):
            if i > 0:
                self.conversation_log += "\n-------------------------\n"
            if entry['role'] == 'assistant':
                self.conversation_log += "Assistant: " + entry['content'] + "\n"
            elif entry['role'] == 'user':
                self.conversation_log += "User: " + entry['content'] + "\n"

        self.update_conversation_log("")

    def update_conversation_log(self, message):
        if message != "":
            self.conversation_log += message
        self.conversation_log_field.delete("1.0", tk.END)
        self.conversation_log_field.insert(tk.END, self.conversation_log)

if __name__ == "__main__":
    from conversation_manager import create_conversation_manager
    
    conversation_manager = create_conversation_manager()
    root = tk.Tk()
    window = ChatWindow(root, conversation_manager)
    root.mainloop()