import speech_recognition as sr
import logging
import time
from langdetect import detect
from .utils import setup_logging

class SpeechToText:
    """
    Handles speech recognition and conversion to text.
    Supports wake word detection and multilingual speech recognition.
    """
    def __init__(self, config):
        """
        Initialize the speech recognition with configuration.
        
        Args:
            config: Configuration dictionary from config.json
        """
        self.config = config
        self.recognizer = sr.Recognizer()
        
        # Configure speech recognition parameters
        speech_config = config["speech"]["input"]
        self.device_index = speech_config["device_index"]
        self.recognizer.energy_threshold = speech_config["energy_threshold"]
        self.recognizer.pause_threshold = speech_config["pause_threshold"]
        self.timeout = speech_config["timeout"]
        
        # Setup language
        self.default_language = config["language"]["default"]
        self.auto_detect_language = config["language"]["auto_detect"]
        
        # Setup logging
        if config["logging"]["enabled"]:
            self.logger = setup_logging(config["logging"]["level"], 
                                       config["logging"]["file"])
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.ERROR)
            
        # Check microphone availability
        self._check_mic_availability()
            
    def _check_mic_availability(self):
        """Check and print available microphones."""
        available_mics = sr.Microphone.list_microphone_names()
        self.logger.info(f"Available microphones: {available_mics}")
        
        # If device_index is None, use default microphone
        if self.device_index is None:
            self.logger.info("Using default microphone")
        else:
            if self.device_index < len(available_mics):
                self.logger.info(f"Using microphone: {available_mics[self.device_index]}")
            else:
                self.logger.warning(f"Specified microphone index {self.device_index} out of range. Using default.")
                self.device_index = None
    
    def listen_for_wake_word(self, wake_word):
        """
        Listen for the wake word. 
        
        Args:
            wake_word: The wake word to listen for, e.g. "jarvis"
            
        Returns:
            bool: True if wake word detected, False otherwise
        """
        with sr.Microphone(device_index=self.device_index) as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                self.logger.debug("Listening for wake word...")
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                try:
                    # Use Google's speech recognition service
                    text = self.recognizer.recognize_google(audio).lower()
                    self.logger.debug(f"Heard: {text}")
                    
                    # Check if wake word is in the recognized text
                    if wake_word.lower() in text.lower():
                        self.logger.info(f"Wake word '{wake_word}' detected")
                        return True
                        
                except sr.UnknownValueError:
                    # Speech wasn't understood
                    pass
                except sr.RequestError as e:
                    self.logger.error(f"Could not request results; {e}")
                    
            except sr.WaitTimeoutError:
                # Timeout occurred
                pass
                
        return False
    
    def listen_and_transcribe(self):
        """
        Listen for speech and convert to text.
        
        Returns:
            tuple: (transcribed_text, detected_language)
        """
        with sr.Microphone(device_index=self.device_index) as source:
            self.logger.info("Listening...")
            
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                audio = self.recognizer.listen(source, timeout=self.timeout, phrase_time_limit=10)
                self.logger.info("Audio captured, transcribing...")
                
                # Try different recognition services
                try:
                    # Try to auto-detect language if configured
                    language = self.default_language
                    
                    if self.auto_detect_language:
                        # First try to recognize with default language
                        try:
                            text = self.recognizer.recognize_google(audio, language=language)
                            
                            # Try to detect language from text
                            detected_lang = detect(text)
                            
                            # If detected language differs from default, re-recognize with detected language
                            if detected_lang != language:
                                language = detected_lang
                                text = self.recognizer.recognize_google(audio, language=language)
                                
                        except Exception:
                            # If failed with default language, try with English
                            text = self.recognizer.recognize_google(audio, language='en')
                            language = 'en'
                    else:
                        # Use default language
                        text = self.recognizer.recognize_google(audio, language=language)
                    
                    self.logger.info(f"Transcribed: '{text}' (Language: {language})")
                    return text, language
                    
                except sr.UnknownValueError:
                    self.logger.warning("Speech Recognition could not understand audio")
                    return None, None
                    
                except sr.RequestError as e:
                    self.logger.error(f"Could not request results; {e}")
                    return None, None
                    
            except sr.WaitTimeoutError:
                self.logger.warning("No speech detected within timeout period")
                return None, None
                
            except Exception as e:
                self.logger.error(f"Error in speech recognition: {e}", exc_info=True)
                return None, None