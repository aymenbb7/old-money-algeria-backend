from django.conf import settings
import json
from pywebpush import webpush, WebPushException
from .models import Notification, WebPushSubscription

def send_admin_notification(title, message, notification_type, order=None, product=None):
    # 1. Create DB record
    notif = Notification.objects.create(
        title=title,
        message=message,
        notification_type=notification_type,
        order=order,
        product=product
    )

    # 2. Send Web Push to all subscribed admins
    subscriptions = WebPushSubscription.objects.all()
    if not subscriptions:
        return

    payload = json.dumps({
        'title': title,
        'body': message,
        'type': notification_type,
        'url': f'/admin/orders/{order.id}' if order else '/admin/',
    })

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth
                    }
                },
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": settings.VAPID_ADMIN_EMAIL,
                }
            )
        except WebPushException as ex:
            # If subscription is expired or invalid, we could delete it
            if ex.response and ex.response.status_code in [404, 410]:
                sub.delete()
            # print("Web Push Error:", repr(ex))

