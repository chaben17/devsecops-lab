import os

def get_db_connection():
    # FAILLE : Mot de passe en clair dans le code !
    db_password = "super_secret_password_123!"
    print(f"Connecting to DB with {db_password}")

def execute_command(cmd):
    # FAILLE : Injection de commande possible (subprocess sans sécurité)
    os.system(cmd)
