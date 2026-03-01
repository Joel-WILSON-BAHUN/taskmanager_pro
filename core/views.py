from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count

from .models import User, Tenant, Project, Task
from .forms import (
    LoginForm, RegisterForm, UserCreateForm, UserEditForm,
    TenantForm, TenantEditForm, ProjectForm, TaskForm, ProfileForm, TaskStatusForm
)


# ─── Auth ─────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenue, {user.get_full_name() or user.username} !")
            return redirect('dashboard')
        messages.error(request, "Identifiants incorrects.")
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('login')


def register_view(request):
    """Inscription publique — choisit soi-même son tenant."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Compte créé avec succès !")
        return redirect('dashboard')
    return render(request, 'core/register.html', {'form': form})


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    tenant = request.user.tenant
    today  = timezone.now().date()

    if not tenant:
        return render(request, 'core/no_tenant.html')

    tasks_qs    = Task.objects.filter(tenant=tenant)
    projects_qs = Project.objects.filter(tenant=tenant)

    stats = {
        'total_projects':   projects_qs.count(),
        'total_tasks':      tasks_qs.count(),
        'tasks_todo':       tasks_qs.filter(statut='todo').count(),
        'tasks_inprogress': tasks_qs.filter(statut='inprogress').count(),
        'tasks_done':       tasks_qs.filter(statut='done').count(),
        'total_users':      User.objects.filter(tenant=tenant).count(),
    }

    urgent_tasks   = tasks_qs.filter(date_limite__lte=today, statut__in=['todo','inprogress']) \
                              .select_related('projet','assigne_a').order_by('date_limite')[:5]
    my_tasks       = tasks_qs.filter(assigne_a=request.user).exclude(statut='done') \
                              .select_related('projet').order_by('date_limite')[:5]
    recent_projects = projects_qs.prefetch_related('membres').order_by('-date_creation')[:4]

    chart_data = {
        'labels': ['À faire','En cours','Terminé'],
        'data':   [stats['tasks_todo'], stats['tasks_inprogress'], stats['tasks_done']],
        'colors': ['#94a3b8','#f59e0b','#10b981'],
    }
    projects_chart = list(
        projects_qs.annotate(task_count=Count('tasks')).values('nom','task_count')[:6]
    )

    return render(request, 'core/dashboard.html', {
        'stats': stats, 'urgent_tasks': urgent_tasks, 'my_tasks': my_tasks,
        'recent_projects': recent_projects, 'chart_data': chart_data,
        'projects_chart': projects_chart, 'today': today,
    })


# ─── Projects ─────────────────────────────────────────────────────────────────

@login_required
def project_list(request):
    tenant   = request.user.tenant
    projects = Project.objects.filter(tenant=tenant).prefetch_related('membres') \
                              .annotate(task_count=Count('tasks')).order_by('-date_creation')
    search = request.GET.get('search','')
    if search:
        projects = projects.filter(nom__icontains=search)
    return render(request, 'core/project_list.html', {'projects': projects, 'search': search})


@login_required
def project_detail(request, pk):
    tenant  = request.user.tenant
    project = get_object_or_404(Project, pk=pk, tenant=tenant)
    return render(request, 'core/project_detail.html', {
        'project':          project,
        'tasks_todo':       project.tasks.filter(statut='todo').select_related('assigne_a'),
        'tasks_inprogress': project.tasks.filter(statut='inprogress').select_related('assigne_a'),
        'tasks_done':       project.tasks.filter(statut='done').select_related('assigne_a'),
    })


@login_required
def project_create(request):
    if not request.user.is_admin:
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('project_list')
    tenant = request.user.tenant
    form   = ProjectForm(request.POST or None, tenant=tenant)
    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        project.tenant     = tenant
        project.created_by = request.user
        project.save(); form.save_m2m()
        messages.success(request, f"Projet « {project.nom} » créé !")
        return redirect('project_detail', pk=project.pk)
    return render(request, 'core/project_form.html', {'form': form, 'action': 'Créer'})


@login_required
def project_edit(request, pk):
    if not request.user.is_admin:
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('project_list')
    tenant  = request.user.tenant
    project = get_object_or_404(Project, pk=pk, tenant=tenant)
    form    = ProjectForm(request.POST or None, instance=project, tenant=tenant)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Projet mis à jour.")
        return redirect('project_detail', pk=project.pk)
    return render(request, 'core/project_form.html', {'form': form, 'project': project, 'action': 'Modifier'})


@login_required
def project_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('project_list')
    tenant  = request.user.tenant
    project = get_object_or_404(Project, pk=pk, tenant=tenant)
    if request.method == 'POST':
        project.delete()
        messages.success(request, "Projet supprimé.")
        return redirect('project_list')
    return render(request, 'core/confirm_delete.html', {'object': project, 'type': 'projet'})


# ─── Tasks ────────────────────────────────────────────────────────────────────

@login_required
def task_list(request):
    tenant = request.user.tenant
    tasks  = Task.objects.filter(tenant=tenant).select_related('projet','assigne_a')

    statut     = request.GET.get('statut','')
    priorite   = request.GET.get('priorite','')
    project_id = request.GET.get('project','')
    assigned   = request.GET.get('assigned','')
    search     = request.GET.get('search','')

    if statut:     tasks = tasks.filter(statut=statut)
    if priorite:   tasks = tasks.filter(priorite=priorite)
    if project_id: tasks = tasks.filter(projet_id=project_id)
    if assigned == 'me': tasks = tasks.filter(assigne_a=request.user)
    if search:     tasks = tasks.filter(titre__icontains=search)

    return render(request, 'core/task_list.html', {
        'tasks':    tasks,
        'projects': Project.objects.filter(tenant=tenant),
        'filters':  {'statut':statut,'priorite':priorite,'project':project_id,'assigned':assigned,'search':search},
    })


@login_required
def task_create(request):
    tenant     = request.user.tenant
    project_id = request.GET.get('project')
    project    = get_object_or_404(Project, pk=project_id, tenant=tenant) if project_id else None
    form       = TaskForm(request.POST or None, tenant=tenant, project=project)
    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.tenant     = tenant
        task.created_by = request.user
        task.save()
        messages.success(request, f"Tâche « {task.titre} » créée.")
        return redirect('project_detail', pk=project.pk) if project else redirect('task_list')
    return render(request, 'core/task_form.html', {'form': form, 'project': project, 'action': 'Créer'})


@login_required
def task_detail(request, pk):
    tenant = request.user.tenant
    task   = get_object_or_404(Task, pk=pk, tenant=tenant)
    return render(request, 'core/task_detail.html', {'task': task})


@login_required
def task_edit(request, pk):
    tenant = request.user.tenant
    task   = get_object_or_404(Task, pk=pk, tenant=tenant)
    if not request.user.is_admin and task.assigne_a != request.user:
        messages.error(request, "Vous ne pouvez pas modifier cette tâche.")
        return redirect('task_list')
    form = TaskForm(request.POST or None, instance=task, tenant=tenant)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Tâche mise à jour.")
        return redirect('task_detail', pk=task.pk)
    return render(request, 'core/task_form.html', {'form': form, 'task': task, 'action': 'Modifier'})


@login_required
def task_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('task_list')
    tenant = request.user.tenant
    task   = get_object_or_404(Task, pk=pk, tenant=tenant)
    if request.method == 'POST':
        project = task.projet
        task.delete()
        messages.success(request, "Tâche supprimée.")
        return redirect('project_detail', pk=project.pk)
    return render(request, 'core/confirm_delete.html', {'object': task, 'type': 'tâche'})


@login_required
def task_update_status(request, pk):
    tenant = request.user.tenant
    task   = get_object_or_404(Task, pk=pk, tenant=tenant)
    if request.method == 'POST':
        new_status = request.POST.get('statut')
        if new_status in ['todo','inprogress','done']:
            task.statut = new_status
            task.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'statut': task.get_statut_display()})
            messages.success(request, "Statut mis à jour.")
    return redirect(request.META.get('HTTP_REFERER','task_list'))


# ─── Users (admin d'entreprise) ───────────────────────────────────────────────

@login_required
def user_list(request):
    if not request.user.is_admin:
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('dashboard')
    tenant = request.user.tenant
    users  = User.objects.filter(tenant=tenant).annotate(task_count=Count('tasks'))
    return render(request, 'core/user_list.html', {'users': users})


@login_required
def user_create(request):
    """
    L'admin d'une entreprise crée un utilisateur dans SON tenant uniquement.
    Le tenant est forcé côté serveur — l'admin ne peut pas choisir un autre tenant.
    """
    if not request.user.is_admin:
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('dashboard')

    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.tenant = request.user.tenant   # ← forcé sur le tenant de l'admin
        user.save()
        messages.success(request, f"Utilisateur « {user.username} » créé dans {user.tenant.nom}.")
        return redirect('user_list')

    return render(request, 'core/user_form.html', {
        'form':   form,
        'action': 'Créer',
        'title':  'Ajouter un utilisateur',
    })


@login_required
def user_edit(request, pk):
    """Modifier un utilisateur du même tenant."""
    if not request.user.is_admin:
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('dashboard')

    tenant = request.user.tenant
    target = get_object_or_404(User, pk=pk, tenant=tenant)  # isolation tenant

    # Empêcher de modifier un autre admin si on n'est pas superuser
    if target.role == 'admin' and not request.user.is_superuser and target != request.user:
        messages.error(request, "Vous ne pouvez pas modifier un autre administrateur.")
        return redirect('user_list')

    form = UserEditForm(request.POST or None, instance=target)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"Utilisateur « {target.username} » mis à jour.")
        return redirect('user_list')

    return render(request, 'core/user_form.html', {
        'form':   form,
        'action': 'Modifier',
        'title':  f'Modifier {target.get_full_name() or target.username}',
        'target': target,
    })


@login_required
def user_delete(request, pk):
    """Supprimer un utilisateur du même tenant."""
    if not request.user.is_admin:
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('dashboard')

    tenant = request.user.tenant
    target = get_object_or_404(User, pk=pk, tenant=tenant)

    if target == request.user:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('user_list')

    if request.method == 'POST':
        username = target.username
        target.delete()
        messages.success(request, f"Utilisateur « {username} » supprimé.")
        return redirect('user_list')

    return render(request, 'core/confirm_delete.html', {'object': target, 'type': 'utilisateur'})


@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profil mis à jour.")
        return redirect('profile')
    my_tasks = Task.objects.filter(assigne_a=request.user).select_related('projet').order_by('date_limite')[:10]
    return render(request, 'core/profile.html', {'form': form, 'my_tasks': my_tasks})


# ─── Tenants (super admin) ────────────────────────────────────────────────────

@login_required
def tenant_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Accès réservé au super-administrateur.")
        return redirect('dashboard')
    tenants = Tenant.objects.all().annotate(
        user_count=Count('users', distinct=True),
        project_count=Count('projects', distinct=True),
    ).order_by('nom')
    return render(request, 'core/tenant_list.html', {'tenants': tenants})


@login_required
def tenant_create(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    form = TenantForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        tenant = form.save()
        messages.success(request, f"Entreprise « {tenant.nom} » créée.")
        return redirect('tenant_list')
    return render(request, 'core/tenant_form.html', {'form': form, 'action': 'Créer'})


@login_required
def tenant_edit(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard')
    tenant = get_object_or_404(Tenant, pk=pk)
    form   = TenantEditForm(request.POST or None, instance=tenant)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"Entreprise « {tenant.nom} » mise à jour.")
        return redirect('tenant_list')
    return render(request, 'core/tenant_form.html', {'form': form, 'tenant': tenant, 'action': 'Modifier'})


@login_required
def tenant_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard')
    tenant = get_object_or_404(Tenant, pk=pk)
    if request.method == 'POST':
        name = tenant.nom
        tenant.delete()
        messages.success(request, f"Entreprise « {name} » supprimée.")
        return redirect('tenant_list')
    return render(request, 'core/confirm_delete.html', {'object': tenant, 'type': 'entreprise'})


@login_required
def tenant_detail(request, pk):
    """Vue détail d'un tenant pour le superadmin : users + projets."""
    if not request.user.is_superuser:
        return redirect('dashboard')
    tenant   = get_object_or_404(Tenant, pk=pk)
    users    = User.objects.filter(tenant=tenant).annotate(task_count=Count('tasks'))
    projects = Project.objects.filter(tenant=tenant).annotate(task_count=Count('tasks'))
    return render(request, 'core/tenant_detail.html', {
        'tenant': tenant, 'users': users, 'projects': projects,
    })


