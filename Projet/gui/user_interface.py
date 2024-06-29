import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog
import tkinter as tk
from tkinter import ttk
import cv2 , os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime


from Projet.inference.inferecing import Inferencing
from Projet.database.databaseHandler import DatabaseHandler
from Projet.gui.bulles import ToolTip

class UserInterface:
    _couleur_menu_bar = "#e5d37f"
    _couleur_bouton_menu = "#fff"

    def __init__(self, model_path):
        self.model = model_path
        self.fen = ctk.CTk()
        self.bar_de_menu = None
        self.conteneur_principal = ctk.CTkFrame(self.fen)
        self.top = None
        self.cap = None
        self.camera_ouvert = False

    
    def mise_en_pause(self):
        self.fen.mainloop()


    def configuration(self):
        # Récupère la largeur et la hauteur de l'écran
        self.screen_width = self.fen.winfo_screenwidth()
        self.screen_height = self.fen.winfo_screenheight()

        # Définir la largeur et la hauteur de la fenêtre (95% de la taille de l'écran)
        window_width = int(self.screen_width * 0.95)
        window_height = int(self.screen_height * 0.95)

        # Calculer la position pour centrer la fenêtre
        position_x = (self.screen_width - window_width) // 2
        position_y = (self.screen_height - window_height) // 2

        # Appliquer les dimensions et la position à la fenêtre
        self.fen.title("Application de reconnaissance faciale")
        self.fen.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        self.fen.configure(fg_color="#fff")

        # Ajouter un binding pour la touche 'q'
        self.fen.bind('<q>', self.stop_camera)

        self.fen.protocol("WM_DELETE_WINDOW", self.on_closing)


    def stop_camera(self, event=None):
        """
        Arrête la capture de la caméra.
        """
        print("Arrêt de la capture vidéo demandé.")
        self.camera_ouvert = False


    def on_closing(self):
        """
        Gestion de la fermeture de l'application.
        """
        self.stop_camera()
        self.fen.destroy()


    def _switch_page(self, frame, page):
        for widget in frame.winfo_children():
            widget.destroy()
        page()

    def add_menu_bar(self):
        self.bar_de_menu = ctk.CTkFrame(self.fen, height= 25, fg_color="#eee", corner_radius=0, border_width=2)
        self.bar_de_menu.pack(side= "top", fill= "x")

        #Placement du bouton pour réaliser l'inférence sur les photos
        
        home_button = ctk.CTkButton(master=self.bar_de_menu, text="", height=30, width=35,
            command=lambda: self._switch_page(self.conteneur_principal, self.add_zone_affiche), fg_color=self._couleur_bouton_menu, hover_color="#888",
            font=("Arial", 12), border_width=0, image=self._image_button("icons/home.png")
        )
        home_button.pack(side="left", padx=5, pady=5)
        ToolTip(home_button, "Page d'accueil")
        
        #Placement du bouton pour réaliser l'inférence sur les photos
        
        photo_button = ctk.CTkButton(master=self.bar_de_menu, text="", height=30,width=35,
            command=lambda: self._switch_page(self.conteneur_principal, self.add_zone_affiche_photo),fg_color=self._couleur_bouton_menu, hover_color="#888", font=("Arial", 12),
            border_width=0,image=self._image_button("icons/photo.png")
        )
        photo_button.pack(side="left", padx=5, pady=5)
        ToolTip(photo_button, "Effectué de l'inférence sur les images")


        # Placement du bouton d'inférence sur les vidéos
        
        video_button = ctk.CTkButton(master=self.bar_de_menu,text="",height=30,
            width=35,
            command=lambda: self._switch_page(self.conteneur_principal, self.add_zone_affiche_video),fg_color=self._couleur_bouton_menu,hover_color="#888",font=("Arial", 12),
            border_width=0,image= self._image_button("icons/video.png")
        )
        video_button.pack(side="left", padx=5, pady=5)
        ToolTip(video_button, "Effectué de l'inférence sur les vidéos")

        # Placement du bouton d'inférence sur les vidéos
        
        video_button = ctk.CTkButton(master=self.bar_de_menu,text="",height=30,
            width=35,
            command=lambda:self._switch_page(self.conteneur_principal, self.add_zone_affiche_camera), fg_color=self._couleur_bouton_menu,hover_color="#888",font=("Arial", 12),
            border_width=0,image= self._image_button("icons/camera.png")
        )
        video_button.pack(side="left", padx=5, pady=5)
        ToolTip(video_button, "Effectué de l'inférence sur les cameras")


    ################################################################################
    ##########################GESTION DE LA PAGE D'ACCUEIL##########################

    def add_zone_affiche(self):
        self.conteneur_principal.destroy()
        #Le conceneur principal
        self.conteneur_principal = ctk.CTkFrame(self.fen)
        self.conteneur_principal.pack(fill= "both", padx=2, pady=2)

        #conteneur d'inférence
        self.inference_conteneur = ctk.CTkFrame(self.conteneur_principal, width= self.screen_width*0.5,
                                    fg_color= "transparent", border_width=1, corner_radius=0)
        self.inference_conteneur.pack(side="left", fill="y", padx=2, pady=2)


        #conteneur résultat
        self.inference_resultat = ctk.CTkFrame(self.conteneur_principal, width= self.screen_width*0.5,
                                    fg_color="transparent", border_width=1, corner_radius=0)
        self.inference_resultat.pack(side="left", fill="y", padx=2, pady=2)

        #titré chaque partie par un label
        ctk.CTkLabel(self.inference_resultat, text="LISTE DES ANCIENNES SOURCES", font=("Garamone", 30, "bold"), 
                    text_color= "#000").pack()
        
        #Définition de l'écran d'affichage
        self.affichage_label = ctk.CTkLabel(self.inference_conteneur, text="Image par défaut", )
        self.affichage_label.pack(padx=5, pady=5)

        image_par_defaut = Image.open("Projet/image/ecran_par_defaut.jpg")
        image_converte_path = ctk.CTkImage(light_image=image_par_defaut, dark_image=image_par_defaut, 
                                           size=(self.screen_width//2, self.screen_height-100))
        self.affichage_label.configure(image = image_converte_path)

        #Définition de la zone d'affichage des résulats
        db = DatabaseHandler()
        sources = db.all_sources()

        #Définition d'un scrollFrame
        zone_bilan = ctk.CTkScrollableFrame(self.inference_resultat, width=self.screen_width//2, height=self.screen_height-30)
        zone_bilan.pack(padx=2, pady=2)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))  # Font size and bold for headings
        style.configure("Treeview", rowheight=35, font=("Arial", 12))  # Font size for rows and row height

        #importation des sources utilisées pour la réalisation de l'inférnce
        self.liste_dectetion = ttk.Treeview(zone_bilan, columns=["numero", "source", "type"], show="headings", height=len(sources))
        self.liste_dectetion.pack(padx=2, pady=2)

        # Configurer les colonnes
        self.liste_dectetion.heading("numero", text="N°")
        self.liste_dectetion.column("numero", width=100)

        self.liste_dectetion.heading("source", text="Nom")
        self.liste_dectetion.column("source", width=700)


        self.liste_dectetion.heading("type", text="Type")
        self.liste_dectetion.column("type", width=200)

        for source in sources:
            id_source= source[0]
            name_source = source[1] if source[1][0] !="[" and source[1][-1]!="]" else source[1][1:-1]
            type_source = source[2]

            self.liste_dectetion.insert("", "end",values = (id_source, name_source, type_source))


        # Lier l'événement de clic à la fonction on_row_click
        self.liste_dectetion.bind("<Double-1>", self.on_row_click)


    def on_row_click(self, event):
        # Récupérer l'élément cliqué
        item = self.liste_dectetion.selection()[0]
        values = self.liste_dectetion.item(item, "values")

        # Créer une nouvelle fenêtre toplevel
        if self.top :
            self.top.destroy()

        self.top = ctk.CTkToplevel(self.fen)
        self.top.title("Détails de la ligne")
        self.top.geometry("600x500")  # Ajuster la taille si nécessaire
        self.top.attributes("-topmost", True)

        # Ajouter des labels pour afficher les informations
        # Extraire les informations spécifiques de la ligne cliquée
        numero, source, type_source = values
        numero = int(numero)

        ctk.CTkLabel(self.top, text="BILAN DE L'INFERENCE", font=("Garamone", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(self.top, text=f"ID: {numero}       TYPE: {type_source}", font=("Garamone", 12, "bold")).pack(pady=2)
        zone_vue = ctk.CTkFrame(self.top, width=600, height=400, fg_color="transparent", corner_radius=0)
        zone_vue.pack(padx=5, pady=5, fill="both", expand=True)

        # Label de visualisation
        visualisation = ctk.CTkLabel(zone_vue, text="")
        visualisation.pack(padx=2, pady=2, fill="both", expand=True)

        self.view = visualisation
        
        

        # Appeler la fonction handle_media pour afficher le contenu
        self.handle_media(type_source.lower(),source ,visualisation, numero)

    
    def handle_media(self, media_type, media_path, label: ctk.CTkLabel, numero : int):

        if media_type == "photo":
            self.show_photo(label,  media_path)
        elif media_type == "video":
            self.play_video(label,  media_path)
        elif media_type == "camera":
            self.show_camera(numero)

    def show_photo(self, label: ctk.CTkLabel, media_path):
        # Charger et afficher l'image (assurez-vous de remplacer le chemin par le vôtre
        try:
            media_path = os.path.splitext(media_path)[0] + '_annotated.jpg'
            img = Image.open(media_path)  # Remplacer par le chemin de l'image
            img_tk = ctk.CTkImage(light_image= img, dark_image= img, size = (400, 350))
            label.configure(image=img_tk)
            ttk.Button(self.top, text="Fermer", command= lambda: self.top.destroy()).pack(pady=10)
        except:
            self.top.destroy()
            messagebox.showerror("Photo introuvable", "La photo sélectionné est introuvable.")
        

    def play_video(self, label , media_path, size=(400, 350)):
        try:
            if self.cap is not None:
                self.cap.release()
            self.cap = cv2.VideoCapture(media_path)  # Remplacer par le chemin de la vidéo
            self.video_running = True

            #les bouthons
            les_boutons = ctk.CTkFrame(self.top, fg_color="transparent", height=35)
            les_boutons.pack( pady=5)
            #bouton pause
            btn_pause = ctk.CTkButton(les_boutons,image= self._image_button("icons/pause.png"), text=""  , 
                                        fg_color="transparent", hover_color="#888", width=30, height=30,command=self.pause_video)
            btn_pause.pack(pady=10,padx=50, side="left")
            ToolTip(btn_pause, "Mettre la video \nen pause")


            btn_continue = ctk.CTkButton(les_boutons,image= self._image_button("icons/play.png"), text=""  , 
                                        fg_color="transparent", hover_color="#888", width=30, height=30,
                                        command=self.continue_video(label))
            btn_continue.pack(pady=10,padx=50, side="left")
            ToolTip(btn_continue, "Cntinuer la vidéo")
            #bouton stop
            btn_stop = ctk.CTkButton(les_boutons,image= self._image_button("icons/stop.png"), text="" , 
                                        fg_color="transparent", hover_color="#888", width=30, height=30,command=self.stop_video)
            btn_stop.pack(pady=10,padx=50, side="left")
            ToolTip(btn_stop, "Stopper la vidéo")

            self.update_video_frame(label, size)
        except Exception as e:
            self.top.destroy()
            messagebox.showerror("Video introuvable", f"la vidéo sélectionnée est introuvable.")


    def update_video_frame(self, label: ctk.CTkLabel,size=(400, 350)):
        if self.video_running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img_tk = ctk.CTkImage(img, size=size)
                label.configure(image=img_tk)
                self._update_id = self.top.after(10, self.update_video_frame, label)  # Store the after ID
            else:
                self.stop_video()

    def pause_video(self):
        self.video_running = False

    def continue_video(self, label: ctk.CTkLabel):
        self.video_running = True
        self.update_video_frame(label)
    

    def stop_video(self):
        self.video_running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if hasattr(self, '_update_id'):
            self.top.after_cancel(self._update_id)


    def show_camera(self, numero: int):
        try:
            # Cacher le label actuel
            for i in self.top.winfo_children():
                i.destroy()

            # Récupérer les données de la base de données
            db = DatabaseHandler()
            res = db.generate_report_camera(numero)

            # Extraire les noms et les comptes des résultats
            names = [r[1] for r in res]
            counts = [int(r[2]) for r in res]

            
            # Créer le diagramme en bâtons seulement si les données existent
            if names and counts:
                try:
                    self.top.configure(height=600)
                    ctk.CTkLabel(self.top, text= "BILAN DE FREQUENTATION", font=("Garamone", 12, "bold"), 
                                 fg_color="transparent").pack()

                    fig, ax = plt.subplots()
                    ax.bar(names, counts)
                    ax.set_xlabel('Nom')
                    ax.set_ylabel('Nombre')
                    ax.set_title('Diagramme en bâtons')
                    ax.grid(True, linestyle='--', linewidth=0.2)

                    # Afficher le graphique dans la fenêtre Toplevel
                    canvas = FigureCanvasTkAgg(fig, master=self.top)
                    canvas.draw()
                    canvas.get_tk_widget().pack(padx=20, pady=20, fill="both", expand=True)
                    
                    ttk.Button(self.top, text="Fermer").pack(pady=10)
                except Exception as e:
                    self.top.destroy()
                    messagebox.showerror("Video introuvable", f"la vidéo sélectionnée est introuvable. {e}")
            else:
                self.top.destroy()
                messagebox.showerror("Video introuvable", f"la vidéo sélectionnée est introuvable.")

        except Exception as e:
                self.top.destroy()
                messagebox.showerror("Video introuvable", f"la vidéo sélectionnée est introuvable.")


 
    def _image_button(self, path):
        img = Image.open(path)
        img_ctk = ctk.CTkImage(img, size=(24,24))
        return img_ctk


    ###########################################################################
    ####################### GESTION DE LA PAGE D'INFERENCE SUR PHOTO #########

    
    def add_zone_affiche_photo(self):
        self.conteneur_principal.destroy()
        #Le conceneur principal
        self.conteneur_principal = ctk.CTkFrame(self.fen)
        self.conteneur_principal.pack(fill= "both", padx=2, pady=2)

        #conteneur d'inférence
        self.inference_conteneur = ctk.CTkFrame(self.conteneur_principal, width= self.screen_width*0.5,
                                    fg_color= "transparent", border_width=1, corner_radius=0)
        self.inference_conteneur.pack(side="left", fill="y", padx=2, pady=2)


        #conteneur résultat
        self.inference_resultat = ctk.CTkFrame(self.conteneur_principal, width= self.screen_width*0.5,
                                    fg_color="transparent", border_width=1, corner_radius=0)
        self.inference_resultat.pack(side="left", fill="y", padx=2, pady=2)

        #titré chaque partie par un label

        ctk.CTkLabel(self.inference_conteneur, text="VISUALISATION DE LA SOURCE: PHOTO", font=("Garamone", 30, "bold"), 
                    text_color= "#000").pack()
        
        inference_title_lb=ctk.CTkLabel(self.inference_resultat, text="BILAN DE LA DERNIERE INFERENCE", font=("Garamone", 30, "bold"), 
                    text_color= "#000")
        inference_title_lb.pack()
        
        #Définition de l'écran d'affichage
        self.affichage_label = ctk.CTkLabel(self.inference_conteneur, text="", )
        self.affichage_label.pack(padx=5, pady=5)

        db = DatabaseHandler()
        id_source = db.last_source_photo_insert()
        source = db.select_one_source(id_source)[0]
     
        
        s_path = source[1] if source[1][0] !="[" and source[1][-1]!="]" else source[1][1:-1]
        
        detections = db.generate_report_photo(id_source)


        try:
            os.path.splitext(s_path)[0] + '_annotated.jpg'
            image_par_defaut = Image.open(os.path.splitext(s_path)[0] + '_annotated.jpg')
            image_converte_path = ctk.CTkImage(light_image=image_par_defaut, dark_image=image_par_defaut, 
                                            size=(self.screen_width//2, self.screen_height-100))
            self.affichage_label.configure(image = image_converte_path)

        except:

            image_par_defaut = Image.open("Projet/image/ecran_par_defaut.jpg")
            image_converte_path = ctk.CTkImage(light_image=image_par_defaut, dark_image=image_par_defaut, 
                                            size=(self.screen_width//2, self.screen_height-100))
            self.affichage_label.configure(image = image_converte_path)

        #Définition de la zone d'affichage des résulats
       

        #Définition d'un scrollFrame
        zone_bilan = ctk.CTkScrollableFrame(self.inference_resultat, width=self.screen_width//2, height=self.screen_height-300,
                                            fg_color="transparent")
        zone_bilan.pack(padx=2, pady=2)

        #les boutons de chargements des images sur lesquels vont porter l'inférence
        zone_boutons = ctk.CTkFrame(self.inference_resultat, width=self.screen_width//2, height=50, fg_color="transparent")
        zone_boutons.pack(side="top", pady=30, padx=2)

        choisir_btn = ctk.CTkButton(zone_boutons, text="", hover_color="#888", fg_color="transparent", width=30,
                                    image=self._image_button("icons/choisir.png"),
                                    command = lambda: choisie_photo(photo_choisie))
        choisir_btn.pack(padx=20, pady=5, side="left")
        ToolTip(choisir_btn, "Choisir une photo pour l'inférence")

        inference_btn = ctk.CTkButton(zone_boutons, text="inference", hover_color="#888", fg_color="transparent", width=30,
                                      image=self._image_button("icons/inference.png"),
                                      command= lambda: realise_inference(photo_choisie))
        inference_btn.pack(padx=20, pady=5, side="left")
        ToolTip(inference_btn, "Réaliser une inférence")

        
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))  # Font size and bold for headings
        style.configure("Treeview", rowheight=35, font=("Arial", 12))  # Font size for rows and row height

        #importation des sources utilisées pour la réalisation de l'inférnce
        self.liste_dectetion = ttk.Treeview(zone_bilan, columns=["numero", "Nom", "Pourcentage", "Date", "Heure"], show="headings", height=len(detections))
        self.liste_dectetion.pack(padx=2, pady=2)

        # Configurer les colonnes
        self.liste_dectetion.heading("numero", text="N°")
        self.liste_dectetion.column("numero", width=100)

        self.liste_dectetion.heading("Nom", text="Nom")
        self.liste_dectetion.column("Nom", width=400)


        self.liste_dectetion.heading("Pourcentage", text="Pourcentage")
        self.liste_dectetion.column("Pourcentage", width=200)

        self.liste_dectetion.heading("Date", text="Date")
        self.liste_dectetion.column("Date", width=200)

        self.liste_dectetion.heading("Heure", text="Heure")
        self.liste_dectetion.column("Heure", width=200)

        for det in detections:
            id = det[0]
            nom = " ".join([det[1].split()[0].upper(), " ".join(det[1].split()[1:]).title()])
            conf = float(det[2])
            date_heure = det[3]
            date = datetime.strftime(date_heure, "%d-%m-%Y")
            heure = datetime.strftime(date_heure, "%H:%M-%S")


            self.liste_dectetion.insert("", "end",values = (id, nom, f"{conf:.2f}", date, heure))


        #les foncions de gestions des photos
        photo_choisie=[]

        def choisie_photo(photo_choisie: list):
            option = [("Image files", "*.jpg *.jpeg *.png")]
            choisir = filedialog.askopenfilename(filetypes=option)

            if choisir:
                photo_choisie.append(choisir)
                image_par_defaut = Image.open(choisir)
                image_converte_path = ctk.CTkImage(light_image=image_par_defaut, dark_image=image_par_defaut, 
                                                size=(self.screen_width//2, self.screen_height-100))
                self.affichage_label.configure(image = image_converte_path)

                
            else:
                messagebox.showinfo("Choix d'une photo", "Aucune photo n'a été sélectionnée")


        def realise_inference(photo_choisie: list):

            if len(photo_choisie)==0:
                messagebox.showwarning("Réalisation de l'inférence", "Aucune photo n'a été sélectionneé ")

            else:

                try:

                    inf = Inferencing(self.model)
                    inf.charging_model()
                    id, path =  inf.inferecing_photo(photo_choisie[0])
                    photo_choisie=[]
                    image_par_defaut = Image.open(path)
                    image_converte_path = ctk.CTkImage(light_image=image_par_defaut, dark_image=image_par_defaut, 
                                                    size=(self.screen_width//2, self.screen_height-100))
                    self.affichage_label.configure(image = image_converte_path)

                    db= DatabaseHandler()

                    resultats = db.generate_report_photo(id)

                    for item in self.liste_dectetion.get_children():
                        self.liste_dectetion.delete(item)


                    for det in resultats:
                        id = det[0]
                        nom = " ".join([det[1].split()[0].upper(), " ".join(det[1].split()[1:]).title()])
                        conf = float(det[2])
                        date_heure = det[3]
                        date = datetime.strftime(date_heure, "%d-%m-%Y")
                        heure = datetime.strftime(date_heure, "%H:%M-%S")


                        self.liste_dectetion.insert("", "end",values = (id, nom, f"{conf:.2f}", date, heure))

                
                except:
                    messagebox.showerror("Réalisation de l'inférence", "Un problème s'est apparue lors de l'inférence.\n Veuillez réessayez")
        


    ###########################################################################
    ####################### GESTION DE LA PAGE D'INFERENCE SUR CAMERA #########

    
    def add_zone_affiche_video(self):
        self.conteneur_principal.destroy()
        #Le conceneur principal
        self.conteneur_principal = ctk.CTkFrame(self.fen)
        self.conteneur_principal.pack(fill= "both", padx=2, pady=2)

        #conteneur d'inférence
        self.inference_conteneur = ctk.CTkFrame(self.conteneur_principal, width= self.screen_width*0.5,
                                    fg_color= "transparent", border_width=1, corner_radius=0)
        self.inference_conteneur.pack(side="left", fill="y", padx=2, pady=2)


        #conteneur résultat
        self.inference_resultat = ctk.CTkFrame(self.conteneur_principal, width= self.screen_width*0.5,
                                    fg_color="transparent", border_width=1, corner_radius=0)
        self.inference_resultat.pack(side="left", fill="y", padx=2, pady=2)

        #titré chaque partie par un label

        ctk.CTkLabel(self.inference_conteneur, text="VISUALISATION DE LA SOURCE: VIDEO", font=("Garamone", 30, "bold"), 
                    text_color= "#000").pack()
        
        inference_title_lb=ctk.CTkLabel(self.inference_resultat, text="BILAN DE LA DERNIERE INFERENCE", font=("Garamone", 30, "bold"), 
                    text_color= "#000")
        inference_title_lb.pack()
        
        #Définition de l'écran d'affichage
        self.affichage_label = ctk.CTkLabel(self.inference_conteneur, text="", )
        self.affichage_label.pack(padx=5, pady=5)

        db = DatabaseHandler()
        id_source = db.last_source_video_insert()
        source = db.select_one_source(id_source)[0]
     
        
        s_path = source[1] if source[1][0] !="[" and source[1][-1]!="]" else source[1][1:-1]
        
        detections = db.generate_report_video(id_source)


        try:

            self.play_video_2(self.affichage_label, s_path)

        except Exception as e:

            image_par_defaut = Image.open("Projet/image/ecran_par_defaut.jpg")
            image_converte_path = ctk.CTkImage(light_image=image_par_defaut, dark_image=image_par_defaut,
                                            size=(self.screen_width//2, self.screen_height-100))
            self.affichage_label.configure(image = image_converte_path,  text=f"{e}")

        #Définition de la zone d'affichage des résulats
       

        #Définition d'un scrollFrame
        zone_bilan = ctk.CTkScrollableFrame(self.inference_resultat, width=self.screen_width//2, height=self.screen_height-300,
                                            fg_color="transparent")
        zone_bilan.pack(padx=2, pady=2)

        #La bar de progression
        progress_bar = ttk.Progressbar(self.inference_resultat, length=self.screen_width//2)
        progress_bar.pack(side="top", pady=10, padx=2)

        #les boutons de chargements des images sur lesquels vont porter l'inférence
        zone_boutons = ctk.CTkFrame(self.inference_resultat, width=self.screen_width//2, height=50, fg_color="transparent")
        zone_boutons.pack(side="top", pady=10, padx=2)

        choisir_btn = ctk.CTkButton(zone_boutons, text="", hover_color="#888", fg_color="transparent", width=30,
                                    image=self._image_button("icons/choisir.png"), command = lambda: choisie_photo(photo_choisie))
        choisir_btn.pack(padx=20, pady=5, side="left")
        ToolTip(choisir_btn, "Choisir une vidéo pour l'inférence")

        inference_btn = ctk.CTkButton(zone_boutons, text="", hover_color="#888", fg_color="transparent", width=30,
                                      image=self._image_button("icons/inference.png"), command= lambda: realise_inference(photo_choisie,self.affichage_label, progress_bar))
        inference_btn.pack(padx=20, pady=5, side="left")
        ToolTip(inference_btn, "Réaliser une inférence")

        arret_btn = ctk.CTkButton(zone_boutons, text="r", hover_color="#888", fg_color="transparent", width=30,
                                  image=self._image_button("icons/stop.png"),command= lambda: self.stop_video_2())
        arret_btn.pack(padx=20, pady=5, side="left")
        ToolTip(arret_btn, "Arrêter la vidéo")


        
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))  # Font size and bold for headings
        style.configure("Treeview", rowheight=35, font=("Arial", 12))  # Font size for rows and row height

        #importation des sources utilisées pour la réalisation de l'inférnce
        self.liste_dectetion = ttk.Treeview(zone_bilan, columns=["numero", "Nom", "Nombre"], show="headings", height=len(detections))
        self.liste_dectetion.pack(padx=2, pady=2)

        # Configurer les colonnes
        self.liste_dectetion.heading("numero", text="N°")
        self.liste_dectetion.column("numero", width=100)

        self.liste_dectetion.heading("Nom", text="Nom")
        self.liste_dectetion.column("Nom", width=600)


        self.liste_dectetion.heading("Nombre", text="Nombre")
        self.liste_dectetion.column("Nombre", width=200)

        
        for det in detections:
            id = det[0]
            nom = " ".join([det[1].split("_")[0].upper(), " ".join(det[1].split("_")[1:]).title()])
            nbre = det[2]
        
            self.liste_dectetion.insert("", "end",values = (id, nom, nbre))


        #les foncions de gestions des photos
        photo_choisie=[]

        def choisie_photo(photo_choisie: list):
            option = [("Image files", "*.avi *.mp4 *.mkw")]
            choisir = filedialog.askopenfilename(filetypes=option)

            try:
                if choisir:
                    photo_choisie.append(choisir)
                    
                    self.play_video_2(self.affichage_label, choisir)

                    
                else:
                    messagebox.showinfo("Choix d'une photo", "Aucune photo n'a été sélectionnée")

            except Exception as e:
                    messagebox.showinfo("Choix d'une photo", f"Aucune photo n'a été sélectionnée {e}")


        def realise_inference(photo_choisie: list, ecran:ctk.CTkLabel , progress : ttk.Progressbar):

            if len(photo_choisie)==0:
                messagebox.showwarning("Réalisation de l'inférence", "Aucune photo n'a été sélectionneé ")

            else:

                try:

                    inf = Inferencing(self.model)
                    inf.charging_model()
                    id, path =  inf.inferecing_video(photo_choisie[0],  progress )
                    photo_choisie=[]
                 

                    db= DatabaseHandler()
                    id= db.last_source_insert()

                    resultats = db.generate_report_photo(id)

                    for item in self.liste_dectetion.get_children():
                        self.liste_dectetion.delete(item)

                    for det in resultats:
                        id = det[0]
                        nom = " ".join([det[1].split()[0].upper(), " ".join(det[1].split()[1:]).title()])
                        conf = float(det[2])
                        date_heure = det[3]
                        date = datetime.strftime(date_heure, "%d-%m-%Y")
                        heure = datetime.strftime(date_heure, "%H:%M-%S")


                        self.liste_dectetion.insert("", "end",values = (id, nom, f"{conf:.2f}", date, heure))

                    self.play_video_2(ecran, path)

                
                except:
                    messagebox.showerror("Réalisation de l'inférence", "Un problème s'est apparue lors de l'inférence.\n Veuillez réessayez")
        

    def play_video_2(self, label , media_path ):

        size=(self.screen_width//2, self.screen_height-100)
        
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(media_path)  # Remplacer par le chemin de la vidéo
        self.video_running = True

        self.update_video_frame_2(label, size)


    
    def update_video_frame_2(self, label: ctk.CTkLabel,size=(400, 350)):

        size=(self.screen_width//2, self.screen_height-100)

        if self.video_running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img_tk = ctk.CTkImage(img, size=size)
                label.configure(image=img_tk)
                self._update_id = self.inference_conteneur.after(10, self.update_video_frame_2, label)  # Store the after ID
            else:
                self.stop_video_2()
     
    
    def stop_video_2(self):
        self.video_running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if hasattr(self, '_update_id'):
            self.inference_conteneur.after_cancel(self._update_id)




    
    ###########################################################################
    #######################          GESTION DE CAMERA                #########

    
    def add_zone_affiche_camera(self):
        self.conteneur_principal.destroy()
        #Le conceneur principal
        self.conteneur_principal = ctk.CTkFrame(self.fen)
        self.conteneur_principal.pack(fill= "both", padx=2, pady=2)

        #conteneur d'inférence
        self.inference_conteneur = ctk.CTkFrame(self.conteneur_principal, width= self.screen_width*0.5,
                                    fg_color= "transparent", border_width=1, corner_radius=0)
        self.inference_conteneur.pack(side="left", fill="y", padx=2, pady=2)


        #conteneur résultat
        self.inference_resultat = ctk.CTkFrame(self.conteneur_principal, width= self.screen_width*0.5,
                                    fg_color="transparent", border_width=1, corner_radius=0)
        self.inference_resultat.pack(side="left", fill="y", padx=2, pady=2)

        #titré chaque partie par un label

        ctk.CTkLabel(self.inference_conteneur, text="VISUALISATION DE LA SOURCE: CAMERA", font=("Garamone", 30, "bold"), 
                    text_color= "#000").pack()
        
        inference_title_lb=ctk.CTkLabel(self.inference_resultat, text="BILAN DE LA DERNIERE INFERENCE", font=("Garamone", 30, "bold"), 
                    text_color= "#000")
        inference_title_lb.pack()
        
        #Définition de l'écran d'affichage
        self.affichage_label = ctk.CTkLabel(self.inference_conteneur, text="", )
        self.affichage_label.pack(padx=5, pady=5)

        db = DatabaseHandler()
        id_source = db.last_source_camera_insert()
        detections = db.generate_report_camera(id_source)

        image_par_defaut = Image.open("Projet/image/ecran_par_defaut.jpg")
        image_converte_path = ctk.CTkImage(light_image=image_par_defaut, dark_image=image_par_defaut, 
                                        size=(self.screen_width//2, self.screen_height-100))
        self.affichage_label.configure(image = image_converte_path)


        #Définition d'un scrollFrame
        zone_bilan = ctk.CTkScrollableFrame(self.inference_resultat, width=self.screen_width//2, height=self.screen_height-800,
                                            fg_color="transparent")
        zone_bilan.pack(padx=2, pady=2)

        #Définition de la zone d'affichage graphique du bilan
        zone_bilan_graphique = ctk.CTkFrame(self.inference_resultat, width=self.screen_width//2, height=130, fg_color="transparent")
        zone_bilan_graphique.pack(side="top", pady=5, padx=2)


        #les boutons de chargements des images sur lesquels vont porter l'inférence
        zone_boutons = ctk.CTkFrame(self.inference_resultat, width=self.screen_width//2, height=50, fg_color="transparent")
        zone_boutons.pack(side="top", pady=5, padx=2)

        choisir_btn = ctk.CTkButton(zone_boutons, text="", hover_color="#888", fg_color="transparent", width=30,
                                    image=self._image_button("icons/inference.png") ,
                                    command = lambda: open_camera(zone_bilan_graphique) )
        choisir_btn.pack(padx=20, pady=5, side="left")
        ToolTip(choisir_btn, "Activer la caméra")

        inference_btn = ctk.CTkButton(zone_boutons, text="",  hover_color="#888", fg_color="transparent", width=30,
                                      image=self._image_button("icons/stop.png"),
                                      command= lambda: self.stop_camera())
        inference_btn.pack(padx=20, pady=5, side="left")
        ToolTip(inference_btn, "Stopper la caméra")

        
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))  # Font size and bold for headings
        style.configure("Treeview", rowheight=35, font=("Arial", 12))  # Font size for rows and row height

        #importation des sources utilisées pour la réalisation de l'inférnce
        self.liste_dectetion = ttk.Treeview(zone_bilan, columns=["numero", "Nom", "Nombre"], show="headings", height=len(detections))
        self.liste_dectetion.pack(padx=2, pady=2)

        # Configurer les colonnes
        self.liste_dectetion.heading("numero", text="N°")
        self.liste_dectetion.column("numero", width=100)

        self.liste_dectetion.heading("Nom", text="Nom")
        self.liste_dectetion.column("Nom", width=700)


        self.liste_dectetion.heading("Nombre", text="Nombre de fréquentation")
        self.liste_dectetion.column("Nombre", width=300)

       

        for det in detections:
            id = det[0]
            nom = " ".join([det[1].split("_")[0].upper(), " ".join(det[1].split("_")[1:]).title()])
            count = det[2]

            self.liste_dectetion.insert("", "end", values= (id, nom, count))
            
        self.graphique_bilan_camera(zone_bilan_graphique,0)

        #Dictionnaire pour concerver le model
        
        def open_camera(frame: ctk.CTkFrame):
            """
                Ouvrir la caméra (le webcame par défaut)

            """

            model = Inferencing(self.model)
            model.charging_model()  #chargement du modèle
            size = (self.screen_width//2, self. screen_height-100)
           
            self.camera_ouvert = True
            model.inferecing_camera(self.affichage_label, self.liste_dectetion, 0,size)

            #représentation graphique du résultat

            self.graphique_bilan_camera(frame, 0)

            
        



    def graphique_bilan_camera(self, frame: ctk.CTkFrame, numero):
        # Clear the existing widgets in the frame
        for widget in frame.winfo_children():
            widget.destroy()

        # Initialize database handler and fetch data
        db = DatabaseHandler()
        try:
            numero = db.last_source_camera_insert()
            res = db.generate_report_camera(numero)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to fetch data from the database. {e}")
            return

        # Extract names and counts from the results
        try:
            names = [r[1] for r in res]
            counts = [int(r[2]) for r in res]
        except Exception as e:
            messagebox.showerror("Data Processing Error", f"Failed to process data. {e}")
            return

        # Check if we have valid data
        if not names or not counts:
            messagebox.showerror("No Data", "No valid data available to plot.")
            return
        
        else:

            # Create the figure and two subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))  # Adjust figsize as needed
            
            try:
                # Bar chart on the left
                ax1.bar(names, counts)
                ax1.set_xlabel('Nom')
                ax1.set_ylabel('Nombre')
                ax1.set_title('Diagramme en bâtons')
                ax1.grid(True, linestyle='--', linewidth=0.2)

                # Pie chart on the right
                ax2.pie(counts, labels=names, autopct='%1.1f%%', startangle=140)
                ax2.set_title('Diagramme circulaire')

                # Adjust the layout to make sure subplots fit into the figure area
                fig.tight_layout()


                # Embed the plot in the Tkinter frame
                canvas = FigureCanvasTkAgg(fig, master=frame)
                canvas.draw()
                canvas.get_tk_widget().pack(padx=5, pady=5, fill="both", expand=True)
                
            except Exception as e:
                messagebox.showerror("Plotting Error", f"An error occurred while plotting the data. {e}")



        





        







        

        