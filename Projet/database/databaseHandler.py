import duckdb
from datetime import datetime, timedelta

class DatabaseHandler:
    def __init__(self, db_path='attendance.db'):
        self.db_path = db_path
        self.setup_database()

    def setup_database(self):
        conn = duckdb.connect(self.db_path)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id_class INTEGER PRIMARY KEY,
            name_class VARCHAR NOT NULL
        )
        """)


        conn.execute("""
        CREATE TABLE IF NOT EXISTS sources(
                    id_source INTEGER PRIMARY KEY,
                    name_source VARCHAR NOT NULL,
                    type_source VARCHAR NOT NULL
                     
                     )""")
        
        conn.execute("""
        CREATE TABLE IF NOT EXISTS detecter (
            id_detecter INTEGER PRIMARY KEY ,
            id_class INTEGER REFERENCES classes(id_class),
            id_source INTEGER REFERENCES sources(id_source),
            detection_time TIMESTAMP,
            confidence FLOAT
        );
        """)
        
    
   
        conn.close()

    def insert_class(self, id_class, name):
        conn = duckdb.connect(self.db_path)
        conn.execute("INSERT INTO classes (id_class, name_class) VALUES (?, ?)", (id_class, name))
        conn.close()


    def insert_detection(self, id_detecter, id_class, id_source, detection_time, confidence):
        conn = duckdb.connect(self.db_path)
        conn.execute("""
            INSERT INTO detecter (id_detecter, id_class, id_source, detection_time, confidence)
            VALUES (?, ?, ?, ?, ?)
        """, (id_detecter, id_class, id_source, detection_time, confidence))
        conn.close()

    
    def insert_source(self, id_source: int, name_source: str, type_source:str):
        """Méthode d'insertion d'une source"""
        conn= duckdb.connect(self.db_path)
        conn.execute("""
            INSERT INTO sources (id_source, name_source, type_source)
            VALUES (?, ?, ?)
        """, (id_source, name_source, type_source))
        conn.close()


    def last_detection_insert(self):
        """
        Méthode qui donne l'id de la derniere detection effectue
        """
        conn=duckdb.connect(self.db_path)
        result = conn.execute("SELECT id_detecter FROM detecter ORDER BY id_source DESC LIMIT 1")
        id= result.fetchone()
        if id:
            id = id[0]
        else :
            id = 0
        conn.close()

        return id


    def last_class_insert(self):
        """
        Méthode qui donne l'id de la dernière class insérer
        """

        conn = duckdb.connect(self.db_path)
        result = conn.execute("SELECT id_class FROM classes ORDER BY id_class DESC LIMIT 1")
        id= result.fetchone()
        if id:
            id = id[0]
        else :
            id = 0
        conn.close()

        return id



    def last_source_insert(self):
        """
        Méthode qui donne l'id de la dernièresource insérer
        """

        conn = duckdb.connect(self.db_path)
        result = conn.execute("SELECT id_source FROM sources ORDER BY id_source DESC LIMIT 1")
        id= result.fetchone()
        if id:
            id = id[0]
        else :
            id = 0
        conn.close()

        return id

    def generate_report_photo(self, id_source):
        conn = duckdb.connect(self.db_path)
        report = conn.execute(f"""
            SELECT c.id_class, c.name_class
            FROM classes c, sources s, detecter d
            WHERE c.id_class = d.id_class AND d.id_source = s.id_source
                 AND s.id_source = '{id_source}' AND s.type_source = 'photo'  
        """).fetchall()
        conn.close()
        return report
    
    def generate_report_video(self, id_source):
        conn = duckdb.connect(self.db_path)
        report = conn.execute(f"""
            SELECT d.id_detecter, c.id_class, c.name_class, detection_time ,confidence
            FROM classes c, sources s, detecter d
            WHERE c.id_class = d.id_class AND d.id_source = s.id_source
                AND s.id_source = '{id_source}' AND s.type_source = 'video'
            ORDER BY c.id_class, d.detection_time ASC
        """).fetchall()
        conn.close()

        # Initialiser le dictionnaire pour stocker les apparitions
        appearances = {}

        

        for row in report:
            id_detecter, id_class, name_class, time_detection, confidence = row
            
            if id_class not in appearances:
                appearances[id_class] = {
                    'name_class': name_class,
                    'last_detection': time_detection,
                    'count': 1
                }
            else:
                last_detection = appearances[id_class]['last_detection']
                # Calculer la différence de temps
                if time_detection - last_detection > timedelta(minutes=1):
                    appearances[id_class]['count'] += 1
                
                # Mettre à jour la dernière détection
                appearances[id_class]['last_detection'] = time_detection

        # Préparer le résultat final
        result = [
            (id_class, data['name_class'], data['count']) 
            for id_class, data in appearances.items()
        ]

        return result






if __name__ == "__main__":
    db = DatabaseHandler()
    res = db.generate_report_video(1)
    print(res)

