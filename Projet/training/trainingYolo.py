

import os, shutil
from ultralytics import YOLO
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from fpdf import FPDF

#Mes classes
import Projet.dataset.preparateDataset as pD


class TrainingYolo:
    """
    Cette classe permet de faire l'entrainement d'un model YOLO et de sauvegarder le
    résultat de l'entrainement dans un dossier TRAIN_RESULT.
    """

    def __init__(self, dataset : pD) -> None:
        
        self.dataset = dataset
        self.model = None
        self.model_name = None
        self.model_path = None


    def download_model_yolo(self, model_name: str):
        """
        Télécharge le modèle YOLO spécifié et le sauvegarde dans le répertoire self.save_dir.
        """
        self.model_name = model_name
        # Télécharge et charge le modèle YOLO
        self.model = YOLO(self.model_name)
        chemin_fichier = os.path.abspath(self.model_name)
        
        fichier  = chemin_fichier+'.pt'
        repertory_path = self.dataset.train_image_path
        repertory_path = "/".join(repertory_path.split("/")[:-3])+"/"


        
        if not os.path.exists(repertory_path):
            os.makedirs(repertory_path)

        # Chemin complet vers le fichier déplacé dans le dossier de destination
        destination = os.path.join(repertory_path, os.path.basename(fichier))
        self.model_path = repertory_path+self.model_name+'.pt'

        # Déplacement du fichier vers le dossier de destination
        shutil.move(fichier, destination)

        return self

        



    def train_yolo_settings(self,dataset : pD, model_path:str, epochs : int, img_size: int, batch_size : int,
                   project_path: str, run_name : str):
        

        if self.model_path == None:
            self.model_path = model_path
                     
        self.data_path = dataset.dataset_yaml   # Chemin vers le fichier .yaml des données
        self.epochs = epochs                          # Nombre d'époques pour l'entraînement
        self.img_size = img_size                       # Taille des images d'entrée
        self.batch_size = batch_size                   # Taille de la batch pour l'entraînement
        self.project_path = project_path               # Chemin vers le répertoire de sortie du projet
        self.run_name = run_name                       # Nom du dossier pour cette exécution

        return self
    

    def train_yolo_model(self):
        """
        Méthode pour entraîner le modèle YOLOv8.
        """
        # Charger le modèle YOLOv8
        model = YOLO(self.model_path)

        # Démarrer l'entraînement
        model.train(
            data=self.data_path,
            epochs=self.epochs,
            imgsz=self.img_size,
            batch=self.batch_size,
            project=self.project_path,
            name=self.run_name
        )

        return self
        
    def train_yolo_analyser(self):
        """
        Une méthode pour analyser le résultat de l'entraînement et générer des rapports.
        """
        # Charger le modèle sauvegardé
        model = YOLO(self.save_path)

        # Évaluer le modèle sur le jeu de données de validation
        results = model.val()

        # Extraire les métriques
        precision = results['metrics']['precision']
        recall = results['metrics']['recall']
        map50 = results['metrics']['map50']
        f1 = results['metrics']['f1']
        
        # Supposons que results contient des pertes d'entraînement et de validation
        train_losses = results['train_losses']
        val_losses = results['val_losses']
        
        # Générer des graphiques de pertes
        self._plot_losses(train_losses, val_losses)

        # Générer des graphiques de précision
        self._plot_precision_recall(precision, recall, map50, f1)
        
        # Générer la matrice de confusion
        y_true = results['true_labels']
        y_pred = results['pred_labels']
        self._plot_confusion_matrix(y_true, y_pred)

        # Générer un rapport PDF avec les graphiques
        self._generate_pdf_report()


    def _plot_losses(self, train_losses, val_losses):
        """
        Génère et sauvegarde un graphique des pertes d'entraînement et de validation.

        Args:
            train_losses (list): Liste des pertes d'entraînement par époque.
            val_losses (list): Liste des pertes de validation par époque.
        """
        plt.figure()
        plt.plot(train_losses, label='Training Loss')
        plt.plot(val_losses, label='Validation Loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        plt.title('Training and Validation Loss')
        plt.savefig('losses.png')


    def _plot_precision_recall(self, precision, recall, map50, f1):
        """
        Génère et sauvegarde un graphique des métriques de précision, rappel, mAP@50, et F1 Score.

        Args:
            precision (float): Précision du modèle.
            recall (float): Rappel du modèle.
            map50 (float): Mean Average Precision à IoU=50.
            f1 (float): F1 Score du modèle.
        """
        plt.figure()
        metrics = [precision, recall, map50, f1]
        metric_names = ['Precision', 'Recall', 'mAP@50', 'F1 Score']
        plt.bar(metric_names, metrics)
        plt.ylim(0, 1)
        plt.title('Precision, Recall, mAP@50, and F1 Score')
        plt.savefig('precision_recall.png')


    def _plot_confusion_matrix(self, y_true, y_pred):
        """
        Génère et sauvegarde la matrice de confusion.

        Args:
            y_true (list): Liste des labels vrais.
            y_pred (list): Liste des labels prédits.
        """
        cm = confusion_matrix(y_true, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot(cmap=plt.cm.Blues)
        plt.title('Confusion Matrix')
        plt.savefig('confusion_matrix.png')


    def _generate_pdf_report(self):
        """
        Génère un rapport PDF contenant les graphiques des pertes, des métriques de précision/rappel,
        et de la matrice de confusion.
        """
        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="YOLOv8 Training Report", ln=True, align='C')

        # Ajouter les graphiques au PDF
        for image in ['losses.png', 'precision_recall.png', 'confusion_matrix.png']:
            pdf.add_page()
            pdf.image(image, x=10, y=10, w=190)

        # Sauvegarder le PDF
        pdf.output("training_report.pdf")
        print("Le rapport d'entraînement a été généré sous la forme de training_report.pdf")



    
