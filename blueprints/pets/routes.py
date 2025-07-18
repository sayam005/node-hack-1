from flask import render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from . import pets_bp

@pets_bp.route('/set_mood/<mood>', methods=['POST'])
@login_required
def set_mood(mood):
    pet = current_user.pet
    if pet and mood in pet.MOOD_HIERARCHY:
        pet.current_mood = mood
        db.session.commit()
        # This message will be displayed in the comic book bubble
        flash(f"You are now feeling {mood}!")
    else:
        flash("Invalid mood selected.")
    return redirect(url_for('main.dashboard'))

@pets_bp.route('/recover_mood', methods=['POST'])
@login_required
def recover_mood():
    """Endpoint for JS to call to improve mood by one level."""
    pet = current_user.pet
    if not pet:
        return jsonify({'success': False, 'message': 'No pet found.'})

    new_mood = pet.recover_mood()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'new_mood': new_mood,
        'message': pet.message,
        'image_path': url_for('static', filename=f'{new_mood}.png')
    })

@pets_bp.route('/recover', methods=['POST'])
@login_required
def recover():
    pet = current_user.pet
    if not pet:
        return jsonify({'success': False, 'message': 'No pet found.'})

    # Set Blobby's mood to match user's mood
    pet.current_mood = mood
    
    # The line "pet.message = ..." was removed as it caused the AttributeError.
    # The message is generated automatically by the @property in the Pet model.
    
    # Save changes
    db.session.commit()
    flash(f"You are now feeling {mood}!")
    return redirect(url_for('main.dashboard'))
