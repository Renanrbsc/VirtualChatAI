import edge_tts
import asyncio
import os
import time
from playsound import playsound


class TextToSpeechConverter:
    """
    A class to convert text to speech and play the audio.
    """
    
    def __init__(self):
        """
        Initializes the TextToSpeechConverter with the output path.
        """
        self.output_path = os.path.abspath(r"audio\output.mp3")

    def play_audio(self, file_path: str) -> None:
        """
        Plays the audio file at the specified file path.

        Args:
            file_path (str): The path to the audio file to be played.
        """
        playsound(file_path)

    def text_to_speech(self, text: str, voice: str = "en-US-JennyNeural") -> None:
        """
        Converts the given text to speech and plays the audio.

        This function uses the edge_tts library to generate speech from text,
        saves it to a specified output path, and plays the audio file.

        Args:
            text (str): The text to be converted to speech.
            voice (str): The voice to use for the speech synthesis. Defaults to "en-US-JennyNeural".
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tts = edge_tts.Communicate(text, voice)
        loop.run_until_complete(tts.save(self.output_path))

        # Play the audio file using playsound
        self.play_audio(self.output_path)

        # Wait briefly and remove the file after playback
        time.sleep(1)
        os.remove(self.output_path)
