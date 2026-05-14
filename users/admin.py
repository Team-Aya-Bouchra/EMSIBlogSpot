from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AdminUser, Author, Reader

admin.site.register(User, UserAdmin)
admin.site.register(AdminUser)
admin.site.register(Author)
admin.site.register(Reader)
