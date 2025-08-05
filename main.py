from flask import Flask, render_template
from routes.settings_routes import settings_bp
from routes.student_routes import student_bp
from routes.auth_routes import auth_bp
from routes.tutor_routes import tutor_bp
from routes.demo_routes import demo_bp

# Creates the Flask app instance
app = Flask(__name__)

# Sets the secret key used for session protection
app.config['SECRET_KEY'] = 'change-this-to-a-very-secret-key'


# Registers route groups for authentication, students, tutors, settings, and demo functionality
app.register_blueprint(auth_bp) # This route handles authentication related functionality like login, registration, and logout
app.register_blueprint(student_bp) # This route handles all student functionality including appointment booking and rating
app.register_blueprint(tutor_bp) # This route handles
app.register_blueprint(settings_bp) # This route handles
app.register_blueprint(demo_bp) # This route

# Returns the homepage of the application
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
