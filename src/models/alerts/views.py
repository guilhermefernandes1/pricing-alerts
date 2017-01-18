from flask import Blueprint, redirect, render_template, request, session, url_for
from src.models.alerts.alert import Alert
from src.models.items.item import Item
import src.models.users.decorators as user_decorators

alert_blueprint = Blueprint('alerts', __name__)


@alert_blueprint.route('/')
@user_decorators.requires_login
def index():
    return redirect(url_for('users.user_alerts'))


@alert_blueprint.route('/new', methods=['GET', 'POST'])
@user_decorators.requires_login
def create_alert():
    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        price_limit = float(request.form['price_limit'])

        item = Item(name, url)
        item.save_to_mongo()

        alert = Alert(session['email'], price_limit, item.get_id())
        alert.load_item_price()  # this already saves to mongo

    return render_template('alerts/new_alert.html')


@alert_blueprint.route('/edit/<string:alert_id>', methods=['GET', 'POST'])
@user_decorators.requires_login
def edit_alert(alert_id):
    alert = Alert.get_by_id(alert_id)
    if request.method == 'POST':
        alert.price_limit = float(request.form['price_limit'])

        alert.save_to_mongo()

        return redirect(url_for('.get_alert_page', alert_id=alert.get_id()))
    return render_template('alerts/edit_alert.html', alert=alert)


@alert_blueprint.route('/activate/<string:alert_id>')
@user_decorators.requires_login
def activate_alert(alert_id):
    Alert.get_by_id(alert_id).activate()
    return redirect(url_for('.get_alert_page', alert_id=alert_id))


@alert_blueprint.route('/deactivate/<string:alert_id>')
@user_decorators.requires_login
def deactivate_alert(alert_id):
    Alert.get_by_id(alert_id).deactivate()
    return redirect(url_for('users.user_alerts'))


@alert_blueprint.route('/<string:alert_id>')
@user_decorators.requires_login
def get_alert_page(alert_id):
    alert = Alert.get_by_id(alert_id)
    return render_template('alerts/alert.html', alert=alert)


@alert_blueprint.route('/check_price/<string:alert_id>')
@user_decorators.requires_login
def check_alert_price(alert_id):
    Alert.get_by_id(alert_id).load_item_price()
    return redirect(url_for('.get_alert_page', alert_id=alert_id))


@alert_blueprint.route('/delete/<string:alert_id>')
@user_decorators.requires_login
def remove_alert(alert_id):
    Alert.get_by_id(alert_id).remove_alert()
    return redirect(url_for('users.user_alerts'))
