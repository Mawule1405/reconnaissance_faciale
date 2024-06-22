
from ultralytics import YOLO
import cv2
import os
from PIL import Image
from datetime import datetime
import numpy as np
import duckdb as db

from Projet.database.databaseHandler import DatabaseHandler

class Inferencing:

    """
    Classe contient des méthodes d'inférence
    """

    def __init__(self, train_model_path: str):
        self.train_model_path = train_model_path
        self.model = None
        self.db = None


    def charging_model(self):
            """
            Charge un modèle YOLO à partir du chemin spécifié.

            Paramètres:
            model_path (str): Le chemin vers le fichier du modèle YOLO.

            Retourne:
            model: Le modèle YOLO chargé.
            """
            model_path = self.train_model_path

            print(f"Loading model from {model_path}...")
            try:
                model = YOLO(model_path, verbose=True)
                self.model = model
                print("Model loaded successfully.")
            except Exception as e:
                 print("Chargement du model a échoué")
                 print(f"Erreur: {e}")
            
            return self


   
    def inferecing_photo(self, image_path: str):
        """
        Effectue une inférence sur une image donnée et dessine des rectangles autour des objets détectés.

        Paramètres:
        image_path (str): Le chemin vers le fichier image.

        Retourne:
        results: Les résultats de l'inférence.
        """
        

        if self.model is None:
            print("Le modèle n'est pas chargé. Veuillez charger le modèle d'abord.")
            return None

        print(f"Loading image from {image_path}...")
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("L'image n'a pas pu être chargée. Vérifiez le chemin.")
            
            # Faire l'inférence
            results = self.model(image)
            
            # Dessiner les résultats sur l'image
            for result in results:
                for box in result.boxes:
                    # Extraction des coordonnées et des autres informations
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = box.conf[0].item() * 100  # Confiance en pourcentage
                    class_id = int(box.cls[0].item())
                    class_name = self.model.names[class_id]

                    # Dessiner le rectangle
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # Texte pour le label et la confiance
                    label = f"{class_name} {confidence:.2f}%"
                    cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    #Enrégistrement des informations
                    #Sauvegarde de la source
                    db = DatabaseHandler()
                    id_source = db.last_source_insert()+1
                    name_source = image_path,
                    type_source = "photo"
                    db.insert_source(id_source, name_source, type_source)
                    
                    #id de la classe
                    id_class = class_id

                    #sauvegarde de la detection
                    id_detecter = db.last_detection_insert() +1
                    time_detection = datetime.now()
                   
                    
                    db.insert_detection(id_detecter, id_class, id_source, time_detection, confidence)
                   
            # Sauvegarder l'image annotée
            output_path = os.path.splitext(image_path)[0] + '_annotated.jpg'
            cv2.imwrite(output_path, image)
            

            return results
        except IndentationError as e:
            print("Inférence a échoué.")
            print(f"Erreur: {e}")
            return None

# Exemple d'utilisation
    def inferecing_video(self, video_path: str, output_path: str):
        """
        Effectue une inférence sur une vidéo donnée et dessine des rectangles autour des objets détectés.

        Paramètres:
        video_path (str): Le chemin vers le fichier vidéo.
        output_path (str): Le chemin où sauvegarder la vidéo annotée.

        Retourne:
        None
        """
        if self.model is None:
            print("Le modèle n'est pas chargé. Veuillez charger le modèle d'abord.")
            return None

        print(f"Loading video from {video_path}...")
        try:
            # Ouvrir la vidéo
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError("La vidéo n'a pas pu être chargée. Vérifiez le chemin.")

            # Obtenir les propriétés de la vidéo
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            #sauvegarde de la source
            db = DatabaseHandler()
            id_source = db.last_source_insert()+1
            name_source = video_path,
            type_source = "video"
            db.insert_source(id_source, name_source, type_source)

            id_detecter = db.last_detection_insert()+1
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Faire l'inférence sur la frame
                results = self.model(frame)
            
                # Dessiner les résultats sur la frame
                for result in results:
                    for box in result.boxes:
                        # Extraction des coordonnées et des autres informations
                        xyxy = box.xyxy[0].cpu().numpy()
                        x1, y1, x2, y2 = map(int, xyxy)
                        confidence = box.conf[0].item() * 100  # Confiance en pourcentage
                        class_id = int(box.cls[0].item())
                        class_name = self.model.names[class_id]

                        # Dessiner le rectangle
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                        # Texte pour le label et la confiance
                        label = f"{class_name} {confidence:.2f}%"
                        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        #id de la classe
                        id_class = class_id

                        #sauvegarde de la detection
                        time_detection = datetime.now()
                        db.insert_detection(id_detecter, id_class, id_source, time_detection, confidence)
                        id_detecter +=1
                    
                # Ecrire la frame annotée dans la vidéo de sortie
                out.write(frame)

            # Libérer les ressources
            cap.release()
            out.release()
            print(f"Vidéo annotée sauvegardée à: {output_path}")
            return id_source, output_path
        except Exception as e:
            print("Inférence a échoué.")
            print(f"Erreur: {e}")
            return None


    def inferecing_camera(self, camera_index: int = 0):
        """
        Effectue une inférence en temps réel sur le flux vidéo d'une caméra.

        Paramètres:
        camera_index (int): L'index de la caméra à utiliser (par défaut 0 pour la webcam).

        Retourne:
        None
        """
        if self.model is None:
            print("Le modèle n'est pas chargé. Veuillez charger le modèle d'abord.")
            return None

        print(f"Starting video capture from camera index {camera_index}...")
        try:
            # Ouvrir la caméra
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                raise ValueError("La caméra n'a pas pu être ouverte. Vérifiez l'index de la caméra.")
            

            db = DatabaseHandler()
            id_source = db.last_source_insert()+1
            name_source = camera_index,
            type_source = "camera"
            db.insert_source(id_source, name_source, type_source)

            id_detecter = db.last_detection_insert()+1
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Erreur lors de la capture de la frame.")
                    break

                # Faire l'inférence sur la frame
                results = self.model(frame)

                # Dessiner les résultats sur la frame
                for result in results:
                    for box in result.boxes:
                        # Extraction des coordonnées et des autres informations
                        xyxy = box.xyxy[0].cpu().numpy()
                        x1, y1, x2, y2 = map(int, xyxy)
                        confidence = box.conf[0].item() * 100  # Confiance en pourcentage
                        class_id = int(box.cls[0].item())
                        class_name = self.model.names[class_id]

                        # Dessiner le rectangle
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                        # Texte pour le label et la confiance
                        label = f"{class_name} {confidence:.2f}%"
                        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        #id de la classe
                        id_class = class_id

                        #sauvegarde de la detection
                        time_detection = datetime.now()
                        db.insert_detection(id_detecter, id_class, id_source, time_detection, confidence)
                        id_detecter +=1
                # Afficher la frame annotée
                cv2.imshow('Camera Inference', frame)

                # Arrêter la capture si la touche 'q' est pressée
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Libérer les ressources
            cap.release()
            cv2.destroyAllWindows()
            print("Capture vidéo terminée.")

        except Exception as e:
            print("Inférence en temps réel a échoué.")
            print(f"Erreur: {e}")
            return None
        
    
    

