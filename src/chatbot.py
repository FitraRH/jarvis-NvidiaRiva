import os
import json
import torch
import logging
import time
from transformers import AutoModelForCausalLM, AutoTokenizer
from .speech_to_text import SpeechToText
from .text_to_speech import TextToSpeech
from .translation import Translator
from .command_handler import CommandHandler
from .utils import setup_logging

class Chatbot:
    """
    Main chatbot class that integrates DialoGPT with speech recognition and synthesis.
    """
    def __init__(self, config_path="config/config.json", use_voice_input=True, 
                 use_voice_output=True, default_language=None):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Override config with parameters if provided
        if default_language:
            self.config["language"]["default"] = default_language
        
        # Setup logging
        if self.config["logging"]["enabled"]:
            self.logger = setup_logging(self.config["logging"]["level"], 
                                      self.config["logging"]["file"])
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.ERROR)
            
        self.logger.info("Initializing chatbot...")
        
        # Initialize components
        self._init_model()
        
        self.translator = Translator(self.config["language"]["default"])
        self.command_handler = CommandHandler(self.config)
        
        self.use_voice_input = use_voice_input
        self.use_voice_output = use_voice_output
        
        if use_voice_input:
            self.stt = SpeechToText(self.config)
            
        if use_voice_output:
            self.tts = TextToSpeech(self.config)
            
        self.conversation_history = []
        self.chat_history_ids = None
        
        self.wake_word = self.config["wake_word"].lower()
        self.logger.info(f"Chatbot initialized with wake word: {self.wake_word}")
        
    def _init_model(self):
        """Initialize the DialoGPT model and tokenizer."""
        model_name = self.config["model"]["name"]
        
        self.logger.info(f"Loading model: {model_name}")
        
        # Check if we need to download the model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Enable model evaluation mode
        self.model.eval()
        
        # Move model to GPU if available
        if torch.cuda.is_available():
            self.logger.info("CUDA available. Moving model to GPU.")
            self.model = self.model.to('cuda')
        
    def process_input(self, user_input, input_language=None):
        """Process text input and generate a response."""
        # Check if this is a command
        command_response = self.command_handler.handle_command(user_input)
        if command_response:
            return command_response
        
        # Handle translation if needed
        detected_language = input_language
        translated_input = user_input
        
        if self.config["language"]["translation_enabled"] and not input_language:
            detected_language, translated_input = self.translator.translate_to_english(user_input)
        
        # Add to conversation history
        self.conversation_history.append(translated_input)
        if len(self.conversation_history) > self.config["model"]["max_history"]:
            self.conversation_history = self.conversation_history[-self.config["model"]["max_history"]:]
        
        # Encode the input
        new_user_input_ids = self.tokenizer.encode(translated_input + self.tokenizer.eos_token, 
                                                  return_tensors='pt')
        
        # Move input to GPU if available
        if torch.cuda.is_available():
            new_user_input_ids = new_user_input_ids.to('cuda')
        
        # Append to chat history
        bot_input_ids = new_user_input_ids
        if self.chat_history_ids is not None:
            bot_input_ids = torch.cat([self.chat_history_ids, new_user_input_ids], dim=-1)
        
        # Generate response
        self.chat_history_ids = self.model.generate(
            bot_input_ids,
            max_length=self.config["model"]["max_length"] + len(bot_input_ids[0]),
            pad_token_id=self.tokenizer.eos_token_id,
            no_repeat_ngram_size=3,
            do_sample=True,
            top_k=50,
            top_p=0.9,
            temperature=0.7
        )
        
        # Decode response
        response = self.tokenizer.decode(self.chat_history_ids[:, bot_input_ids.shape[-1]:][0], 
                                        skip_special_tokens=True)
        
        # Translate back if needed
        if self.config["language"]["translation_enabled"] and detected_language != "en":
            response = self.translator.translate_from_english(response, detected_language)
            
        return response
    
    def listen(self):
        """Listen for wake word and then for a command."""
        if not self.use_voice_input:
            return input("You: ")
        
        # Listen for wake word
        while True:
            wake_word_detected = self.stt.listen_for_wake_word(self.wake_word)
            if wake_word_detected:
                self.logger.info("Wake word detected. Listening for command...")
                if self.use_voice_output:
                    self.tts.speak("I'm listening")
                
                # Listen for command
                user_input, language = self.stt.listen_and_transcribe()
                if user_input:
                    return user_input, language
            
            # Sleep briefly to reduce CPU usage
            time.sleep(0.1)
    
    def speak(self, text):
        """Convert text to speech if voice output is enabled."""
        if self.use_voice_output:
            self.tts.speak(text)
        print(f"Bot: {text}")
            
    def start(self):
        """Start the conversation loop."""
        print(f"Chatbot initialized. Say '{self.wake_word}' to start talking.")
        
        try:
            while True:
                # Get user input
                if self.use_voice_input:
                    user_input, detected_language = self.listen()
                    print(f"You: {user_input}")
                else:
                    user_input = input("You: ")
                    detected_language = None
                
                # Check for exit command
                if user_input.lower() in self.config["commands"]["exit_commands"]:
                    self.speak("Goodbye!")
                    break
                
                # Process input and get response
                response = self.process_input(user_input, detected_language)
                
                # Speak the response
                self.speak(response)
                
        except KeyboardInterrupt:
            print("\nExiting chatbot...")
        except Exception as e:
            self.logger.error(f"Error in chatbot: {e}", exc_info=True)
            print(f"An error occurred: {e}")
        
        print("Chatbot terminated.")

if __name__ == "__main__":
    # Example usage
    chatbot = Chatbot()
    chatbot.start()