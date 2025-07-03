from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import main_bp

@main_bp.route('/')
def index():
    # If the user is already logged in, take them to the dashboard.
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    # Otherwise, the main page should be the login page.
    return redirect(url_for('auth.login'))

@main_bp.route('/about')
def about():
    # This creates a dedicated page for "About Us".
    return render_template('about.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    pet = current_user.pet
    if not pet:
        flash('You don\'t have a pet! Something went wrong.')
        return redirect(url_for('main.index'))
    
    # Get bond counter data
    bond_count = pet.daily_bonds
    bond_name = pet.bond_display_name
    
    # Get timer info for display
    timer_info = pet.get_timer_info()
    
    # Pass all data to frontend team
    return render_template('dashboard.html', 
                         user=current_user,
                         pet=pet,
                         bond_count=bond_count,
                         bond_name=bond_name,
                         timer_info=timer_info)
