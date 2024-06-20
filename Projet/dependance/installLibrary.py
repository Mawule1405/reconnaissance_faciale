
class InstallLibrary:
    def __init__(self, libraries:list[str]):
        self.install_libraries(libraries)

    @classmethod
    def install_libraries(libraries):
        """
        Installe les bibliothèques spécifiées dans la liste 'libraries' en utilisant pip.

        Paramètres:
        libraries (list): Liste des noms des bibliothèques à installer.

        Exemple d'utilisation:
        install_libraries(['ultralytics', 'duckdb', 'pandas'])
        """
        for lib in libraries:
            print(f"Installing {lib}...")
            exec("!pip install {lib}")
            print(f"Installation des bibliothèques terminée: {lib}.")

