import os
import logging
from datetime import datetime

def setup_logging(level_name="INFO", log_file=None):
    """
    Set up logging configuration.
    
    Args:
        level_name: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        
    Returns:
        logger: Configured logger object
    """
    # Map string level to logging level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    level = level_map.get(level_name.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log file is specified
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
    
def extract_wake_word(text, wake_word):
    """
    Check if the wake word is in the text.
    
    Args:
        text: Input text
        wake_word: Wake word to check for
        
    Returns:
        bool: True if wake word is in the text, False otherwise
    """
    return wake_word.lower() in text.lower()
    
def get_timestamp():
    """
    Get current timestamp string.
    
    Returns:
        str: Current timestamp in format YYYY-MM-DD_HH-MM-SS
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
def clean_text(text):
    """
    Clean text by removing extra whitespace and punctuation.
    
    Args:
        text: Input text
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
        
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()
    
def save_conversation(conversation_history, filename=None):
    """
    Save conversation history to a file.
    
    Args:
        conversation_history: List of conversation messages
        filename: Output filename (default: conversation_TIMESTAMP.txt)
        
    Returns:
        str: Path to saved file
    """
    if not filename:
        timestamp = get_timestamp()
        filename = f"conversation_{timestamp}.txt"
        
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(filename)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # Write conversation to file
    with open(filename, 'w', encoding='utf-8') as f:
        for i, message in enumerate(conversation_history):
            role = "User" if i % 2 == 0 else "Bot"
            f.write(f"{role}: {message}\n")
            
    return filename