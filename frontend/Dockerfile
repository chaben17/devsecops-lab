# On utilise une image Nginx très légère (Alpine Linux)
FROM nginx:alpine

# On supprime la page d'accueil par défaut de Nginx
RUN rm -rf /usr/share/nginx/html/*

# On copie TON fichier html dans le dossier du serveur web
COPY index.html /usr/share/nginx/html/index.html

# Le port standard web
EXPOSE 80

# Nginx se lance tout seul, pas besoin de CMD
