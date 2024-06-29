import duckdb

# Créer une connexion à la base de données en mémoire
conn = duckdb.connect(':memory:')

# Exécuter une requête SQL
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR)")
conn.execute("INSERT INTO users VALUES (1, 'Alice')")
conn.execute("INSERT INTO users VALUES (2, 'Bob')")

# Exécuter une requête SELECT
result = conn.execute("SELECT name FROM users WHERE id=2")
print(result.fetchdf())  # Afficher le résultat sous forme de DataFrame pandas
