from __future__ import annotations

import hashlib
import hmac
import re
from html import escape
from typing import Callable, Iterable

from werkzeug.wrappers import Request, Response

StartResponse = Callable[[str, list[tuple[str, str]]], Callable[..., object]]
WSGIApp = Callable[[dict[str, object], StartResponse], Iterable[bytes]]


class PresentationPasswordGate:
    """Require a presentation-specific password before calling a WSGI app."""

    def __init__(
        self,
        app: WSGIApp,
        *,
        presentation_id: str,
        title: str,
        password: str,
        mount_path: str,
    ) -> None:
        self.app = app
        self.title = title
        self.password = password
        self.mount_path = mount_path.rstrip("/") or "/"
        safe_id = re.sub(r"[^a-z0-9]+", "_", presentation_id.casefold()).strip("_")
        self.cookie_name = f"premise_presentation_{safe_id}"
        self.cookie_value = hmac.new(
            password.encode("utf-8"),
            f"premise-hub:{presentation_id}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def __call__(
        self, environ: dict[str, object], start_response: StartResponse
    ) -> Iterable[bytes]:
        request = Request(environ)
        supplied_cookie = request.cookies.get(self.cookie_name, "")
        if hmac.compare_digest(supplied_cookie, self.cookie_value):
            return self.app(environ, start_response)

        error = False
        if request.method == "POST":
            supplied_password = request.form.get("password", "").strip()
            if hmac.compare_digest(supplied_password, self.password):
                response = Response(status=303)
                response.headers["Location"] = f"{self.mount_path}/"
                response.set_cookie(
                    self.cookie_name,
                    self.cookie_value,
                    httponly=True,
                    secure=self._is_secure(request),
                    samesite="Lax",
                    path=self.mount_path,
                )
                response.headers["Cache-Control"] = "no-store"
                return response(environ, start_response)
            error = True

        response = Response(
            self._login_page(error=error),
            status=401,
            content_type="text/html; charset=utf-8",
        )
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; "
            "form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
        )
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response(environ, start_response)

    @staticmethod
    def _is_secure(request: Request) -> bool:
        forwarded_protocol = request.headers.get("X-Forwarded-Proto", "")
        return (
            request.is_secure or forwarded_protocol.split(",", 1)[0].strip() == "https"
        )

    def _login_page(self, *, error: bool) -> str:
        title = escape(self.title)
        action = escape(f"{self.mount_path}/", quote=True)
        error_markup = (
            '<p class="error" role="alert">That password is not correct.</p>'
            if error
            else ""
        )
        return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="noindex, nofollow">
    <title>Protected presentation · {title}</title>
    <style>
      :root {{ color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
      * {{ box-sizing: border-box; }}
      body {{ min-height: 100vh; margin: 0; display: grid; place-items: center; padding: 24px; color: #18343f; background: #f1f5f5; }}
      main {{ width: min(100%, 430px); padding: 34px; border: 1px solid #d7e1e4; border-top: 6px solid #008a82; border-radius: 18px; background: #fff; box-shadow: 0 18px 50px rgba(24, 52, 63, .12); }}
      img {{ display: block; width: 132px; height: auto; margin-bottom: 28px; }}
      small {{ color: #006b8f; font-size: 11px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }}
      h1 {{ margin: 8px 0 10px; font-size: clamp(25px, 6vw, 34px); line-height: 1.08; }}
      p {{ margin: 0 0 24px; color: #5c6f77; line-height: 1.5; }}
      label {{ display: block; margin-bottom: 8px; font-size: 13px; font-weight: 800; }}
      input {{ width: 100%; min-height: 48px; padding: 11px 13px; border: 1px solid #aebdc3; border-radius: 9px; font: inherit; letter-spacing: .04em; }}
      input:focus {{ border-color: #006b8f; outline: 3px solid rgba(0, 107, 143, .17); }}
      button {{ width: 100%; min-height: 48px; margin-top: 14px; border: 0; border-radius: 9px; color: #fff; background: #006b8f; font: inherit; font-weight: 800; cursor: pointer; }}
      button:hover {{ background: #005873; }}
      .error {{ margin: 11px 0 0; color: #a52a2a; font-size: 13px; font-weight: 700; }}
    </style>
  </head>
  <body>
    <main>
      <img src="/static/premise-logo-transparent.png" alt="Premise">
      <small>Protected presentation</small>
      <h1>{title}</h1>
      <p>Enter the password to continue.</p>
      <form method="post" action="{action}">
        <label for="password">Password</label>
        <input id="password" name="password" type="password" autocomplete="current-password" required autofocus>
        <button type="submit">Open presentation</button>
        {error_markup}
      </form>
    </main>
  </body>
</html>"""
