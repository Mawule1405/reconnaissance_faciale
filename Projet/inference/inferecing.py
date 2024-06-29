
from ultralytics import YOLO
import cv2
import os
from PIL import Image
from datetime import datetime
import numpy as np
import duckdb as db
import customtkinter as ctk
from tkinter import ttk

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
            #Sauvegarde de la source
            db = DatabaseHandler()
            id_source = db.last_source_insert()+1
            name_source = image_path,
            type_source = "photo"
            db.insert_source(id_source, name_source, type_source)
                    
            
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
                    
                    #id de la classe
                    id_class = class_id

                    #sauvegarde de la detection
                    id_detecter = db.last_detection_insert() +1
                    time_detection = datetime.now()
                   
                    
                    db.insert_detection(id_detecter, id_class, id_source, time_detection, confidence)
                   
            # Sauvegarder l'image annotée
            output_path = os.path.splitext(image_path)[0] + '_annotated.jpg'
            cv2.imwrite(output_path, image)
            

            return id_source, output_path
        
        except IndentationError as e:
            print("Inférence a échoué.")
            print(f"Erreur: {e}")
            return None
    def inferecing_video(self, video_path: str, progressbar: ttk.Progressbar):
        """
        Effectue une inférence sur une vidéo donnée et dessine des rectangles autour des objets détectés.
        Met à jour une barre de progression pour suivre l'avancement.

        Paramètres:
        video_path (str): Le chemin vers le fichier vidéo.
        progressbar (ttk.Progressbar): La barre de progression à mettre à jour.

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
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            output_path = os.path.splitext(video_path)[0] + '_annotated.' + video_path.split(".")[-1]
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            # Initialiser la barre de progression
            progressbar['maximum'] = frame_count
            progressbar['value'] = 0

            # Sauvegarde de la source
            db = DatabaseHandler()
            id_source = db.last_source_insert() + 1
            name_source = output_path
            type_source = "video"
            db.insert_source(id_source, name_source, type_source)

            id_detecter = db.last_detection_insert() + 1
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Faire l'inférence sur la frame
                results = self.model(frame)

                # Dessiner les résultats sur la frame
                if results:
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

                            # ID de la classe
                            id_class = class_id

                            # Sauvegarde de la détection
                            time_detection = datetime.now()
                            db.insert_detection(id_detecter, id_class, id_source, time_detection, confidence)
                            id_detecter += 1

                # Mettre à jour la barre de progression
                progressbar['value'] += 1
                progressbar.update()

                # Écrire la frame annotée dans la vidéo de sortie
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





    def inferecing_camera(self, label: ctk.CTkLabel, tree: ttk.Treeview, camera_index: int = 0,size= (200, 300)):
        """
        Effectue une inférence en temps réel sur le flux vidéo d'une caméra et affiche le résultat dans un label.

        Paramètres:
        label (ctk.CTkLabel): Le label dans lequel afficher la vidéo.
        tree (ttk.Treeview): Le treeview pour afficher les résultats.
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
            id_source = db.last_source_insert() + 1
            name_source = camera_index,
            type_source = "camera"
            db.insert_source(id_source, name_source, type_source)

            id_detecter = db.last_detection_insert() + 1
            self.camera_ouvert = True
            while self.camera_ouvert:
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
                        label_text = f"{class_name} {confidence:.2f}%"
                        cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        # id de la classe
                        id_class = class_id

                        # sauvegarde de la detection
                        time_detection = datetime.now()
                        db.insert_detection(id_detecter, id_class, id_source, time_detection, confidence)
                        id_detecter += 1

                        id_source = db.last_source_camera_insert()
                        detections = db.generate_report_camera(id_source)

                        for item in tree.get_children():
                            tree.delete(item)

                        for det in detections:
                            id = det[0]
                            nom = " ".join([det[1].split()[0].upper(), " ".join(det[1].split()[1:]).title()])
                            count = det[2]

                            tree.insert("", "end", values=(id, nom, count))

                # Convertir la frame pour l'affichage dans le label
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img_tk = ctk.CTkImage(light_image=img, size=size)
                label.configure(image=img_tk)
                label.update_idletasks()  # Assurez-vous que l'interface utilisateur est mise à jour

                # Arrêter la capture si la touche 'q' est pressée
               
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.camera_ouvert = False
                    break

            # Libérer les ressources
            cap.release()
            cv2.destroyAllWindows()
            

        except Exception as e:
            print("Inférence en temps réel a échoué.")
            print(f"Erreur: {e}")
            return None
    

