import os
import groq
import json
from datetime import datetime

from groq import Groq
from pynput import keyboard
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Initialize Groq client with API key from .env file
API_KEY = os.getenv("GROQ_API_KEY")
client = groq.Groq(api_key=API_KEY)

# Shared flag to control program exit
running = True

# Initialize conversation history
conversation_history = [
    {"role": "system", "content": "You are a helpful assistant"}
]

# Folder path for conversations
folder_path = "conversations"

# Create a timestamped file name for the conversation
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
file_name = f"conversation_{timestamp}.json"
file_path = os.path.join("conversations", file_name)

# Ensure the folder exists
os.makedirs("conversations", exist_ok=True)

# Function to save conversation history to file
def save_conversation():
    with open(file_path, "w") as f:
        json.dump(conversation_history, f, indent=4)

def load_conversation():
    """Load an existing conversation from a file."""
    files = os.listdir(folder_path)
    json_files = [f for f in files if f.endswith(".json")]
    
    # Display available conversations
    if not json_files:
        print("No saved conversations found.")
        return False

    print("Available conversations:")
    for i, file in enumerate(json_files):
        print(f"{i + 1}. {file}")
    
    # Prompt user to select a conversation
    choice = int(input("Select a conversation to load (enter number): ")) - 1
    if choice < 0 or choice >= len(json_files):
        print("Invalid selection.")
        return False

    selected_file = os.path.join(folder_path, json_files[choice])

    # Load conversation from the selected file
    with open(selected_file, "r") as f:
        loaded_history = json.load(f)
        conversation_history.clear()
        conversation_history.extend(loaded_history)
    
    print(f"Loaded conversation from {json_files[choice]}")
    return True

def send_llm_message(message):
    # Add user message to conversation history
    conversation_history.append({"role": "user", "content": message})
    # Send the entire conversation history to maintain context
    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="llama3-8b-8192",  # Ensure this model exists
        stream=False,
    )

    # Get assistant's response and add it to conversation history
    response = chat_completion.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": response})
    
    # Save updated conversation history to file
    save_conversation()
    
    return response

def on_press(key):
    global running
    if key == keyboard.Key.esc:
        # Set running to False to exit the loop
        running = False
        return False  # Stop the listener

# Option to load a conversation
if input("Would you like to load a previous conversation? (y/n): ").strip().lower() == 'y':
    if not load_conversation():
        print("Starting a new conversation.")

# Start the listener
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Main loop
while running:
    message = input("You: ")
    if not running:  # Check if ESC was pressed to break the loop
        print("Exiting program...")
        break
    llm_response = send_llm_message(message)
    print("LLM:", llm_response)

# Stop the listener when exiting
listener.stop()
listener.join()

