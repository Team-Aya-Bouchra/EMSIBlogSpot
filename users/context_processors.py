from django.utils import timezone

def notifications_processor(request):
    user = request.user
    if not user.is_authenticated or not hasattr(user, 'author'):
        return {}
        
    from interactions.models import ArticleLike, Follow
    from comments.models import Comment
    
    notifications = []
    
    recent_likes = ArticleLike.objects.filter(article__author=user.author).order_by('-created_at')[:10]
    for like in recent_likes:
        notifications.append({
            'type': 'like',
            'user': like.reader.username,
            'text': f"liked your article: {like.article.title}",
            'timestamp': like.created_at,
            'link': f"/article/{like.article.slug}/"
        })
        
    recent_comments = Comment.objects.filter(article__author=user.author).exclude(user=user).order_by('-created_at')[:10]
    for comment in recent_comments:
        notifications.append({
            'type': 'comment',
            'user': comment.user.username,
            'text': f"commented on your article: {comment.article.title}",
            'timestamp': comment.created_at,
            'link': f"/article/{comment.article.slug}/#comments-section"
        })
        
    recent_followers = Follow.objects.filter(author=user.author).order_by('-created_at')[:10]
    for follow in recent_followers:
        notifications.append({
            'type': 'follow',
            'user': follow.reader.username,
            'text': "started following you",
            'timestamp': follow.created_at,
            'link': "" # No view button for follow
        })
        
    notifications.sort(key=lambda x: x['timestamp'], reverse=True)
    
    has_unread = False
    last_check_str = request.session.get('last_notification_check')
    
    if last_check_str:
        from django.utils.dateparse import parse_datetime
        last_check = parse_datetime(last_check_str)
        if last_check and notifications and notifications[0]['timestamp'] > last_check:
            has_unread = True
    elif notifications:
        has_unread = True
        
    return {
        'notifications': notifications,
        'has_unread_notifications': has_unread
    }
