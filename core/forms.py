from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Tenant, Project, Task


class LoginForm(AuthenticationForm):
    """Formulaire de connexion standard."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'})
    )


class RegisterForm(UserCreationForm):
    """Inscription publique (sans tenant pré-assigné)."""
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Prénom'}))
    last_name  = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Nom'}))
    email      = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'vous@exemple.com'}))
    tenant     = forms.ModelChoiceField(queryset=Tenant.objects.all(), label="Entreprise")
    role       = forms.ChoiceField(choices=User.ROLE_CHOICES, label="Rôle")

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'tenant', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('placeholder', f.label)


class UserCreateForm(UserCreationForm):
    """
    Formulaire utilisé par l'admin d'entreprise pour créer un utilisateur
    dans SON propre tenant. Le tenant est injecté en backend, pas affiché.
    """
    first_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'placeholder': 'Prénom'}))
    last_name  = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'placeholder': 'Nom'}))
    email      = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'placeholder': 'email@exemple.com'}))
    role       = forms.ChoiceField(choices=User.ROLE_CHOICES, label="Rôle", initial='employee')

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = "nom_utilisateur"


class UserEditForm(forms.ModelForm):
    """Modification d'un utilisateur par l'admin de son tenant."""
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'role', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'last_name':  forms.TextInput(attrs={'placeholder': 'Nom'}),
            'email':      forms.EmailInput(attrs={'placeholder': 'email@exemple.com'}),
            'role':       forms.Select(),
            'is_active':  forms.CheckboxInput(),
        }
        labels = {'is_active': 'Compte actif'}


class TenantForm(forms.ModelForm):
    class Meta:
        model  = Tenant
        fields = ['nom', 'description']
        widgets = {
            'nom':         forms.TextInput(attrs={'placeholder': "Nom de l'entreprise"}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Description (optionnel)'}),
        }


class TenantEditForm(forms.ModelForm):
    class Meta:
        model  = Tenant
        fields = ['nom', 'description']
        widgets = {
            'nom':         forms.TextInput(attrs={'placeholder': "Nom de l'entreprise"}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model  = Project
        fields = ['nom', 'description', 'date_debut', 'date_fin', 'membres']
        widgets = {
            'nom':         forms.TextInput(attrs={'placeholder': 'Nom du projet'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'date_debut':  forms.DateInput(attrs={'type': 'date'}),
            'date_fin':    forms.DateInput(attrs={'type': 'date'}),
            'membres':     forms.SelectMultiple(attrs={'size': '6'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['membres'].queryset = User.objects.filter(tenant=tenant)


class TaskForm(forms.ModelForm):
    class Meta:
        model  = Task
        fields = ['titre', 'description', 'projet', 'assigne_a', 'statut', 'priorite', 'date_limite']
        widgets = {
            'titre':       forms.TextInput(attrs={'placeholder': 'Titre de la tâche'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'projet':      forms.Select(),
            'assigne_a':   forms.Select(),
            'statut':      forms.Select(),
            'priorite':    forms.Select(),
            'date_limite': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['projet'].queryset   = Project.objects.filter(tenant=tenant)
            self.fields['assigne_a'].queryset = User.objects.filter(tenant=tenant)
        if project:
            self.fields['projet'].initial = project


class ProfileForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'bio']
        widgets = {
            'first_name': forms.TextInput(),
            'last_name':  forms.TextInput(),
            'email':      forms.EmailInput(),
            'bio':        forms.Textarea(attrs={'rows': 3}),
        }


class TaskStatusForm(forms.ModelForm):
    class Meta:
        model   = Task
        fields  = ['statut']
        widgets = {'statut': forms.Select()}
