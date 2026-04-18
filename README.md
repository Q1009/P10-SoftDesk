# SoftDesk Support API

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-green)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.17-red)](https://www.django-rest-framework.org/)

API REST de suivi et de remontée de problèmes techniques sur des applications informatiques.
Développée avec Django REST Framework, elle permet la gestion de projets, d'issues et de commentaires avec un système de permissions basé sur les contributeurs.

---

## Prérequis

- Python 3.13+
- [Poetry](https://python-poetry.org/docs/#installation)

---

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/quentintellier/p10-softdesk.git
cd p10-softdesk
```

### 2. Installer les dépendances

```bash
poetry install
```

### 3. Appliquer les migrations

```bash
poetry run python manage.py migrate
```

### 4. (Optionnel) Charger des données de démonstration

```bash
# Initialisation (idempotent)
poetry run python manage.py seed_data

# Réinitialisation complète
poetry run python manage.py seed_data --reset
```

> Mot de passe des comptes de démo : `DemoPass2026!`

### 5. Lancer le serveur

```bash
poetry run python manage.py runserver
```

L'API est accessible sur `http://127.0.0.1:8000/`.

---

## Authentification

L'API utilise des **JWT (JSON Web Tokens)** via `djangorestframework-simplejwt`.

| Méthode | Endpoint | Description |
|---|---|---|
| POST | `/api/token/` | Obtenir un access token et un refresh token |
| POST | `/api/token/refresh/` | Renouveler l'access token |

**Exemple de requête :**

```json
POST /api/token/
{
    "username": "alice_martin",
    "password": "DemoPass2026!"
}
```

Inclure le token dans toutes les requêtes suivantes :

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### Utilisateurs

| Méthode | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/users/register/` | Créer un compte | Non |
| GET | `/api/users/me/` | Consulter son profil | Oui |
| PATCH | `/api/users/me/` | Modifier son profil | Oui |
| DELETE | `/api/users/me/` | Supprimer son compte (droit à l'oubli) | Oui |

**Champs requis à l'inscription :**

```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "motdepasse123",
    "date_of_birth": "1995-06-15",
    "can_be_contacted": true,
    "can_data_be_shared": false
}
```

> L'âge minimum requis est de **15 ans** (conformité RGPD).

---

### Projets

| Méthode | Endpoint | Description | Restriction |
|---|---|---|---|
| GET | `/api/projects/` | Lister les projets | Authentifié |
| POST | `/api/projects/` | Créer un projet | Authentifié |
| GET | `/api/projects/{id}/` | Détail d'un projet | Contributeur |
| PATCH | `/api/projects/{id}/` | Modifier un projet | Auteur |
| DELETE | `/api/projects/{id}/` | Supprimer un projet | Auteur |
| POST | `/api/projects/{id}/add-contributor/` | Ajouter un contributeur | Auteur |
| POST | `/api/projects/{id}/remove-contributor/` | Retirer un contributeur | Auteur |

**Champs requis à la création :**

```json
{
    "name": "Mon projet",
    "description": "Description du projet",
    "project_type": "BE"
}
```

> Types de projet : `BE` (Back-end), `FE` (Front-end), `IOS`, `AND` (Android)

**Ajouter un contributeur :**

```json
POST /api/projects/{id}/add-contributor/
{
    "user_id": 3,
    "contribution": "Développeur"
}
```

---

### Issues

| Méthode | Endpoint | Description | Restriction |
|---|---|---|---|
| GET | `/api/projects/{project_pk}/issues/` | Lister les issues | Contributeur |
| POST | `/api/projects/{project_pk}/issues/` | Créer une issue | Contributeur |
| GET | `/api/projects/{project_pk}/issues/{id}/` | Détail d'une issue | Contributeur |
| PATCH | `/api/projects/{project_pk}/issues/{id}/` | Modifier une issue | Auteur |
| DELETE | `/api/projects/{project_pk}/issues/{id}/` | Supprimer une issue | Auteur |

**Champs requis à la création :**

```json
{
    "title": "Titre de l'issue",
    "description": "Description",
    "assignee": 2
}
```

> `assignee` doit être l'`id` d'un contributeur du projet. Les champs `project` et `author` sont automatiquement renseignés.

**Champs disponibles en modification (PATCH) :**

| Champ | Valeurs possibles |
|---|---|
| `type` | `BUG`, `FEATURE`, `TASK` |
| `priority` | `LOW`, `MEDIUM`, `HIGH` |
| `status` | `TO_DO`, `IN_PROGRESS`, `FINISHED` |

---

### Commentaires

| Méthode | Endpoint | Description | Restriction |
|---|---|---|---|
| GET | `/api/projects/{project_pk}/issues/{issue_pk}/comments/` | Lister les commentaires | Contributeur |
| POST | `/api/projects/{project_pk}/issues/{issue_pk}/comments/` | Créer un commentaire | Contributeur |
| GET | `/api/projects/{project_pk}/issues/{issue_pk}/comments/{id}/` | Détail d'un commentaire | Contributeur |
| PATCH | `/api/projects/{project_pk}/issues/{issue_pk}/comments/{id}/` | Modifier un commentaire | Auteur |
| DELETE | `/api/projects/{project_pk}/issues/{issue_pk}/comments/{id}/` | Supprimer un commentaire | Auteur |

**Champs requis à la création :**

```json
{
    "content": "Contenu du commentaire"
}
```

> Les champs `issue` et `author` sont automatiquement renseignés.

---

## Permissions

| Rôle | Droits |
|---|---|
| Non authentifié | Inscription uniquement |
| Authentifié | Créer un projet, consulter ses projets |
| Contributeur | Lire les ressources du projet, créer des issues et commentaires |
| Auteur | Modifier et supprimer ses propres ressources, gérer les contributeurs |

---

## Pagination

Les listes sont paginées par défaut avec **5 éléments par page**.

Paramètres disponibles : `limit` et `offset`.

```
GET /api/projects/?limit=10&offset=0
```

---

## Qualité du code

Analyse PEP8 avec flake8 :

```bash
poetry run flake8 --format=html --htmldir=flake8-report
```

Le rapport HTML est généré dans `flake8-report/index.html`.
