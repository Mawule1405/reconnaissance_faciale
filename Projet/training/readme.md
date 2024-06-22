# Classe `TrainingYolo`
Cette classe permet de faire l'entraînement d'un modèle YOLO et de sauvegarder le résultat de l'entraînement dans un dossier `TRAIN_RESULT`.

## `__init__(self, dataset: pD) -> None`
Initialise une instance de la classe `TrainingYolo` avec le jeu de données spécifié.

## `download_model_yolo(self, model_name: str)`
Télécharge le modèle YOLO spécifié et le sauvegarde dans un répertoire désigné.

## `train_yolo_settings(self, dataset: pD, model_path: str, epochs: int, img_size: int, batch_size: int, project_path: str, run_name: str)`
Configure les paramètres d'entraînement du modèle YOLO, tels que le nombre d'époques, la taille des images, la taille des lots, etc.

## `train_yolo_model(self)`
Méthode pour entraîner le modèle YOLOv8 avec les paramètres spécifiés.

## `train_yolo_analyser(self)`
Analyse les résultats de l'entraînement du modèle et génère des rapports contenant les métriques de performance et les graphiques associés.

## `_plot_losses(self, train_losses, val_losses)`
Génère et sauvegarde un graphique des pertes d'entraînement et de validation par époque.

## `_plot_precision_recall(self, precision, recall, map50, f1)`
Génère et sauvegarde un graphique des métriques de précision, rappel, mAP@50, et F1 Score.

## `_plot_confusion_matrix(self, y_true, y_pred)`
Génère et sauvegarde la matrice de confusion basée sur les étiquettes vraies et prédictes.

## `_generate_pdf_report(self)`
Génère un rapport PDF contenant les graphiques des pertes, des métriques de précision/rappel, et de la matrice de confusion.

# Exemple d'utilisation dans le script principal
Entraîne le modèle YOLO en utilisant un dataset spécifique et enregistre les résultats dans un répertoire désigné.
