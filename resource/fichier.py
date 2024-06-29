
import duckdb

con = duckdb.connect("apprendre.db")

con.execute("""
CREATE TABLE IF NOT EXISTS classes(
           id_class INTEGER PRIMARY KEY,
           name_class VARCHAR
);""")


# Création de la séquence si elle n'existe pas
con.execute("""
CREATE SEQUENCE IF NOT EXISTS seq_id_source START 1;
""")

# Création de la table sources si elle n'existe pas
con.execute("""
CREATE TABLE IF NOT EXISTS sources (
    id_source INTEGER PRIMARY KEY DEFAULT NEXTVAL('seq_id_source'),
    name_source VARCHAR,
    type_source VARCHAR
);
""")

# Insertion des données
data = [
    ("video1.mp4", "video"),
    ("video2.mp4", "video"),
    ("video3.mp4", "video"),
    ("image1.jpg", "image"),
    ("image2.jpg", "image"),
    ("image3.jpg", "image"),
    ("stream1", "stream"),
    ("stream2", "stream"),
    ("stream3", "stream")
]

for name_source, type_source in data:
    con.execute("INSERT INTO sources (name_source, type_source) VALUES (?, ?)", (name_source, type_source))

# Affichage des données insérées
print(con.execute("SELECT * FROM sources").fetchall())
con.close()
