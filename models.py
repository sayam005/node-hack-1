from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Corrected relationship using back_populates
    pet = db.relationship('Pet', back_populates='user', uselist=False, cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default='Blobby')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    current_mood = db.Column(db.String(20), default='happy')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    daily_bonds = db.Column(db.Integer, default=0)
    last_visit_date = db.Column(db.Date, default=datetime.utcnow().date)
    bond_display_name = db.Column(db.String(50), default="Daily Bonds")
    last_logout_time = db.Column(db.DateTime)
    last_login_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', back_populates='pet')

    MOOD_HIERARCHY = ['dead', 'sick', 'sad', 'normal', 'happy', 'playing']

    def update_on_login(self):
        """Updates all stats when a user logs in. Returns True if mood changed."""
        mood_did_change = self._update_mood_from_offline_time()
        self._update_daily_bonds()
        self.last_login_time = datetime.utcnow()
        return mood_did_change

    def update_on_logout(self):
        """Updates stats when a user logs out."""
        self.last_logout_time = datetime.utcnow()

    def _update_mood_from_offline_time(self):
        """Calculates mood drop. Returns True if mood changed."""
        if not self.last_logout_time:
            return False

        minutes_offline = (datetime.utcnow() - self.last_logout_time).total_seconds() / 60
        levels_to_drop = int(minutes_offline)

        if levels_to_drop > 0:
            try:
                current_index = self.MOOD_HIERARCHY.index(self.current_mood)
                new_index = max(0, current_index - levels_to_drop)
                new_mood = self.MOOD_HIERARCHY[new_index]
                if new_mood != self.current_mood:
                    self.current_mood = new_mood
                    return True
            except ValueError:
                return False
        return False

    def _update_daily_bonds(self):
        """Updates the daily bond streak."""
        today = datetime.utcnow().date()
        if self.last_visit_date == today:
            return
        
        if self.last_visit_date == (today - timedelta(days=1)):
            self.daily_bonds += 1
        else:
            self.daily_bonds = 1
        self.last_visit_date = today

    def recover_mood(self):
        """Improves mood by one level for online recovery."""
        try:
            current_index = self.MOOD_HIERARCHY.index(self.current_mood)
            if current_index < len(self.MOOD_HIERARCHY) - 1:
                self.current_mood = self.MOOD_HIERARCHY[current_index + 1]
                db.session.commit()
        except ValueError:
            pass # Mood not in hierarchy, do nothing
        return self.current_mood

    def get_timer_info(self):
        """Calculates various time-based stats for the pet."""
        now = datetime.utcnow()
        
        offline_minutes = 0
        if self.last_logout_time and self.last_login_time and self.last_login_time > self.last_logout_time:
            offline_minutes = (self.last_login_time - self.last_logout_time).total_seconds() / 60
            
        online_minutes = 0
        if self.last_login_time:
            online_minutes = (now - self.last_login_time).total_seconds() / 60
            
        return {
            'offline_minutes': offline_minutes,
            'online_minutes': online_minutes,
            'total_deterioration': offline_minutes,
            'recovery_progress': online_minutes
        }

    @property
    def message(self):
        """Dynamic message based on pet's mood."""
        mood_messages = {
            'dead': "Blobby is feeling lifeless...",
            'sick': "Blobby is not feeling well...",
            'sad': "Blobby is feeling down...",
            'normal': "Blobby is feeling okay.",
            'happy': "Blobby is in a good mood!",
            'playing': "Blobby is having a great time!",
        }
        return mood_messages.get(self.current_mood, "How are you feeling today?")
