import time
import os
import pyaudio # Handles audio input/output.
from vosk import Model, KaldiRecognizer # speech recognition framework
import pyttsx3  # Converts text to speech
import ollama

# Load Vosk model for offline speech recognition
def load_vosk_model():
    model_path = "models/vosk-model-small-en-us"
    if not os.path.exists(model_path):
        raise FileNotFoundError("Vosk model not found! Download and place it in the 'models' directory.")
    return Model(model_path)

# Listen to microphone input and transcribe using Vosk
def listen_and_transcribe(model):
    rec = KaldiRecognizer(model, 16000)  # Vosk model and a sample rate of 16000 Hz
    audio = pyaudio.PyAudio() # Initializes the PyAudio instance for handling audio input/output.
    stream = audio.open(
        format=pyaudio.paInt16, # Opens an audio input stream
        channels=1, # Indicates mono audio (single channel).
        rate=16000, #The sample rate
        input=True, #Specifies that this stream is for audio input.
        frames_per_buffer=8192 # Sets the size of the buffer that holds audio data before being processed.
        )
    stream.start_stream()  # Begins the audio stream 

    print("Listening... Speak now.")
    engine = pyttsx3.init()
    engine.say("What is your prompt?")
    engine.runAndWait()
    time.sleep(0.7)
    while True:
        data = stream.read(4096) # Reads 4096 bytes of audio data (half of the buffer size)
        if rec.AcceptWaveform(data):   #Processes the audio chunk Returns True if the audio chunk is sufficient
            result = rec.Result()  #Retrieves the transcription result as a JSON string.
            text = eval(result).get('text', '')  # Converts the JSON string into a Python dictionary
            if text:
                return text

# Send the transcribed text to Ollama and get a response
def query_ollama(input_text):
    first = ollama.generate(model='tinyllama', prompt=input_text)  # Stream the response, Enables streaming the response incrementally instead of loading it all at once.
    result = first['response'] # Raises an exception
    with open("output.txt", "w") as file:
        file.write(result)



# Main function to integrate all components
def main():
    try:
        # Load Vosk model
        model = load_vosk_model()

        while True:
            # Listen to user input
            user_input = listen_and_transcribe(model)
            print(f"You said: {user_input}")

            # Query Ollama API
            saythis = query_ollama(user_input)
            

            # Speak Ollama's response
            
            engine = pyttsx3.init()
            with open("output.txt", "r") as file:
                text = file.read()
            engine.say(text)
            engine.runAndWait()
            time.sleep(63)
            engine.say("Speak now")
            engine.runAndWait()
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nExiting. Goodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
