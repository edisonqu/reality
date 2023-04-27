import io
import os
import queue
from queue import Queue
import threading
import whisper

import speech_recognition as sr

from datetime import datetime, timedelta
from time import sleep


class Recorder:
    def __init__(
        self,
        output_dir: str,
        whisper_model_path: str,
        sample_rate: int = 16000,
        group_silence_duration: float = 10.0,
        phrase_time_limit: "int | None" = 30,
        batch_length: float = 120.0,
        energy_threshold: int = 1000,
    ) -> None:

        self.output_dir = output_dir

        os.makedirs(output_dir, exist_ok=True)

        self.phrase_time_limit = phrase_time_limit
        self.group_id = None
        self.item_id = 0
        self.group_silence_duration = group_silence_duration
        self.last_recorded_audio = None
        self.batch_length = batch_length
        self.microphone = sr.Microphone(sample_rate=sample_rate)
        self.recognizer = self.setup_recognizer(
            energy_threshold=energy_threshold)
        self.audio_queue = Queue()
        self.processing_queue = Queue()
        self.processing_thread = threading.Thread(
            target=self.process_audio, daemon=True)
        self.stop_processing = False

        self.whisper = whisper.load_model(whisper_model_path)
        self.current_batch = bytes()
        self.current_batch_duration = 0.0

    def setup_recognizer(self, energy_threshold: int) -> sr.Recognizer:

        recorder = sr.Recognizer()
        recorder.energy_threshold = energy_threshold
        recorder.dynamic_energy_threshold = False
        with self.microphone:
            recorder.adjust_for_ambient_noise(self.microphone)

        return recorder

    def start(self) -> None:
        self.background_listener = self.recognizer.listen_in_background(
            self.microphone, self.record_callback, phrase_time_limit=self.phrase_time_limit)
        self.processing_thread.start()

    def process_current_batch(self):
        file_name = f"{self.group_id}_{self.item_id}.mp3"
        file_path = os.path.join(self.output_dir, file_name)
        audio_data = sr.AudioData(
            self.current_batch, self.microphone.SAMPLE_RATE, self.microphone.SAMPLE_WIDTH)
        wav_data = io.BytesIO(audio_data.get_wav_data())
        with open(file_path, "wb") as f:
            f.write(wav_data.read())

        print(self.whisper.transcribe(file_path))

    def process_audio(self) -> None:
        while not self.stop_processing:
            try:
                audio = self.audio_queue.get(timeout=1)

                if self.group_id is None:
                    self.group_id = datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")

                if audio == "NEW_GROUP":

                    self.process_current_batch()
                    self.group_id = None
                    self.item_id = 0
                    self.current_batch = bytes()
                elif audio == "NEW_ITEM":

                    self.process_current_batch()
                    self.item_id += 1
                    self.current_batch = bytes()
                else:

                    self.processing_queue.put(audio)

                while not self.processing_queue.empty():

                    audio = self.processing_queue.get()
                    self.current_batch += audio.get_raw_data()
                    print(len(self.current_batch))

                sleep(0.1)
            except queue.Empty:
                continue

    def record_callback(self, _, audio: sr.AudioData) -> None:

        if self.group_id is None:
            self.group_id = datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")

        now = datetime.utcnow()
        num_samples = len(audio.get_wav_data()) // audio.sample_width
        duration = num_samples / float(audio.sample_rate)

        adj_time = now - timedelta(seconds=duration)
        if self.new_group(adj_time):
            self.audio_queue.put("NEW_GROUP")
        elif self.current_batch_duration + duration >= self.batch_length:
            self.audio_queue.put("NEW_ITEM")
            self.current_batch_duration = duration
        else:
            self.current_batch_duration += duration

        self.audio_queue.put(audio)
        self.last_recorded_audio = now

    def new_group(self, now: datetime) -> bool:

        if self.last_recorded_audio is None:
            return False

        elapsed = now - self.last_recorded_audio

        if elapsed >= timedelta(seconds=self.group_silence_duration):
            return True

        return False

    def stop(self) -> None:

        self.stop_processing = True
        self.background_listener(wait_for_stop=False)
        self.processing_thread.join()

        while not self.processing_queue.empty():
            audio = self.processing_queue.get()
            self.current_batch += audio.get_raw_data()
        self.process_current_batch()


if __name__ == "__main__":

    recorder = Recorder(".note_files", "./models/base.en.pt")
    try:
        recorder.start()
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        recorder.stop()
