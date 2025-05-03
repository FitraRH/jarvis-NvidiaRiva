# Multilingual Voice Chatbot

A Jarvis-like conversational assistant built with Python, DialoGPT, and NVIDIA Riva support. This chatbot can understand voice commands in multiple languages, convert speech to text, conduct natural conversations using Microsoft's DialoGPT, and respond with voice output.

## Features

- **Voice Interaction**: Speak to the chatbot using your microphone and hear responses through your speakers
- **Wake Word Detection**: Activate the chatbot by saying "Jarvis" (customizable)
- **Natural Conversation**: Uses Microsoft's DialoGPT model for human-like responses
- **Multilingual Support**: Process input and generate output in over 100 languages
- **Custom Commands**: Built-in commands for time, date, weather, and more
- **Extensible Architecture**: Easily add your own custom commands and features
- **NVIDIA Riva Integration**: Optional high-quality speech synthesis

## Requirements

### Hardware
- Microphone (for voice input)
- Speakers/headphones (for voice output)
- NVIDIA GPU (optional, for Riva integration)

### Software
- Python 3.8+
- PyTorch
- Transformers library
- SpeechRecognition
- pyttsx3
- googletrans
- PyAudio
- NVIDIA Riva SDK (optional)

## Quick Start

1. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download the DialoGPT model**:
   ```bash
   python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-large'); model = AutoModelForCausalLM.from_pretrained('microsoft/DialoGPT-large')"
   ```

3. **Run the example**:
   ```bash
   python examples/example_usage.py
   ```

4. **Say "Jarvis" to activate** and speak your question or command.

## Project Structure

```
multilingual-voice-chatbot/
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── src/                    # Source code
│   ├── __init__.py
│   ├── chatbot.py          # Main chatbot implementation
│   ├── speech_to_text.py   # Voice input processing
│   ├── text_to_speech.py   # Voice output generation
│   ├── translation.py      # Language translation
│   ├── command_handler.py  # Command processing
│   └── utils.py            # Utility functions
├── config/
│   └── config.json         # Configuration settings
├── examples/
│   └── example_usage.py    # Example implementation
└── logs/                   # Log files (created at runtime)
```

## Configuration

Customize the chatbot by editing `config/config.json`. Key settings include:

- **Wake Word**: Change the activation phrase (default: "jarvis")
- **Model**: Configure DialoGPT model options
- **Speech**: Adjust microphone and speaker settings
- **Language**: Set default language and translation options
- **Commands**: Define custom command patterns
- **Logging**: Configure log level and output location

## Using NVIDIA Riva (Optional)

For higher quality speech synthesis:

1. Install NVIDIA Riva SDK following instructions at [developer.nvidia.com/riva](https://developer.nvidia.com/riva)
2. Update the config.json file to enable Riva:
   ```json
   "riva": {
     "enabled": true,
     "server_url": "localhost:50051",
     "auth_key": ""
   }
   ```

## Advanced Usage

### Custom Commands

Add your own commands by extending the CommandHandler class:

```python
def handle_custom_command(self, command):
    # Your command processing logic here
    return "Command response"

command_handler.add_custom_command_handler("custom_type", handle_custom_command)
```

### Different DialoGPT Models

Choose between different model sizes based on your needs:
- **DialoGPT-small**: Faster but less capable
- **DialoGPT-medium**: Balanced performance
- **DialoGPT-large**: Best quality but slower

Update the model in config.json:
```json
"model": {
  "name": "microsoft/DialoGPT-medium",
  ...
}
```

## Language Support

The chatbot supports over 100 languages including:

- English, Spanish, French, German, Italian, Portuguese
- Chinese (Simplified and Traditional), Japanese, Korean
- Russian, Arabic, Hindi, and many more

See the complete list in `src/translation.py`.

## Troubleshooting

- **Microphone not working**: Check your system's default input device
- **Speech recognition errors**: Try speaking more clearly or adjusting microphone sensitivity
- **Model loading errors**: Ensure you have enough disk space and memory
- **NVIDIA Riva issues**: Check CUDA configuration and GPU compatibility

## References

- [DialoGPT GitHub Repository](https://github.com/microsoft/DialoGPT)
- [DialoGPT on Hugging Face](https://huggingface.co/microsoft/DialoGPT-large)
- [Neural Networks from Scratch](https://nnfs.io/)
- [NVIDIA Riva](https://developer.nvidia.com/riva)
