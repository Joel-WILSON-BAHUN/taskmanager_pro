from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('register/', views.register_view, name='register'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Projects
    path('projects/',                   views.project_list,   name='project_list'),
    path('projects/new/',               views.project_create, name='project_create'),
    path('projects/<int:pk>/',          views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/',     views.project_edit,   name='project_edit'),
    path('projects/<int:pk>/delete/',   views.project_delete, name='project_delete'),

    # Tasks
    path('tasks/',                      views.task_list,          name='task_list'),
    path('tasks/new/',                  views.task_create,        name='task_create'),
    path('tasks/<int:pk>/',             views.task_detail,        name='task_detail'),
    path('tasks/<int:pk>/edit/',        views.task_edit,          name='task_edit'),
    path('tasks/<int:pk>/delete/',      views.task_delete,        name='task_delete'),
    path('tasks/<int:pk>/status/',      views.task_update_status, name='task_update_status'),

    # Users (admin d'entreprise)
    path('users/',                      views.user_list,   name='user_list'),
    path('users/new/',                  views.user_create, name='user_create'),
    path('users/<int:pk>/edit/',        views.user_edit,   name='user_edit'),
    path('users/<int:pk>/delete/',      views.user_delete, name='user_delete'),

    # Profile
    path('profile/', views.profile_view, name='profile'),

    # Tenants (super admin uniquement)
    path('tenants/',                    views.tenant_list,   name='tenant_list'),
    path('tenants/new/',                views.tenant_create, name='tenant_create'),
    path('tenants/<int:pk>/',           views.tenant_detail, name='tenant_detail'),
    path('tenants/<int:pk>/edit/',      views.tenant_edit,   name='tenant_edit'),
    path('tenants/<int:pk>/delete/',    views.tenant_delete, name='tenant_delete'),
]
