import cv2
import numpy as np
from pygame import mixer
import pyaudio
import wave
import struct
import tkinter as Tk
import scipy.signal as sps


WIDTH = 2
CHANNELS = 1
RATE = 16000
output_byte = 0
MAX = 2**15 -1
BLOCKLEN = 533
output_block = [0] * BLOCKLEN
Thresh = 100

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

def fun_quit(event):   # quit
    global Continue
    print('You pressed ' + event.char)
    if event.char == 'q':
        print('Good bye')
        Continue = False
        root.quit()
        root.destroy()

print('press q to quit')

root.bind("<Key>", fun_quit)

# initialize widget
s = Tk.StringVar()   # legend
s.set("control threshold")
thresh_var = Tk.DoubleVar()   # threshold of hue
thresh_var.set(Thresh)

# define widget

L1 = Tk.Label(root, textvariable=s)
S_thresh = Tk.Scale(root, label = 'thresh', variable = thresh_var, from_ = 0, to = 255, tickinterval = 5)    # time to repeat the increase and decrease signal, also refers to the modulation frequency (1/T)

# place widget

L1.pack(side = Tk.TOP)
S_thresh.pack(side = Tk.LEFT)





# set up vedio

video_capture = cv2.VideoCapture(0)

IS_BRIGHT = True
Continue = True


def isbright(image, dim=10, thresh=100.0):
    # Resize image to 10x10
    image = cv2.resize(image, (dim, dim))
    # Convert color space to LAB format and extract L channel
    im_hsv = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2LAB))
    # Normalize channel by dividing all pixel values with maximum pixel value
    v = im_hsv[:][:][0]
    # Return True if mean is greater than thresh else False
    return 'light' if np.mean(im_hsv[:][:][0]) > thresh else 'dark'


def play_background_music(image):
    global IS_BRIGHT
    global thresh_var
    tsh = thresh_var.get()
    if isbright(image,thresh=tsh) == 'light' and not IS_BRIGHT:
        mixer.music.stop()
        mixer.music.load('light_music2.wav')
        mixer.music.play()
        print(isbright(image))
        IS_BRIGHT = True

    if isbright(image,thresh=tsh) == 'dark' and IS_BRIGHT:
        mixer.music.stop()
        mixer.music.load('dark_music2.wav')
        mixer.music.play()
        print(isbright(image))
        IS_BRIGHT = False


mixer.init()






i = 1
while Continue:
    i += 1
    print(i)

    root.update()

    ret, frame = video_capture.read()

    # Display the resulting frame
    cv2.imshow('camera capture', frame)

    # Get bright or dark on webcam
    image = frame.copy()
    play_background_music(image)

    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break


    input_tuple = stream.read(BLOCKLEN, exception_on_overflow=False)
    input_array = struct.unpack('h'*BLOCKLEN, input_tuple)

    # output
    output_array = input_array
    output_clip = np.clip(output_array, -MAX, MAX)
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