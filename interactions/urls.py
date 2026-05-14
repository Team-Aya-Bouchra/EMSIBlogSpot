from django.urls import path
from .views import toggle_like, follow_author

urlpatterns = [
    path('<int:article_id>/like/', toggle_like, name='toggle_like'),
    path('follow/<int:author_id>/', follow_author, name='follow_author'),
]
