#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 13:10:45 2022

@author: Poppingary
"""
import cv2
import asyncio
import pyaudio
import struct

def clip16( x ):    
    # Clipping for 16 bits
    if x > 32767:
        x = 32767
    elif x < -32768:
        x = -32768
    else:
        x = x        
    return (x)
  
async def webcam():
    video_capture = cv2.VideoCapture(0)
    print("Webcam\n")
    
    while True:
        #await asyncio.sleep(0.01)
        ret, frame = video_capture.read()
        cv2.imshow('camera capture', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    video_capture.release()
    cv2.destroyAllWindows()
  
async def microphone():
    WIDTH       = 2         # Number of bytes per sample
    CHANNELS    = 1         # mono
    RATE        = 16000     # Sampling rate (frames/second)

    # Difference equation coefficients
    b0 =  0.008442692929081
    b2 = -0.016885385858161
    b4 =  0.008442692929081

    # a0 =  1.000000000000000
    a1 = -3.580673542760982
    a2 =  4.942669993770672
    a3 = -3.114402101627517
    a4 =  0.757546944478829

    # Initialization
    x1 = 0.0
    x2 = 0.0
    x3 = 0.0
    x4 = 0.0
    y1 = 0.0
    y2 = 0.0
    y3 = 0.0
    y4 = 0.0

    p = pyaudio.PyAudio()

    # Open audio stream
    stream = p.open(
        format      = p.get_format_from_width(WIDTH),
        channels    = CHANNELS,
        rate        = RATE,
        input       = True,
        output      = True)
    
    print("Microphone\n")
    while True:
        #await asyncio.sleep(0.01)
        #input_bytes = stream.read(1)
        input_bytes = stream.read(1, exception_on_overflow = False)
        input_tuple = struct.unpack('h', input_bytes)
        x0 = input_tuple[0]
        y0 = b0*x0 + b2*x2 + b4*x4 - a1*y1 - a2*y2 - a3*y3 - a4*y4
        
        x4 = x3
        x3 = x2
        x2 = x1
        x1 = x0
        y4 = y3
        y3 = y2
        y2 = y1
        y1 = y0
        
        output_value = int(clip16(10*y0))
        output_bytes = struct.pack('h', output_value)
        stream.write(output_bytes)
        
    stream.stop_stream()
    stream.close()
    p.terminate()

loop = asyncio.get_event_loop()
asyncio.ensure_future(webcam())
asyncio.ensure_future(microphone())
loop.run_forever()