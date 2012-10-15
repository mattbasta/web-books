import json
from StringIO import StringIO
import tempfile
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
    title = request.form.get("title", "Untitled")
    author = request.form.get("author", "Anonymous")

    with tempfile.NamedTemporaryFile(delete=False, mode="w") as sio:
        tfn = sio.name

        with zipfile.ZipFile(file=sio, mode="w") as app:

            # Write the manifest to the webapp.
            manifest = {
                "version": "1.0",
                "name": title,
                "description": "%s by %s" % (title, author),
                "icons": {
                    "128": "/static/img/icon.png"
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
            asset("static/js/pdf.js")
            asset("static/js/grommet.js")
            asset("static/js/book.js")
            asset("static/js/bastaflip.js")
            asset("static/img/icon.png")
            asset("static/css/book.css")
            asset("static/css/bastaflip.css")
            asset("static/css/carrois.woff")
            asset("static/img/wood.png")

            app.writestr(
                "index.html",
                render_template("demo.html", pdf="/book.pdf", title=title,
                                author=author))

    with open(tfn, mode="r") as sio:
        resp = make_response(sio.read(), 200)
        resp.headers["Content-Disposition"] = (
            'attachment; filename="book.zip"')
        resp.headers["Content-Type"] = "application/octet-stream"
        return resp


if __name__ == "__main__":
    app.debug = True
    app.run()
