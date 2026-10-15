from flask import Flask, render_template
from config import Config
from database.db import db
from routes.auth import auth_bp
from routes.donor import donor_bp
from routes.receiver import receiver_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

from models import *

app.register_blueprint(auth_bp)
app.register_blueprint(donor_bp)
app.register_blueprint(receiver_bp)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

if __name__ == "__main__":
    app.run(debug=True)

