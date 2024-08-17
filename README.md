# TTS_STT
Text to Speech and Speech to  Text

這是一個簡單的 Python 應用程式，可以接受拖放的文字檔和音檔，並根據檔案類型進行相應的處理。該應用程式具備以下功能：

1. 以應用程式的姿態出現在作業系統，並且有一個圖示，接受使用者將檔案拖進去處理。
2. 當文字檔拖進去的時候，自動進行 TTS（文字轉語音），使用的是 `pyttsx4` 程式庫（預設使用系統的語音合成器），輸出 `.wav` 檔。
3. 當音檔（`.wav` 或 `.mp3`）拖進去的時候，自動進行語音辨識，使用的是 `whisper` API base 模型，輸出帶時間標籤的 `.txt` 檔。
4. 當影片檔(mp4)拖進去的時候，自動分離出wav音檔，然後接著音檔處理程序。

## 安裝步驟

首先，你需要安裝一些必要的 Python 程式庫。你可以使用以下命令來安裝：

```bash
pip install pydub pyttsx4 whisper tkinterdnd2
```

## 使用方法
```
python TTSnWhisper.py
```

## 程式碼說明
程式碼很短，她自我說明了  


![image](https://github.com/user-attachments/assets/10c19430-8fe8-42ce-a3be-e5de4554091c)
