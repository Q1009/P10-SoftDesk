from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from .models import Project, Issue, Comment
from .serializers import ProjectDetailSerializer, ProjectListSerializer, IssueDetailSerializer, IssueListSerializer, CommentSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsContributor

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
    permission_classes = [IsAuthenticated, IsContributor]

    def get_queryset(self):
        # L'action retrieve est protégée par IsContributor, donc on peut retourner tous les projets ici
        return Project.objects.all()
    
    @action(detail=True, methods=['post'], url_path='add-contributor')
    def add_contributor(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get('user_id')
        contribution = request.data.get('contribution')

        if not user_id or not contribution:
            return Response({'error': 'user_id and contribution are required.'}, status=400)

        try:
            project.add_contributor(user_id, contribution)
            return Response({'status': 'contributor added'}, status=200)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
    
class IssueViewset(MultipleSerializerMixin, ModelViewSet):

    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer
    permission_classes = [IsAuthenticated, IsContributor]

    def get_queryset(self):
        return Issue.objects.filter(
            project_id=self.kwargs['project_pk'],
            project__contributors=self.request.user,
        )

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        serializer.save(project=project, author=self.request.user)

class CommentViewset(ModelViewSet):

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsContributor]

    def get_queryset(self):
        return Comment.objects.filter(
            issue_id=self.kwargs['issue_pk'],
            issue__project_id=self.kwargs['project_pk'],
            issue__project__contributors=self.request.user,
        )

    def perform_create(self, serializer):
        issue = get_object_or_404(Issue, pk=self.kwargs['issue_pk'], project_id=self.kwargs['project_pk'])
        serializer.save(issue=issue, author=self.request.user)