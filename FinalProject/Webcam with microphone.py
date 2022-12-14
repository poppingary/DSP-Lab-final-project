import cv2
import numpy as np
from pygame import mixer
import pyaudio
import struct

WIDTH = 2
CHANNELS = 1
RATE = 16000
output_byte = 0
MAX = 2**15 - 1
BLOCKLEN = 1200
output_block = [0] * BLOCKLEN

p = pyaudio.PyAudio()
# Open audio stream
stream = p.open(
    format      = p.get_format_from_width(WIDTH),
    channels    = CHANNELS,
    rate        = RATE,
    input       = True,
    output      = True)

video_capture = cv2.VideoCapture(0)

IS_BRIGHT = True

def isbright(image, dim=10, thresh=100):
    # Resize image to 10x10
    image = cv2.resize(image, (dim, dim))
    # Convert color space to LAB format and extract L channel
    im_hsv = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2LAB))
    # Normalize channel by dividing all pixel values with maximum pixel value
    v = im_hsv[:][:][0]
    # Return True if mean is greater than thresh else False
    return 'light' if np.mean(v) > thresh else 'dark'

def play_background_music(image):
    global IS_BRIGHT
    if isbright(image) == 'light' and not IS_BRIGHT:
        mixer.music.stop()
        mixer.music.load('light_music2.wav')
        mixer.music.set_volume(0.1)
        mixer.music.play()
        print(isbright(image))
        IS_BRIGHT = True

    if isbright(image) == 'dark' and IS_BRIGHT:
        mixer.music.stop()
        mixer.music.load('dark_music2.wav')
        mixer.music.set_volume(0.1)
        mixer.music.play()
        print(isbright(image))
        IS_BRIGHT = False

mixer.init()

while True:
    ret, frame = video_capture.read()

    # Display the resulting frame
    cv2.imshow('camera capture', frame)

    # Get bright or dark on webcam
    image = frame.copy()
    play_background_music(image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

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