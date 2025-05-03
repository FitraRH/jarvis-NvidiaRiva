import pyttsx3
import logging
import os
import platform
from .utils import setup_logging

class TextToSpeech:
    """
    Handles text-to-speech functionality with support for different engines.
    Supports pyttsx3 by default, with optional NVIDIA Riva integration.
    """
    def __init__(self, config):
        """
        Initialize the text-to-speech engine.
        
        Args:
            config: Configuration dictionary from config.json
        """
        self.config = config
        
        # Setup logging
        if config["logging"]["enabled"]:
            self.logger = setup_logging(config["logging"]["level"], 
                                       config["logging"]["file"])
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.ERROR)
            
        # Get speech config
        self.speech_config = config["speech"]["output"]
        
        # Initialize the appropriate TTS engine
        self.engine_type = self.speech_config["engine"]
        
        if self.engine_type == "pyttsx3":
            self._init_pyttsx3()
        elif self.engine_type == "riva" and config["speech"]["riva"]["enabled"]:
            self._init_riva()
        else:
            self.logger.warning(f"Unknown TTS engine: {self.engine_type}. Falling back to pyttsx3.")
            self.engine_type = "pyttsx3"
            self._init_pyttsx3()
            
    def _init_pyttsx3(self):
        """Initialize the pyttsx3 engine."""
        self.logger.info("Initializing pyttsx3 TTS engine")
        self.engine = pyttsx3.init()
        
        # Configure voice properties
        self.engine.setProperty('rate', self.speech_config["rate"])
        self.engine.setProperty('volume', self.speech_config["volume"])
        
        # Set voice if specified
        voice_id = self.speech_config["voice_id"]
        if voice_id:
            self.engine.setProperty('voice', voice_id)
        else:
            # Try to set a good default voice based on the system
            self._set_default_voice()
            
    def _set_default_voice(self):
        """Set a default voice based on the system."""
        try:
            voices = self.engine.getProperty('voices')
            
            if len(voices) == 0:
                self.logger.warning("No voices found for pyttsx3")
                return
                
            # Get system information
            system = platform.system()
            
            if system == "Windows":
                # On Windows, try to find a female voice (usually better quality)
                for voice in voices:
                    if "female" in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        self.logger.info(f"Selected voice: {voice.name}")
                        return
                        
            elif system == "Darwin":  # macOS
                # On macOS, try to find a high-quality voice
                for voice in voices:
                    if "samantha" in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        self.logger.info(f"Selected voice: {voice.name}")
                        return
                        
            # Fallback to the first available voice
            self.engine.setProperty('voice', voices[0].id)
            self.logger.info(f"Selected default voice: {voices[0].name}")
            
        except Exception as e:
            self.logger.error(f"Error setting default voice: {e}")
            
    def _init_riva(self):
        """Initialize NVIDIA Riva TTS engine if available."""
        self.logger.info("Initializing NVIDIA Riva TTS engine")
        
        try:
            # Check if Riva dependencies are installed
            import grpc
            
            # Try to import Riva modules with error handling
            try:
                import nvidia.riva.client
                from nvidia.riva.client import SpeechSynthesisClient
                
                # Initialize Riva client
                riva_config = self.config["speech"]["riva"]
                auth = None
                
                if riva_config["auth_key"]:
                    auth = nvidia.riva.client.Auth(api_key=riva_config["auth_key"])
                    
                self.riva_client = SpeechSynthesisClient(
                    riva_config["server_url"],
                    auth=auth
                )
                
                self.logger.info("NVIDIA Riva TTS engine initialized successfully")
                return
                
            except ImportError:
                self.logger.warning("NVIDIA Riva modules not installed. Falling back to pyttsx3.")
            except Exception as e:
                self.logger.error(f"Error initializing Riva: {e}")
                
        except ImportError:
            self.logger.warning("gRPC not installed. Cannot use NVIDIA Riva.")
            
        # Fallback to pyttsx3
        self.engine_type = "pyttsx3"
        self._init_pyttsx3()
        
    def speak(self, text):
        """
        Convert text to speech.
        
        Args:
            text: The text to speak
        """
        if not text:
            self.logger.warning("Empty text provided to TTS engine")
            return
            
        self.logger.info(f"Speaking: {text}")
        
        if self.engine_type == "pyttsx3":
            self._speak_pyttsx3(text)
        elif self.engine_type == "riva":
            self._speak_riva(text)
            
    def _speak_pyttsx3(self, text):
        """Use pyttsx3 to speak the text."""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Error in pyttsx3 TTS: {e}")
            
    def _speak_riva(self, text):
        """Use NVIDIA Riva to speak the text."""
        try:
            # Synthesize speech using Riva
            resp = self.riva_client.synthesize(
                text=text,
                language_code="en-US",
                voice_name="English-US-Female-1",
                sample_rate_hz=44100
            )
            
            # Save to a temporary file and play it
            import tempfile
            import soundfile as sf
            import sounddevice as sd
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_filename = temp_file.name
                
            # Save the audio to the temp file
            audio_samples = resp.audio
            sf.write(temp_filename, audio_samples, 44100)
            
            # Play the audio
            data, fs = sf.read(temp_filename)
            sd.play(data, fs)
            sd.wait()
            
            # Clean up
            try:
                os.unlink(temp_filename)
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"Error in Riva TTS: {e}")
            
            # Fallback to pyttsx3 if Riva fails
            if hasattr(self, 'engine'):
                self._speak_pyttsx3(text)