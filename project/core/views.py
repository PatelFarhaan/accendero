from flask import render_template, Blueprint


core_blueprint = Blueprint('core', __name__, template_folder='templates')


@core_blueprint.route('/')
def index():
    return render_template('index.html')