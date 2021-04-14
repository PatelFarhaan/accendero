import datetime
from flask_login import UserMixin
from project import db, login_manager


########################################################################################################################
###############################################* LOGIN MANAGER *########################################################
########################################################################################################################
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
########################################################################################################################


########################################################################################################################
#####################################################* USERS *##########################################################
########################################################################################################################
class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(64))
    hashed_password = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    mobile_number = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(128), unique=True, index=True, nullable=False)
    register_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    storage = db.relationship('Storage', backref='user', lazy=True)
########################################################################################################################


########################################################################################################################
#################################################* STORAGE *############################################################
########################################################################################################################
class Storage(db.Model):
    __tablename__ = 'storage'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    file_url = db.Column(db.String(1000))
    filename = db.Column(db.String(1000), nullable=False, unique=True)
    file_desc = db.Column(db.String(1000), default='No description provided')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_on = db.Column(db.DateTime, default=datetime.datetime.utcnow(), nullable=False)

########################################################################################################################