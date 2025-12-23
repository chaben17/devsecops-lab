from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
import os

app = FastAPI()

# --- BLOC CORS À AJOUTER ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En prod, on mettrait l'URL précise du frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------------------

# 1. Configuration OIDC
# Remplacez ceci par la longue chaîne que vous avez copiée !
PUBLIC_KEY_STR = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxi+al0SFUZoNWixwMgJL5XzjQ7ABa77qKb4SBBswD75RghsRZlOsajRj6/Zt+euMacokc7+Q+7EYLfXknAgHP+dQHNzug/rnV/lzQXya/F7xUZNYhoaX+xSIK/y7OoawJkqgdKIX6WKKQChAvJa3KZuyHum6WBGg6thKm4PjjzDwkzpPY2zpRKDaY9gurgZZ2feHa2ps9TKa0p9mtVKvzAxFApwx2nR24/kQBdKYRBkj71hgiavZmhZi4zTBkmNVV0Ckn4hJKac8PjZQthVjJTADgmTCH3vhsMkdFvNLIh2q5b5pYXJ+okAciv29kSOLECM3cS3VBb5mbLo1LYtwkQIDAQAB" # <--- COLLEZ VOTRE CLÉ ICI (gardez les guillemets)

# On formate la clé pour qu'elle soit valide pour la librairie
PUBLIC_KEY = f"-----BEGIN PUBLIC KEY-----\n{PUBLIC_KEY_STR}\n-----END PUBLIC KEY-----"

# L'algorithme utilisé par Keycloak (vu dans le header du token)
ALGORITHM = "RS256"

# Cela permet à FastAPI de savoir où chercher le token dans la requête (Header: Authorization Bearer ...)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Chemin vers le fichier "base de données"
DB_FILE = "/data/products.txt"

# Modèle de données pour valider l'entrée
class Product(BaseModel):
    id: str
    nom: str
    type: str
    prix: float

# 2. La fonction de vérification (La Douane)
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        # On tente de décoder et vérifier la signature du token
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM], audience="account")
        return payload
    except JWTError as e:
        # Si la signature est fausse ou le token expiré
        raise HTTPException(status_code=401, detail=f"Token invalide: {str(e)}")

@app.post("/products/")
def add_product(product: Product, token: dict = Depends(verify_token)):
    # --- VÉRIFICATION RBAC ---
    # On cherche la liste des rôles dans le token
    roles = token.get("realm_access", {}).get("roles", [])
    
    # Si le rôle "editor" n'est pas dans la liste, on rejette !
    if "writer" not in roles:
        raise HTTPException(
            status_code=403, # 403 Forbidden (Interdit)
            detail="Accès refusé : Vous n'avez pas le rôle 'writer'."
        )
    # -------------------------

    try:
        product_json = product.model_dump_json()
    except AttributeError:
        product_json = product.json()

    try:
        with open(DB_FILE, "a") as f:
            f.write(product_json + "\n")
        return {"message": "Produit ajouté", "product": product}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
