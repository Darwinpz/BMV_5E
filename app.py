from flask import Flask
from flask_wtf.csrf import CSRFProtect
from database.mongoDb import DatabaseConnection
from controllers.indexController import index_bp
from controllers.userController import user_bp
from controllers.errorController import error_bp
from controllers.vocacionalController import vocacional_bp
from dotenv import load_dotenv
from commands.adminCommands import seed_admin_command
import os

load_dotenv()

app = Flask(__name__, static_folder='public', static_url_path='')

app.secret_key = os.getenv("SECRET_KEY")

CSRFProtect(app)

with app.app_context():
    DatabaseConnection.initialize()

# -- Control de Cache --
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# -- Rutas BluePrint --
app.register_blueprint(error_bp)
app.register_blueprint(index_bp)
app.register_blueprint(user_bp)
app.register_blueprint(vocacional_bp)

#-- Comandos CLI--
app.cli.add_command(seed_admin_command)

# -- Ejecución --

if __name__ == '__main__':
    app.run(host=os.getenv("HOST"), port=os.getenv("PORT"), debug=os.getenv("DEBUG"))