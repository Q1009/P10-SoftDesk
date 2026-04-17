from django.db import models, transaction
from django.conf import settings
import uuid

# Create your models here.
class Project(models.Model):
    BACK_END = 'BE'
    FRONT_END = 'FE'
    IOS = 'IOS'
    ANDROID = 'AND'

    PROJECT_TYPE_CHOICES = (
        (BACK_END, 'Back-end'),
        (FRONT_END, 'Front-end'),
        (IOS, 'iOS'),
        (ANDROID, 'Android'),
    )

    name = models.CharField(max_length=255, verbose_name='Nom du projet')
    project_type = models.CharField(max_length=3, choices=PROJECT_TYPE_CHOICES, verbose_name='Type de projet')
    description = models.TextField(max_length=1000, verbose_name='Description')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Auteur')
    contributors = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ProjectContributor', related_name='contributed_projects', blank=True, verbose_name='Contributeurs')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de mise à jour')

    def __str__(self):
        return self.name
    
    @transaction.atomic
    def add_contributor(self, user, contribution):
        if not self.contributors.filter(id=user.id).exists():
            ProjectContributor.objects.create(project=self, contributor=user, contribution=contribution)
        else:
            raise ValueError("L'utilisateur est déjà un contributeur de ce projet.")

    @transaction.atomic
    def remove_contributor(self, user):
        if user == self.author:
            raise ValueError("Impossible de retirer l'auteur du projet.")
        deleted, _ = ProjectContributor.objects.filter(project=self, contributor=user).delete()
        if not deleted:
            raise ValueError("Cet utilisateur n'est pas contributeur de ce projet.")
        

class ProjectContributor(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Projet')
    contributor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Utilisateur')
    contribution = models.CharField(max_length=255, verbose_name='Contribution')

    class Meta:
        unique_together = ('project', 'contributor')

    def __str__(self):
        return f"{self.contributor.username} - {self.project.name} ({self.contribution})"
    
class Issue(models.Model):
    TO_DO = 'TO_DO'
    IN_PROGRESS = 'IN_PROGRESS'
    FINISHED = 'FINISHED'

    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'

    BUG = 'BUG'
    FEATURE = 'FEATURE'
    TASK = 'TASK'

    ISSUE_TYPE_CHOICES = (
        (BUG, 'Bug'),
        (FEATURE, 'Fonctionnalité'),
        (TASK, 'Tâche'),
    )

    PRIORITY_CHOICES = (
        (LOW, 'Faible'),
        (MEDIUM, 'Moyenne'),
        (HIGH, 'Élevée'),
    )

    STATUS_CHOICES = (
        (TO_DO, 'À faire'),
        (IN_PROGRESS, 'En cours'),
        (FINISHED, 'Terminé'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues', verbose_name='Projet')
    title = models.CharField(max_length=255, verbose_name='Titre de l\'issue')
    description = models.TextField(max_length=1000, verbose_name='Description de l\'issue')
    type = models.CharField(max_length=10, choices=ISSUE_TYPE_CHOICES, default=TASK, verbose_name='Type de l\'issue')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=TO_DO, verbose_name='Statut de l\'issue')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=MEDIUM, verbose_name='Priorité de l\'issue')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_issues', verbose_name='Auteur de l\'issue')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues', verbose_name='Assigné à')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de mise à jour')

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    unique_id = models.AutoField(primary_key=True, verbose_name='ID unique du commentaire')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID du commentaire')
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments', verbose_name='Issue')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments', verbose_name='Auteur du commentaire')
    content = models.TextField(max_length=1000, verbose_name='Description')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de mise à jour')

    def __str__(self):
        return f"Commentaire de {self.author.username} sur {self.issue.title}"