from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Pet
from . import auth_bp
from datetime import datetime

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
            
            # Update pet when user logs in
            if user.pet:
                # Record login time for timer
                user.pet.last_login_time = datetime.utcnow()
                
                # Update daily bonds (streak counter)
                user.pet.update_daily_bonds()
                
                # Show welcome message with bond info
                bond_count = user.pet.daily_bonds
                bond_name = user.pet.bond_display_name
                flash(f'Welcome back! {bond_name}: {bond_count} days 🐾')
            else:
                flash('Welcome back!')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create Blobby for new user
        pet = Pet(user_id=user.id, daily_bonds=1)  # Start with 1 day bond
        
        db.session.add(pet)
        db.session.commit()
        
        flash('Welcome! Meet Blobby the Moody Blob! 🐾 Start building your bond!')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    # Record logout time for timer calculation
    if current_user.pet:
        current_user.pet.last_logout_time = datetime.utcnow()
        db.session.commit()
        
        bond_count = current_user.pet.daily_bonds
        bond_name = current_user.pet.bond_display_name
        flash(f'Goodbye! Blobby will miss you! Current {bond_name}: {bond_count} days 🐾')
    
    logout_user()
    return redirect(url_for('main.index'))
