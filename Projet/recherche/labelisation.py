import cv2
import numpy as np
import face_recognition
from retinaface import RetinaFace  # Assurez-vous d'avoir installé cette bibliothèque

class FaceRecognition:
    def __init__(self):
        # Initialisation sans base de données
        print("Initialisation de la reconnaissance faciale sans base de données.")

    def detect_faces_and_recognize(self, frame):
        # Utiliser RetinaFace pour détecter les visages
        detections = RetinaFace.detect_faces(frame)

        for key in detections.keys():
            identity = detections[key]
            x1, y1, x2, y2 = identity['facial_area']
            face_image = frame[y1:y2, x1:x2]
            
            # Convertir le visage en RGB pour l'encodage
            rgb_face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            
            # Obtenir l'encodage du visage
            face_encodings = face_recognition.face_encodings(rgb_face_image)
            
            if face_encodings:
                encoding = face_encodings[0]
                print(f"Encodage du visage: {encoding}")
                
                # Dessiner un rectangle autour du visage détecté
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        return frame

    def start_video_capture(self):
        video_capture = cv2.VideoCapture(0)

        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            frame = self.detect_faces_and_recognize(frame)
            cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    face_recog = FaceRecognition()
    face_recog.start_video_capture()
