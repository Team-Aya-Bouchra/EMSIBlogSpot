from django.db import models
from django.conf import settings
from tags.models import Tag

class Article(models.Model):
    author = models.ForeignKey('users.Author', on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, null=True, blank=True)
    content = models.TextField()
    cover_image = models.ImageField(upload_to='articles/', null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    status = models.CharField(max_length=50, default='Publié')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
