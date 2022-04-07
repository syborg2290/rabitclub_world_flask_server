import os
from flask import Flask, request, session, jsonify, json
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from moviepy.editor import *
import base64


UPLOAD_FOLDER = "uploads"

app = Flask(__name__)
cors = CORS(app)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/upload_watch_party", methods=["POST"])
@cross_origin()
def fileUpload():
    target = os.path.join(UPLOAD_FOLDER, "watch_party")
    if not os.path.isdir(target):
        os.mkdir(target)
    file = request.files["file"]
    # file_ext = os.path.splitext(file.filename)[1]
    filename = secure_filename(file.filename)
    destination = "/".join([target, filename])
    file.save(destination)
    session["uploadFilePath"] = destination
    response = "done"
    return response


@app.route("/get_video_chunk", methods=["POST"])
@cross_origin()
def chunkVideo():
    rawdata = request.data
    data = json.loads(rawdata)
    clip = VideoFileClip("uploads/watch_party/" + data.watch_party_id + ".mp4")
    clip = clip.subclip(data.startTimestamp, data.endTimestamp)
    clip.write_videofile(
        "uploads/watch_party/" + data.watch_party_id + "chunk" + ".mp4"
    )
    video_chunk_data = open(
        "uploads/watch_party/" + data.watch_party_id + "chunk" + ".mp4", "r"
    ).read()
    encoded = base64.b64encode(video_chunk_data)
    return jsonify({"message": "done", "result": encoded}), 201


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True, host="0.0.0.0", use_reloader=False)
