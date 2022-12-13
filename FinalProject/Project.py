import cv2
import numpy as np
from pygame import mixer

video_capture = cv2.VideoCapture(0)

IS_BRIGHT = True

def isbright(image, dim=10, thresh=0.5):
    # Resize image to 10x10
    image = cv2.resize(image, (dim, dim))
    # Convert color space to LAB format and extract L channel
    L, A, B = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2LAB))
    # Normalize L channel by dividing all pixel values with maximum pixel value
    L = L / np.max(L)
    # Return True if mean is greater than thresh else False
    return 'light' if np.mean(L) > thresh else 'dark'
    
def play_background_music(image):
    global IS_BRIGHT
    if isbright(image) == 'light' and not IS_BRIGHT:
        mixer.music.stop()
        mixer.music.load('/Users/Poppingary/Documents/DSP Lab/FinalProject/light_music.wav')
        mixer.music.play()
        print(isbright(image))
        IS_BRIGHT = True

    if isbright(image) == 'dark' and IS_BRIGHT:
        mixer.music.stop()
        mixer.music.load('/Users/Poppingary/Documents/DSP Lab/FinalProject/dark_music.wav')
        mixer.music.play()
        print(isbright(image))
        IS_BRIGHT = False


mixer.init()

while True:
    # Capture the video frame
    # by frame
    ret, frame = video_capture.read()
  
    # Display the resulting frame
    cv2.imshow('camera capture', frame)
    
    # Get bright or dark on webcam
    image = frame.copy()
    play_background_music(image)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  
    
# After the loop release the cap object
video_capture.release()
# Destroy all the windows
cv2.destroyAllWindows()