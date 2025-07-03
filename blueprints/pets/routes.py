from flask import render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from . import pets_bp
import random

@pets_bp.route('/set_mood/<mood>', methods=['POST'])
@login_required
def set_mood(mood):
    """Handle user clicking mood button"""
    pet = current_user.pet
    if not pet:
        flash('You don\'t have a pet!')
        return redirect(url_for('main.dashboard'))
    
    # Valid moods (the 6 moods)
    valid_moods = ['playing', 'happy', 'normal', 'sad', 'sick', 'dead']
    if mood not in valid_moods:
        flash('Invalid mood!')
        return redirect(url_for('main.dashboard'))
    
    # Set Blobby's mood to match user's mood
    pet.current_mood = mood
    
    # Blobby's responses to each mood
    responses = {
        'playing': "You're feeling playful! Let's have fun! 🎮",
        'happy': "You are happy! That makes me happy too! 😊", 
        'normal': "You're feeling normal today. That's perfectly okay! 😐",
        'sad': "You are sad... I'm here for you. 😢",
        'sick': "You're feeling sick... Take care of yourself! 🤒",
        'dead': "You feel emotionally drained... Let's talk about it. 💀"
    }
    
    # Get Blobby's response
    response = responses.get(mood, "Thanks for sharing your feelings with me!")
    
    # Generate new random question for next time
    questions = [
        "How are you feeling today?",
        "What's your mood right now?", 
        "How are things going for you?",
        "Tell me, how do you feel?",
        "What's your vibe today?",
        "How's your day treating you?",
        "What mood are you in?",
        "How are you doing emotionally?",
        "Share your feelings with me!",
        "What's your current state of mind?"
    ]
    pet.message = random.choice(questions)
    
    # Save changes
    db.session.commit()
    flash(f"You've set Blobby's mood to {mood}!")
    return redirect(url_for('main.dashboard'))

@pets_bp.route('/recover', methods=['POST'])
@login_required
def recover_mood():
    """Endpoint for JS to call to improve mood by one level."""
    if current_user.pet:
        new_mood = current_user.pet.recover_mood()
        return jsonify({'success': True, 'new_mood': new_mood, 'image_path': f'/static/{new_mood}.png'})
    return jsonify({'success': False, 'error': 'Pet not found'}), 404
