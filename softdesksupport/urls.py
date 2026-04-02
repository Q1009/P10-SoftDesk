from django.urls import path, include
from rest_framework import routers
from .views import ProjectViewset, IssueViewset, CommentViewset

app_name = 'softdesksupport'

router = routers.SimpleRouter()
router.register('project', ProjectViewset, basename='project')
router.register('issue', IssueViewset, basename='issue')
router.register('comment', CommentViewset, basename='comment')

urlpatterns = [
    path('api/', include(router.urls)),
]
