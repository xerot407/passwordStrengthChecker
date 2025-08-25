# app.py
from flask import Flask, render_template, request, jsonify
import random
import string
import re

app = Flask(__name__)

def check_password_strength(password):
    """
    Checks the strength of a given password based on several criteria.
    Returns a dictionary with strength score and an assessment.
    """
    # Initialize strength score and criteria checks
    score = 0
    feedback = []

    # Criteria weights
    length_weight = 20
    complexity_weight = 20
    mix_weight = 20
    unique_weight = 20

    # 1. Length check
    # Score 0-20 based on length
    length = len(password)
    if length >= 12:
        score += length_weight
        feedback.append("Excellent length (12+ characters)")
    elif length >= 8:
        score += length_weight * 0.75
        feedback.append("Good length (8-11 characters)")
    else:
        score += length_weight * 0.25
        feedback.append("Password is too short (< 8 characters)")

    # 2. Character set checks (for complexity)
    has_lowercase = bool(re.search(r'[a-z]', password))
    has_uppercase = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_symbol = bool(re.search(r'[^a-zA-Z0-9\s]', password))

    # Score based on number of character types present
    char_types = sum([has_lowercase, has_uppercase, has_digit, has_symbol])
    if char_types == 4:
        score += complexity_weight
        feedback.append("Includes all character types")
    elif char_types == 3:
        score += complexity_weight * 0.75
        feedback.append("Includes 3 character types")
    elif char_types == 2:
        score += complexity_weight * 0.5
        feedback.append("Includes 2 character types")
    else:
        score += complexity_weight * 0.25
        feedback.append("Only includes one character type")

    # 3. Character mix (avoiding repetition or simple sequences)
    if len(set(password)) / length > 0.8:
        score += mix_weight
    elif len(set(password)) / length > 0.6:
        score += mix_weight * 0.75
    else:
        score += mix_weight * 0.5
    if len(set(password)) / length < 0.6:
        feedback.append("Consider using more unique characters")

    # 4. Uniqueness check (simple check for common patterns)
    unique_chars = len(set(password))
    if unique_chars >= 8:
        score += unique_weight
    else:
        score += unique_weight * (unique_chars / 8)
    if unique_chars < 8:
        feedback.append(f"Fewer than 8 unique characters ({unique_chars})")

    # 5. Final score and assessment
    score = min(int(score), 100) # Cap the score at 100
    
    assessment = ""
    if score >= 90:
        assessment = "Excellent"
    elif score >= 75:
        assessment = "Strong"
    elif score >= 50:
        assessment = "Good"
    elif score >= 25:
        assessment = "Weak"
    else:
        assessment = "Very Weak"

    return {
        'score': score,
        'assessment': assessment,
        'feedback': feedback
    }

def generate_password(length=16): # Increased default length for stronger passwords
    """Generates a random password with a mix of characters."""
    # Define character sets for password generation
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = string.punctuation

    all_chars = lowercase + uppercase + digits + symbols
    
    # Ensure the password contains at least one of each character type
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(symbols)
    ]

    # Fill the rest of the password length with random characters
    password += random.choices(all_chars, k=length - 4)
    
    # Shuffle the list to ensure randomness and return as a string
    random.shuffle(password)
    return "".join(password)

@app.route('/')
def home():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """API endpoint to generate a new password."""
    try:
        data = request.json
        length = int(data.get('length', 16))
        password = generate_password(length)
        return jsonify({'password': password})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/check-strength', methods=['POST'])
def check_strength():
    """API endpoint to check the strength of a password."""
    try:
        data = request.json
        password = data.get('password', '')
        strength = check_password_strength(password)
        return jsonify(strength)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)