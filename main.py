import json
from StringIO import StringIO
import zipfile

from flask import Flask, make_response, render_template, request, url_for
app = Flask("Web Books")


@app.route("/")
def home():
    return render_template("home.html")


demos = {"aiw": {"title": "Alice in Wonderland",
                 "author": "Lewis Carroll"}}

@app.route("/demo/<name>")
def demo(name):
    if not name:
        return "Nothing to see here", 400
    if name not in demos:
        return "Unknown demo", 404

    return render_template(
        "demo.html",
        pdf=url_for("static", filename="Alice In Wonderland.pdf"),
        title=demos[name]["title"],
        author=demos[name]["author"])


@app.route("/upload", methods=["POST"])
def upload():
    title = request.args.get("title", "Untitled")
    author = request.args.get("author", "Anonymous")

    sio = StringIO()
    with zipfile.ZipFile(file=sio, mode="w") as app:

        # Write the manifest to the webapp.
        manifest = {
            "version": "1.0",
            "name": title,
            "description": "%s by %s" % (title, author),
            "icons": {
                "256": "/icons/256.png"
            },
            "developer": {
                "name": author
            },
            "installs_allowed_from": [
                "https://marketplace.mozilla.org/",
                "https://marketplace-dev.mozilla.org/"
            ],
            "launch_path": "/index.html",
            "default_locale": "en"
        }
        app.writestr("manifest.webapp", json.dumps(manifest))

        # Add the PDF to the app.
        app.writestr("book.pdf", request.files["upload"].read())

        def asset(path):
            with open(path, mode="r") as ass:  # LOL
                app.writestr(path, ass.read())

        # Write all the standard assets to the app.
        asset("static/js/vendor/jquery-1.8.2.min.js")
        asset("static/js/pdf.min.js")
        asset("static/js/turn.min.js")
        asset("static/js/book.js")
        asset("static/css/book.css")
        asset("static/css/carrois.woff")
        asset("static/img/wood.png")

    sio.seek(0)
    resp = make_response(sio.getvalue(), 200)
    resp.headers["Content-Disposition"] = (
        'attachment; filename="book.zip"')
    resp.headers["Content-Type"] = "application/octet-stream"
    return resp


if __name__ == "__main__":
    app.debug = True
    app.run()
