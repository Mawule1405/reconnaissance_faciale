import duckdb
from datetime import datetime

class DatabaseHandler:
    def __init__(self, db_path='attendance.db'):
        self.db_path = db_path
        self.setup_database()

    def setup_database(self):
        conn = duckdb.connect(self.db_path)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            person_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            detection_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            person_id INTEGER REFERENCES persons(person_id),
            image_id INTEGER REFERENCES images(image_id),
            detection_time TIMESTAMP,
            confidence FLOAT
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS video_sessions (
            session_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            start_time TIMESTAMP,
            end_time TIMESTAMP
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS images (
            image_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            session_id INTEGER REFERENCES video_sessions(session_id),
            image_path TEXT NOT NULL,
            timestamp TIMESTAMP
        );
        """)
        conn.close()

    def insert_person(self, person_id, name):
        conn = duckdb.connect(self.db_path)
        conn.execute("INSERT INTO persons (person_id, name) VALUES (?, ?)", (person_id, name))
        conn.close()

    def insert_detection(self, person_id, image_id, detection_time, confidence):
        conn = duckdb.connect(self.db_path)
        conn.execute("""
            INSERT INTO detections (person_id, image_id, detection_time, confidence)
            VALUES (?, ?, ?, ?)
        """, (person_id, image_id, detection_time, confidence))
        conn.close()

    def insert_video_session(self, start_time):
        conn = duckdb.connect(self.db_path)
        conn.execute("INSERT INTO video_sessions (start_time) VALUES (?)", (start_time,))
        session_id = conn.execute("SELECT LAST_INSERT_ID()").fetchone()[0]
        conn.close()
        return session_id

    def end_video_session(self, session_id, end_time):
        conn = duckdb.connect(self.db_path)
        conn.execute("UPDATE video_sessions SET end_time = ? WHERE session_id = ?", (end_time, session_id))
        conn.close()

    def insert_image(self, session_id, image_path, timestamp):
        conn = duckdb.connect(self.db_path)
        conn.execute("""
            INSERT INTO images (session_id, image_path, timestamp)
            VALUES (?, ?, ?)
        """, (session_id, image_path, timestamp))
        image_id = conn.execute("SELECT LAST_INSERT_ID()").fetchone()[0]
        conn.close()
        return image_id

    def generate_report(self):
        conn = duckdb.connect(self.db_path)
        report = conn.execute("""
            SELECT p.name, COUNT(d.detection_id) AS appearance_count, 
                   MIN(d.detection_time) AS first_seen, MAX(d.detection_time) AS last_seen,
                   MAX(d.detection_time) - MIN(d.detection_time) AS duration
            FROM detections d
            JOIN persons p ON d.person_id = p.person_id
            GROUP BY p.name
            ORDER BY appearance_count DESC;
        """).fetchall()
        conn.close()
        return report


if __name__ == '__main__':
    db_handler = DatabaseHandler()

    # Exemple d'ajout de personnes
    db_handler.insert_person(1, 'Alice')
    db_handler.insert_person(2, 'Bob')

    # Démarrer une nouvelle session vidéo
    session_id = db_handler.insert_video_session(datetime.now())

    # Ajouter une image à la session
    image_id = db_handler.insert_image(session_id, 'path_to_image.jpg', datetime.now())

    # Ajouter des détections
    db_handler.insert_detection(1, image_id, datetime.now(), 0.95)
    db_handler.insert_detection(2, image_id, datetime.now(), 0.85)

    # Terminer la session vidéo
    db_handler.end_video_session(session_id, datetime.now())

    # Générer le rapport de fréquentation
    report = db_handler.generate_report()
    for row in report:
        print(row)
