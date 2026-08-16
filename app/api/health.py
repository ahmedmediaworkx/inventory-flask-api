from flask_smorest import Blueprint

blueprint = Blueprint("health", __name__, url_prefix="/api/v1", description="Service health")


@blueprint.route("/health")
def health():
    return {"status": "ok"}
