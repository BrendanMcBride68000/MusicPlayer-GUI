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
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import platform
import time

# Initialize Pygame mixer
pygame.mixer.init()

# Check if running on Raspberry Pi
is_raspberry_pi = platform.system() == 'Linux'

if is_raspberry_pi:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    LSBFIRST = 1
    MSBFIRST = 2
    dataPin = 11
    latchPin = 13
    clockPin = 15

    redPin = 16
    yellowPin = 18
    greenPin = 22

    def gpio_setup():
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(dataPin, GPIO.OUT)
        GPIO.setup(latchPin, GPIO.OUT)
        GPIO.setup(clockPin, GPIO.OUT)
        GPIO.setup(redPin, GPIO.OUT)
        GPIO.setup(yellowPin, GPIO.OUT)
        GPIO.setup(greenPin, GPIO.OUT)

    def shiftOut(dPin, cPin, order, val):
        for i in range(0, 8):
            GPIO.output(cPin, GPIO.LOW)
            if order == LSBFIRST:
                GPIO.output(dPin, (0x01 & (val >> i) == 0x01) and GPIO.HIGH or GPIO.LOW)
            elif order == MSBFIRST:
                GPIO.output(dPin, (0x80 & (val << i) == 0x80) and GPIO.HIGH or GPIO.LOW)
            GPIO.output(cPin, GPIO.HIGH)

    def led_loop():
        delay_time = 0.05
        while led_running:
            x = 0x01
            for i in range(0, 8):
                if not led_running:
                    break
                GPIO.output(latchPin, GPIO.LOW)
                shiftOut(dataPin, clockPin, LSBFIRST, x)
                GPIO.output(latchPin, GPIO.HIGH)
                x <<= 1
                time.sleep(delay_time)
            x = 0x80
            for i in range(0, 8):
                if not led_running:
                    break
                GPIO.output(latchPin, GPIO.LOW)
                shiftOut(dataPin, clockPin, LSBFIRST, x)
                GPIO.output(latchPin, GPIO.HIGH)
                x >>= 1
                time.sleep(delay_time)
        # Turn off all LEDs when stopping
        GPIO.output(latchPin, GPIO.LOW)
        shiftOut(dataPin, clockPin, LSBFIRST, 0x00)
        GPIO.output(latchPin, GPIO.HIGH)

    def set_led_state(red, yellow, green):
        GPIO.output(redPin, red)
        GPIO.output(yellowPin, yellow)
        GPIO.output(greenPin, green)

else:
    def gpio_setup():
        pass  # No-op for non-Raspberry Pi systems

    def led_loop():
        pass  # No-op for non-Raspberry Pi systems

    def set_led_state(red, yellow, green):
        pass  # No-op for non-Raspberry Pi systems

    # Define GPIO.LOW and GPIO.HIGH for non-Raspberry Pi systems
    class GPIO:
        LOW = False
        HIGH = True

def start_led_loop():
    global led_running, led_thread
    led_running = True
    led_thread = threading.Thread(target=led_loop)
    led_thread.start()

def stop_led_loop():
    global led_running, led_thread
    led_running = False
    if led_thread:
        led_thread.join()
        led_thread = None

# Flag to track if the music is paused
is_paused = False
current_file = None
total_length = 0
led_running = False
led_thread = None

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
        start_led_loop()
        set_led_state(GPIO.LOW, GPIO.LOW, GPIO.HIGH)  # Green on, Red and Yellow off
        update_time_remaining()
    except pygame.error as e:
        messagebox.showerror("Error", f"Could not play music file: {e}")

def stop_music_file():
    global is_paused
    # Stop the playback of the music file.
    pygame.mixer.music.stop()
    is_paused = False
    stop_led_loop()
    set_led_state(GPIO.HIGH, GPIO.LOW, GPIO.LOW)  # Red on, Yellow and Green off
    time_remaining_label.config(text="Time Remaining: 00:00")

def pause_music_file():
    global is_paused
    # Pause or unpause the playback of the music file.
    if is_paused:
        pygame.mixer.music.unpause()
        pause_button.config(text="Pause")
        is_paused = False
        start_led_loop()
        set_led_state(GPIO.LOW, GPIO.LOW, GPIO.HIGH)  # Green on, Red and Yellow off
        update_time_remaining()
    else:
        pygame.mixer.music.pause()
        pause_button.config(text="Resume")
        is_paused = True
        stop_led_loop()
        set_led_state(GPIO.LOW, GPIO.HIGH, GPIO.LOW)  # Yellow on, Red and Green off

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

class MyServer(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        html = '''
           <html>
           <body style="width:960px; margin: 20px auto;">
           <h1>Welcome to Brendan's exciting Music Player!!!</h1>
           <form action="/" method="POST">
               <input type="submit" name="submit" value="Play">
               <input type="submit" name="submit" value="Pause">
               <input type="submit" name="submit" value="Stop">
           </form>
           </body>
           </html>
        '''
        self.do_HEAD()
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        post_data = post_data.split("=")[1]

        if post_data == 'Play':
            play_music_file()
        elif post_data == 'Pause':
            pause_music_file()
        elif post_data == 'Stop':
            stop_music_file()

        self._redirect('/')

def start_http_server():
    server_address = (host_name, host_port)
    httpd = HTTPServer(server_address, MyServer)
    httpd.serve_forever()

if __name__ == "__main__":
    host_name = 'x.x.x.x'  # Your IPv4 Address goes here
    host_port = 3000

    # Start HTTP server in a separate thread
    server_thread = threading.Thread(target=start_http_server)
    server_thread.daemon = True
    server_thread.start()

    # Create the GUI
    create_gui()
