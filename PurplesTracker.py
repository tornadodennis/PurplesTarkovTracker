import os
import pyperclip
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import keyboard
from threading import Thread
import time
import pygame
import sys

# Helper function to get the path to bundled resources
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class FileCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Name Copier")
        self.root.geometry('500x500')  # Set window size to 500x500
        self.folder_path = ""
        self.keybind = None
        self.is_running = False

        # Initialize pygame mixer to play sound
        pygame.mixer.init()

        # Load the background image using relative path
        self.original_image = Image.open(resource_path("Capture.PNG"))
        self.background_image = ImageTk.PhotoImage(self.original_image)
        
        self.background_label = tk.Label(root)
        self.background_label.place(relwidth=1, relheight=1)

        # Adjust image size dynamically
        self.update_background_image()
        self.root.bind('<Configure>', self.update_background_image)  # Bind the window resize event to update image

        # Create buttons and labels
        self.start_stop_btn = tk.Button(root, text="Start", command=self.toggle_monitoring)
        self.start_stop_btn.pack(pady=10)

        self.choose_folder_btn = tk.Button(root, text="Choose Folder", command=self.select_folder)
        self.choose_folder_btn.pack(pady=10)

        self.folder_label = tk.Label(root, text="No folder selected")
        self.folder_label.pack(pady=5)

        self.set_keybind_btn = tk.Button(root, text="Set Keybind", command=self.set_keybind)
        self.set_keybind_btn.pack(pady=10)

        self.keybind_label = tk.Label(root, text="No keybind set")
        self.keybind_label.pack(pady=5)

        self.status_label = tk.Label(root, text="Status: Stopped")
        self.status_label.pack(pady=10)

        # Add "Made by PurplePC" button in the bottom-right corner that plays a sound
        self.signature_button = tk.Button(root, text="Made by PurplePC", fg="purple", font=("Arial", 10), command=self.play_sound)
        self.signature_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)  # Position in bottom-right corner

    def play_sound(self):
        """Play the MP3 file when the button is pressed."""
        mp3_path = resource_path("MadeByMe.mp3")  # Use the relative path to your MP3 file
        if not pygame.mixer.music.get_busy():  # Check if no sound is currently playing
            pygame.mixer.music.load(mp3_path)  # Load the MP3 file
            pygame.mixer.music.play()  # Play the sound

    def update_background_image(self, event=None):
        """Resize background image to fit window dimensions."""
        new_width = self.root.winfo_width()
        new_height = self.root.winfo_height()
        resized_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.background_image = ImageTk.PhotoImage(resized_image)
        self.background_label.config(image=self.background_image)

    def toggle_monitoring(self):
        if self.is_running:
            self.is_running = False
            self.start_stop_btn.config(text="Start")
            self.status_label.config(text="Status: Stopped")
            keyboard.unhook_all_hotkeys()  # Remove all keybind listeners
        else:
            if not self.folder_path or not self.keybind:
                self.status_label.config(text="Status: Please set folder and keybind")
                return
            self.is_running = True
            self.start_stop_btn.config(text="Stop")
            self.status_label.config(text="Status: Running")
            self.monitor_keybind()  # Start event-based keybind monitoring

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.folder_label.config(text=f"Folder: {self.folder_path}")

    def set_keybind(self):
        self.status_label.config(text="Press any key to set as keybind...")
        self.root.update()  # Update the GUI to show the message
        key = keyboard.read_event()  # Capture keypress event
        if key.event_type == "down":
            self.keybind = key.name
            self.keybind_label.config(text=f"Keybind: {self.keybind}")

    def monitor_keybind(self):
        # Add a hotkey event listener for the keybind
        keyboard.add_hotkey(self.keybind, self.on_keypress)

    def on_keypress(self):
        time.sleep(1.5)  # Small delay before copying
        latest_file = self.get_latest_file()
        if latest_file:
            pyperclip.copy(latest_file)
            self.status_label.config(text=f"Copied to clipboard: {latest_file}")
        keyboard.remove_hotkey(self.keybind)  # Reset keybind after pressing
        self.monitor_keybind()  # Rebind the keybind

    def get_latest_file(self):
        files = [f for f in os.listdir(self.folder_path) if os.path.isfile(os.path.join(self.folder_path, f))]
        if files:
            latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(self.folder_path, f)))
            return latest_file
        return None

# Create the main application window
root = tk.Tk()
app = FileCopyApp(root)
root.mainloop()
