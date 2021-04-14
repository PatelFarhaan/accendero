import sys
sys.path.append('../../')

import boto3
from project import db
from project.users.models import Users, Storage
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required
from flask import render_template, request, Blueprint, redirect, url_for, session


admin_blueprint = Blueprint('admin', __name__, template_folder='templates')
file_bucket = "relex-dev"
zip_file_bucket = "relex-dev-zip"
s3_delete = boto3.resource('s3',
                    aws_access_key_id="AKIAUXXYHWV6HE563SE2",
                    aws_secret_access_key="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")


@admin_blueprint.route('/admin', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        admin_email = request.form.get('admin_email', None)
        admin_password = request.form.get('admin_password', None)

        if admin_email == None:
            return render_template('admin.html', warning='Admin Email cannot be Empty')

        if admin_password == None:
            return render_template('admin.html', warning='Admin Password cannot be Empty')

        admin = Users.query.filter_by(email=admin_email).first()
        if admin == None:
            return render_template('admin.html', warning='Admin does not Exist.')

        elif check_password_hash(admin.hashed_password, admin_password) and admin.is_admin:
            login_user(admin)
            return redirect(url_for('admin.admin_page'))
    return render_template ('admin.html')


@admin_blueprint.route('/admin-page', methods=['GET', 'POST'])
@login_required
def admin_page():
    storage = Storage.query.all()
    final_result = []
    for i in storage:
        temp_dict = {}
        user_obj = Users.query.filter_by(id=i.user_id).first()
        temp_dict['file_link'] = i.file_url
        temp_dict['zip_link'] = i.zip_file_url
        temp_dict['filename'] = i.filename
        temp_dict['email'] = user_obj.email
        temp_dict['username'] = user_obj.name
        temp_dict['mobile_number'] = user_obj.mobile_number
        final_result.append(temp_dict)

    if request.method == 'POST':
        filename = request.form.get('delete_filename', None)
        if not filename:
            return redirect(url_for('admin.admin_page'))
        else:
            try:
                hm = {
                    filename: file_bucket,
                    filename + ".zip": zip_file_bucket,
                }
                delete_file_from_s3(filename, hm)
                return redirect(url_for('admin.admin_page'))
            except:
                return redirect(url_for('admin.admin_page'))

    return render_template ('admin_page.html', info=final_result)


@admin_blueprint.route('/admin-logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('users.login'))


def delete_file_from_s3(model_key, filename):
    for key, bucket in filename.items():
        file_obj = s3_delete.Object(bucket, key)
        file_obj.delete()

    storage_obj_delete = Storage.query.filter_by(filename=model_key).first()
    db.session.delete(storage_obj_delete)
    db.session.commit()
