import time
import os
import cv2
import pickle
import smtplib
import RPi.GPIO as GPIO
from picamera2 import Picamera2
from email.message import EmailMessage
from time import sleep
import face_recognition
import numpy as np
import paho.mqtt.client as mqtt  # MQTT client

# --- MQTT Configuration ---
MQTT_BROKER = "piface.local"       # Replace with your broker IP or domain
MQTT_PORT = 1883
MQTT_TOPIC = "home/door"

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(MQTT_TOPIC)
client.loop_start()

def send_mqtt_message(message):
    print(f"Sending MQTT message: {message}")
    client.publish(MQTT_TOPIC, message)

# --- GPIO Setup ---
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setup(11, GPIO.OUT)  # Servo
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pushbutton with pull-up resistor

# --- Email Setup ---
from_email_addr = "example@huh.com"
from_email_pass = "app password"
to_email_addr = "exampleeee"

def send_email(body, image_path):
    msg = EmailMessage()
    msg['From'] = from_email_addr
    msg['To'] = to_email_addr
    msg['Subject'] = 'Face Detected!'
    msg.set_content(body)

    with open(image_path, 'rb') as img:
        msg.add_attachment(img.read(), maintype='image', subtype='jpeg', filename=os.path.basename(image_path))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(from_email_addr, from_email_pass)
        server.send_message(msg)
        print('Email sent.')

# --- Load Face Encodings ---
print("Loading Encodings...")
with open("encodings.pickle", "rb") as f:
    data = pickle.loads(f.read())

known_face_encodings = data["encodings"]
known_face_names = data["names"]
print('Encodings loaded')

# --- Camera Setup ---
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (500, 500)}))
picam2.start()
print('Camera Initialized')

cv_scaler = 4
face_locations = []
face_encodings = []
face_names = []

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

            p = GPIO.PWM(11, 50)
            p.start(0)

            # Turn servo 90 degrees
            p.ChangeDutyCycle(7.5)
            sleep(2)

            # Return to original
            p.ChangeDutyCycle(2.5)
            sleep(1)
            p.stop()

            body = 'The correct face has been detected.'
            send_mqtt_message("access_granted")
        else:
            body = 'The incorrect face has been detected.'

        face_names.append(name)

        img_path = "detected_face.jpg"
        cv2.imwrite(img_path, frame)
        try:
            send_email(body, img_path)
        except Exception as e:
            print(f"Email failed: {e}")
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
    while True:
        # --- Check pushbutton ---
        if GPIO.input(27) == GPIO.LOW:
            print("Button Pressed")
            send_mqtt_message("button_pressed")
            sleep(0.1)  # Debounce

        # --- Camera frame and processing ---
        frame = picam2.capture_array()
        processed_frame = process_frame(frame)
        display_frame = draw_results(processed_frame)

        # Show frame
        cv2.imshow('Video', display_frame)

        if cv2.waitKey(1) == ord("q"):
            break

finally:
    GPIO.cleanup()
    client.loop_stop()
    client.disconnect()
    cv2.destroyAllWindows()
    picam2.stop()
