import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from pydub import AudioSegment
import pyttsx4
# note: pip install openai-whisper
import whisper
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import time
import random
import string
from moviepy.editor import VideoFileClip

class FileProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Processor")
        self.root.geometry("400x200")

        self.label = tk.Label(root, text="Drag and drop a file here")
        self.label.pack(pady=20)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=20)

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

        # 進行系統 benchmark
        self.tts_time_per_char, self.stt_time_per_second = self.benchmark_system()

    def on_drop(self, event):
        file_path = event.data
        if os.path.isfile(file_path):
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension == '.txt':
                self.process_text_file(file_path)
            elif file_extension in ['.wav', '.mp3']:
                self.process_audio_file(file_path)
            elif file_extension in ['.mp4']:
                self.process_video_file_audio_extration(file_path)
            else:
                messagebox.showinfo("File Type", f"Unsupported file type: {file_extension}")
        else:
            messagebox.showinfo("File Type", "Not a valid file")

    def process_text_file(self, file_path):
        messagebox.showinfo("File Type", "Text file detected")
        # 在這裡添加 TTS 處理邏輯
        threading.Thread(target=self.text_to_speech, args=(file_path,)).start()

    def process_audio_file(self, file_path):
        messagebox.showinfo("File Type", "Audio file detected")
        # 在這裡添加語音辨識邏輯
        threading.Thread(target=self.speech_to_text, args=(file_path,)).start()

    def process_video_file_audio_extration(self, file_path):
        video = VideoFileClip(file_path)
        video.audio.write_audiofile("temp.wav", codec='pcm_s16le')
        video.close()
        self.process_audio_file("temp.wav")
        
    def text_to_speech(self, file_path):
        self.progress["value"] = 0
        self.progress["maximum"] = 100
        self.root.update_idletasks()

        with open(file_path, 'r') as file:
            text = file.read()

        engine = pyttsx4.init()
        engine.save_to_file(text, "output.wav")

        # 啟動進度條更新線程
        progress_thread = threading.Thread(target=self.update_progress, args=(len(text) * self.tts_time_per_char,))
        progress_thread.start()

        engine.runAndWait()

        # 提早結束進度條更新線程
        self.progress["value"] = 100
        self.root.update_idletasks()

        messagebox.showinfo("TTS", "Text-to-Speech completed. Output saved as output.wav")
        self.progress["value"] = 0
        self.root.update_idletasks()

    def speech_to_text(self, file_path):
        self.progress["value"] = 0
        self.progress["maximum"] = 100
        self.root.update_idletasks()

        if file_path.endswith('.mp3'):
            audio = AudioSegment.from_mp3(file_path)
            file_path = file_path.replace('.mp3', '.wav')
            audio.export(file_path, format="wav")

        audio = AudioSegment.from_wav(file_path)
        total_duration = len(audio) / 1000  # 總時長（秒）

        model = whisper.load_model("medium")

        # 啟動進度條更新線程
        progress_thread = threading.Thread(target=self.update_progress, args=(total_duration * self.stt_time_per_second,))
        progress_thread.start()

        result = model.transcribe(file_path)
#         print(result)
        # 提早結束進度條更新線程
        self.progress["value"] = 100
        self.root.update_idletasks()

        with open("output.srt", "w", encoding='UTF-8') as file:
            for i, segment in enumerate(result['segments']):
                start_time = self.format_time(segment['start'])
                end_time = self.format_time(segment['end'])
                file.write(f"{i+1}\n")
                file.write(f"{start_time} --> {end_time}\n")
                file.write(f"{segment['text']}\n\n")

        messagebox.showinfo("Speech-to-Text", "Speech-to-Text completed. Output saved as output.srt")
        self.progress["value"] = 0
        self.root.update_idletasks()

    def update_progress(self, total_time):
        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time
            progress = (elapsed_time / total_time) * 100
            self.progress["value"] = progress
            self.root.update_idletasks()
            if progress >= 100:
                break
            time.sleep(0.1)  # 更新間隔

    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    def benchmark_system(self):
        # 生成隨機文字
        random_text = '白日依山盡，黃河入海流，欲窮千里目，更上一層樓'

        # TTS benchmark
        engine = pyttsx4.init()
        start_time = time.time()
        engine.save_to_file(random_text, "benchmark.wav")
        engine.runAndWait()
        tts_time = time.time() - start_time
        tts_time_per_char = tts_time / len(random_text)

        # 語音辨識 benchmark
        model = whisper.load_model("medium")
        start_time = time.time()
        result = model.transcribe("benchmark.wav")
        stt_time = time.time() - start_time
        audio = AudioSegment.from_wav("benchmark.wav")
        total_duration = len(audio) / 1000  # 總時長（秒）
        stt_time_per_second = stt_time / total_duration / 4

        return tts_time_per_char, stt_time_per_second

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FileProcessorApp(root)
    root.mainloop()
