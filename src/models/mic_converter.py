import os
import wave
import json
import pyaudio
import keyboard
from vosk import Model, KaldiRecognizer, SetLogLevel
SetLogLevel(-1)


class MicConverter:
    """
    A class to handle audio recording from the microphone and
    transcription using the Vosk model.
    """
    def __init__(self, input_language: str = "en"):
        """
        Initialize the MicConverter.
        """
        self.output_filename = os.path.abspath(r"audio\input.wav")
        self.define_model(input_language)

    def define_model(self, input_language: str):
        """
        Define the Vosk model to be used for transcription.
        """
        
        model_path = os.path.abspath(r"audio_models")
        if input_language == "en":
            self.model_path = os.path.join(model_path, "vosk-model-small-en-us-0.15")
        elif input_language == "pt":
            self.model_path = os.path.join(model_path, "vosk-model-small-pt-0.3")
        else:
            print("Error: Invalid input language!")
            return ""
        
        if not os.path.exists(self.model_path):
            print("Error: Vosk model not found!")
            return ""
            
        self.model = Model(self.model_path)


    def record_audio(self) -> str:
        """
        Records audio from the user's microphone until the RIGHT_SHIFT key is released,
        saves it as a WAV file, and transcribes the audio using the Vosk model.

        Returns:
            str: The transcription as produced by the Vosk model.
        """
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        audio_interface = pyaudio.PyAudio()
        audio_stream = audio_interface.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        frames = []
        print("Recording...")
        recording = True
        while recording:
            if keyboard.is_pressed("SPACE"):
                frame = audio_stream.read(CHUNK)
                frames.append(frame)

            # Check if the key is released
            if not keyboard.is_pressed("SPACE"):
                recording = False

        print("Stopped recording.")

        audio_stream.stop_stream()
        audio_stream.close()
        audio_interface.terminate()

        with wave.open(self.output_filename, "wb") as wave_file:
            wave_file.setnchannels(CHANNELS)
            wave_file.setsampwidth(audio_interface.get_sample_size(FORMAT))
            wave_file.setframerate(RATE)
            wave_file.writeframes(b"".join(frames))

        transcription = self.transcribe_audio(self.output_filename)
        return transcription
    
    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribes the audio from the given WAV file using the Vosk model.

        The function checks that the specified model exists and that the audio file
        is a mono WAV in PCM format.

        Args:
            audio_path (str): Path to the WAV audio file to transcribe.

        Returns:
            str: The complete transcription as a single string.
                Returns an empty string if an error occurs.
        """
        transcription_fragments = []
        try:
            with wave.open(audio_path, "rb") as wf:
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                    print("Error: The audio file must be a mono WAV in PCM format.")
                    return ""

                recognizer = KaldiRecognizer(self.model, wf.getframerate())
                data = wf.readframes(4000)
                while data:
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        transcription_fragments.append(result.get("text", ""))
                    data = wf.readframes(4000)
                final_result = json.loads(recognizer.FinalResult())
                transcription_fragments.append(final_result.get("text", ""))
        except Exception as error:
            print("Error during transcription:", error)
            return ""

        transcription = " ".join(
            fragment for fragment in transcription_fragments if fragment
        ).strip()
        return transcription