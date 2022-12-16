import cv2
import numpy as np
from pygame import mixer
import pyaudio
import pygame
import struct
import tkinter as Tk
from scipy import signal


WIDTH = 2
CHANNELS = 1
RATE = 16000
output_byte = 0
MAX = 2**15 -1
BLOCKLEN = 512
output_block = [0] * BLOCKLEN
Thresh = 100      # hsv v value threshold initialized
background = 0.2   # gain of volume of background music
counter = 1   # counter seeing dark or bright
ORDER = 5  # order of filter

states = [0] * ORDER   # initial states

f1 = 800   # cutoff freq for highpass filter
f2 = 1600  # cutoff freq for lowpass filter
MUSIC_STYLE = 1   # indicator for index of music style



p = pyaudio.PyAudio()
# Open audio stream
stream = p.open(
    format      = p.get_format_from_width(WIDTH),
    channels    = CHANNELS,
    rate        = RATE,
    input       = True,
    output      = True )


# define TKinter

# TK object
root = Tk.Tk()

def fun_quit():   # quit
    global Continue
    print('Good bye')
    Continue = False
    root.quit()
    root.destroy()

def music_change():   # change music
    global MUSIC_STYLE
    if MUSIC_STYLE == 1:    # from style 1 change to style 2
        MUSIC_STYLE = 2    # change to style 2
        mixer.music.stop()
        if counter == 1:  # bright
            mixer.music.load('light_music2.wav')
        elif counter ==2: # dark
            mixer.music.load('quiet_music2.wav')
    else:   # from style 2 change to style 1
        MUSIC_STYLE = 1    # change to style 1
        mixer.music.stop()
        if counter == 1:  # bright
            mixer.music.load('light_music1.wav')
        elif counter ==2: # dark
            mixer.music.load('quiet_music1.wav')
    mixer.music.play()



print('press q to quit')

root.bind("<Key>", fun_quit)

# initialize widget
s = Tk.StringVar()   # legend
s.set("control panel")
thresh_var = Tk.DoubleVar()   # threshold of hue
thresh_var.set(Thresh)
vol_var = Tk.DoubleVar()  # gain of background music volume
vol_var.set(background)
highpass_freq = Tk.DoubleVar()  # low pass filter cutoff freq
lowpass_freq = Tk.DoubleVar() # high pass filter cutoff freq
highpass_freq.set(f1)
lowpass_freq.set(f2)


def vol_func():
    pygame.mixer.music.set_volume(S_volume.get())

# define widget

L1 = Tk.Label(root, textvariable=s)
S_thresh = Tk.Scale(root, label = 'brightness thresh', variable = thresh_var, from_ = 0, to = 255, tickinterval = 5)   # Threshold hsv value
S_volume = Tk.Scale(root, label = 'volume', variable = vol_var, from_ = 0, to = 1, tickinterval = 0.05, resolution = 0.01)  # background volume slider
# S_back = Tk.Scale(root, label = 'volume', variable = back_var, from_ = 0, to = 1, tickinterval = 0.05, resolution = 0.01)
S_highpass = Tk.Scale(root, label = 'highpass cutoff (hz)', variable = highpass_freq, from_ = 10, to = 1500, tickinterval = 50)    # control the highpass filter cutoff frequency
S_lowpass = Tk.Scale(root, label = 'lowpass cutoff (hz)', variable = lowpass_freq, from_ = 100, to = 2500, tickinterval = 50)     # control the lowpass filter cutoff frequency
B_music = Tk.Button(root, text = 'change music', command = music_change)
B1 = Tk.Button(root, text = 'Quit', command = fun_quit)


# place widget

L1.pack(side = Tk.TOP)
S_thresh.pack(side = Tk.LEFT)
S_volume.pack(side = Tk.RIGHT)
S_highpass.pack(side = Tk.RIGHT)
S_lowpass.pack(side = Tk.RIGHT)
B_music.pack(side = Tk.BOTTOM)
B1.pack(side = Tk.BOTTOM)






# set up vedio

video_capture = cv2.VideoCapture(0)

IS_BRIGHT = False
Continue = True




def isbright(image, dim=10, thresh=100.0):
    # Resize image to 10x10
    image = cv2.resize(image, (dim, dim))
    # Convert color space to HSV format and extract V channel
    im_hsv = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2HSV))
    v = im_hsv[:][:][2]
    # Return True if mean is greater than thresh else False
    return 'light' if np.mean(v) > thresh else 'dark'


def play_background_music(image):
    global IS_BRIGHT
    global thresh_var
    global back_var
    global counter
    global MUSIC_STYLE
    tsh = thresh_var.get()
    if isbright(image,thresh=tsh) == 'light' and not IS_BRIGHT:
        mixer.music.stop()
        mixer.music.load('light_music1.wav')
        mixer.music.play()
        print(isbright(image))
        IS_BRIGHT = True
        MUSIC_STYLE = 1
        counter = 1

    if isbright(image,thresh=tsh) == 'dark' and IS_BRIGHT:
        mixer.music.stop()
        mixer.music.load('quiet_music1.wav')
        # mixer.music.set_volume(volume)
        mixer.music.play()
        print(isbright(image))
        IS_BRIGHT = False
        MUSIC_STYLE = 1
        counter = 2



mixer.init()


# start loop
print('* Start, please wait a few seconds for camera start')

while Continue:
    vol_var.trace('w', vol_func())
    print(MUSIC_STYLE)
    root.update()

    ret, frame = video_capture.read()

    # Display the resulting frame
    cv2.imshow('camera capture', frame)

    # Get bright or dark on webcam
    image = frame.copy()
    play_background_music(image)


    input_tuple = stream.read(BLOCKLEN, exception_on_overflow=False)
    input_array = struct.unpack('h'*BLOCKLEN, input_tuple)



    # apply filter
    if counter == 1:
        f1 = highpass_freq.get()
        b,a = signal.butter(ORDER, f1 / (RATE/2) , btype='highpass')   # apply highpass filter for bright space
        [f_signal,states] = signal.lfilter(b,a,input_array, zi=states)
    elif counter == 2:
        f2 = lowpass_freq.get()
        b, a = signal.butter(ORDER, f2 / (RATE / 2), btype='lowpass')   # apply low pass filter for dark space
        [f_signal,states] = signal.lfilter(b, a, input_array, zi=states)

    # output
    output_array = f_signal

    output_clip = np.clip(output_array, -MAX, MAX)  # clipping
    output_clip = output_clip.astype(int)

    binary_data = struct.pack('h'*BLOCKLEN, *output_clip)

    stream.write(binary_data)


print('* Finished')
stream.stop_stream()
stream.close()
p.terminate()

# After the loop release the cap object
video_capture.release()
# Destroy all the windows
cv2.destroyAllWindows()