import os
import dropbox
import re
from flask import Flask, request, redirect, render_template

# --- CONFIG ---
ACCESS_TOKEN = "sl.u.AFzl8z8Kd5vPydS1uFEfbN11N6oxyIaqhS7aGnhQKF0uC7P6pcO5jh0Hr0eFAFU6PGPAAdstcPcQY9rs808noUOb8siuA16qogu1KCShGlP8kHBGydGeo8Ty-vKuiRpJv-OF2VXb-75j9ATMUy9uCsAtoJx2T3dGqMyVLAv6edFELV2xbEVqYKNmcgJ9fXGtnfkYy55ZkG1FD7jR5C98ThB-UWyd1_rlWGA0hgSjlm1TSMcbH-hYYTvJT8el2X3tVmmGHtUcgEFr9V8Bu9rH9EBBVgfhd9bjlDhfTWWb9jPaqgjPYe2hEZV898yg7I7wC334RnW6LPH41PDRH2KCQk3x0J6iIUcgA0iMVwnEHYZobuntGz4v_IkdTUjwAP_7HUViCaMPws41e_aj0QubkEKLimp-dM2mEAx4dylwELg0QYbi94U8JKRN-sB_Xuh_4RN7_Rp1RHU1Aq05JKTkY5fsC8JlbW19Q59axhq3Ua2jrOMFj3uHH9Bg5--zhBgfv22ymY0oC50Z7G88BMYCw00phkTR1CKe5CLpnFqDOC57sbZ7Nw4Ppues2wlr8Z10zdbFcfrWeZSoJhe-RfVmnMcGWFbBKW69qyGUrxUdef2_Nnxk2RRHZxQDC0dhFP9ckoDd4XtrkP0jobT_R3MUjxg6THVXj5Ush-syKNnNK_sKOrp3D0BQKydWKIdTffZ1i5AsH3MtSr2Plc_yvMeb0HnTqa_j-J32tG8LJw1oZSEbAw8yEt5HYkUdqYom5TYiodOl2CVin_VSjEYC-ukTftPZeEdEXOvhxs9bGG1anp_cyrwhzdsgqo9dBj04SPpVWqo8zgo_jIn7ij5ocYd0AT5QhzZsp0O00FrmuJUzDGsOBxcXMTuuJ98XceUXf_WKZPUdHzEB1z5_PkvP_Y5Z6eK23gc_IxV8GwxA_rZXEjFE8caRknoME7t0yxAu2JdRfb_E1krbtghW0iH6HO_5-yYPXWLZPlPMEPTRbX5J3TXbN0cOZGNNwrwoKDz2XHok6tlGtCg5Gr2SOSJrH_zPt-Y0UdLk4CWrD8eqD_MwyzKSJZTtFJvFuj1uiipaoPE4ZLWWx6zU19olKP1iOAQfSdN2IVbzsxQzeNVA0ejHccy73cydcVSfxcdH_TkJod5JYvpr49Xew4R7rwQa3cKPThK4vhrH8fkrb0gTMCTOP2GVwP2AUMJOy-R5rGjoMphTVW2X9gJBndimb0XNEL5sZI-TsnvclSHkU9rIoEk9dKZk_aJ_Essg1jXVKE6sq45UExLZNuiyB1dSbRWeF7kPRIrV"
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
