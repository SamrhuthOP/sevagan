import json
from pywebpush import WebPushException, webpush


def send_web_push(subscription_info, message_title, message_body):
    """Sends a native Web Push notification using your generated VAPID private key."""
    payload = json.dumps({"title": message_title, "body": message_body})

    try:
        response = webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key="vapid_private.pem",
            vapid_claims={"sub": "mailto:admin@sevagan.com"},
        )
        return True
    except WebPushException as ex:
        print(f"WebPush Error: {ex}")
        if ex.response is not None:
            print(ex.response.json())
        return False
