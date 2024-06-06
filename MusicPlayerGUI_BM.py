#############################################################################
# Filename    : Music_Player.py
# Description : A simple music player to load, play, pause, stop, and display metadata for various music files
# Author      : Brendan McBride
# Date        : 2024/06/06
########################################################################
import pygame
import tkinter as tk
from tkinter import filedialog, messagebox
from mutagen import File

# Initialize Pygame mixer
pygame.mixer.init()

# Flag to track if the music is paused
is_paused = False

def load_music_file():
    # Load a music file using a file dialog.
    filepath = filedialog.askopenfilename(filetypes=[("Music files(*.mod *.mp3 *.wav *.ogg *.flac *.s3m *.umx *.it *.xm)", "*.mod *.mp3 *.wav *.ogg *.flac *.s3m *.umx *.it *.xm"), ("All files", "*.*")])
    if filepath:
        try:
            pygame.mixer.music.load(filepath)
            current_file = filepath
            display_metadata(filepath)
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

def display_metadata(filepath):
    # Displays the metadata of the file
    try:
        audio = File(filepath)
        metadata = {
            "Title": audio.get("TIT2", "Unknown Title"),
            "Artist": audio.get("TPE1", "Unknown Artist"),
            "Album": audio.get("TALB", "Unknown Album"),
            "Year": audio.get("TDRC", "Unknown Year"),
            "Genre": audio.get("TCON", "Unknown Genre")
        }
        filename_label.config(text=f"File: {filepath.split('/')[-1]}")
        metadata_label.config(text="\n".join(f"{key}: {value}" for key, value in metadata.items()))
    except Exception as e:
        filename_label.config(text="File: Unknown")
        metadata_label.config(text=f"Could not retrieve metadata: {e}")
        
def create_gui():
    # Create the GUI using tkinter.
    global pause_button, filename_label, metadata_label
    
    root = tk.Tk()
    root.title("Music Player")

    load_button = tk.Button(root, text="Load Music File (*.mod *.mp3 *.wav *.ogg *.flac *.s3m *.umx *.it *.xm)", command=load_music_file)
    load_button.pack(pady=10)

    play_button = tk.Button(root, text="Play", command=play_music_file)
    play_button.pack(pady=5)

    pause_button = tk.Button(root, text="Pause", command=pause_music_file)
    pause_button.pack(pady=5)

    stop_button = tk.Button(root, text="Stop", command=stop_music_file)
    stop_button.pack(pady=5)

    filename_label = tk.Label(root, text="File: None")
    filename_label.pack(pady=5)

    metadata_label = tk.Label(root, text="Metadata: None")
    metadata_label.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
