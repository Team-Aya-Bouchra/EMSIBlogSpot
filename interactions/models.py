from django.db import models
from django.conf import settings
from articles.models import Article

class ArticleLike(models.Model):
    reader = models.ForeignKey('users.Reader', on_delete=models.CASCADE, related_name='article_likes')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['reader', 'article'], name='unique_article_like')
        ]

    def __str__(self):
        return f"{self.reader.username} likes {self.article.title}"

class Follow(models.Model):
    reader = models.ForeignKey('users.Reader', on_delete=models.CASCADE, related_name='following')
    author = models.ForeignKey('users.Author', on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['reader', 'author'], name='unique_follow')
        ]

    def __str__(self):
        return f"{self.reader.username} follows {self.author.username}"
