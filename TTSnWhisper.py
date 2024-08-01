import tkinter as tk
from tkinter import filedialog, messagebox
import os
from pydub import AudioSegment
import pyttsx4
import whisper
from tkinterdnd2 import DND_FILES, TkinterDnD

class FileProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Processor")
        self.root.geometry("400x200")

        self.label = tk.Label(root, text="Drag and drop a file here")
        self.label.pack(pady=20)

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

    def on_drop(self, event):
        file_path = event.data
        if os.path.isfile(file_path):
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension == '.txt':
                self.process_text_file(file_path)
            elif file_extension in ['.wav', '.mp3']:
                self.process_audio_file(file_path)
            else:
                messagebox.showinfo("File Type", f"Unsupported file type: {file_extension}")
        else:
            messagebox.showinfo("File Type", "Not a valid file")

    def process_text_file(self, file_path):
        messagebox.showinfo("File Type", "Text file detected")
        # 在這裡添加 TTS 處理邏輯
        self.text_to_speech(file_path)

    def process_audio_file(self, file_path):
        messagebox.showinfo("File Type", "Audio file detected")
        # 在這裡添加語音辨識邏輯
        self.speech_to_text(file_path)

    def text_to_speech(self, file_path):
        with open(file_path, 'r') as file:
            text = file.read()
        engine = pyttsx4.init()
        engine.save_to_file(text, "output.wav")
        engine.runAndWait()
        messagebox.showinfo("TTS", "Text-to-Speech completed. Output saved as output.wav")

    def speech_to_text(self, file_path):
        if file_path.endswith('.mp3'):
            audio = AudioSegment.from_mp3(file_path)
            file_path = file_path.replace('.mp3', '.wav')
            audio.export(file_path, format="wav")

        model = whisper.load_model("base")
        result = model.transcribe(file_path)
        with open("output.txt", "w") as file:
            for segment in result['segments']:
                file.write(f"{segment['start']} - {segment['end']}: {segment['text']}\n")
        messagebox.showinfo("Speech-to-Text", "Speech-to-Text completed. Output saved as output.txt")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FileProcessorApp(root)
    root.mainloop()
