from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User
from . import profile_bp

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def view_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        if not username or not email:
            flash('Username and email are required!')
            return redirect(url_for('profile.view_profile'))
        
        # Check if username is taken by another user
        existing_user = User.query.filter(User.username == username, User.id != current_user.id).first()
        if existing_user:
            flash('Username already taken!')
            return redirect(url_for('profile.view_profile'))

        # Check if email is taken by another user
        existing_email = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing_email:
            flash('Email already registered!')
            return redirect(url_for('profile.view_profile'))

        current_user.username = username
        current_user.email = email
        db.session.commit()
        flash('Profile updated successfully! 🎉')
        return redirect(url_for('profile.view_profile'))

    # For GET requests, display the stats
    pet = current_user.pet
    if not pet:
        flash('You don\'t have a pet!')
        return redirect(url_for('main.dashboard'))
    timer_info = pet.get_timer_info()
    stats = {
        'account_created': current_user.created_at.strftime('%B %d, %Y') if hasattr(current_user, 'created_at') and current_user.created_at else 'Unknown',
        'pet_created': pet.created_at.strftime('%B %d, %Y') if hasattr(pet, 'created_at') and pet.created_at else 'Unknown',
        'current_streak': pet.daily_bonds,
        'streak_name': pet.bond_display_name,
        'last_login': pet.last_login_time.strftime('%B %d, %Y at %I:%M %p') if pet.last_login_time else 'Never',
        'last_logout': pet.last_logout_time.strftime('%B %d, %Y at %I:%M %p') if pet.last_logout_time else 'Never',
        'current_mood': pet.current_mood.capitalize(),
        'current_message': pet.message,
        'offline_time': f"{timer_info['offline_minutes']:.1f} minutes",
        'online_time': f"{timer_info['online_minutes']:.1f} minutes",
        'total_deterioration': f"{timer_info['total_deterioration']:.1f} minutes",
        'recovery_progress': f"{timer_info['recovery_progress']:.1f} minutes"
    }
    return render_template('profile/profile.html', user=current_user, pet=pet, stats=stats)

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        if not username or not email:
            flash('Username and email are required!')
            return render_template('profile/edit.html', user=current_user)
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Username already taken!')
            return render_template('profile/edit.html', user=current_user)
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != current_user.id:
            flash('Email already registered!')
            return render_template('profile/edit.html', user=current_user)
        current_user.username = username
        current_user.email = email
        db.session.commit()
        flash('Profile updated successfully! 🎉')
        return redirect(url_for('profile.view_profile'))
    return render_template('profile/edit.html', user=current_user)

@profile_bp.route('/stats')
@login_required
def user_stats():
    pet = current_user.pet
    if not pet:
        flash('You don\'t have a pet!')
        return redirect(url_for('main.dashboard'))
    timer_info = pet.get_timer_info()
    stats = {
        'account_created': current_user.created_at.strftime('%B %d, %Y') if hasattr(current_user, 'created_at') and current_user.created_at else 'Unknown',
        'pet_created': pet.created_at.strftime('%B %d, %Y') if hasattr(pet, 'created_at') and pet.created_at else 'Unknown',
        'current_streak': pet.daily_bonds,
        'streak_name': pet.bond_display_name,
        'last_login': pet.last_login_time.strftime('%B %d, %Y at %I:%M %p') if pet.last_login_time else 'Never',
        'last_logout': pet.last_logout_time.strftime('%B %d, %Y at %I:%M %p') if pet.last_logout_time else 'Never',
        'current_mood': pet.current_mood.capitalize(),
        'current_message': pet.message,
        'offline_time': f"{timer_info['offline_minutes']:.1f} minutes",
        'online_time': f"{timer_info['online_minutes']:.1f} minutes",
        'total_deterioration': f"{timer_info['total_deterioration']:.1f} minutes",
        'recovery_progress': f"{timer_info['recovery_progress']:.1f} minutes"
    }
    return render_template('profile/stats.html', user=current_user, pet=pet, stats=stats)
