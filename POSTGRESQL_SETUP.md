# 🐘 Guide PostgreSQL + pgAdmin — TaskManager Pro

## Option A — Installation locale (sans Docker)

### 1. Installer PostgreSQL

**Windows :**
- Télécharger l'installeur sur https://www.postgresql.org/download/windows/
- Installer avec les options par défaut
- Retenir le mot de passe `postgres` que vous saisissez pendant l'install
- pgAdmin est **inclus** dans l'installeur Windows ✅

**Port par défaut :** `5432`

---

### 2. Créer la base de données dans pgAdmin

Ouvrir **pgAdmin 4** → connectez-vous avec le mot de passe `postgres`

Puis exécuter dans **Query Tool** (clic droit sur PostgreSQL > Query Tool) :

```sql
-- Créer l'utilisateur
CREATE USER joel WITH PASSWORD 'joel2311';

-- Créer la base de données
CREATE DATABASE taskmanager_db OWNER joel;

-- Accorder tous les droits
GRANT ALL PRIVILEGES ON DATABASE taskmanager_db TO joel;
```

---

### 3. Configurer le fichier .env

Ouvrir `taskmanager_pro/.env` et ajuster si besoin :

```env
SECRET_KEY=change-moi-en-production-cle-secrete-longue
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=taskmanager_db
DB_USER=taskmanager_user
DB_PASSWORD=taskmanager_pass
DB_HOST=localhost
DB_PORT=5432
```

---

### 4. Installer les dépendances Python

```bash
cd taskmanager_pro
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

> `psycopg2-binary` est le driver Python → PostgreSQL, il est déjà dans `requirements.txt`

---

### 5. Lancer les migrations et le serveur

```bash
python manage.py makemigrations core
python manage.py migrate
python seed_data.py
python manage.py runserver
```

**Accès :**
- Application → http://127.0.0.1:8000
- pgAdmin    → inclus dans PostgreSQL (icône dans le menu démarrer)

---

## Option B — Tout en Docker (PostgreSQL + pgAdmin + Django)

### 1. S'assurer que Docker Desktop est installé

https://www.docker.com/products/docker-desktop/

### 2. Lancer tous les services

```bash
cd taskmanager_pro
docker-compose up -d --build
```

Cela démarre automatiquement :
- **PostgreSQL** sur le port `5432`
- **pgAdmin** sur http://localhost:5050
- **Django** sur http://localhost:8000 (via Nginx sur port 80)

### 3. Migrations initiales (première fois)

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python seed_data.py
```

### 4. Accéder à pgAdmin (Docker)

URL : http://localhost:5050

| Champ    | Valeur                  |
|----------|-------------------------|
| Email    | admin@taskmanager.pro   |
| Password | pgadmin123              |

#### Ajouter la connexion au serveur PostgreSQL dans pgAdmin :

1. Clic droit **Servers** → **Register** → **Server**
2. Onglet **General** → Name : `TaskManager DB`
3. Onglet **Connection** :

| Champ            | Valeur            |
|------------------|-------------------|
| Host             | `db` (si Docker)  |
| Port             | `5432`            |
| Database         | `taskmanager_db`  |
| Username         | `taskmanager_user`|
| Password         | `taskmanager_pass`|

4. Cliquer **Save** ✅

---

## Vérifier que tout fonctionne

Dans pgAdmin, vous devez voir :
```
Servers
└── TaskManager DB
    └── Databases
        └── taskmanager_db
            └── Schemas
                └── public
                    └── Tables
                        ├── core_user
                        ├── core_tenant
                        ├── core_project
                        └── core_task
```

---

## Comptes de démonstration

| Utilisateur  | Mot de passe | Rôle            |
|-------------|--------------|-----------------|
| superadmin  | super123     | Super Admin     |
| admin_a     | admin123     | Admin TechCorp  |
| emp_a       | emp123       | Employé TechCorp|
| admin_b     | admin123     | Admin InnovateLab|
| emp_b       | emp123       | Employé InnovateLab|

---

## Commandes utiles

```bash
# Voir les logs Django
docker-compose logs -f web

# Accéder au shell Django
docker-compose exec web python manage.py shell

# Créer un superuser manuellement
docker-compose exec web python manage.py createsuperuser

# Sauvegarder la base de données
docker-compose exec db pg_dump -U taskmanager_user taskmanager_db > backup.sql

# Restaurer une sauvegarde
docker-compose exec -T db psql -U taskmanager_user taskmanager_db < backup.sql

# Arrêter tous les services
docker-compose down

# Arrêter ET supprimer les données
docker-compose down -v
```
