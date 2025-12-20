terraform {
  required_providers {
    keycloak = {
      source  = "mrparkers/keycloak"
      version = ">= 4.0.0"
    }
  }
}

provider "keycloak" {
  client_id     = "admin-cli"
  username      = "admin"
  password      = "admin"
  url           = "http://devsecops.local:8080"
}

# 1. On récupère le Realm
data "keycloak_realm" "realm" {
  realm = "devsecops"
}

# 2. On récupère le Rôle "writer" (CORRECTION ICI)
data "keycloak_role" "writer_role" {
  realm_id  = data.keycloak_realm.realm.id
  # client_id = ...  <-- J'AI SUPPRIMÉ CETTE LIGNE
  # En l'absence de client_id, Terraform cherche dans les "Realm Roles"
  name      = "writer"
}

# ---------------------------------------------------------
# CRÉATION DES RESSOURCES
# ---------------------------------------------------------

# 3. Création de l'utilisateur
resource "keycloak_user" "user3" {
  realm_id   = data.keycloak_realm.realm.id
  username   = "user3"
  enabled    = true
  email      = "user3@devsecops.local"
  email_verified = true
  first_name = "User"
  last_name  = "Three"

  initial_password {
    value     = "1234"
    temporary = false
  }
}

# 4. Assignation du rôle à l'utilisateur
resource "keycloak_user_roles" "user3_roles" {
  realm_id = data.keycloak_realm.realm.id
  user_id  = keycloak_user.user3.id

  role_ids = [
    data.keycloak_role.writer_role.id
  ]
}
