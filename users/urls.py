from django.urls import path
from .views import register_view, login_view, logout_view, dashboard_router, moderator_ban_user, author_profile, request_author_promotion, promote_user, update_profile, cancel_author_promotion, google_login, google_callback, delete_account, custom_admin_dashboard, toggle_user_status, submit_report, admin_readers_list, admin_authors_list, admin_user_detail, admin_articles_list, mark_notifications_read, notifications_view

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_router, name='dashboard'),
    path('ban/', moderator_ban_user, name='moderator_ban_user'),
    path('author/<str:username>/', author_profile, name='author_profile'),
    path('request-promotion/', request_author_promotion, name='request_author_promotion'),
    path('cancel-promotion/', cancel_author_promotion, name='cancel_author_promotion'),
    path('promote/<str:username>/', promote_user, name='promote_user'),
    path('update-profile/', update_profile, name='update_profile'),
    path('delete-account/', delete_account, name='delete_account'),
    path('google/login/', google_login, name='google_login'),
    path('google/callback/', google_callback, name='google_callback'),
    path('admin/', custom_admin_dashboard, name='custom_admin_dashboard'),
    path('admin/readers/', admin_readers_list, name='admin_readers'),
    path('admin/authors/', admin_authors_list, name='admin_authors'),
    path('admin/articles/', admin_articles_list, name='admin_articles'),
    path('admin/user/<str:username>/', admin_user_detail, name='admin_user_detail'),
    path('toggle-status/<str:username>/', toggle_user_status, name='toggle_user_status'),
    path('report/', submit_report, name='submit_report'),
    path('notifications/mark-read/', mark_notifications_read, name='mark_notifications_read'),
    path('notifications/', notifications_view, name='notifications_view'),
]
