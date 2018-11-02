
from flask import redirect, render_template, request, session, url_for
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not "user_id" in session:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function