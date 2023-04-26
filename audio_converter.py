import whisper

model = whisper.load_model("./models/large-v2.pt")
result = model.transcribe("./.note_files/2023_04_26_01_32_02.mp3")

print(result)
