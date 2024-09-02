import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from pydub import AudioSegment
import pyttsx4
# note: pip install openai-whisper
# import whisper

from faster_whisper import WhisperModel
model_size = "large-v3"

from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import time
import random
import string
from moviepy.editor import VideoFileClip

os.environ['KMP_DUPLICATE_LIB_OK']='True'
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

    def replace_extension_and_avoid_duplicate(self, full_path, new_extension):
        """
        替換檔案的副檔名，並避免目的地已經有同名檔案存在。

        參數:
        full_path (str): 包含檔案名稱的全路徑字串。
        new_extension (str): 新的副檔名（包括點號，例如 '.new'）。

        回傳:
        str: 新的檔案全路徑。
        """
        # 提取檔案名稱和副檔名
        file_name_with_extension = os.path.basename(full_path)
        file_name, _ = os.path.splitext(file_name_with_extension)

        # 構建新的檔案名稱
        new_file_name = file_name + new_extension
        new_full_path = os.path.join(os.path.dirname(full_path), new_file_name)

        # 檢查目的地是否已經存在同名檔案
        counter = 1
        while os.path.exists(new_full_path):
            new_file_name = f"{file_name}_{counter}{new_extension}"
            new_full_path = os.path.join(os.path.dirname(full_path), new_file_name)
            counter += 1

        return new_full_path

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
        output_file_path = self.replace_extension_and_avoid_duplicate(file_path, ".wav")
        video.audio.write_audiofile(output_file_path, codec='pcm_s16le')
        video.close()
        self.process_audio_file(output_file_path)
        
    def text_to_speech(self, file_path):
        self.progress["value"] = 0
        self.progress["maximum"] = 100
        self.root.update_idletasks()

        with open(file_path, 'r') as file:
            text = file.read()

        engine = pyttsx4.init()
        output_file_path = self.replace_extension_and_avoid_duplicate(file_path, ".wav")
        engine.save_to_file(text, output_file_path)

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
#             file_path = file_path.replace('.mp3', '.wav')
            file_path = self.replace_extension_and_avoid_duplicate(file_path, ".wav")
            audio.export(file_path, format="wav")

        audio = AudioSegment.from_wav(file_path)
        total_duration = len(audio) / 1000  # 總時長（秒）

#         model = whisper.load_model("medium")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        # 啟動進度條更新線程
        progress_thread = threading.Thread(target=self.update_progress, args=(total_duration * self.stt_time_per_second,))
        progress_thread.start()

        result, info = model.transcribe(file_path, beam_size=5)
        print(result, info)
        # 提早結束進度條更新線程
        self.progress["value"] = 100
        self.root.update_idletasks()
        
        output_file_path = self.replace_extension_and_avoid_duplicate(file_path, ".srt")
        output_file_path_txt = self.replace_extension_and_avoid_duplicate(file_path, ".txt")
        with open(output_file_path, "w", encoding='UTF-8') as file, open(output_file_path_txt, "w", encoding='UTF-8') as file2:
#             print(result['segments'])
#             for i, segment in enumerate(result['segments']):
#                 start_time = self.format_time(segment['start'])
#                 end_time = self.format_time(segment['end'])
#                 file.write(f"{i+1}\n")
#                 file.write(f"{start_time} --> {end_time}\n")
#                 file.write(f"{segment['text']}\n\n")
            for i, segment in enumerate(result):
                start_time = self.format_time(segment.start)
                end_time = self.format_time(segment.end)
                print(f"{i+1}")
                print(f"{start_time} --> {end_time}")
                print(f"{segment.text}\n")
                                
                file.write(f"{i+1}\n")
                file.write(f"{start_time} --> {end_time}\n")
                file.write(f"{segment.text}\n\n")
                file2.write(f"{segment.text}\n")
                

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
#         model = whisper.load_model("medium")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        start_time = time.time()
        result, info = model.transcribe("benchmark.wav", beam_size=5)
        stt_time = time.time() - start_time
        audio = AudioSegment.from_wav("benchmark.wav")
        total_duration = len(audio) / 1000  # 總時長（秒）
        stt_time_per_second = stt_time / total_duration / 2

        return tts_time_per_char, stt_time_per_second

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FileProcessorApp(root)
    root.mainloop()
