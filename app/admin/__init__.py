from flask import Blueprint

admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="templates",
    static_folder="static",
)

# import view modules to register routes
from . import routes, auth
