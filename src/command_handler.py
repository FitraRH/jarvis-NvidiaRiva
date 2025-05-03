import logging
import datetime
import re
import random
from .utils import setup_logging

class CommandHandler:
    """
    Handles built-in and custom commands for the chatbot.
    """
    def __init__(self, config):
        """
        Initialize the command handler.
        
        Args:
            config: Configuration dictionary from config.json
        """
        self.config = config
        self.commands_config = config["commands"]
        
        # Setup logging
        if config["logging"]["enabled"]:
            self.logger = setup_logging(config["logging"]["level"], 
                                      config["logging"]["file"])
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.ERROR)
            
        # Extract command patterns
        self.exit_commands = self.commands_config["exit_commands"]
        self.custom_commands = self.commands_config["custom_commands"]
        
        # Initialize builtin commands handlers
        self.builtin_handlers = {
            "time": self._handle_time_command,
            "date": self._handle_date_command,
            "weather": self._handle_weather_command,
            "help": self._handle_help_command,
        }
        
        self.logger.info("Command handler initialized")
        
    def handle_command(self, user_input):
        """
        Check if the user input is a command and handle it if it is.
        
        Args:
            user_input: User input text
            
        Returns:
            str or None: Command response if it's a command, None otherwise
        """
        if not user_input:
            return None
            
        # Check if it's an exit command
        if user_input.lower() in self.exit_commands:
            return "Goodbye!"
            
        # Check custom commands
        lowercase_input = user_input.lower()
        
        for command_type, patterns in self.custom_commands.items():
            for pattern in patterns:
                if pattern.lower() in lowercase_input:
                    # Found a matching command
                    self.logger.info(f"Detected command: {command_type}")
                    
                    # Check if we have a handler for this command type
                    if command_type in self.builtin_handlers:
                        return self.builtin_handlers[command_type](user_input)
                        
        # No command matched
        return None
        
    def _handle_time_command(self, command):
        """Handle time-related commands."""
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."
        
    def _handle_date_command(self, command):
        """Handle date-related commands."""
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {current_date}."
        
    def _handle_weather_command(self, command):
        """
        Handle weather-related commands.
        
        Note: This is a placeholder. In a real implementation, you would
        call a weather API to get actual weather data.
        """
        # Extract location from command using regex
        location_match = re.search(r"(?:in|at|for)\s+([a-zA-Z\s]+)(?:\?)?$", command)
        
        if location_match:
            location = location_match.group(1).strip()
        else:
            location = "your location"
            
        # Placeholder responses (would be replaced with actual API call)
        weather_conditions = [
            "sunny", "partly cloudy", "cloudy", "rainy", "stormy",
            "windy", "snowy", "foggy", "humid", "clear"
        ]
        
        temperatures = list(range(0, 40))  # 0 to 39 degrees
        
        condition = random.choice(weather_conditions)
        temperature = random.choice(temperatures)
        
        return f"The weather in {location} is currently {condition} with a temperature of {temperature}°C. " \
               f"Note: This is a placeholder response. To implement actual weather data, " \
               f"you would need to integrate with a weather API."
               
    def _handle_help_command(self, command):
        """Handle help commands."""
        help_text = "Here are the commands I understand:\n"
        
        # Add time commands
        if "time" in self.custom_commands:
            help_text += "- Ask for the time: " + ", ".join(self.custom_commands["time"]) + "\n"
            
        # Add date commands
        if "date" in self.custom_commands:
            help_text += "- Ask for the date: " + ", ".join(self.custom_commands["date"]) + "\n"
            
        # Add weather commands
        if "weather" in self.custom_commands:
            help_text += "- Ask for weather: " + ", ".join(self.custom_commands["weather"]) + "\n"
            
        # Add exit commands
        help_text += "- Exit commands: " + ", ".join(self.exit_commands) + "\n"
        
        return help_text
        
    def add_custom_command_handler(self, command_type, handler_function):
        """
        Add a custom command handler.
        
        Args:
            command_type: Type of command (should match entries in config.json)
            handler_function: Function to handle the command
        """
        if command_type not in self.custom_commands:
            self.logger.warning(f"Command type '{command_type}' not found in configuration")
            return False
            
        self.builtin_handlers[command_type] = handler_function
        self.logger.info(f"Added custom handler for command type: {command_type}")
        return True