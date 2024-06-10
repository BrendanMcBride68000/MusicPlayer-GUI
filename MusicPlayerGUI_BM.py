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
current_file = None
total_length = 0

def load_music_file():
    global current_file, total_length
    # Load a music file using a file dialog.
    filepath = filedialog.askopenfilename(filetypes=[("Music files(*.mod *.mp3 *.wav *.ogg *.flac *.s3m *.umx *.it *.xm)", "*.mod *.mp3 *.wav *.ogg *.flac *.s3m *.umx *.it *.xm"), ("All files", "*.*")])
    if filepath:
        try:
            pygame.mixer.music.load(filepath)
            current_file = filepath
            display_metadata(filepath)
            total_length = get_music_length(filepath)
            #messagebox.showinfo("File Loaded", "Music file loaded successfully!")
        except pygame.error as e:
            messagebox.showerror("Error", f"Could not load music file: {e}")

def play_music_file():
    global is_paused
    # Play the loaded music file.
    try:
        pygame.mixer.music.play()
        is_paused = False
        update_time_remaining()
    except pygame.error as e:
        messagebox.showerror("Error", f"Could not play music file: {e}")

def stop_music_file():
    global is_paused
    # Stop the playback of the music file.
    pygame.mixer.music.stop()
    is_paused = False
    time_remaining_label.config(text="Time Remaining: 00:00")

def pause_music_file():
    global is_paused
    # Pause or unpause the playback of the music file.
    global is_paused
    if is_paused:
        pygame.mixer.music.unpause()
        pause_button.config(text="Pause")
        is_paused = False
        update_time_remaining()
    else:
        pygame.mixer.music.pause()
        pause_button.config(text="Resume")
        is_paused = True

def set_volume(val):
    # Volume slider
    volume = int(val) / 100
    pygame.mixer.music.set_volume(volume)

def display_metadata(filepath):
    # Displays the metadata of the file
    try:
        audio = File(filepath)
        if audio:
            metadata = {
                "Title": audio.get("TIT2", audio.get("title", "Unknown Title")),
                "Artist": audio.get("TPE1", audio.get("artist", "Unknown Artist")),
                "Album": audio.get("TALB", audio.get("album", "Unknown Album")),
                "Year": audio.get("TDRC", audio.get("date", "Unknown Year")),
                "Genre": audio.get("TCON", audio.get("genre", "Unknown Genre"))
            }
        else:
            metadata = {
                "Title": "Unknown Title",
                "Artist": "Unknown Artist",
                "Album": "Unknown Album",
                "Year": "Unknown Year",
                "Genre": "Unknown Genre"
            }
        filename_label.config(text=f"File: {filepath.split('/')[-1]}")
        metadata_label.config(text="\n".join(f"{key}: {value}" for key, value in metadata.items()))
    except Exception as e:
        filename_label.config(text="File: Unknown")
        metadata_label.config(text=f"Could not retrieve metadata: {e}")

def get_music_length(filepath):
    audio = File(filepath)
    return audio.info.length

def update_time_remaining():
    if pygame.mixer.music.get_busy() and not is_paused:
        current_pos = pygame.mixer.music.get_pos() / 1000  # get_pos() returns time in milliseconds
        remaining_time = int(total_length - current_pos)
        mins, secs = divmod(remaining_time, 60)
        time_remaining_label.config(text=f"Time Remaining: {mins:02}:{secs:02}")
        root.after(1000, update_time_remaining)
        
def create_gui():
    # Create the GUI using tkinter.
    global pause_button, filename_label, metadata_label, time_remaining_label, root
    
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

    volume_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Volume", command=set_volume)
    volume_slider.set(100)  # Set initial volume to 100%
    volume_slider.pack(pady=5)
    
    filename_label = tk.Label(root, text="File: None")
    filename_label.pack(pady=5)

    metadata_label = tk.Label(root, text="Metadata: None")
    metadata_label.pack(pady=5)

    time_remaining_label = tk.Label(root, text="Time Remaining: 00:00")
    time_remaining_label.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
