
from management.models import Notification
def notifications_context(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by(
            '-created_at')
        notifications_count = len(notifications)
        print(notifications, notifications_count)
        return {'notifications': notifications, 'notifications_count': notifications_count}
    return {}
