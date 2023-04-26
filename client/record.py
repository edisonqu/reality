import os
import queue
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
        phrase_time_limit: "int | None" = None,
        energy_threshold: int = 1500,
    ) -> None:

        self.output_dir = output_dir
        # self.output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), output_dir)

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
            try:
                audio = self.audio_queue.get(timeout=1)

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
            except queue.Empty:
                continue

    def record_callback(self, _, audio: sr.AudioData) -> None:

        now = datetime.utcnow()
        num_samples = len(audio.get_wav_data()) // audio.sample_width
        duration = num_samples / float(audio.sample_rate)

        adj_time = now - timedelta(seconds=duration)
        if self.new_group(adj_time):
            self.audio_queue.put(None)

        self.audio_queue.put(audio)
        self.last_recorded_audio = now

    def new_group(self, now: datetime) -> bool:

        if self.last_recorded_audio is None:
            return True

        elapsed = now - self.last_recorded_audio

        if elapsed >= timedelta(seconds=self.group_silence_duration):
            return True

        return False

    def stop(self) -> None:

        self.stop_processing = True
        self.background_listener(wait_for_stop=True)
        self.processing_thread.join()


if __name__ == "__main__":

    recorder = Recorder(".note_files")
    try:
        recorder.start()
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        recorder.stop()