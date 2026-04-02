from rest_framework import serializers
from .models import Project, Issue, Comment


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'project_type',
                  'author', 'created_at', 'updated_at']


class ProjectDetailSerializer(serializers.ModelSerializer):
    issues = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'project_type',
                  'author', 'created_at', 'updated_at', 'issues']

    def get_issues(self, instance):
        queryset = instance.issues.all()
        serializers = IssueListSerializer(queryset, many=True)
        return serializers.data

class IssueListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'project',
                  'author', 'assignee', 'created_at', 'updated_at']

class IssueDetailSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'project',
                  'author', 'assignee', 'created_at', 'updated_at', 'comments']

    def get_comments(self, instance):
        queryset = instance.comments.all()
        serializers = CommentSerializer(queryset, many=True)
        return serializers.data


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['unique_id', 'content', 'issue',
                  'author', 'created_at', 'updated_at']
