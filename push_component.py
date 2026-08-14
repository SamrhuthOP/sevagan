import streamlit.components.v1 as components


def get_public_key_string():
    """Reads the generated public key file."""
    try:
        with open("vapid_public.pem", "r") as f:
            return f.read().strip()
    except Exception:
        return ""


def render_push_subscription_ui():
    """Renders the frontend JS button to request notification permission and subscribe."""
    public_key = get_public_key_string()

    js_code = f"""
    <script>
    const vapidPublicKey = `{public_key}`;

    function urlBase64ToUint8Array(base64String) {{
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding).replace(/\\-/g, '+').replace(/_/g, '/');
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        for (let i = 0; i < rawData.length; ++i) {{
            outputArray[i] = rawData.charCodeAt(i);
        }}
        return outputArray;
    }}

    async function subscribeUser() {{
        if (!('serviceWorker' in navigator) || !('PushManager' in window)) {{
            alert('Push messaging is not supported in this browser.');
            return;
        }}

        const permission = await Notification.requestPermission();
        if (permission === 'granted') {{
            alert('Notification permission granted! App can now send push alerts.');
        }} else {{
            alert('Notification permission denied.');
        }}
    }}
    </script>

    <button onclick="subscribeUser()" style="
        background-color: #FF4B4B;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
    ">
        🔔 Enable App Notifications
    </button>
    """
    components.html(js_code, height=60)
