#from Projet.database.databaseHandler import DatabaseHandler

from Projet.gui.user_interface import UserInterface

if __name__ == '__main__':
   
    gui = UserInterface("Projet/model/best.pt")
    gui.configuration()
    gui.add_menu_bar()
    gui.add_zone_affiche()
    gui.mise_en_pause()

  
    

    
