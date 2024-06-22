# Inferencing

`Inferencing` est une classe Python pour effectuer des inférences sur des images, des vidéos et des flux de caméra en utilisant un modèle YOLO pré-entraîné. Elle inclut des méthodes pour charger le modèle, effectuer des inférences, annoter les images/vidéos avec les résultats et enregistrer les informations de détection dans une base de données DuckDB.

## Méthodes

### `__init__(self, train_model_path: str)`
Initialise la classe avec le chemin du modèle YOLO pré-entraîné.

### `charging_model(self)`
Charge un modèle YOLO à partir du chemin spécifié et l'initialise pour une utilisation future.

### `inferecing_photo(self, image_path: str)`
Effectue une inférence sur une image donnée, dessine des rectangles autour des objets détectés et enregistre les informations de détection dans la base de données. Sauvegarde également l'image annotée.

### `inferecing_video(self, video_path: str, output_path: str)`
Effectue une inférence sur une vidéo donnée, dessine des rectangles autour des objets détectés et enregistre les informations de détection dans la base de données. Sauvegarde également la vidéo annotée.

### `inferecing_camera(self, camera_index: int = 0)`
Effectue une inférence en temps réel sur le flux vidéo d'une caméra, dessine des rectangles autour des objets détectés et enregistre les informations de détection dans la base de données.

## Exemple d'utilisation

```python
if __name__ == "__main__":
    infer = Inferencing("path_to_trained_model")
    infer.charging_model()
    
    # Inférence sur une image
    image_results = infer.inferecing_photo("path_to_image.jpg")
    print(image_results)

    # Inférence sur une vidéo
    video_results = infer.inferecing_video("path_to_video.mp4", "output_path.mp4")
    print(video_results)
    
    # Inférence en temps réel avec une webcam
    infer.inferecing_camera(0)
