from functools import wraps
from flask import session, redirect, url_for, request, render_template
import src.config as app_config


def requires_login(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'email' not in session.keys() or session['email'] is None:
            return redirect(url_for('users.user_login', next=request.path))
        return func(*args, **kwargs)
    return decorated_function


def requires_admin_permission(func):
    @wraps(func)
    def decorator_admin_function(*args, **kwargs):
        if session['email'] not in app_config.ADMINS:
            return render_template('/home.html')
        return func(*args, **kwargs)
    return decorator_admin_function
