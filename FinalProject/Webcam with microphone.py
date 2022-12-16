# Import the required libraries
from tkinter import *
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import pygame
import cv2
import numpy as np
import pyaudio
import struct
from scipy import signal

import _thread
import time

root = Tk()
root.title('Webcam and background music controller')
root.maxsize(1700, 900)  # specify the max size the window can expand to
root.config(bg="skyblue")  # specify background color

# Initialze Pygame Mixer
pygame.mixer.init()

VALUME = 0.2
def volume(x):
    global VALUME
    VALUME = volume_slider.get()
    pygame.mixer.music.set_volume(VALUME)
    
THRESH = 100
def brightness_thresh(x):
    global THRESH
    THRESH = brightness_thresh_slider.get()
    
HIGH_PASS_FREQ = 750
def high_pass(x):
    global HIGH_PASS_FREQ
    HIGH_PASS_FREQ = high_pass_slider.get()
    
def next_song(x):
	print("next song")

# Create left and right frames
left_frame = Frame(root, width=200, height=400, bg='grey')
left_frame.grid(row=0, column=0, padx=10, pady=5)

right_frame = Frame(root, width=950, height=780, bg='grey')
right_frame.grid(row=0, column=1, padx=10, pady=5)

# Create frames and labels in left_frame
Label(left_frame, text="Background music").grid(row=0, column=0, padx=5, pady=5)

# load music image
small_image = ImageTk.PhotoImage(Image.open('images/hello_world.png').resize((180, 180)))
Label(left_frame, image = small_image).grid(row = 1, column = 0, padx = 5, pady = 5)

# Webcam is in right_frame
large_image = ImageTk.PhotoImage(Image.open('images/pikachu.png').resize((940, 770)))
webcam_label = Label(right_frame, image = large_image)
webcam_label.grid(row = 0,column = 0, padx = 5, pady = 5)

# Create tool bar frame
tool_bar = Frame(left_frame, width = 200, height = 185)
tool_bar.grid(row = 2, column = 0, padx = 5, pady = 5)

# Create volume label frame
volume_frame = LabelFrame(tool_bar, text = "Volume")
volume_frame.grid(row = 0 , column = 0)

# Create brightness thresh label frame
brightness_thresh_frame = LabelFrame(tool_bar, text = "Brightness thresh")
brightness_thresh_frame.grid(row = 1 , column = 0)

# Create high pass filter label frame
high_pass_frame = LabelFrame(tool_bar, text = "High-pass filter")
high_pass_frame.grid(row = 2 , column = 0)

# Create next song button image
next_button_image = ImageTk.PhotoImage(Image.open('images/next_btn.png').resize((100, 40)))

# Example labels that could be displayed under the "Tool" menu
volume_slider = ttk.Scale(volume_frame, from_ = 0, to = 1, orient = HORIZONTAL, value = VALUME, command = volume, length = 200)
volume_slider.pack(pady = 10)
brightness_thresh_slider = ttk.Scale(brightness_thresh_frame, from_ = 0, to = 255, orient = HORIZONTAL, value = THRESH, command = brightness_thresh, length = 200)
brightness_thresh_slider.pack(pady = 10)
high_pass_slider = ttk.Scale(high_pass_frame, from_ = 10, to = 1500, orient = HORIZONTAL, value = HIGH_PASS_FREQ, command = high_pass, length = 200)
high_pass_slider.pack(pady = 10)
Label(tool_bar, image = next_button_image).grid(row = 3, column = 0, padx = 5, pady = 5, columnspan = 2)
button = Button(root, image = next_button_image, command = next_song, borderwidth = 0)

video_capture = cv2.VideoCapture(0)
IS_BRIGHT = True

def isbright(image, dim=10):
    global THRESH
    # Resize image to 10x10
    image = cv2.resize(image, (dim, dim))
    # Convert color space to HSV format and extract V channel
    im_hsv = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2HSV))
    v = im_hsv[:][:][2]
    # Return True if mean is greater than thresh else False
    return 'light' if np.mean(v) > THRESH else 'dark'

def play_background_music(image):
    global IS_BRIGHT
    if isbright(image) == 'light' and not IS_BRIGHT:
        pygame.mixer.music.stop()
        pygame.mixer.music.load('light_music.wav')
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play()
        print(isbright(image))
        IS_BRIGHT = True

    if isbright(image) == 'dark' and IS_BRIGHT:
        pygame.mixer.music.stop()
        pygame.mixer.music.load('quiet_music1.wav')
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play()
        print(isbright(image))
        IS_BRIGHT = False

def show_frames():
   ret, frame = video_capture.read()

   # Get bright or dark on webcam
   play_background_music(frame.copy())

   # Get the latest frame and convert into Image
   cv2image = cv2.cvtColor(video_capture.read()[1], cv2.COLOR_BGR2RGB)
   img = Image.fromarray(cv2image)
   # Convert image to PhotoImage
   imgtk = ImageTk.PhotoImage(image = img)
   webcam_label.imgtk = imgtk
   webcam_label.configure(image = imgtk)
   webcam_label.after(1, show_frames)

show_frames()


def microphone():
   global states
   global HIGH_PASS_FREQ
   WIDTH = 2
   CHANNELS = 1
   RATE = 16000
   output_byte = 0
   MAX = 2**15 - 1
   BLOCKLEN = 1200
   output_block = [0] * BLOCKLEN
   ORDER = 5  # order of filter
   states = [0] * ORDER   # initial states

   p = pyaudio.PyAudio()
   # Open audio stream
   stream = p.open(
       format      = p.get_format_from_width(WIDTH),
       channels    = CHANNELS,
       rate        = RATE,
       input       = True,
       output      = True)

   while True:
       input_tuple = stream.read(BLOCKLEN, exception_on_overflow = False)
       input_array = struct.unpack('h'*BLOCKLEN, input_tuple)

       b, a = signal.butter(ORDER, HIGH_PASS_FREQ / (RATE / 2) , btype = 'highpass')   # apply highpass filter for bright space
       [filter_signal, states] = signal.lfilter(b, a, input_array, zi = states)

       # output
       output_array = filter_signal
       output_clip = np.clip(output_array, -MAX, MAX)
       output_clip = output_clip.astype(int)

       binary_data = struct.pack('h'*BLOCKLEN, *output_clip)

       stream.write(binary_data)
       
   print('* Finished')
   stream.stop_stream()
   stream.close()
   p.terminate()
   
MICROPHONE_THREAD_COUNTER = 0
if MICROPHONE_THREAD_COUNTER == 0:
    _thread.start_new_thread(microphone, ())
    MICROPHONE_THREAD_COUNTER += 1


root.mainloop()



# After the loop release the cap object
video_capture.release()
# Destroy all the windows
cv2.destroyAllWindows()