import tkinter as tk
import customtkinter as ctk
import pygame.camera
from PIL import Image, ImageTk
from ultralytics import YOLO
import numpy as np

class FullScreenApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("1400x550+0+0")

        # Créer un conteneur principal pour les frames
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Créer les deux frames
        left_frame = tk.Frame(main_frame, bg='white', width=self.winfo_screenwidth() // 3)
        left_frame.grid(row=0, column=0, sticky='nsew')

        right_frame = tk.Frame(main_frame, bg='#000')
        right_frame.grid(row=0, column=1, sticky='nsew')

        #Ajout de bouton

        ouvrir_cam = ctk.CTkButton(left_frame, text= "Ouvrir la camera",width=50, command= lambda: self.capture_video())
        ouvrir_cam.pack(pady=3)

        fermer_cam = ctk.CTkButton(left_frame, text= "Fermer la camera",width=50, command= lambda: self.quit())
        fermer_cam.pack(pady=3)


        self.camera_label = tk.Label(right_frame)
        self.camera_label.pack(fill="y", pady=10, side="right")

        self.camera_label.img_tk = None  # Initialisation de l'image à afficher

        # Configurer le comportement de redimensionnement
        main_frame.grid_columnconfigure(0, weight=1)  # 1/8 de la largeur
        main_frame.grid_columnconfigure(1, weight=7)  # 7/8 de la largeur
        main_frame.grid_rowconfigure(0, weight=1)  # Une seule ligne, étendue pour tout remplir

        # Initialiser Pygame camera
        pygame.camera.init()
        self.cam = pygame.camera.Camera(pygame.camera.list_cameras()[0])
        

        

    def capture_video(self):
        # Capturer une image de la webcam avec Pygame camera
        self.cam.start()
        img = self.cam.get_image()

        # Convertir l'image Pygame en format PIL
        img_str = pygame.image.tostring(img, "RGB", False)
        pil_img = Image.frombytes("RGB", img.get_size(), img_str)
        
        # Redimensionner l'image si nécessaire pour qu'elle s'adapte au Label
        pil_img_resized = pil_img.resize((1000, 900))  # Ajuster la taille selon vos besoins

        # Convertir l'image PIL en format utilisable par YOLO (numpy array)
        img_np = np.array(pil_img_resized)
        img_np = np.transpose(img_np, (2, 0, 1))  # Mettre les canaux en premier pour YOLO

        # Charger le modèle YOLO
        model = self.load_your_model()

        # Faire une prédiction avec YOLO
        results = model(img_np)

        print(results)
        # Traiter les résultats de la prédiction ici
        # Vous pouvez par exemple dessiner des cadres autour des objets détectés

        # Convertir l'image PIL redimensionnée en format Tkinter PhotoImage
        img_tk = ImageTk.PhotoImage(image=pil_img_resized)

        # Mettre à jour l'image dans le Label
        self.camera_label.img_tk = img_tk  # Garder une référence pour éviter la suppression par le garbage collector
        self.camera_label.config(image=img_tk)

        # Attendre 10 ms entre chaque frame (ajuster selon la fréquence d'images de la webcam)
        self.camera_label.after(10, self.capture_video)




    def quit(self):
        # Arrêter la capture de la webcam et quitter
        self.cam.stop()
        
    def load_your_model(self):
        # Ici vous devrez implémenter le chargement de votre modèle de prédiction
        # Par exemple, avec PyTorch :
        model_path = "C:/Users/zakaria.gamane/Downloads/best.pt"

        # Charger le modèle YOLO avec Ultralytics
        model = YOLO(model_path)  # Spécifiez le device selon votre configuration
        
        model.eval()  # Mettre le modèle en mode évaluation
        return model
    

if __name__ == '__main__':
    app = FullScreenApp()
    app.mainloop()
