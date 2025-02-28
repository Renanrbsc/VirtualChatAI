import edge_tts
import asyncio
import os
import time
from playsound import playsound
import threading


class TextToSpeechConverter:
    """
    A class to convert text to speech and play the audio.
    """
    
    def __init__(self, input_language: str = "en"):
        """
        Initializes the TextToSpeechConverter with the output path.
        """
        self.output_path = os.path.abspath(r"audio\output.mp3")
        self.define_voice(input_language)

    def define_voice(self, input_language: str) -> None:
        """
        Defines the voice to be used for speech synthesis.

        voice (str): The voice to use for the speech synthesis. 
                         Alternatives for English:  en-US-AvaMultilingualNeural
                                                    en-US-AndrewMultilingualNeural
                                                    en-US-EmmaMultilingualNeural
                                                    en-US-BrianMultilingualNeural
                                I liked her         en-US-AvaNeural
                                                    en-US-AndrewNeural
                                                    en-US-EmmaNeural
                                                    en-US-BrianNeural
                                                    en-US-AnaNeural
                                                    en-US-AriaNeural
                                                    en-US-ChristopherNeural
                                                    en-US-EricNeural
                                                    en-US-GuyNeural
                                                    en-US-JennyNeural
                                                    en-US-MichelleNeural
                                                    en-US-RogerNeural
                                                    en-US-SteffanNeural
                         Alternatives for Portuguese: pt-BR-ThalitaMultilingualNeural
                                                      pt-BR-AntonioNeural
                                I liked her           pt-BR-FranciscaNeural
        """
        if input_language == "en":
            self.voice = "en-US-AvaNeural"
        elif input_language == "pt":
            self.voice = "pt-BR-FranciscaNeural"
        else:
            self.voice = "en-US-AvaMultilingualNeural"

    def play_audio(self, file_path: str) -> None:
        """
        Plays the audio file at the specified file path.

        Args:
            file_path (str): The path to the audio file to be played.
        """
        playsound(file_path)

    def text_to_speech(self, text: str) -> None:
        """
        Converts text to speech asynchronously
        """
        def convert_and_play():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tts = edge_tts.Communicate(text, self.voice)
            loop.run_until_complete(tts.save(self.output_path))

            # Play the audio file using playsound
            self.play_audio(self.output_path)

            # Wait briefly and remove the file after playback
            time.sleep(1)
            os.remove(self.output_path)

        # Run conversion and playback in a separate thread
        threading.Thread(target=convert_and_play, daemon=True).start()
