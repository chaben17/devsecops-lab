from fastapi.middleware.cors import CORSMiddleware
# 1. On ajoute APIRouter aux imports
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
import os

app = FastAPI()

# --- BLOC CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -----------------

# 2. CRÉATION DU ROUTER (C'est la clé du succès !)
# Cela dit à FastAPI : "Toutes les routes ici commencent par /service-a"
router = APIRouter(prefix="/service-a")

# Configuration OIDC
PUBLIC_KEY_STR = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxi+al0SFUZoNWixwMgJL5XzjQ7ABa77qKb4SBBswD75RghsRZlOsajRj6/Zt+euMacokc7+Q+7EYLfXknAgHP+dQHNzug/rnV/lzQXya/F7xUZNYhoaX+xSIK/y7OoawJkqgdKIX6WKKQChAvJa3KZuyHum6WBGg6thKm4PjjzDwkzpPY2zpRKDaY9gurgZZ2feHa2ps9TKa0p9mtVKvzAxFApwx2nR24/kQBdKYRBkj71hgiavZmhZi4zTBkmNVV0Ckn4hJKac8PjZQthVjJTADgmTCH3vhsMkdFvNLIh2q5b5pYXJ+okAciv29kSOLECM3cS3VBb5mbLo1LYtwkQIDAQAB" 
PUBLIC_KEY = f"-----BEGIN PUBLIC KEY-----\n{PUBLIC_KEY_STR}\n-----END PUBLIC KEY-----"
ALGORITHM = "RS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

DB_FILE = "/data/products.txt"

class Product(BaseModel):
    id: str
    nom: str
    type: str
    prix: float

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM], audience="account")
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token invalide: {str(e)}")

# 3. ON UTILISE LE ROUTER ICI (et plus @app)
# J'ai retiré le "/" final pour correspondre au frontend (/service-a/products)
@router.post("/products")
def add_product(product: Product, token: dict = Depends(verify_token)):
    # --- VÉRIFICATION RBAC ---
    roles = token.get("realm_access", {}).get("roles", [])
    
    if "writer" not in roles:
        raise HTTPException(
            status_code=403,
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

# 4. ON COLLE LE ROUTER À L'APPLICATION PRINCIPALE
app.include_router(router)
