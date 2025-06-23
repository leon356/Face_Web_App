import os
import dropbox
import re
from flask import Flask, request, redirect, render_template

# --- CONFIG ---
ACCESS_TOKEN = os.environ["DROPBOX_TOKEN"]
UPLOAD_FOLDER = "/faces/"
ALLOWED_EXT = {"png", "jpg", "jpeg"}
# --------------

app = Flask(__name__)
dbx = dropbox.Dropbox(ACCESS_TOKEN)

def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def sanitize_filename(name):
    # Remove any unsafe characters
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("username")
        file = request.files.get("selfie")

        if file and allowed(file.filename) and name:
            ext = file.filename.rsplit(".", 1)[1].lower()
            safe_name = sanitize_filename(name.strip())
            filename = f"{safe_name}.{ext}"

            data = file.read()
            dbx.files_upload(data, UPLOAD_FOLDER + filename, mode=dropbox.files.WriteMode("overwrite"))
            return redirect("/success")

    return render_template("index.html")

@app.route("/success")
def success():
    return "<h2>✅ Uploaded! Your face was saved with your name to Dropbox.</h2>"

if __name__ == "__main__":
    app.run(debug=True)
