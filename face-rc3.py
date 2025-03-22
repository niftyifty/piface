import os
import cv2
import time
import pickle
import smtplib
import face_recognition
import numpy as np
import RPi.GPIO as GPIO
from gpiozero import LED
from picamera2 import Picamera2
from email.message import EmailMessage
from time import sleep
from gtts import gTTS

print('Imports completed')

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)

from_email_addr = "piface36@gmail.com"
from_email_pass = "lfmo kpvt glho cvpk"
to_email_addrs = ["21chaudharil@bluecoatstudent.org.uk", "21zhengt@bluecoatstudent.org.uk", "iftekharsyed@proton.me"]

def log_message(message):
    with open("activity_log.txt", "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def speak(text):
    tts = gTTS(text=text, lang='en')
    filename = "voice.mp3"
    tts.save(filename)
    os.system(f"mpg321 {filename}")

def send_email(body, image_path):
    msg = EmailMessage()
    msg['From'] = from_email_addr
    msg['To'] = ", ".join(to_email_addrs)
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

rf_transmitter = LED(18)

def doorbell():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    BUTTON_PIN = 4
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
        print("Button pressed.")
        print("Sending signal...")
        
        rf_transmitter.on()
        sleep(5)
        rf_transmitter.off()
        sleep(0.5)
        print('Signal sent.')

def motion_detected(frame, prev_frame, threshold=30):
    diff = cv2.absdiff(frame, prev_frame)
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh_diff = cv2.threshold(gray_diff, 25, 255, cv2.THRESH_BINARY)
    motion_count = np.sum(thresh_diff > 0)
    return motion_count > threshold

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
        
        if matches[best_match_index] and face_distances[best_match_index] < 0.6:  # confidence threshold
            name = known_face_names[best_match_index]
            GPIO.setup(11, GPIO.OUT)
            p = GPIO.PWM(11, 50)
            p.start(0)
            p.ChangeDutyCycle(3)
            sleep(1)
            p.ChangeDutyCycle(12)
            sleep(1)
            
            body = f'The correct face has been detected as {name}.'
            log_message(body)
            speak(body)
        else:
            body = 'The incorrect face has been detected.'
            log_message(body)
            speak(body)
        
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

print('Loop begun')

try:
    prev_frame = picam2.capture_array()
    while True:
        frame = picam2.capture_array()
        
        if motion_detected(frame, prev_frame):
            processed_frame = process_frame(frame)
            display_frame = draw_results(processed_frame)
            doorbell()
            cv2.imshow('Video', display_frame)
            
        prev_frame = frame
        
        if cv2.waitKey(1) == ord("q"):
            break
finally:
    GPIO.cleanup()
    cv2.destroyAllWindows()
    picam2.stop()