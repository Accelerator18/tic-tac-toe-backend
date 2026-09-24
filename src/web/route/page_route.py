from flask import Blueprint, render_template


def create_page_blueprint() -> Blueprint:
    page_blueprint = Blueprint("pages", __name__)

    @page_blueprint.get("/")
    def index():
        return render_template("index.html")

    return page_blueprint
