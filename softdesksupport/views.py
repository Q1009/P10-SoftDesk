from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Project, Issue, Comment
from .permissions import IsContributor
from .serializers import (
    ProjectDetailSerializer,
    ProjectListSerializer,
    IssueDetailSerializer,
    IssueListSerializer,
    CommentSerializer,
)

User = get_user_model()


class MultipleSerializerMixin:
    detail_serializer_class = None

    def get_serializer_class(self):
        if (
            self.action in ("retrieve", "update", "partial_update")
            and self.detail_serializer_class is not None
        ):
            return self.detail_serializer_class
        return super().get_serializer_class()


class ProjectViewset(MultipleSerializerMixin, ModelViewSet):

    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer
    permission_classes = [IsAuthenticated, IsContributor]

    def get_queryset(self):
        # L'action retrieve est protégée par IsContributor, donc on peut retourner tous les projets ici
        return Project.objects.select_related("author").prefetch_related(
            "contributors", "issues"
        )

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        project.add_contributor(self.request.user, "Auteur")

    @action(detail=True, methods=["post"], url_path="add-contributor")
    def add_contributor(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get("user_id")
        contribution = request.data.get("contribution")

        if not user_id or not contribution:
            return Response(
                {"error": "user_id and contribution are required."}, status=400
            )

        user = get_object_or_404(User, pk=user_id)
        try:
            project.add_contributor(user, contribution)
            return Response(
                {"status": f"{user.first_name} {user.last_name} contribue au projet !"},
                status=200,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=True, methods=["post"], url_path="remove-contributor")
    def remove_contributor(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id is required."}, status=400)
        user = get_object_or_404(User, pk=user_id)
        try:
            project.remove_contributor(user)
            return Response(
                {
                    "status": f"{user.first_name} {user.last_name} ne contribue plus au projet."
                },
                status=200,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=400)


class IssueViewset(MultipleSerializerMixin, ModelViewSet):

    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer
    permission_classes = [IsAuthenticated, IsContributor]

    def get_queryset(self):
        return Issue.objects.filter(
            project_id=self.kwargs["project_pk"],
            project__contributors=self.request.user,
        ).select_related("author", "assignee", "project")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        project_pk = self.kwargs.get("project_pk")
        if project_pk:
            context["project_id"] = project_pk
            context["project"] = get_object_or_404(
                Project.objects.prefetch_related("contributors"), pk=project_pk
            )
        return context

    def perform_create(self, serializer):
        project = self.get_serializer_context()["project"]
        serializer.save(project=project, author=self.request.user)


class CommentViewset(ModelViewSet):

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsContributor]

    def get_queryset(self):
        return Comment.objects.filter(
            issue_id=self.kwargs["issue_pk"],
            issue__project_id=self.kwargs["project_pk"],
            issue__project__contributors=self.request.user,
        ).select_related("author", "issue__project")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["project_id"] = self.kwargs.get("project_pk")
        return context

    def perform_create(self, serializer):
        issue = get_object_or_404(
            Issue, pk=self.kwargs["issue_pk"], project_id=self.kwargs["project_pk"]
        )
        serializer.save(issue=issue, author=self.request.user)
