import time
import RPi.GPIO as GPIO
import pygame
from gpiozero import Button

RF_PIN = 17

pygame.mixer.init()

SOUND_FILE = '/home/piface/Downloads/Sounds/Ringtones/(AOSP) Lyon.ogg'

GPIO.setmode(GPIO.BCM)
GPIO.setup(RF_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def play_sound():
    pygame.mixer.music.load(SOUND_FILE)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

try:
    print("Doorbell receiver running... waiting for signal...")
    while True:
        if GPIO.input(RF_PIN) == GPIO.LOW:  
            print("Signal received! Playing sound...")
            play_sound()
            time.sleep(1) 
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Program interrupted.")
finally:
    GPIO.cleanup()
