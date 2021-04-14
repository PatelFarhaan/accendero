import sys
sys.path.append('../../')

import os
import boto3
import shutil
from project import db, app
from project.users.models import Users, Storage
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template, url_for, redirect, request, Blueprint, session


file_bucket = "relex-dev"
aws_access_key_id = "place your s3 access key here"
aws_secret_access_key = "place your s3 secret key here"
users_blueprint = Blueprint('users', __name__, template_folder='templates')
s3 = boto3.client('s3',
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key)

s3_delete = boto3.resource('s3',
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key)


@users_blueprint.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('users.login'))


@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    session.clear()
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        mobile_number = request.form.get('mobile_number')
        repeat_password = request.form.get('repeat_password')

        valid_payload_check = {
            name: "name",
            email: "email",
            password: "password",
            mobile_number: "mobile_number",
            repeat_password: "repeat_password"
        }

        for k, v in valid_payload_check.items():
            if not k or k == "":
                return render_template('register.html', warning=f'{v} cannot be Empty')

        if not (password == repeat_password):
            return render_template('register.html', warning='Both passwords should be same.')

        existing_user_email = Users.query.filter_by(email=email).first()

        if existing_user_email is not None:
            return render_template('register.html', warning='Email already exists. Please login to continue')

        else:
            email = email.lower()
            new_user = Users(email=email, name=name, mobile_number=mobile_number,
                             hashed_password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('users.login'))
    return render_template('register.html')


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        valid_payload_check = {
            email: "email",
            password: "password",
        }

        for k, v in valid_payload_check.items():
            if not k or k == "":
                return render_template('register.html', warning=f'{v} cannot be Empty')

        user = Users.query.filter_by(email=email).first()
        if not user:
            return render_template('login.html', warning='Email Does not exist!!!')

        if check_password_hash(user.hashed_password, password):
            login_user(user)
            session['email'] = user.email
            return redirect(url_for('users.after_login'))
        else:
            return render_template('login.html', warning='Password is incorrect')
    return render_template('login.html')


@users_blueprint.route('/after-login', methods=['GET', 'POST'])
@login_required
def after_login():
    user = Users.query.filter_by(email=session['email']).first()
    error_flag = False

    try:
        page = request.args.get('page', 1, type=int)
        user_storage_files = Storage.query.filter_by(user_id=user.id).paginate(page=page, per_page=5)
    except:
        error_flag = True

    if request.method == 'POST':
        file_obj = request.files.get('file_obj')
        if file_obj:
            file_path = os.getcwd() + '/tmp/'
            if not os.path.exists(file_path):
                os.mkdir(file_path)

            file_obj.save(os.path.join(app.config['UPLOAD_FOLDER'], file_obj.filename))
            file_obj_path = file_path + f'{file_obj.filename}'
            resp = max_file_size(file_obj_path)

            if not resp:
                shutil.rmtree(file_path)
                return render_template('after_login.html', user_name=user.name, user_storage_files=user_storage_files,
                                       warning='Please upload a file less than 10 MB in size!')

            file_desc = request.form.get("file_desc")
            filename = file_obj.filename.replace(' ', '')
            filename = f"{current_user.id}/{filename}"
            storage_files = Storage.query.all()
            files_list = []

            for i in storage_files:
                files_list.append(i.filename)

            if filename is None or filename == '':
                if error_flag:
                    return render_template('after_login.html', user_name=user.name,
                                           warning='Please select a fle to upload')
                else:
                    return render_template('after_login.html', user_name=user.name,
                                           user_storage_files=user_storage_files,
                                           warning='Please select a fle to upload')
            elif filename in files_list:
                return render_template('after_login.html', user_name=user.name, user_storage_files=user_storage_files,
                                       warning='File already exists. Try with a new file name')

            public_url = file_upload_to_s3(file_path, filename, file_obj.filename)
            storage_obj = Storage(
                user_id=user.id,
                filename=filename,
                file_url=public_url,
                file_desc=file_desc)
            db.session.add(storage_obj)
            db.session.commit()

            page = request.args.get('page', 1, type=int)
            user_storage_files = Storage.query.filter_by(user_id=user.id).paginate(page=page, per_page=5)
            return render_template('after_login.html', user_name=user.name, user_storage_files=user_storage_files)
        else:
            filename = request.form.get('delete_filename')
            if filename:
                delete_file_from_s3(file_bucket, filename)
                return redirect(url_for('users.after_login'))
        return redirect(url_for('users.after_login'))

    if error_flag:
        return render_template('after_login.html', user_name=user.name)
    else:
        return render_template('after_login.html', user_name=user.name, user_storage_files=user_storage_files)


def file_upload_to_s3(directory_path, file_name, file_obj_name):
    file_path = directory_path + file_obj_name
    s3.upload_file(file_path, file_bucket, file_name, ExtraArgs={"ACL": "public-read"})
    public_url = f"https://{file_bucket}.s3.amazonaws.com/{file_name}"
    return public_url


def max_file_size(file_path):
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        if file_info.st_size > 10000000:
            return False
        else:
            return True


def delete_file_from_s3(bucket, key):
    file_obj = s3_delete.Object(bucket, key)
    file_obj.delete()
    storage_obj_delete = Storage.query.filter_by(filename=key).first()
    db.session.delete(storage_obj_delete)
    db.session.commit()
