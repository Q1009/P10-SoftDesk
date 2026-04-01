from django.contrib import admin
from .models import Project, Issue, Comment

# Register your models here.

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_type', 'description', 'author', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'author__username')
    list_filter = ('project_type', 'author', 'created_at')

class IssueAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'type', 'status', 'priority', 'assignee', 'description', 'created_at', 'author', 'updated_at')
    search_fields = ('title', 'description', 'author__username', 'project__name')
    list_filter = ('project', 'type', 'status', 'priority', 'assignee')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('issue', 'author', 'content', 'created_at', 'updated_at')
    search_fields = ('content', 'author__username', 'issue__title')
    list_filter = ('issue', 'author')

admin.site.register(Project, ProjectAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Comment, CommentAdmin)
