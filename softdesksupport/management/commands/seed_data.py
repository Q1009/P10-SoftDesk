import random
from django.core.management.base import BaseCommand
from django.db import transaction
from authentication.models import User
from softdesksupport.models import Project, ProjectContributor, Issue, Comment


# --- Données de référence ---

USERS_DATA = [
    {"username": "alice_martin",  "first_name": "Alice",  "last_name": "Martin",  "email": "alice.martin@example.com",  "age": 28, "can_be_contacted": True,  "can_data_be_shared": False},
    {"username": "bob_dupont",    "first_name": "Bob",    "last_name": "Dupont",   "email": "bob.dupont@example.com",    "age": 35, "can_be_contacted": False, "can_data_be_shared": False},
    {"username": "claire_bernard","first_name": "Claire", "last_name": "Bernard",  "email": "claire.bernard@example.com","age": 24, "can_be_contacted": True,  "can_data_be_shared": True},
    {"username": "david_leroy",   "first_name": "David",  "last_name": "Leroy",    "email": "david.leroy@example.com",   "age": 42, "can_be_contacted": True,  "can_data_be_shared": False},
    {"username": "emma_petit",    "first_name": "Emma",   "last_name": "Petit",    "email": "emma.petit@example.com",    "age": 31, "can_be_contacted": False, "can_data_be_shared": True},
]

PROJECTS_DATA = [
    {
        "name": "SoftDesk API",
        "project_type": Project.BACK_END,
        "description": "API REST principale du projet SoftDesk, gestion des utilisateurs, projets et issues.",
    },
    {
        "name": "SoftDesk Frontend",
        "project_type": Project.FRONT_END,
        "description": "Interface web du projet SoftDesk, consomme l'API REST.",
    },
    {
        "name": "Application iOS SoftDesk",
        "project_type": Project.IOS,
        "description": "Application mobile iOS pour accéder aux fonctionnalités SoftDesk.",
    },
    {
        "name": "Application Android SoftDesk",
        "project_type": Project.ANDROID,
        "description": "Application mobile Android pour accéder aux fonctionnalités SoftDesk.",
    },
    {
        "name": "Dashboard Analytics",
        "project_type": Project.FRONT_END,
        "description": "Tableau de bord analytique pour visualiser les métriques des projets en temps réel.",
    },
]

# Titres d'issues par type
ISSUE_TITLES = {
    Issue.BUG: [
        "Erreur 500 lors de la connexion",
        "Le token JWT expire trop tôt",
        "Crash au chargement de la liste des projets",
        "Les permissions ne sont pas correctement vérifiées",
        "L'endpoint de suppression retourne un code 200 au lieu de 204",
        "La pagination ne fonctionne pas sur les issues",
        "Doublon de données lors de la création d'un contributeur",
        "Le filtre par statut ne retourne pas les bons résultats",
        "L'image de profil n'est pas sauvegardée correctement",
        "Le champ email ne valide pas le format",
    ],
    Issue.FEATURE: [
        "Ajouter la recherche full-text sur les issues",
        "Implémenter l'export CSV des projets",
        "Permettre le tri des issues par priorité",
        "Ajouter les notifications par email",
        "Intégrer l'authentification OAuth2",
        "Ajouter un système de tags sur les issues",
        "Implémenter la pagination cursor-based",
        "Permettre l'assignation multiple sur une issue",
        "Ajouter un historique des modifications",
        "Intégrer un système de mentions dans les commentaires",
    ],
    Issue.TASK: [
        "Mettre à jour la documentation de l'API",
        "Écrire les tests unitaires pour les serializers",
        "Configurer le pipeline CI/CD",
        "Refactoriser les vues des projets",
        "Mettre à jour les dépendances Python",
        "Ajouter les indexes sur les champs filtrables",
        "Rédiger le guide de déploiement",
        "Nettoyer les migrations inutiles",
        "Configurer le logging en production",
        "Valider la conformité RGPD des données stockées",
    ],
}

# Contenus de commentaires génériques
COMMENT_CONTENTS = [
    "J'ai reproduit le problème sur mon environnement local, je vais investiguer.",
    "Cette fonctionnalité est bloquante pour la mise en production, priorité haute.",
    "J'ai commencé à travailler dessus, je ferai une PR d'ici vendredi.",
    "Avez-vous testé avec la dernière version de l'API ?",
    "Je pense que la source du problème vient des migrations. À vérifier.",
    "Lien utile : la documentation officielle Django REST Framework traite ce cas.",
    "La correction est en cours de review, merci de valider avant fusion.",
    "Problème confirmé en staging, pas uniquement en local.",
    "J'ai besoin de précisions supplémentaires sur les critères d'acceptance.",
    "Il faudrait également mettre à jour les tests automatisés en conséquence.",
    "Cette tâche dépend de la résolution de l'issue #12 dans le même projet.",
    "Voici les logs obtenus lors de la reproduction du bug :\n```\nERROR 2026-04-01 ...\n```",
    "Merge request créée, en attente de validation de l'équipe.",
    "Le problème est lié à la désérialisation des données imbriquées.",
    "Tests passés avec succès sur les environnements dev et staging.",
]


class Command(BaseCommand):
    """Commande pour initialiser la base de données avec des données de démonstration."""

    help = "Initialise la base de données avec des données de démonstration"

    def add_arguments(self, parser):
        # Option pour réinitialiser les données existantes
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Supprime les données existantes avant de créer les nouvelles",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Point d'entrée principal de la commande."""

        if options["reset"]:
            self._reset_data()

        users = self._create_users()
        projects = self._create_projects(users)
        self._create_issues_and_comments(projects, users)

        self.stdout.write(self.style.SUCCESS("\nInitialisation terminée avec succès !"))
        self._print_summary(users, projects)

    # --- Réinitialisation ---

    def _reset_data(self):
        """Supprime toutes les données liées aux utilisateurs de démonstration."""
        usernames = [u["username"] for u in USERS_DATA]
        deleted_count, _ = User.objects.filter(username__in=usernames).delete()
        self.stdout.write(self.style.WARNING(
            f"Réinitialisation : {deleted_count} utilisateur(s) supprimé(s) (cascade sur projets, issues, commentaires)."
        ))

    # --- Création des utilisateurs ---

    def _create_users(self):
        """Crée les 5 utilisateurs de démonstration s'ils n'existent pas déjà."""
        users = []
        for data in USERS_DATA:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "email": data["email"],
                    "age": data["age"],
                    "can_be_contacted": data["can_be_contacted"],
                    "can_data_be_shared": data["can_data_be_shared"],
                    "is_staff": False,
                    "is_superuser": False,
                },
            )
            if created:
                # Mot de passe sécurisé par défaut (à changer en production)
                user.set_password("DemoPass2026!")
                user.save()
                self.stdout.write(f"  Utilisateur créé : {user.username}")
            else:
                self.stdout.write(f"  Utilisateur existant ignoré : {user.username}")
            users.append(user)
        return users

    # --- Création des projets ---

    def _create_projects(self, users):
        """Crée les 5 projets et assigne des contributeurs aléatoires."""
        projects = []
        for i, data in enumerate(PROJECTS_DATA):
            # L'auteur du projet tourne parmi les utilisateurs
            author = users[i % len(users)]
            project, created = Project.objects.get_or_create(
                name=data["name"],
                defaults={
                    "project_type": data["project_type"],
                    "description": data["description"],
                    "author": author,
                },
            )
            if created:
                self._add_contributors(project, author, users)
                self.stdout.write(f"  Projet créé : {project.name} (auteur : {author.username})")
            else:
                self.stdout.write(f"  Projet existant ignoré : {project.name}")
            projects.append(project)
        return projects

    def _add_contributors(self, project, author, users):
        """Ajoute 2 à 3 contributeurs aléatoires (hors auteur) au projet."""
        ROLES = ["Développeur", "Testeur", "Reviewer", "Analyste", "Responsable QA"]
        # Sélection aléatoire de 2 à 3 autres utilisateurs comme contributeurs
        other_users = [u for u in users if u != author]
        nb_contributors = random.randint(2, min(3, len(other_users)))
        contributors = random.sample(other_users, nb_contributors)
        for user in contributors:
            ProjectContributor.objects.get_or_create(
                project=project,
                contributor=user,
                defaults={"contribution": random.choice(ROLES)},
            )

    # --- Création des issues et commentaires ---

    def _create_issues_and_comments(self, projects, users):
        """Crée entre 3 et 10 issues par projet, et entre 3 et 10 commentaires par issue."""
        issue_types = [Issue.BUG, Issue.FEATURE, Issue.TASK]
        priorities = [Issue.LOW, Issue.MEDIUM, Issue.HIGH]
        statuses = [Issue.TO_DO, Issue.IN_PROGRESS, Issue.FINISHED]

        for project in projects:
            # Ne pas recréer les issues si le projet existait déjà
            if project.issues.exists():
                self.stdout.write(f"  Issues existantes ignorées pour : {project.name}")
                continue

            nb_issues = random.randint(3, 10)
            # Pool des contributeurs du projet (auteur inclus) pour assigner des issues
            contributor_ids = list(
                ProjectContributor.objects.filter(project=project)
                .values_list("contributor_id", flat=True)
            )
            assignable_users = list(User.objects.filter(id__in=contributor_ids + [project.author_id]))

            for _ in range(nb_issues):
                issue_type = random.choice(issue_types)
                title = random.choice(ISSUE_TITLES[issue_type])
                # L'assignee peut être None (non assigné)
                assignee = random.choice(assignable_users + [None])
                issue = Issue.objects.create(
                    project=project,
                    title=title,
                    description=f"Description détaillée : {title.lower()}.",
                    status=random.choice(statuses),
                    priority=random.choice(priorities),
                    author=random.choice(assignable_users),
                    assignee=assignee,
                )
                self._create_comments(issue, assignable_users)

            self.stdout.write(f"  {nb_issues} issue(s) créée(s) pour : {project.name}")

    def _create_comments(self, issue, users):
        """Crée entre 3 et 10 commentaires pour une issue donnée."""
        nb_comments = random.randint(3, 10)
        available_contents = COMMENT_CONTENTS.copy()
        random.shuffle(available_contents)

        for i in range(nb_comments):
            content = available_contents[i % len(available_contents)]
            Comment.objects.create(
                issue=issue,
                author=random.choice(users),
                content=content,
            )

    # --- Résumé final ---

    def _print_summary(self, users, projects):
        """Affiche un résumé des données créées."""
        total_issues = sum(p.issues.count() for p in projects)
        total_comments = sum(
            Comment.objects.filter(issue__project=p).count() for p in projects
        )
        self.stdout.write(self.style.SUCCESS(
            f"\nRésumé :\n"
            f"  - {len(users)} utilisateur(s)\n"
            f"  - {len(projects)} projet(s)\n"
            f"  - {total_issues} issue(s)\n"
            f"  - {total_comments} commentaire(s)"
        ))
