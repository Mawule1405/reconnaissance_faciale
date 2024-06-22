# PreparateDatasetYolo

`PreparateDatasetYolo` est une classe Python pour préparer des ensembles de données au format YOLO. Elle comprend des méthodes pour décompresser des fichiers, convertir des images, séparer les données en ensembles d'entraînement et de validation, et créer un fichier de configuration YAML.

## Méthodes

### `__init__(self, dataset_path)`
Initialise la classe avec le chemin du fichier zip du dataset.

### `un_zip_dataset(self)`
Décompresse un fichier .zip et place les fichiers dans un répertoire portant le nom du fichier .zip (sans extension).

### `_convert_to_jpg(self)`
Convertit tous les fichiers .png et .jpeg dans le dataset en .jpg.

### `_delete_file_without_txt(self)`
Supprime tous les fichiers de n'importe quel format qui n'ont pas de fichier .txt correspondant.

### `separate_dataset_yolo(self, train_ratio=0.8)`
Sépare les données du dataset en ensembles d'entraînement et de validation. Le ratio d'entraînement par défaut est de 80%.

### `create_dataset_yaml_file(self)`
Crée un fichier de configuration YAML pour le dataset YOLO.
