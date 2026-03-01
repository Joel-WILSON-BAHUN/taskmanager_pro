"""
Commande de génération de données de démonstration.
Usage: python manage.py seed_data
"""
import os
import sys
import django

def create_demo_data():
    from django.contrib.auth.hashers import make_password
    from core.models import Tenant, User, Project, Task
    from django.utils import timezone
    from datetime import date, timedelta

    print("🌱 Création des données de démonstration...")

    # Supprimer les données existantes
    Task.objects.all().delete()
    Project.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    Tenant.objects.all().delete()

    # ─── Tenants ────────────────────────────────────────────
    entreprise_a = Tenant.objects.create(
        nom="TechCorp Solutions",
        description="Entreprise spécialisée en développement logiciel"
    )
    entreprise_b = Tenant.objects.create(
        nom="InnovateLab",
        description="Startup IA & Data Science"
    )

    # ─── Users – Entreprise A ────────────────────────────────
    admin_a = User.objects.create(
        username="admin_a",
        email="admin@techcorp.com",
        first_name="Alice",
        last_name="Martin",
        tenant=entreprise_a,
        role="admin",
        is_active=True,
        password=make_password("admin123")
    )
    emp_a1 = User.objects.create(
        username="emp_a",
        email="bob@techcorp.com",
        first_name="Bob",
        last_name="Dupont",
        tenant=entreprise_a,
        role="employee",
        is_active=True,
        password=make_password("emp123")
    )
    emp_a2 = User.objects.create(
        username="clara_a",
        email="clara@techcorp.com",
        first_name="Clara",
        last_name="Bernard",
        tenant=entreprise_a,
        role="employee",
        is_active=True,
        password=make_password("emp123")
    )

    # ─── Users – Entreprise B ────────────────────────────────
    admin_b = User.objects.create(
        username="admin_b",
        email="admin@innovatelab.com",
        first_name="David",
        last_name="Leroy",
        tenant=entreprise_b,
        role="admin",
        is_active=True,
        password=make_password("admin123")
    )
    emp_b1 = User.objects.create(
        username="emp_b",
        email="eva@innovatelab.com",
        first_name="Eva",
        last_name="Petit",
        tenant=entreprise_b,
        role="employee",
        is_active=True,
        password=make_password("emp123")
    )

    # ─── Projects – Entreprise A ─────────────────────────────
    proj1 = Project.objects.create(
        nom="Refonte Site Web",
        description="Modernisation complète du site institutionnel avec React et Django REST",
        tenant=entreprise_a,
        date_debut=date.today() - timedelta(days=30),
        date_fin=date.today() + timedelta(days=30),
        created_by=admin_a
    )
    proj1.membres.set([admin_a, emp_a1, emp_a2])

    proj2 = Project.objects.create(
        nom="Application Mobile CRM",
        description="Développement d'une app mobile pour la gestion des clients",
        tenant=entreprise_a,
        date_debut=date.today() - timedelta(days=10),
        date_fin=date.today() + timedelta(days=60),
        created_by=admin_a
    )
    proj2.membres.set([emp_a1, emp_a2])

    proj3 = Project.objects.create(
        nom="Migration Cloud AWS",
        description="Migration de l'infrastructure on-premise vers AWS",
        tenant=entreprise_a,
        date_debut=date.today() + timedelta(days=5),
        date_fin=date.today() + timedelta(days=90),
        created_by=admin_a
    )
    proj3.membres.set([admin_a, emp_a1])

    # ─── Tasks – Projet 1 (Refonte Site) ─────────────────────
    tasks_proj1 = [
        ("Maquettes Figma", "Créer les maquettes UI/UX pour toutes les pages", "done", "high", emp_a2, -20),
        ("Développement frontend React", "Implémenter les composants React", "inprogress", "high", emp_a1, 10),
        ("API Django REST", "Créer les endpoints REST pour le backend", "inprogress", "high", admin_a, 15),
        ("Tests unitaires", "Écrire les tests Jest et pytest", "todo", "medium", emp_a1, 25),
        ("Déploiement staging", "Déployer sur l'environnement de staging", "todo", "medium", emp_a2, 28),
        ("Mise en production", "Go-live officiel", "todo", "high", admin_a, 30),
    ]
    for titre, desc, statut, prio, assigne, delta in tasks_proj1:
        Task.objects.create(
            titre=titre, description=desc, projet=proj1, tenant=entreprise_a,
            statut=statut, priorite=prio, assigne_a=assigne,
            date_limite=date.today() + timedelta(days=delta)
        )

    # ─── Tasks – Projet 2 (App Mobile) ───────────────────────
    tasks_proj2 = [
        ("Analyse des besoins", "Rédiger le cahier des charges fonctionnel", "done", "high", admin_a, -5),
        ("Choix technologique", "Choisir entre React Native et Flutter", "done", "medium", emp_a1, -3),
        ("Prototype iOS", "Développer le prototype pour iOS", "inprogress", "high", emp_a1, 15),
        ("Prototype Android", "Développer le prototype pour Android", "todo", "high", emp_a2, 20),
        ("Intégration API CRM", "Connecter l'app à l'API Salesforce", "todo", "medium", emp_a1, 45),
    ]
    for titre, desc, statut, prio, assigne, delta in tasks_proj2:
        Task.objects.create(
            titre=titre, description=desc, projet=proj2, tenant=entreprise_a,
            statut=statut, priorite=prio, assigne_a=assigne,
            date_limite=date.today() + timedelta(days=delta)
        )

    # Tâche en retard pour la démo
    Task.objects.create(
        titre="Rapport de sécurité Q3",
        description="Audit sécurité en retard - URGENT",
        projet=proj1, tenant=entreprise_a,
        statut="todo", priorite="high", assigne_a=emp_a1,
        date_limite=date.today() - timedelta(days=5)
    )

    # ─── Projects – Entreprise B ─────────────────────────────
    proj_b1 = Project.objects.create(
        nom="Modèle de Prédiction ML",
        description="Développement d'un modèle de ML pour la prédiction des ventes",
        tenant=entreprise_b,
        date_debut=date.today() - timedelta(days=15),
        date_fin=date.today() + timedelta(days=45),
        created_by=admin_b
    )
    proj_b1.membres.set([admin_b, emp_b1])

    proj_b2 = Project.objects.create(
        nom="Dashboard Analytics",
        description="Tableau de bord analytique temps réel",
        tenant=entreprise_b,
        date_debut=date.today(),
        date_fin=date.today() + timedelta(days=30),
        created_by=admin_b
    )
    proj_b2.membres.set([emp_b1])

    tasks_b = [
        ("Collecte des données", "Scraping et nettoyage des données historiques", "done", "high", emp_b1, -10, proj_b1),
        ("Entraînement du modèle", "Entraîner le modèle XGBoost", "inprogress", "high", admin_b, 10, proj_b1),
        ("Évaluation des métriques", "Calculer MAE, RMSE, R²", "todo", "medium", emp_b1, 20, proj_b1),
        ("Design du dashboard", "Créer les wireframes", "todo", "high", emp_b1, 15, proj_b2),
        ("Intégration Grafana", "Connecter les sources de données", "todo", "medium", admin_b, 25, proj_b2),
    ]
    for titre, desc, statut, prio, assigne, delta, projet in tasks_b:
        Task.objects.create(
            titre=titre, description=desc, projet=projet, tenant=entreprise_b,
            statut=statut, priorite=prio, assigne_a=assigne,
            date_limite=date.today() + timedelta(days=delta)
        )

    # ─── Superuser ───────────────────────────────────────────
    if not User.objects.filter(username="superadmin").exists():
        User.objects.create_superuser(
            username="superadmin",
            email="super@taskmanager.pro",
            password="super123",
            first_name="Super",
            last_name="Admin"
        )

    print("✅ Données créées avec succès !")
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  COMPTES DE DÉMONSTRATION")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  TechCorp Solutions (Entreprise A)")
    print("    admin_a   / admin123  → Admin")
    print("    emp_a     / emp123    → Employé")
    print("    clara_a   / emp123    → Employé")
    print()
    print("  InnovateLab (Entreprise B)")
    print("    admin_b   / admin123  → Admin")
    print("    emp_b     / emp123    → Employé")
    print()
    print("  Super Admin")
    print("    superadmin / super123 → Superuser")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


if __name__ == "__main__":
    # Allow running directly
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")
    django.setup()
    create_demo_data()
