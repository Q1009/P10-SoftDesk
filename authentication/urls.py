from django.urls import path, include

app_name = 'authentication'

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
