from rest_framework.permissions import BasePermission
from .models import Project, Issue, Comment

class IsContributor(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            return request.user in obj.contributors.all()
        if isinstance(obj, Issue):
            return request.user in obj.project.contributors.all()
        if isinstance(obj, Comment):
            return request.user in obj.issue.project.contributors.all()
        return False