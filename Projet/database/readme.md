# DatabaseHandler

`DatabaseHandler` est une classe Python pour gérer une base de données DuckDB utilisée pour suivre les classes, les sources et les détections. Elle comprend des méthodes pour créer la base de données, insérer des données et générer des rapports.

## Méthodes

### `__init__(self, db_path='attendance.db')`
Initialise la classe avec le chemin de la base de données DuckDB.

### `setup_database(self)`
Crée les tables `classes`, `sources` et `detecter` si elles n'existent pas déjà.

### `insert_class(self, id_class, name)`
Insère une nouvelle classe dans la table `classes`.

### `insert_detection(self, id_detecter, id_class, id_source, detection_time, confidence)`
Insère une nouvelle détection dans la table `detecter`.

### `insert_source(self, id_source: int, name_source: str, type_source: str)`
Insère une nouvelle source dans la table `sources`.

### `last_detection_insert(self)`
Retourne l'ID de la dernière détection insérée dans la table `detecter`.

### `last_class_insert(self)`
Retourne l'ID de la dernière classe insérée dans la table `classes`.

### `last_source_insert(self)`
Retourne l'ID de la dernière source insérée dans la table `sources`.

### `generate_report_photo(self, id_source)`
Génère un rapport pour une source de type "photo", listant les classes détectées.

### `generate_report_video(self, id_source)`
Génère un rapport pour une source de type "video", comptant le nombre d'apparitions pour chaque classe détectée avec un intervalle de temps supérieur à une minute entre les détections successives.
