"""Password-only access to slides, callbacks, assets and downloads."""
import hashlib
import fcntl
import hmac
import os
from pathlib import Path
import secrets

from flask import make_response, redirect, render_template_string, request
from itsdangerous import BadSignature, URLSafeTimedSerializer

WEBINAR_DATE = '2026-09-11'
DEFAULT_PASSWORD = '11092026'
COOKIE = 'ccus_webinar_access'
MAX_AGE = 12 * 60 * 60
LOGIN = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Enter the webinar</title><style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;
background:#f3f6f7;color:#163a48;font-family:Arial,sans-serif;padding:24px}
main{width:100%;max-width:460px;padding:40px;background:white;border:1px solid #dce5e9;
border-radius:18px;box-shadow:0 12px 40px #163a4810}h1{font-size:26px;line-height:1.25;
margin:0 0 28px}label{display:block;margin-bottom:10px}input,button{width:100%;
font:inherit;padding:14px;border-radius:8px}input{border:1px solid #8ca3ae}
button{margin-top:18px;background:#006b7d;color:white;border:0;cursor:pointer}
input:focus-visible,button:focus-visible{outline:3px solid #efad43;outline-offset:3px}
.error{color:#b22929;font-size:14px}</style></head><body><main>
<h1>LCA of CCS and CCUS applied to cement production</h1>
<form method="post" action="{{ action }}"><label for="password">Webinar password</label>
<input id="password" name="password" type="password" autocomplete="current-password" required autofocus>
<input type="hidden" name="next" value="{{ destination }}">
{% if error %}<p class="error" role="alert">Incorrect password. Please try again.</p>{% endif %}
<button type="submit">Enter the webinar</button></form></main></body></html>'''


def _signing_key():
    configured = os.environ.get('CCUS_WEBINAR_SECRET_KEY')
    if configured:
        return configured
    # Shared across local workers/reloads; this directory is excluded from Git.
    path = Path(__file__).resolve().parents[1] / 'generated/access/session.key'
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'a+', opener=lambda p, flags: os.open(p, flags, 0o600)) as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.seek(0)
        key = handle.read().strip()
        if not key:
            handle.write(secrets.token_hex(32))
            handle.flush()
            handle.seek(0)
            key = handle.read().strip()
        return key


def install_password_gate(server):
    key = _signing_key()
    signer = URLSafeTimedSerializer(key, salt='ccus-webinar-access')
    prefix = os.environ.get('CCUS_WEBINAR_REQUESTS_PREFIX', '/').rstrip('/')
    login_path = prefix + '/login'

    def password():
        return os.environ.get('CCUS_WEBINAR_PASSWORD', DEFAULT_PASSWORD)

    def fingerprint():
        return hmac.new(key.encode(), password().encode(), hashlib.sha256).hexdigest()

    def safe_destination(value):
        if (not value.startswith(prefix + '/') or value.startswith('//')
                or '\\' in value or any(ord(c) < 32 for c in value)):
            return prefix + '/'
        return value

    def login_page(error=False):
        destination = safe_destination(request.form.get('next', prefix + '/')
            if request.method == 'POST' else request.script_root + request.full_path.rstrip('?'))
        response = make_response(render_template_string(LOGIN, action=login_path,
            destination=destination, error=error), 401 if error else 200)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @server.before_request
    def require_password():
        if request.path in ('/login', login_path) and request.method == 'POST':
            supplied = request.form.get('password', '')
            if password() and hmac.compare_digest(supplied.encode(), password().encode()):
                response = redirect(safe_destination(request.form.get('next', prefix + '/')), 303)
                response.set_cookie(COOKIE, signer.dumps(fingerprint()), max_age=MAX_AGE,
                    httponly=True, secure=request.is_secure, samesite='Lax', path=prefix + '/')
                return response
            return login_page(error=True)
        try:
            token = signer.loads(request.cookies.get(COOKIE, ''), max_age=MAX_AGE)
            if isinstance(token, str) and hmac.compare_digest(token, fingerprint()):
                return None
        except BadSignature:
            pass
        if request.method == 'GET' and request.path in ('/', '/presenter', '/login',
                prefix + '/', prefix + '/presenter', login_path):
            return login_page()
        return make_response('Enter the webinar password to continue.', 401)

    @server.after_request
    def prevent_shared_caching(response):
        response.headers['Cache-Control'] = 'no-store'
        return response
