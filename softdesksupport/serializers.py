from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import Project, Issue, Comment


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "project_type",
            "author",
            "contributors",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author", "contributors"]

    def validate_name(self, value):
        if Project.objects.filter(name=value).exists():
            raise serializers.ValidationError("Ce projet existe déjà.")
        return value


class ProjectDetailSerializer(serializers.ModelSerializer):
    issues = serializers.SerializerMethodField()
    contributors = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "project_type",
            "author",
            "contributors",
            "created_at",
            "updated_at",
            "issues",
        ]
        read_only_fields = ["author", "contributors"]

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
        fields = ["username", "email", "can_be_contacted"]


class AssigneeFromProjectMixin:
    """Sets the assignee queryset to the project's contributors."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project = self.context.get("project")
        if project is None:
            project_id = self.context.get("project_id")
            if project_id:
                try:
                    project = Project.objects.prefetch_related("contributors").get(
                        pk=project_id
                    )  # difference entre prefetch_related et select_related ? --- IGNORE ---
                except Project.DoesNotExist:
                    project = None
        if project:
            self.fields["assignee"].queryset = project.contributors.all()


class IssueListSerializer(AssigneeFromProjectMixin, serializers.ModelSerializer):
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.none(),
        allow_null=True,
        required=True,
        error_messages={
            "does_not_exist": "Cet utilisateur n'est pas un contributeur du projet."
        },
    )

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "project",
            "author",
            "assignee",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author", "project"]

    def validate_title(self, value):
        project_id = self.context.get("project_id")
        if (
            project_id
            and Issue.objects.filter(title=value, project_id=project_id).exists()
        ):
            raise serializers.ValidationError("Cette tâche existe déjà dans ce projet.")
        return value


class IssueDetailSerializer(AssigneeFromProjectMixin, serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.none(),
        allow_null=True,
        required=False,
        error_messages={
            "does_not_exist": "Cet utilisateur n'est pas un contributeur du projet."
        },
    )

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "project",
            "author",
            "assignee",
            "type",
            "priority",
            "status",
            "created_at",
            "updated_at",
            "comments",
        ]
        read_only_fields = ["author", "project"]

    def get_comments(self, instance):
        queryset = instance.comments.all()
        serializers = CommentSerializer(
            queryset,
            many=True,
            context={
                **self.context,
                "project_id": instance.project_id,
            },
        )
        return serializers.data


class CommentSerializer(serializers.ModelSerializer):
    issue_url = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "uuid",
            "content",
            "issue",
            "issue_url",
            "author",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["issue", "issue_url", "author"]

    def get_issue_url(self, instance):
        project_id = self.context.get("project_id")
        issue_id = instance.issue_id
        request = self.context.get("request")
        if project_id and issue_id:
            return reverse(
                "softdesksupport:issue-detail",
                kwargs={"project_pk": project_id, "pk": issue_id},
                request=request,
            )
        return None
