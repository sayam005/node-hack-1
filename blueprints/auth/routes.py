from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Pet
from . import auth_bp
from datetime import datetime

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username already taken!')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered!')
            return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        # This is the corrected way to create and link a pet
        new_pet = Pet(name='Blobby')
        new_user.pet = new_pet

        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            if user.pet:
                mood_changed = user.pet.update_on_login()
                db.session.commit()
                if mood_changed:
                    flash("You were away for a while. Blobby missed you!")
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    if current_user.pet:
        current_user.pet.update_on_logout()
        db.session.commit()
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))
