import time
import os
import cv2
import pickle
import smtplib
import RPi.GPIO as GPIO
from gpiozero import LED
from picamera2 import Picamera2
from email.message import EmailMessage
from time import sleep
import face_recognition
import numpy as np
import pigpio
import asyncio
import websockets
import threading
 
# Initialize the pigpio library for controlling GPIO pins
pi = pigpio.pi()
 
if not pi.connected:
    print("Unable to connect to pigpio daemon")
    exit()
 
# Initialize the RF Transmitter (GPIO 27)
RF_PIN = 27
rf_transmitter = LED(RF_PIN)
pi.set_mode(27, pigpio.OUTPUT)
 
# Initialize GPIO
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
 
from_email_addr = "piface36@gmail.com"
from_email_pass = "lfmo kpvt glho cvpk"
to_email_addr = "iftekharsyed@proton.me"
 
def send_email(body, image_path):
    msg = EmailMessage()
    msg['From'] = from_email_addr
    msg['To'] = to_email_addr
    msg['Subject'] = 'Face Detected!'
    msg.set_content(body)
    with open(image_path, 'rb') as img:
        img_data = img.read()
        msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename=os.path.basename(image_path))
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(from_email_addr, from_email_pass)
        server.send_message(msg)
        print('Email sent.')
 
print("Loading Encodings...")
with open("encodings.pickle", "rb") as f:
    data = pickle.loads(f.read())
 
known_face_encodings = data["encodings"]
known_face_names = data["names"]
 
print('Encodings loaded')
 
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (500, 500)}))
picam2.start()
 
print('Camera Initialized')
 
cv_scaler = 4
face_locations = []
face_encodings = []
face_names = []
 
# Function to send RF signal
def send_rf_signal():
    print("Sending RF signal")
 
    # Send 433 MHz modulated signal using simple bursts of 1ms on, 1ms off
    for _ in range(10):  # Repeat the signal 10 times for example
        pi.write(RF_PIN, 1)  # Send High (ON)
        time.sleep(0.001)  # Sleep for 1ms (High time)
        pi.write(RF_PIN, 0)  # Send Low (OFF)
        time.sleep(0.001)
 
 
def process_frame(frame):
    global face_locations, face_encodings, face_names
    resized_frame = cv2.resize(frame, (0, 0), fx=(1/cv_scaler), fy=(1/cv_scaler))
    rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_resized_frame)
    face_encodings = face_recognition.face_encodings(rgb_resized_frame, face_locations, model='large')
    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown Person"
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            GPIO.setup(11, GPIO.OUT)
            p = GPIO.PWM(11, 50)
            p.start(0)
            # Turn servo 90 degrees
            p.ChangeDutyCycle(7.5)
            sleep(3)
            # Turn servo back to original position
            p.ChangeDutyCycle(2.5)
            sleep(1)
            p.stop()
            body = 'The correct face has been detected.'
            # Send RF signal since the correct person was detected
            send_rf_signal()
        else:
            body = 'The incorrect face has been detected.'
        face_names.append(name)
        img_path = "detected_face.jpg"
        cv2.imwrite(img_path, frame)
        send_email(body, img_path)
        os.remove(img_path)
 
    return frame
 
def draw_results(frame):
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= cv_scaler
        right *= cv_scaler
        bottom *= cv_scaler
        left *= cv_scaler
        cv2.rectangle(frame, (left, top), (right, bottom), (244, 42, 3), 3)
        cv2.rectangle(frame, (left - 3, top - 35), (right + 3, top), (244, 42, 3), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, top - 6), font, 1.0, (255, 255, 255), 1)
    return frame
 
# WebSocket Server to receive messages from the app
async def websocket_server(websocket, path):
    async for message in websocket:
        print(f"Received WebSocket message: {message}")
        if message == "SEND_RF":
            print("Executing send_rf_signal() via WebSocket command.")
            send_rf_signal()
 
 
# Function to start the WebSocket server
def start_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server = websockets.serve(websocket_server, "127.0.1.1", 8765)  # Raspberry Pi as server
    loop.run_until_complete(server)
    loop.run_forever()
 
 
# Start WebSocket server in a separate thread
websocket_thread = threading.Thread(target=start_websocket_server, daemon=True)
websocket_thread.start()
 
print("WebSocket Server Running and Ready to Receive Commands")
 
# Main loop for face recognition
print('Loop begun')
 
try:
    while True:
        frame = picam2.capture_array()
        processed_frame = process_frame(frame)
        display_frame = draw_results(processed_frame)
        # Show the video feed with face recognition results
        cv2.imshow('Video', display_frame)
        # Exit the loop when "q" is pressed
        if cv2.waitKey(1) == ord("q"):
            break
finally:
    GPIO.cleanup()
    cv2.destroyAllWindows()
    picam2.stop()
