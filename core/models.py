from django.db import models
from django.contrib.auth.models import AbstractUser


class Tenant(models.Model):
    """Entreprise / Organisation (multi-tenant)"""
    nom = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    description = models.TextField(blank=True, verbose_name="Description")
    date_creation = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def get_stats(self):
        projects = self.projects.count()
        tasks = Task.objects.filter(projet__tenant=self)
        return {
            'projects': projects,
            'tasks_todo': tasks.filter(statut='todo').count(),
            'tasks_inprogress': tasks.filter(statut='inprogress').count(),
            'tasks_done': tasks.filter(statut='done').count(),
            'tasks_total': tasks.count(),
        }


class User(AbstractUser):
    """Utilisateur lié à un tenant avec un rôle"""
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('employee', 'Employé'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Entreprise"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='employee',
        verbose_name="Rôle"
    )
    bio = models.TextField(blank=True, verbose_name="Biographie")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    def get_pending_tasks(self):
        return self.tasks.exclude(statut='done').count()


class Project(models.Model):
    """Projet appartenant à un tenant"""
    nom = models.CharField(max_length=200, verbose_name="Nom du projet")
    description = models.TextField(blank=True, verbose_name="Description")
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name="Entreprise"
    )
    membres = models.ManyToManyField(
        User,
        blank=True,
        related_name='projects',
        verbose_name="Membres"
    )
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    date_creation = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_projects',
        verbose_name="Créé par"
    )

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-date_creation']

    def __str__(self):
        return self.nom

    def get_progress(self):
        total = self.tasks.count()
        if total == 0:
            return 0
        done = self.tasks.filter(statut='done').count()
        return int((done / total) * 100)

    def get_status_color(self):
        progress = self.get_progress()
        if progress == 100:
            return 'success'
        elif progress >= 50:
            return 'warning'
        return 'danger'


class Task(models.Model):
    """Tâche liée à un projet et assignée à un utilisateur"""
    STATUT_CHOICES = [
        ('todo', 'À faire'),
        ('inprogress', 'En cours'),
        ('done', 'Terminé'),
    ]
    PRIORITE_CHOICES = [
        ('low', 'Basse'),
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
    ]

    titre = models.CharField(max_length=300, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    projet = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Projet"
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Entreprise"
    )
    assigne_a = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name="Assigné à"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='todo',
        verbose_name="Statut"
    )
    priorite = models.CharField(
        max_length=10,
        choices=PRIORITE_CHOICES,
        default='medium',
        verbose_name="Priorité"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_limite = models.DateField(null=True, blank=True, verbose_name="Date limite")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
        verbose_name="Créé par"
    )

    class Meta:
        verbose_name = "Tâche"
        verbose_name_plural = "Tâches"
        ordering = ['-date_creation']

    def __str__(self):
        return self.titre

    def get_statut_badge(self):
        badges = {
            'todo': 'secondary',
            'inprogress': 'warning',
            'done': 'success',
        }
        return badges.get(self.statut, 'secondary')

    def get_priorite_badge(self):
        badges = {
            'low': 'info',
            'medium': 'warning',
            'high': 'danger',
        }
        return badges.get(self.priorite, 'secondary')

    def is_overdue(self):
        from django.utils import timezone
        if self.date_limite and self.statut != 'done':
            return self.date_limite < timezone.now().date()
        return False
