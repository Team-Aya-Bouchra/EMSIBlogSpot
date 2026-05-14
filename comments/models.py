from django.db import models
from django.conf import settings
from articles.models import Article

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    is_liked_by_author = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        # hasattr check because of Multi-Table Inheritance One-to-One
        if hasattr(self.user, 'adminuser'):
            raise ValidationError("Admins cannot comment on articles.")
        super().clean()

    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"
