import os
import cv2
import pickle
import face_recognition
from imutils import paths

print("[STATUS] Scanning dataset for images...")

img_paths = list(paths.list_images("dataset"))
encoded_faces = []
person_labels = []

for idx, img_path in enumerate(img_paths):
    print(f"[STATUS] Processing image {idx + 1} of {len(img_paths)}...")
    person_name = os.path.basename(os.path.dirname(img_path))
    
    img = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    face_boxes = face_recognition.face_locations(img_rgb, model="hog")
    face_encodings = face_recognition.face_encodings(img_rgb, face_boxes)
    
    for encoding in face_encodings:
        encoded_faces.append(encoding)
        person_labels.append(person_name)

print("[STATUS] Saving face encodings...")
face_data = {"encodings": encoded_faces, "names": person_labels}

with open("encodings.pickle", "wb") as file:
    pickle.dump(face_data, file)

print("[SUCCESS] Face encoding process complete! Data saved in 'encodings.pickle'.")