import os
from queue import Queue
import threading

import speech_recognition as sr

from datetime import datetime, timedelta
from time import sleep


class Recorder:
    def __init__(
        self,
        output_dir: str,
        sample_rate: int = 16000,
        group_silence_duration: float = 10.0,
        phrase_time_limit: float | None = None,
        energy_threshold: int = 1000,
    ) -> None:

        self.output_dir = output_dir

        os.makedirs(output_dir, exist_ok=True)

        self.phrase_time_limit = phrase_time_limit
        self.group_id = None
        self.item_id = 0
        self.group_silence_duration = group_silence_duration
        self.last_recorded_audio = None
        self.recognizer = self.setup_recognizer(
            energy_threshold=energy_threshold)
        self.microphone = sr.Microphone(sample_rate=sample_rate)
        self.audio_queue = Queue()
        self.processing_queue = Queue()
        self.processing_thread = threading.Thread(
            target=self.process_audio, daemon=True)
        self.stop_processing = False

    def setup_recognizer(self, energy_threshold: int) -> sr.Recognizer:

        recorder = sr.Recognizer()
        recorder.energy_threshold = energy_threshold
        recorder.dynamic_energy_threshold = False

        return recorder

    def start(self) -> None:
        self.background_listener = self.recognizer.listen_in_background(
            self.microphone, self.record_callback, phrase_time_limit=self.phrase_time_limit)
        self.processing_thread.start()

    def process_audio(self) -> None:
        while not self.stop_processing:
            audio = self.audio_queue.get()

            if audio is None:
                self.group_id = None
                self.item_id = 0
            else:
                self.processing_queue.put(audio)

            while not self.processing_queue.empty():
                if self.group_id is None:
                    self.group_id = datetime.utcnow()

                audio = self.processing_queue.get()
                item_id = str(self.item_id)
                file_name = f"{self.group_id}_{item_id}.mp3"
                file_path = os.path.join(self.output_dir, file_name)
                with open(file_path, "wb") as f:
                    f.write(audio.get_wav_data())
                self.item_id += 1
            sleep(0.1)

    def record_callback(self, _, audio: sr.AudioData) -> None:

        now = datetime.utcnow()
        if self.new_group(now):
            self.audio_queue.put(None)

        self.audio_queue.put(audio)
        self.last_recorded_audio = now

    def new_group(self, now: datetime) -> bool:

        if self.last_recorded_audio is None:
            return True

        if now - self.last_recorded_audio >= timedelta(seconds=self.group_silence_duration):
            return True

        return False

    def stop(self) -> None:

        self.stop_processing = True
        self.background_listener(wait_for_stop=False)
        self.processing_thread.join()


if __name__ == "__main__":

    recorder = Recorder(".note_files")
    try:
        recorder.start()
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        recorder.stop()
