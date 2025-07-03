from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from . import auth_bp
from models import db, User, Pet
from datetime import datetime

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            if user.pet:
                user.pet.last_login_time = datetime.utcnow()
                db.session.commit()
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password')
            
    return render_template('login.html', title='Sign In')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username already taken.')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered.')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            new_pet = Pet(user=user, last_login_time=datetime.utcnow())
            db.session.add(user)
            db.session.add(new_pet)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('auth.login'))
            
    return render_template('register.html', title='Register')

@auth_bp.route('/logout')
def logout():
    if current_user.pet:
        current_user.pet.update_on_logout()
        db.session.commit()
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))
