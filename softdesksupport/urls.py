from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ProjectViewset, IssueViewset, CommentViewset

app_name = 'softdesksupport'

router = SimpleRouter()
router.register('projects', ProjectViewset, basename='project')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'projects/<int:project_pk>/issues/',
        IssueViewset.as_view({'get': 'list', 'post': 'create'}),
        name='issue-list',
    ),
    path(
        'projects/<int:project_pk>/issues/<int:pk>/',
        IssueViewset.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='issue-detail',
    ),
    path(
        'projects/<int:project_pk>/issues/<int:issue_pk>/comments/',
        CommentViewset.as_view({'get': 'list', 'post': 'create'}),
        name='comment-list',
    ),
    path(
        'projects/<int:project_pk>/issues/<int:issue_pk>/comments/<int:pk>/',
        CommentViewset.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='comment-detail',
    ),
]
