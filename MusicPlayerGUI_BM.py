# MusicPlayerGUI_BM.py by Brendan McBride
#
# Currently supports .mod, .mp3, .wav, .ogg, .flac files

import pygame
import tkinter as tk
from tkinter import filedialog, messagebox

# Initialize Pygame mixer
pygame.mixer.init()

# Flag to track if the music is paused
is_paused = False

def load_music_file():
    # Load a music file using a file dialog.
    filepath = filedialog.askopenfilename(filetypes=[("Music files(*.mod *.mp3 *.wav *.ogg *.flac)", "*.mod *.mp3 *.wav *.ogg *.flac")])
    if filepath:
        try:
            pygame.mixer.music.load(filepath)
            messagebox.showinfo("File Loaded", "Music file loaded successfully!")
        except pygame.error as e:
            messagebox.showerror("Error", f"Could not load music file: {e}")

def play_music_file():
    # Play the loaded music file.
    try:
        pygame.mixer.music.play()
    except pygame.error as e:
        messagebox.showerror("Error", f"Could not play music file: {e}")

def stop_music_file():
    # Stop the playback of the music file.
    pygame.mixer.music.stop()

def pause_music_file():
    # Pause or unpause the playback of the music file.
    global is_paused
    if is_paused:
        pygame.mixer.music.unpause()
        pause_button.config(text="Pause")
    else:
        pygame.mixer.music.pause()
        pause_button.config(text="Resume")
    is_paused = not is_paused

def create_gui():
    # Create the GUI using tkinter.
    global pause_button
    
    root = tk.Tk()
    root.title("Music Player")

    load_button = tk.Button(root, text="Load Music File (*.mod *.mp3 *.wav *.ogg *.flac)", command=load_music_file)
    load_button.pack(pady=10)

    play_button = tk.Button(root, text="Play", command=play_music_file)
    play_button.pack(pady=5)

    pause_button = tk.Button(root, text="Pause", command=pause_music_file)
    pause_button.pack(pady=5)

    stop_button = tk.Button(root, text="Stop", command=stop_music_file)
    stop_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
