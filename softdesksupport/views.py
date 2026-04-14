from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from .models import Project, Issue, Comment
from .serializers import ProjectDetailSerializer, ProjectListSerializer, IssueDetailSerializer, IssueListSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated

class MultipleSerializerMixin:
    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()

# Create your views here.
class ProjectViewset(MultipleSerializerMixin, ModelViewSet):

    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # return Project.objects.filter(author=self.request.user).order_by('-created_at')
        return Project.objects.all()
    
class IssueViewset(MultipleSerializerMixin, ModelViewSet):

    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer

    def get_queryset(self):
        return Issue.objects.filter(project_id=self.kwargs['project_pk'])

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        serializer.save(project=project, author=self.request.user)

class CommentViewset(ModelViewSet):

    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(
            issue_id=self.kwargs['issue_pk'],
            issue__project_id=self.kwargs['project_pk'],
        )

    def perform_create(self, serializer):
        issue = get_object_or_404(Issue, pk=self.kwargs['issue_pk'], project_id=self.kwargs['project_pk'])
        serializer.save(issue=issue, author=self.request.user)