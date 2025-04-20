from flask import Flask
from flasgger import Swagger
from docs.swagger_config import swagger_template
from routes.automation import api
import os


def create_app():
    app = Flask(__name__)
    Swagger(app, template=swagger_template)
    app.register_blueprint(api, url_prefix="/api/automation")
    return app

app = create_app()

if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8080, debug=True)
    port = int(os.environ.get("PORT", 8080))  # usa a porta definida pela Render
    app.run(host="0.0.0.0", port=port)
