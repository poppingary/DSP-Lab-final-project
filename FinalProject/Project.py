import cv2
import numpy as np

video_capture = cv2.VideoCapture(0)

def isbright(image, dim=10, thresh=0.5):
    # Resize image to 10x10
    image = cv2.resize(image, (dim, dim))
    # Convert color space to LAB format and extract L channel
    L, A, B = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2LAB))
    # Normalize L channel by dividing all pixel values with maximum pixel value
    L = L / np.max(L)
    # Return True if mean is greater than thresh else False
    return 'light' if np.mean(L) > thresh else 'dark'
    
while True:
    # Capture the video frame
    # by frame
    ret, frame = video_capture.read()
  
    # Display the resulting frame
    cv2.imshow('frame', frame)
    
    # Get bright or dark on webcam
    image = frame.copy()
    print(isbright(image))
      
    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    
    #webcam_properties()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  
    
# After the loop release the cap object
video_capture.release()
# Destroy all the windows
cv2.destroyAllWindows()