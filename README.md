# TaskManager Pro 🚀

Application SaaS de gestion de tâches multi-tenant construite avec Django.

---

## 🏗️ Architecture

```
Proxmox VM (IaaS)
  └── Docker Compose (PaaS)
        ├── Nginx (reverse proxy + static files)
        └── Django + Gunicorn (SaaS = TaskManager Pro)
```

## 📁 Structure du projet

```
taskmanager_pro/
├── taskmanager/          # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                 # Application principale
│   ├── models.py         # Tenant, User, Project, Task
│   ├── views.py          # Toutes les vues
│   ├── forms.py          # Formulaires
│   ├── urls.py           # Routes
│   ├── admin.py          # Interface admin
│   └── templates/core/   # Templates HTML Bootstrap
├── seed_data.py          # Données de démonstration
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── nginx.conf
```

## ⚡ Installation rapide (développement)

```bash
# 1. Cloner / copier le projet
cd taskmanager_pro

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate       # Linux/macOS
# venv\Scripts\activate        # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Migrations
python manage.py makemigrations core
python manage.py migrate

# 5. Données de démonstration
python seed_data.py

# 6. Lancer le serveur
python manage.py runserver
```

Accéder à : http://127.0.0.1:8000

## 🐳 Déploiement Docker (production / Proxmox)

```bash
# Build et lancement
docker-compose up -d --build

# Vérifier les logs
docker-compose logs -f web
```

Accéder à : http://<IP_VM>

## 👤 Comptes de démonstration

| Utilisateur | Mot de passe | Rôle | Entreprise |
|-------------|--------------|------|------------|
| `admin_a` | `admin123` | Admin | TechCorp Solutions |
| `emp_a` | `emp123` | Employé | TechCorp Solutions |
| `clara_a` | `emp123` | Employé | TechCorp Solutions |
| `admin_b` | `admin123` | Admin | InnovateLab |
| `emp_b` | `emp123` | Employé | InnovateLab |
| `superadmin` | `super123` | Super Admin | — |

## 🔒 Modèle multi-tenant

- Chaque utilisateur appartient à un `Tenant` (entreprise)
- Isolation logique par `tenant_id` : un tenant ne voit **jamais** les données d'un autre
- L'admin Django (`/admin/`) permet la gestion globale

## 📊 Fonctionnalités

- ✅ Tableau de bord avec graphiques Chart.js
- ✅ Gestion des projets (CRUD)
- ✅ Gestion des tâches (CRUD + Kanban)
- ✅ Mise à jour rapide du statut
- ✅ Filtres avancés sur les tâches
- ✅ Gestion des utilisateurs (admin)
- ✅ Isolation multi-tenant
- ✅ Interface Bootstrap 5 responsive
- ✅ Tâches urgentes / en retard

## 🛠️ Technologies

- **Backend** : Django 4.2 + SQLite
- **Frontend** : Bootstrap 5 + Bootstrap Icons + Chart.js
- **Déploiement** : Docker + Nginx + Gunicorn
- **Infrastructure** : Proxmox VM
