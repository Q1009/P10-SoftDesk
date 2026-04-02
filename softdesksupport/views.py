from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Project, Issue, Comment
from .serializers import ProjectDetailSerializer, ProjectListSerializer, IssueDetailSerializer, IssueListSerializer, CommentSerializer

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

    def get_queryset(self):
        # return Project.objects.filter(author=self.request.user).order_by('-created_at')
        return Project.objects.all()
    
class IssueViewset(MultipleSerializerMixin, ModelViewSet):

    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer

    def get_queryset(self):
        queryset = Issue.objects.all()
        project_id = self.request.GET.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        # return Issue.objects.filter(project__author=self.request.user).order_by('-created_at')
        return queryset
    
class CommentViewset(ModelViewSet):

    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = Comment.objects.all()
        issue_id = self.request.GET.get('issue_id')
        if issue_id:
            queryset = queryset.filter(issue_id=issue_id)
        # return Comment.objects.filter(issue__project__author=self.request.user).order_by('-created_at')
        return queryset