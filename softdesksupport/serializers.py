from rest_framework import serializers
from .models import Project, Issue, Comment
from django.contrib.auth import get_user_model


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'project_type',
                  'author', 'contributors', 'created_at', 'updated_at']
        
    def validate_name(self, value):
        if Project.objects.filter(name=value).exists():
            raise serializers.ValidationError("A project with this name already exists.")
        return value


class ProjectDetailSerializer(serializers.ModelSerializer):
    issues = serializers.SerializerMethodField()
    contributors = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'project_type',
                  'author', 'contributors', 'created_at', 'updated_at', 'issues']

    def get_issues(self, instance):
        queryset = instance.issues.all()
        serializers = IssueListSerializer(queryset, many=True)
        return serializers.data
    
    def get_contributors(self, instance):
        queryset = instance.contributors.all()
        serializers = ContributorListSerializer(queryset, many=True)
        return serializers.data
    
class ContributorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'can_be_contacted']

class IssueListSerializer(serializers.ModelSerializer):
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.none(),
        allow_null=True,
        required=True,
    )

    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'project',
                  'author', 'assignee', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project_id = self.context.get('project_id')
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
                self.fields['assignee'].queryset = project.contributors.all()
            except Project.DoesNotExist:
                pass

class IssueDetailSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'project',
                  'author', 'assignee', 'type', 'priority', 'status', 'created_at', 'updated_at', 'comments']

    def get_comments(self, instance):
        queryset = instance.comments.all()
        serializers = CommentSerializer(queryset, many=True)
        return serializers.data


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['unique_id', 'content', 'issue',
                  'author', 'created_at', 'updated_at']
