#from Projet.database.databaseHandler import DatabaseHandler
from Projet.inference.inferecing import Inferencing
from Projet.database.databaseHandler import DatabaseHandler

if __name__ == '__main__':
   
    db = DatabaseHandler()
    
    inf =Inferencing("C:/Users/zakaria.gamane/Downloads/best.pt")
    inf.charging_model()
    inf.inferecing_video("WhatsApp Video 2024-06-19 at 18.03.08_78a7128e.mp4", "a.mp4")

    answ = db.generate_report_video(1)
    for i in answ:
        print(i)


    # Exemple d'inférence sur une vidéo
    #yolo_inference.inferecing_video('path_to_video.mp4')

    # Exemple d'inférence sur un flux de caméra
    #yolo_inference.inferecing_camera(camera_index=0)

    #Générer le rapport de fréquentation
  
    

    
