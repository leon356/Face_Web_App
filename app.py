import os
import dropbox
import json
from flask import Flask, request, redirect, render_template

# === CONFIG ===
ACCESS_TOKEN = os.environ["DROPBOX_TOKEN"]
UPLOAD_FOLDER = "/faces/"
ALLOWED_EXT = {"png", "jpg", "jpeg"}

app = Flask(__name__)
dbx = dropbox.Dropbox(ACCESS_TOKEN)

def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("selfie")
        username = request.form.get("username", "").strip().upper()
        fan = 'fan' in request.form
        lights = 'lights' in request.form
        duration = int(request.form.get("duration", 30))  # default 30s

        if file and allowed(file.filename) and username:
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{username}.{ext}"
            img_data = file.read()

            # Upload image
            dbx.files_upload(img_data, UPLOAD_FOLDER + filename, mode=dropbox.files.WriteMode("overwrite"))

            # Upload config JSON
            config = {
                "name": username,
                "fan": fan,
                "lights": lights,
                "duration": duration
            }
            config_bytes = json.dumps(config).encode()
            dbx.files_upload(config_bytes, UPLOAD_FOLDER + f"{username}.json", mode=dropbox.files.WriteMode("overwrite"))

            return redirect("/success")

    return render_template("index.html")

@app.route("/success")
def success():
    return "<h2>✅ Upload successful! Your settings and image were uploaded.</h2>"

if __name__ == "__main__":
    app.run(debug=True)
