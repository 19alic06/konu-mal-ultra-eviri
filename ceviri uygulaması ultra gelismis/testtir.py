import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
from openai import OpenAI
from gtts import gTTS
import pygame
import os
import threading
import time

API_KEY = ""
MODEL_ADI = "google/gemini-2.0-flash-001"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

class JarvisCeviri:
    def __init__(self, root):
        self.root = root
        self.root.title("ÇEVİRİ")
        self.root.geometry("450x400")
        self.root.configure(bg="#0a0a0a") 

        pygame.mixer.init()

      
        self.lbl_title = tk.Label(root, text="ÇEVİRİ SİSTEMİ", bg="#0a0a0a", fg="#00ff00", font=("Courier", 14, "bold"))
        self.lbl_title.pack(pady=15)

        self.lbl_info = tk.Label(root, text="Hedef Dil Seçin:", bg="#0a0a0a", fg="white")
        self.lbl_info.pack()

        self.diller = {"İngilizce": "English", "Almanca": "German", "Fransızca": "French", "Rusça": "Russian", "İspanyolca": "Spanish","Japonca":"Japanese","Çince":"Chinese"}
        self.combo = ttk.Combobox(root, values=list(self.diller.keys()), state="readonly")
        self.combo.current(0)
        self.combo.pack(pady=5)

        self.btn = tk.Button(root, text="SİSTEMİ TETİKLE", command=self.baslat, bg="#00ff00", fg="black", font=("Courier", 12, "bold"), height=2)
        self.btn.pack(pady=20, fill="x", padx=50)

        self.status = tk.Label(root, text="Beklemede...", bg="#0a0a0a", fg="#555555")
        self.status.pack()

        self.output = tk.Text(root, height=6, bg="#111111", fg="#00ff00", font=("Consolas", 10), borderwidth=0)
        self.output.pack(pady=10, padx=20)

    def baslat(self):
        
        threading.Thread(target=self.islem_yap, daemon=True).start()

    def islem_yap(self):
        self.btn.config(state="disabled", text="DİNLENİYOR...")
        self.status.config(text="Mikrofon aktif, konuşun...", fg="red")
        
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
               
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5)
                metin = recognizer.recognize_google(audio, language="tr-TR")
                
                hedef_dil = self.diller[self.combo.get()]
                self.status.config(text="Çeviriliyor", fg="#00ff00")

                
                response = client.chat.completions.create(
                    model=MODEL_ADI,
                    messages=[
                        {"role": "system", "content": f"Sen bir çevirmensin. Verilen cümleyi sadece {hedef_dil} diline çevir. Ekstra açıklama yapma."},
                        {"role": "user", "content": metin}
                    ]
                )
                
                cevirilen = response.choices[0].message.content
                
                self.output.delete(1.0, tk.END)
                self.output.insert(tk.END, f"TR: {metin}\n{hedef_dil}: {cevirilen}")

                
                self.seslendir(cevirilen)

            except Exception as e:
                self.output.insert(tk.END, f"\nHata: {str(e)}")
            
            self.status.config(text="Sistem Hazır", fg="#555555")
            self.btn.config(state="normal", text="SİSTEMİ TETİKLE")

    def seslendir(self, metin):
        try:
           
            filename = f"speech_{int(time.time())}.mp3"
            tts = gTTS(text=metin, lang='en') 
            tts.save(filename)
            
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            pygame.mixer.music.unload()
            os.remove(filename)
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisCeviri(root)
    root.mainloop()