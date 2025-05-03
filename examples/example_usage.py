import os
import sys
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chatbot import Chatbot
from src.speech_to_text import SpeechToText
from src.text_to_speech import TextToSpeech
from src.translation import Translator, LANGUAGE_MAPPING
from src.command_handler import CommandHandler

def basic_chatbot_example():
    """Run a basic example of the chatbot."""
    print("Starting basic chatbot example...")
    
    # Initialize chatbot with default settings
    chatbot = Chatbot(
        config_path="../config/config.json",
        use_voice_input=True,
        use_voice_output=True
    )
    
    # Start the conversation
    chatbot.start()

def text_only_chatbot_example():
    """Run a text-only example of the chatbot."""
    print("Starting text-only chatbot example...")
    
    # Initialize chatbot with voice input disabled but voice output enabled
    chatbot = Chatbot(
        config_path="../config/config.json",
        use_voice_input=False,
        use_voice_output=True,  # Ubah dari False menjadi True
        default_language="en"   # Tambahkan parameter ini untuk memastikan bahasa default Inggris
    )
    
    # Start the conversation
    chatbot.start()

def multilingual_chatbot_example():
    """Run a multilingual example of the chatbot."""
    print("Starting multilingual chatbot example...")
    
    # Load config
    with open("../config/config.json", 'r') as f:
        config = json.load(f)
    
    # Print available languages
    print("Available languages:")
    for i, (lang_name, lang_code) in enumerate(sorted(LANGUAGE_MAPPING.items())):
        print(f"{i+1}. {lang_name.title()} ({lang_code})")
    
    # Ask for language choice
    while True:
        lang_choice = input("\nEnter language name or code (default: english): ").strip().lower()
        
        if not lang_choice:
            lang_choice = "en"
            break
            
        # Check if it's a valid language name or code
        if lang_choice in LANGUAGE_MAPPING:
            lang_choice = LANGUAGE_MAPPING[lang_choice]
            break
        elif lang_choice in LANGUAGE_MAPPING.values():
            break
        else:
            print("Invalid language. Please try again.")
    
    # Initialize chatbot with selected language
    chatbot = Chatbot(
        config_path="../config/config.json",
        use_voice_input=True,
        use_voice_output=True,
        default_language=lang_choice
    )
    
    # Start the conversation
    chatbot.start()

def custom_commands_example():
    """Run an example with custom commands."""
    print("Starting custom commands example...")
    
    # Load config
    with open("../config/config.json", 'r') as f:
        config = json.load(f)
    
    # Initialize command handler
    cmd_handler = CommandHandler(config)
    
    # Add a custom command handler
    def handle_joke_command(command):
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "What do you call fake spaghetti? An impasta!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "I'm reading a book on anti-gravity. It's impossible to put down!"
        ]
        import random
        return random.choice(jokes)
    
    # Register the custom command
    cmd_handler.add_custom_command_handler("joke", handle_joke_command)
    
    # Add joke patterns to config
    config["commands"]["custom_commands"]["joke"] = [
        "tell me a joke", "joke", "make me laugh", "be funny"
    ]
    
    # Initialize chatbot with custom command handler
    chatbot = Chatbot(config_path="../config/config.json")
    chatbot.command_handler = cmd_handler
    
    # Start the conversation
    chatbot.start()

def main():
    """Main function to select and run an example."""
    print("==== Multilingual Voice Chatbot Examples ====")
    print("1. Basic Chatbot (voice input/output)")
    print("2. Text-Only Chatbot")
    print("3. Multilingual Chatbot")
    print("4. Custom Commands Example")
    
    choice = input("\nSelect an example (1-4): ")
    
    if choice == '1':
        basic_chatbot_example()
    elif choice == '2':
        text_only_chatbot_example()
    elif choice == '3':
        multilingual_chatbot_example()
    elif choice == '4':
        custom_commands_example()
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()