import pprint
import whisper

from datetime import datetime

import moviepy.editor as mp

from speechbrain.pretrained import SpeakerRecognition

pp = pprint.PrettyPrinter(indent=4)

model = whisper.load_model("./models/large-v2.pt")

start = datetime.now()
result = model.transcribe("./.note_files/2023_04_26_15_27_06_4.mp3")
print("whisper transcription", result["text"])
print("whisper transcription run_time: ", datetime.now() - start)

sound = mp.AudioFileClip("./.note_files/2023_04_26_15_27_06_4.mp3")

verification = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb", savedir="./models/spkrec-ecapa-voxceleb")

for segment in result["segments"]:

    start = segment["start"]
    end = segment["end"]

    extract = sound.subclip(start, end)
    extract.write_audiofile("./.note_files/temp.mp3")
    score, prediction = verification.verify_files(
        "./.note_files/reference.mp3", "./.note_files/temp.mp3")
    print(score, prediction, segment["text"])
