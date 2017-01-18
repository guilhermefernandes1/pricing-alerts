from flask import Blueprint, request, render_template, session, url_for
from werkzeug.utils import redirect
import src.models.users.errors as user_errors
import src.models.users.decorators as user_decorators

from src.models.users.user import User

user_blueprint = Blueprint('users', __name__)


@user_blueprint.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            if User.is_login_valid(email, password):
                session['email'] = email
                return redirect(url_for(".user_alerts"))
        except user_errors.UserError as e:
            return e.message

    return render_template("users/login.html")


@user_blueprint.route('/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            if User.register_user(email, password):
                session['email'] = email
                return redirect(url_for(".user_alerts"))
        except user_errors.UserError as e:
            return e.message

    return render_template("users/register.html")


@user_blueprint.route('/alerts')
@user_decorators.requires_login
def user_alerts():
    user = User.get_user_by_email(session["email"])
    alerts = user.get_alerts()
    return render_template("users/alerts.html", alerts=alerts)


@user_blueprint.route('/logout')
def user_logout():
    session['email'] = None
    return redirect(url_for('home'))
