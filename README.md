# Django Odoo Sync

Ce projet Django permet de synchroniser les contacts depuis Odoo vers une base de données PostgreSQL. Le script `sync_contacts.py` se charge de la synchronisation automatique des contacts.

## Prérequis

- Python 3.12
- PostgreSQL
- Un compte Odoo avec les permissions appropriées

## Installation

1. **Clonez le dépôt** :
   ```sh
   git clone git@github.com:fred1599/chift.git
   cd chift

2. **Installez les dépendances** :
    ```sh
    python -m pip install --upgrade pip
    pip install -r requirements.txt

3. **Configurer les variables d'environnement** :

Créez un fichier `.env` à la racine de votre projet et ajoutez les variables suivantes :
    ```sh
    URL_ODOO=https://votre-instance.odoo.com

    DB_ODOO=nom_de_votre_base
    USERNAME_ODOO=votre_nom_utilisateur
    API_KEY_ODOO=votre_clé_api
    URL_DATABASE=postgres://votre-utilisateur:votre-mot-de-passe@votre-hôte:5432/votre-base-de-données

## Utilisation

### Obtenir un jeton (Token)

Pour obtenir un jeton, envoyez une requête POST à `/api/token/` avec votre nom d'utilisateur et votre mot de passe.

**Exemple de requête :**

```sh
curl -X POST -d "username=votre_nom_utilisateur&password=votre_mot_de_passe" http://votre-domaine/api/token/
```

## Recevoir la liste des contacts

Une fois que vous avez le jeton, utilisez-le pour authentifier vos requêtes afin d'obtenir la liste des contacts.

**Exemple de requête :**

```sh
curl -H "Authorization: Bearer votre_jeton" http://votre-domaine/api/contacts/
```

## Script `sync_contacts.py`

Le script `sync_contacts.py` se charge de synchroniser les contacts depuis Odoo vers PostgreSQL. Il est exécuté automatiquement en tant que worker sur Heroku.

### Fonctionnement du script

- **Chargement des variables d'environnement :**
  Le script charge les variables d'environnement à partir du fichier `.env` pour se connecter à Odoo et PostgreSQL.

- **Connexion à Odoo :**
  Le script utilise les informations de connexion fournies pour authentifier et accéder aux données de contact d'Odoo.

- **Connexion à PostgreSQL :**
  Le script se connecte à la base de données PostgreSQL en utilisant la bibliothèque `psycopg2`.

- **Récupération des contacts depuis Odoo :**
  Le script récupère une liste de contacts depuis Odoo.

- **Synchronisation des contacts :**
  Pour chaque contact, le script vérifie s'il existe déjà dans la base de données. Si c'est le cas, il met à jour les informations. Sinon, il insère un nouveau contact.

- **Exécution en tant que worker :**
  Le script est configuré pour s'exécuter en continu en tant que worker sur Heroku, permettant une synchronisation régulière des contacts.

## Déploiement sur Heroku

### Ajouter votre application Heroku comme remote :

```sh
heroku git:remote -a votre-app-heroku
```

### Déployer l'application :

```sh
git push heroku master
```

Le déploiement sur master se fait de manière automatisée depuis la plateforme Heroku.
