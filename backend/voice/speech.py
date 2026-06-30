import speech_recognition as sr
from core.logger import log_info, log_error
from utils.helpers import normalize_text


class SpeechRecognizer:

    def __init__(self, mic_index=None):
        self.recognizer = sr.Recognizer()
        self.mic_index = mic_index

    def listen(self, timeout=5, phrase_time_limit=6):
        try:
            with sr.Microphone(device_index=self.mic_index) as source:
                log_info("🎤 Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            return audio
        except sr.WaitTimeoutError:
            log_error("Timeout: no speech detected")
            return None
        except Exception as e:
            log_error(f"Mic error: {e}")
            return None

    def to_text(self, audio) -> str | None:
        try:
            text = self.recognizer.recognize_google(audio)
            text = normalize_text(text)
            log_info(f"🗣️ Heard: {text}")
            return text
        except sr.UnknownValueError:
            log_error("Could not understand audio")
            return None
        except sr.RequestError:
            log_error("Speech API error (internet?)")
            return None
        except Exception as e:
            log_error(f"Recognition error: {e}")
            return None

    def listen_and_recognize(self) -> str | None:
        audio = self.listen()
        if not audio:
            return None
        return self.to_text(audio)