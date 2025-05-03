import logging
from langdetect import detect
from googletrans import Translator as GoogleTranslator
from .utils import setup_logging

# Language mapping dictionary
LANGUAGE_MAPPING = {
    'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar', 'armenian': 'hy', 'azerbaijani': 'az',
    'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn', 'bosnian': 'bs', 'bulgarian': 'bg', 'catalan': 'ca',
    'cebuano': 'ceb', 'chichewa': 'ny', 'chinese (simplified)': 'zh-cn', 'chinese (traditional)': 'zh-tw',
    'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da', 'dutch': 'nl', 'english': 'en',
    'esperanto': 'eo', 'estonian': 'et', 'filipino': 'tl', 'finnish': 'fi', 'french': 'fr', 'frisian': 'fy',
    'galician': 'gl', 'georgian': 'ka', 'german': 'de', 'greek': 'el', 'gujarati': 'gu', 'haitian creole': 'ht',
    'hausa': 'ha', 'hawaiian': 'haw', 'hebrew': 'he', 'hindi': 'hi', 'hmong': 'hmn', 'hungarian': 'hu',
    'icelandic': 'is', 'igbo': 'ig', 'indonesian': 'id', 'irish': 'ga', 'italian': 'it', 'japanese': 'ja',
    'javanese': 'jw', 'kannada': 'kn', 'kazakh': 'kk', 'khmer': 'km', 'korean': 'ko', 'kurdish (kurmanji)': 'ku',
    'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la', 'latvian': 'lv', 'lithuanian': 'lt', 'luxembourgish': 'lb',
    'macedonian': 'mk', 'malagasy': 'mg', 'malay': 'ms', 'malayalam': 'ml', 'maltese': 'mt', 'maori': 'mi',
    'marathi': 'mr', 'mongolian': 'mn', 'myanmar (burmese)': 'my', 'nepali': 'ne', 'norwegian': 'no',
    'odia': 'or', 'pashto': 'ps', 'persian': 'fa', 'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa',
    'romanian': 'ro', 'russian': 'ru', 'samoan': 'sm', 'scots gaelic': 'gd', 'serbian': 'sr', 'sesotho': 'st',
    'shona': 'sn', 'sindhi': 'sd', 'sinhala': 'si', 'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so',
    'spanish': 'es', 'sundanese': 'su', 'swahili': 'sw', 'swedish': 'sv', 'tajik': 'tg', 'tamil': 'ta',
    'telugu': 'te', 'thai': 'th', 'turkish': 'tr', 'ukrainian': 'uk', 'urdu': 'ur', 'uyghur': 'ug', 'uzbek': 'uz',
    'vietnamese': 'vi', 'welsh': 'cy', 'xhosa': 'xh', 'yiddish': 'yi', 'yoruba': 'yo', 'zulu': 'zu'
}

# Reverse mapping
CODE_TO_LANGUAGE = {code: lang for lang, code in LANGUAGE_MAPPING.items()}

class Translator:
    """
    Handles language translation between multiple languages.
    Uses Google Translate API for translations.
    """
    def __init__(self, default_language="en", config=None):
        """
        Initialize the translator.
        
        Args:
            default_language: Default language code (e.g., 'en' for English)
            config: Optional configuration dictionary
        """
        self.default_language = default_language
        self.translator = GoogleTranslator()
        
        # Setup logging
        if config and config.get("logging", {}).get("enabled", False):
            self.logger = setup_logging(config["logging"]["level"], 
                                       config["logging"]["file"])
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            
        self.logger.info(f"Translator initialized with default language: {default_language}")
        
    def detect_language(self, text):
        """
        Detect the language of the input text.
        
        Args:
            text: Text to detect language from
            
        Returns:
            str: Detected language code
        """
        try:
            detected = detect(text)
            self.logger.debug(f"Detected language: {detected} for text: {text[:30]}...")
            return detected
        except Exception as e:
            self.logger.error(f"Error detecting language: {e}")
            return self.default_language
            
    def translate(self, text, source_lang=None, target_lang="en"):
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code (auto-detect if None)
            target_lang: Target language code
            
        Returns:
            str: Translated text
        """
        if not text:
            return ""
            
        try:
            # Auto-detect source language if not provided
            if source_lang is None:
                source_lang = self.detect_language(text)
                
            # Skip translation if source and target are the same
            if source_lang == target_lang:
                return text
                
            # Perform translation
            translation = self.translator.translate(
                text,
                src=source_lang,
                dest=target_lang
            )
            
            self.logger.debug(f"Translated from {source_lang} to {target_lang}: {text[:30]}... -> {translation.text[:30]}...")
            
            return translation.text
            
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            return text  # Return original text on error
            
    def translate_to_english(self, text):
        """
        Translate text to English and detect source language.
        
        Args:
            text: Text to translate
            
        Returns:
            tuple: (detected_language, translated_text)
        """
        # Detect language
        detected_lang = self.detect_language(text)
        
        # Skip translation if already English
        if detected_lang == "en":
            return detected_lang, text
            
        # Translate to English
        translated = self.translate(text, source_lang=detected_lang, target_lang="en")
        
        return detected_lang, translated
        
    def translate_from_english(self, text, target_lang):
        """
        Translate text from English to target language.
        
        Args:
            text: English text to translate
            target_lang: Target language code
            
        Returns:
            str: Translated text
        """
        # Skip translation if target is English
        if target_lang == "en":
            return text
            
        # Translate from English
        translated = self.translate(text, source_lang="en", target_lang=target_lang)
        
        return translated
        
    def get_language_code(self, language_name):
        """
        Get language code from language name.
        
        Args:
            language_name: Language name (e.g., 'english')
            
        Returns:
            str: Language code (e.g., 'en')
        """
        return LANGUAGE_MAPPING.get(language_name.lower(), language_name)
        
    def get_language_name(self, language_code):
        """
        Get language name from language code.
        
        Args:
            language_code: Language code (e.g., 'en')
            
        Returns:
            str: Language name (e.g., 'english')
        """
        return CODE_TO_LANGUAGE.get(language_code, language_code)