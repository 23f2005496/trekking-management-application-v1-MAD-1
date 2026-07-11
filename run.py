from app import db, create_app, login_manager
from flask import render_template
from config.commands import register_commands
from app.models.user import User
# Blueprints
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.staff import staff_bp
from app.routes.trekker import trekker_bp

app = create_app()

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(trekker_bp)

register_commands(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
