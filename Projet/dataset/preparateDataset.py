"""
Class: preparateDataset
"""
import os, zipfile, shutil, random
from PIL import Image
import yaml

class PreparateDatasetYolo:

    def __init__(self, datatset_path):
        self.dataset_path     = datatset_path
        self.train_image_path = datatset_path[: -4]+"/images/train"
        self.train_label_path = datatset_path[: -4]+'/labels/train'
        self.val_image_path   = datatset_path[: -4]+"/images/val" 
        self.val_label_path   = datatset_path[: -4]+'/labels/val'
        self.classes_txt = datatset_path[: -4]+"/classes.txt"
        self.dataset_yaml = datatset_path[: -4]+"/dataset.yaml"


    def un_zip_dataset(self):
        """
        Décompresse un fichier .zip et place les fichiers dans un répertoire portant le nom du fichier .zip (sans extension).

        :param zip_file_path: Chemin vers le fichier .zip à décompresser.
        """
        zip_file_path = self.dataset_path
        # Vérifier si le fichier .zip existe
        if not os.path.exists(zip_file_path):
            raise FileNotFoundError(f"Le fichier {zip_file_path} n'existe pas.")

        # Extraire le nom de base du fichier .zip (sans extension)
        base_name = os.path.basename(zip_file_path)
        folder_name = os.path.splitext(base_name)[0]

        # Déterminer le chemin du répertoire cible
        target_folder = os.path.join(os.path.dirname(zip_file_path), folder_name)

        # Sauvegarder le chemin du dataset
        self.dataset_path = target_folder

        # Créer le répertoire cible si ce n'est pas déjà fait
        os.makedirs(target_folder, exist_ok=True)

        # Décompresser le fichier .zip dans un répertoire temporaire
        temp_extract_path = os.path.join(target_folder, 'temp')
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_path)

        # Déplacer les fichiers du répertoire temporaire vers le répertoire cible
        for root, dirs, files in os.walk(temp_extract_path):
            for file in files:
                shutil.move(os.path.join(root, file), target_folder)

        # Supprimer le répertoire temporaire
        shutil.rmtree(temp_extract_path)

        return self
    
    def _convert_to_jpg(self):
        """
        Convertit tous les fichiers .png et .jpeg dans le dataset en .jpg.
        """
        for root, dirs, files in os.walk(self.dataset_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpeg')):
                    # Construire les chemins d'origine et de destination
                    original_file_path = os.path.join(root, file)
                    new_file_path = os.path.join(root, os.path.splitext(file)[0] + '.jpg')
                    
                    # Ouvrir l'image et la convertir en .jpg
                    with Image.open(original_file_path) as img:
                        img = img.convert('RGB')  # Convertir en RGB pour éviter les problèmes avec les canaux alpha
                        img.save(new_file_path, 'JPEG')
                    # Supprimer l'ancien fichier
                    os.remove(original_file_path)

        


    def _delete_file_without_txt(self):
        """
        Supprime tous les fichiers de n'importe quel format qui n'ont pas de fichier .txt correspondant.
        """
        # Lister tous les fichiers dans le dataset
        for root, dirs, files in os.walk(self.dataset_path):
            for file in files:
                if not file.lower().endswith('.txt'):
                    # Construire le chemin du fichier actuel
                    file_path = os.path.join(root, file)
                    # Construire le chemin du fichier .txt correspondant
                    txt_file_path = os.path.join(root, os.path.splitext(file)[0] + '.txt')
                    
                    # Supprimer le fichier s'il n'a pas de .txt correspondant
                    if not os.path.exists(txt_file_path):
                        os.remove(file_path)
                        print(f"Fichier supprimé : {file_path}")
        
        return self


    def separate_dataset_yolo(self, train_ratio = 0.8):
        """
        Sépare les données du dataset en ensembles d'entraînement et de validation.

        :param train_ratio: Ratio des données pour l'entraînement (par défaut 80%).
        """
        # Chemins des répertoires pour les données d'entraînement et de validation
        train_image = os.path.join(self.dataset_path, 'images/train')
        train_label = os.path.join(self.dataset_path, 'labels/train')
        val_image = os.path.join(self.dataset_path, 'images/val')
        val_label = os.path.join(self.dataset_path, 'labels/val')
        self._convert_to_jpg()
        self._delete_file_without_txt()
        # Sauvegarde des chemins
        self.train_image_path = train_image
        self.train_label_path = train_label
        self.val_image_path = val_image
        self.val_label_path = val_label

        # Création des répertoires s'ils n'existent pas
        os.makedirs(train_image, exist_ok=True)
        os.makedirs(train_label, exist_ok=True)
        os.makedirs(val_image, exist_ok=True)
        os.makedirs(val_label, exist_ok=True)

        # Récupération des fichiers d'images et de labels
        image_extensions = ('.jpg')
        images = [f for f in os.listdir(self.dataset_path) if f.lower().endswith(image_extensions)]
        labeled_images = [(img, img.rsplit('.', 1)[0] + '.txt') for img in images]

        # Vérification que les fichiers de labels existent pour chaque image
        labeled_images = [(img, lbl) for img, lbl in labeled_images if os.path.exists(os.path.join(self.dataset_path, lbl))]

        # Mélanger les paires d'images et de labels de manière aléatoire
        random.shuffle(labeled_images)

        # Calculer la taille des ensembles d'entraînement (80%) et de validation (20%)
        split_index = int(len(labeled_images) * train_ratio)

        # Diviser les fichiers en ensembles d'entraînement et de validation
        train_files = labeled_images[:split_index]
        val_files = labeled_images[split_index:]

        # Copier les fichiers dans les répertoires d'entraînement
        for image, label in train_files:
            shutil.move(os.path.join(self.dataset_path, image), train_image)
            shutil.move(os.path.join(self.dataset_path, label), train_label)

        # Copier les fichiers dans les répertoires de validation
        for image, label in val_files:
            shutil.move(os.path.join(self.dataset_path, image), val_image)
            shutil.move(os.path.join(self.dataset_path, label), val_label)

        return self

    def create_dataset_yaml_file(self):
        """
        Methode permettant de créer un fichier .yaml
        
        """
        # Récupéreration des données de yaml
        try:
            chemin_du_fichier = self.classes_txt
            with open(chemin_du_fichier, 'r') as fichier:
                lignes = fichier.readlines()
            lignes = [ligne.strip() for ligne in lignes]

            train_path = self.train_image_path.replace("\\", "/")
            val_path = self.val_image_path.replace("\\", "/") 

            self.train_image_path = self.train_image_path.replace("\\", "/")
            self.val_image_path = self.val_image_path.replace("\\", "/")
            self.train_label_path = self.val_label_path.replace("\\", "/")
            self.train_label_path = self.val_label_path.replace("\\", "/")

            contenu_yaml_file = "#Les informations prémordials du dataset\n\n"
            contenu_yaml_file += f"train: {train_path}\n"
            contenu_yaml_file += f"val: {val_path}\n\n"
            contenu_yaml_file += "#Autres paramètres\n\n"
            contenu_yaml_file += f"nc : {len(lignes)} # Nombre de classes\n"
            contenu_yaml_file += f"names: {lignes}  #La liste des classes"

            chemin= self.dataset_yaml.replace("\\", "/")

            
            # Écrire le contenu dans le fichier .yaml
            with open(chemin, 'w', encoding='utf-8') as file:
                file.write(contenu_yaml_file)

            return self
        except Exception as e:
            
            return None

if __name__ == "__main__":
    # Chemin du fichier .zip à décompresser
    zip_file_path = "Cersei_Lannister-20240531T233048Z-001.zip"

    # Instanciation et utilisation de la classe
    preparer = PreparateDatasetYolo(zip_file_path).un_zip_dataset().separate_dataset_yolo().create_dataset_yaml_file()

    print(preparer.train_image_path)


    