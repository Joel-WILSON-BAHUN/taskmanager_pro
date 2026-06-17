# TaskManager Pro — Deploiement Django sur Debian 13

**Projet 04 — Module Administration des Serveurs Web — IAI Gabon — ING 2 — 2025/2026**

Auteurs : WILSON-BAHUN Adjevi Mawougnon, DANSOU Koffi Junior, MAHANGA MBOUMBA Jamarthe Celly, EYA BILOGHE Norwen  
Superviseur : M. Brice ONDJIBOU

---

## Sommaire

1. [Prerequis et environnement](#1-prerequis-et-environnement)
2. [Configuration reseau de la VM](#2-configuration-reseau-de-la-vm)
3. [Acces SSH depuis Windows](#3-acces-ssh-depuis-windows)
4. [Installation des services](#4-installation-des-services)
5. [Configuration PostgreSQL](#5-configuration-postgresql)
6. [Utilisateur systeme dedie](#6-utilisateur-systeme-dedie)
7. [Transfert du projet et virtualenv](#7-transfert-du-projet-et-virtualenv)
8. [Fichier .env et initialisation Django](#8-fichier-env-et-initialisation-django)
9. [Configuration systemd (Gunicorn)](#9-configuration-systemd-gunicorn)
10. [Configuration Nginx et HTTPS](#10-configuration-nginx-et-https)
11. [Verification finale](#11-verification-finale)
12. [Comptes de demonstration](#12-comptes-de-demonstration)
13. [Structure du projet](#13-structure-du-projet)

---

## 1. Prerequis et environnement

### Machine hote
- Windows 10 avec VMware Workstation 17
- PowerShell ou Windows Terminal pour SSH

### Machine virtuelle
| Parametre     | Valeur                              |
|---------------|-------------------------------------|
| Hyperviseur   | VMware Workstation 17               |
| OS invite     | Debian 13 Trixie (64 bits)          |
| RAM           | 4 Go                                |
| vCPU          | 2                                   |
| Disque        | 30 Go (thin provisioned)            |
| Carte reseau 1| NAT (acces internet / apt)          |
| Carte reseau 2| Host-Only (192.168.56.10 — SSH)     |

> **Note importante :** Debian 13 integre Python 3.13 par defaut.
> Ce projet utilise Python 3.11 pour la compatibilite avec les dependances.
> Python 3.11 est disponible dans les depots officiels de Debian 13 sans source tierce.

---

## 2. Configuration reseau de la VM

Apres le premier demarrage de la VM, identifier les deux interfaces :

```bash
ip a
```

- `ens33` : carte NAT (configuree automatiquement par DHCP — acces internet)
- `ens34` : carte Host-Only (a configurer en IP fixe pour SSH)

Editer la configuration reseau :

```bash
nano /etc/network/interfaces
```

Ajouter en fin de fichier :

```
auto ens34
iface ens34 inet static
    address   192.168.56.10
    netmask   255.255.255.0
```

Appliquer :

```bash
systemctl restart networking
ip a show ens34
```

La carte Host-Only n'a pas besoin de passerelle : elle sert uniquement a la
communication directe entre la VM et la machine hote Windows.

---

## 3. Acces SSH depuis Windows

Depuis PowerShell ou Windows Terminal sur la machine hote :

```powershell
ssh wilson@192.168.56.10
```

Toutes les commandes suivantes s'executent en SSH sur la VM, en tant que root
(ou via sudo si root direct est desactive).

---

## 4. Installation des services

```bash
apt update && apt upgrade -y

# Nginx
apt install -y nginx

# PostgreSQL 17
apt install -y postgresql postgresql-contrib

# Python 3.11 (depots officiels Debian 13)
apt install -y python3.11 python3.11-venv python3.11-dev \
               python3-pip python3-full libpq-dev build-essential

# Outils complementaires
apt install -y openssl logrotate curl git unrar-free

# Verifications
nginx -v
psql --version
python3.11 --version
```

---

## 5. Configuration PostgreSQL

```bash
# Demarrer et activer PostgreSQL
systemctl enable --now postgresql

# Ouvrir le shell PostgreSQL en tant que postgres
sudo -u postgres psql
```

Dans le shell psql :

```sql
CREATE USER taskmanager_user WITH PASSWORD 'Mot2Passe_Fort!';
CREATE DATABASE taskmanager_db OWNER taskmanager_user;
GRANT ALL PRIVILEGES ON DATABASE taskmanager_db TO taskmanager_user;
\q
```

---

## 6. Utilisateur systeme dedie

Gunicorn tournera sous un utilisateur sans privileges pour limiter l'exposition
en cas de compromission :

```bash
useradd --system --no-create-home \
    --shell /usr/sbin/nologin \
    --gid www-data taskmanager

mkdir -p /var/www/taskmanager_pro
chown taskmanager:www-data /var/www/taskmanager_pro
chmod 750 /var/www/taskmanager_pro
```

---

## 7. Transfert du projet et virtualenv

Le projet est disponible sur GitHub mais sans le fichier `.env` (exclu pour
des raisons de securite). Utiliser l'archive `.rar` qui contient l'integralite
des fichiers.

Depuis PowerShell Windows, transferer l'archive via SCP :

```powershell
scp taskmanager_pro.rar wilson@192.168.56.10:/tmp/
```

Sur la VM, extraire et creer le virtualenv :

```bash
cd /var/www
unrar x /tmp/taskmanager_pro.rar taskmanager_pro/

# Creer le virtualenv en Python 3.11 explicitement
# (python3 pointe vers 3.13 sur Debian 13)
python3.11 -m venv /var/www/taskmanager_pro/venv

# Activer et installer les dependances
/var/www/taskmanager_pro/venv/bin/pip install --upgrade pip

/var/www/taskmanager_pro/venv/bin/pip install \
    django==4.2 gunicorn psycopg2-binary \
    python-decouple whitenoise Pillow

# Ou si un requirements.txt est present :
# /var/www/taskmanager_pro/venv/bin/pip install -r requirements.txt
```

> **Pourquoi `python3.11` et non `python3` ?**
> Sur Debian 13, `python3` pointe vers Python 3.13. Utiliser `python3.11 -m venv`
> garantit que le virtualenv utilise bien Python 3.11 pour toutes les commandes
> `venv/bin/python` et `venv/bin/pip`.

---

## 8. Fichier .env et initialisation Django

Creer le fichier `.env` :

```bash
nano /var/www/taskmanager_pro/.env
```

Contenu :

```env
SECRET_KEY=REMPLACER-PAR-UNE-CLE-GENEREE
DEBUG=False
ALLOWED_HOSTS=192.168.56.10,taskmanager.local
DB_NAME=taskmanager_db
DB_USER=taskmanager_user
DB_PASSWORD=Mot2Passe_Fort!
DB_HOST=localhost
DB_PORT=5432
```

Generer la SECRET_KEY :

```bash
python3.11 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Coller la valeur generee dans `.env` a la place de `REMPLACER-PAR-UNE-CLE-GENEREE`.

Securiser le fichier `.env` :

```bash
chown taskmanager:www-data /var/www/taskmanager_pro/.env
chmod 640 /var/www/taskmanager_pro/.env
```

Initialiser la base de donnees et les fichiers statiques :

```bash
cd /var/www/taskmanager_pro

venv/bin/python manage.py makemigrations core
venv/bin/python manage.py migrate
venv/bin/python manage.py collectstatic --noinput

# Charger les donnees de demonstration
venv/bin/python seed_data.py

# Corriger les permissions apres toutes les operations
chown -R taskmanager:www-data /var/www/taskmanager_pro
```

---

## 9. Configuration systemd (Gunicorn)

### gunicorn.socket

Creer `/etc/systemd/system/gunicorn.socket` :

```ini
[Unit]
Description=Gunicorn socket — TaskManager Pro

[Socket]
ListenStream=/run/gunicorn/gunicorn.sock
SocketUser=www-data
SocketGroup=www-data
SocketMode=0660

[Install]
WantedBy=sockets.target
```

### gunicorn.service

Creer `/etc/systemd/system/gunicorn.service` :

```ini
[Unit]
Description=Gunicorn WSGI — TaskManager Pro (Django)
Requires=gunicorn.socket
After=network.target postgresql.service gunicorn.socket

[Service]
User=taskmanager
Group=www-data
WorkingDirectory=/var/www/taskmanager_pro
EnvironmentFile=/var/www/taskmanager_pro/.env
RuntimeDirectory=gunicorn
RuntimeDirectoryMode=0755
ExecStart=/var/www/taskmanager_pro/venv/bin/gunicorn \
    --workers 5 \
    --worker-class sync \
    --bind unix:/run/gunicorn/gunicorn.sock \
    --timeout 60 \
    --max-requests 1000 \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile  /var/log/gunicorn/error.log \
    --log-level info \
    taskmanager.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5s
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

### Activation

```bash
mkdir -p /var/log/gunicorn
chown taskmanager:www-data /var/log/gunicorn

systemctl daemon-reload
systemctl enable --now gunicorn.socket
systemctl enable gunicorn.service

# Verifier
systemctl status gunicorn.socket
systemctl status gunicorn.service
```

---

## 10. Configuration Nginx et HTTPS

### Certificat auto-signe

```bash
mkdir -p /etc/ssl/taskmanager

openssl req -x509 -nodes -days 1095 -newkey rsa:2048 \
    -keyout /etc/ssl/taskmanager/key.pem \
    -out    /etc/ssl/taskmanager/cert.pem \
    -subj "/C=GA/ST=Libreville/O=IAI/CN=taskmanager.local"

chmod 600 /etc/ssl/taskmanager/key.pem
chmod 644 /etc/ssl/taskmanager/cert.pem
```

### VHost Nginx

Creer `/etc/nginx/sites-available/taskmanager` :

```nginx
server {
    listen 80;
    server_name taskmanager.local 192.168.56.10;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name taskmanager.local 192.168.56.10;

    ssl_certificate     /etc/ssl/taskmanager/cert.pem;
    ssl_certificate_key /etc/ssl/taskmanager/key.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;

    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options           "DENY"             always;
    add_header X-Content-Type-Options    "nosniff"          always;

    access_log /var/log/nginx/taskmanager_access.log combined;
    error_log  /var/log/nginx/taskmanager_error.log  warn;
    client_max_body_size 10m;

    location /static/ {
        alias   /var/www/taskmanager_pro/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    location /media/ {
        alias /var/www/taskmanager_pro/media/;
        expires 7d;
        access_log off;
    }

    location / {
        proxy_pass         http://unix:/run/gunicorn/gunicorn.sock;
        proxy_http_version 1.1;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection        "";
        proxy_connect_timeout 10s;
        proxy_read_timeout    60s;
    }

    location ~ /\. { deny all; access_log off; }
    location ~ \.(env|sql|git|bak)$ { deny all; }
}
```

Activer le site :

```bash
ln -s /etc/nginx/sites-available/taskmanager \
      /etc/nginx/sites-enabled/taskmanager

rm -f /etc/nginx/sites-enabled/default

nginx -t && systemctl reload nginx
```

---

## 11. Verification finale

```bash
# Services systemd
systemctl status gunicorn.socket
systemctl status gunicorn.service
systemctl status nginx
systemctl status postgresql

# Test HTTP vers HTTPS
curl -I http://192.168.56.10
# Attendu : 301 Moved Permanently

# Test HTTPS (certificat auto-signe : -k pour ignorer la validation)
curl -Ik https://192.168.56.10
# Attendu : 200 OK

# Logs en temps reel
tail -f /var/log/nginx/taskmanager_access.log
tail -f /var/log/gunicorn/access.log

# Test apres reboot
reboot
# Puis reconnexion SSH et :
systemctl status gunicorn.socket gunicorn.service nginx postgresql
```

Depuis le navigateur Windows : ouvrir `https://192.168.56.10`
(accepter l'avertissement lie au certificat auto-signe).

---

## 12. Comptes de demonstration

| Identifiant  | Mot de passe | Role                                        |
|--------------|--------------|---------------------------------------------|
| superadmin   | super123     | Super-administrateur — gestion des tenants  |
| admin_a      | admin123     | Administrateur TechCorp Solutions           |
| emp_a        | emp123       | Employe TechCorp Solutions                  |
| admin_b      | admin123     | Administrateur InnovateLab                  |
| emp_b        | emp123       | Employe InnovateLab                         |

---

## 13. Structure du projet

```
/var/www/taskmanager_pro/
├── venv/                    # Virtualenv Python 3.11 (non versionne)
├── .env                     # Variables sensibles (non versionne)
├── manage.py
├── taskmanager/
│   ├── settings.py
│   ├── wsgi.py
│   └── urls.py
├── core/
│   ├── models.py
│   ├── views.py
│   └── ...
├── staticfiles/             # Genere par collectstatic
├── media/                   # Uploads utilisateurs
├── requirements.txt
└── seed_data.py             # Donnees de demonstration

/etc/systemd/system/
├── gunicorn.socket
└── gunicorn.service

/etc/nginx/sites-available/
└── taskmanager

/etc/ssl/taskmanager/
├── cert.pem
└── key.pem

/var/log/
├── nginx/taskmanager_access.log
├── nginx/taskmanager_error.log
├── gunicorn/access.log
└── gunicorn/error.log
```

---

*Rapport de TP — Institut Africain d'Informatique — Libreville, Gabon — 2025/2026*
