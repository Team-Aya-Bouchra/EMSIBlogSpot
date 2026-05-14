from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Base class for authentication
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True, null=True)

class AdminUser(User):
    role = models.CharField(max_length=20, default="Admin")

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"
    
    def can_moderate_content(self):
        return True

    def promote_user_role(self):
        pass

class Author(User):
    role = models.CharField(max_length=20, default="Author")
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def upload_article(self):
        pass

    def view_followers(self):
        pass

    def count_followers(self):
        return self.followers.count()

    def like_comment(self):
        pass

    def reply_comment(self):
        pass

class Reader(User):
    role = models.CharField(max_length=20, default="Reader")
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    wants_to_be_author = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Reader"
        verbose_name_plural = "Readers"

    def follow_author(self, author_id):
        pass

    def comment_article(self):
        pass

    def like_article(self):
        pass
