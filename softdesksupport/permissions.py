from rest_framework.permissions import BasePermission

from .models import Project, Issue, Comment


class IsContributor(BasePermission):

    def has_permission(self, request, view):
        """
        Called by DRF before every action (list, create, retrieve, update, destroy).

        1. Checks that the user is authenticated. If not, access is denied.

        2. Retrieves project_pk from the URL parameters (view.kwargs):
           - On /projects/3/issues/ -> project_pk = 3
           - On /projects/           -> project_pk = None

        3. If project_pk is present (nested URL for issues/comments):
           Checks in the database that the user is a contributor of the project.
           This also protects 'create', because has_object_permission is not
           called for that action (no existing object at that point).

        4. If project_pk is absent (URL /projects/):
           Allows any authenticated user through.
           Ownership checks for retrieve/update/destroy are then handled
           by has_object_permission.
        """
        if not (request.user and request.user.is_authenticated):
            return False
        project_pk = view.kwargs.get('project_pk')
        if project_pk:
            return Project.objects.filter(pk=project_pk, contributors=request.user).exists()
        return True

    def has_object_permission(self, request, view, obj):
        """
        Called by DRF only after an existing object has been retrieved via
        get_object() (retrieve, update, destroy). Never called on create.
        - For read actions: checks that the user is a contributor of the project.
        - For write actions (update, destroy): checks that the user is the author.
        """
        WRITE_ACTIONS = ('update', 'partial_update', 'destroy', 'add_contributor', 'remove_contributor')

        if isinstance(obj, Project):
            if view.action in WRITE_ACTIONS:
                return request.user == obj.author
            return obj.contributors.filter(id=request.user.id).exists()

        if isinstance(obj, Issue):
            if view.action in WRITE_ACTIONS:
                return request.user == obj.author
            return obj.project.contributors.filter(id=request.user.id).exists()

        if isinstance(obj, Comment):
            if view.action in WRITE_ACTIONS:
                return request.user == obj.author
            return obj.issue.project.contributors.filter(id=request.user.id).exists()

        return False
