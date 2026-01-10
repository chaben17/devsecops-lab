package main

# Règle : Interdire le tag 'latest'
deny[msg] {
  # 1. On cible les fichiers de type "Deployment" ou "Pod"
  input.kind == "Deployment"
  
  # 2. On parcourt la liste des conteneurs définis dans le YAML
  # Kubernetes structure: spec -> template -> spec -> containers
  container := input.spec.template.spec.containers[_]
  
  # 3. On vérifie si l'image se termine par ":latest" ou n'a pas de tag (implicitement latest)
  endswith(container.image, "latest")
  
  # 4. Si c'est vrai, on génère ce message d'erreur
  msg = sprintf("Politique OPA violée : Le conteneur '%s' utilise l'image '%s'. Le tag 'latest' est interdit en production.", [container.name, container.image])
}

# Cas particulier : Image sans aucun tag (ex: "nginx") -> c'est considéré comme latest
deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not contains(container.image, ":")
  msg = sprintf("Politique OPA violée : Le conteneur '%s' utilise l'image '%s' sans tag explicite. Veuillez spécifier une version.", [container.name, container.image])
}
