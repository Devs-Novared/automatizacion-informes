import json
import traceback as tr
import logging
import logging
import logging.config
import yaml

from flask import Flask, Response, redirect, request
from flask_cors import CORS

from src.shared import APP_FLASK_DATA
#from src.archer_api_handler import archer_login, get_data_of_content_id, update_nroTicket, getUserName


app = Flask(__name__)

CORS(app)
# CORS(app, resources={r"/api/*": {"origins": "*"}})
port, host, debug_mode = [APP_FLASK_DATA[index] for index in range(0,3)]

@app.get("/")
def home() -> Response:
    """Recurso GET para home de la aplicacion flask.

    Returns:
        Response: Redireccion a la ruta "/userHours"
    """
    return redirect("/Informes")


if __name__ == "__main__":
    app.run(debug= True, port=5000, host="0.0.0.0")
