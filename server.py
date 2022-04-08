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
def chunkVideo():
    rawdata = request.data
    data = json.loads(rawdata)

    fullvideo_path = "uploads/watch_party/" + data.watch_party_id + ".mp4"
    chunkVideo_path = "uploads/watch_party/" + data.watch_party_id + "chunk" + ".mp4"

    if os.path.exists(fullvideo_path):
        clip = VideoFileClip(fullvideo_path)
        clip = clip.subclip(data.startTimestamp, data.endTimestamp)
        clip.write_videofile(chunkVideo_path)
        video_chunk_data = open(chunkVideo_path, "r", encoding="utf-8").read()
        encoded = base64.b64encode(video_chunk_data)
        return jsonify({"message": "done", "result": encoded}), 200

    return jsonify({"message": "undone"})


@app.route("/video_chunk_base64", methods=["POST"])
def chunkVideoToBase64():
    target = os.path.join(UPLOAD_FOLDER, "watch_party")
    if not os.path.isdir(target):
        os.mkdir(target)
    file = request.files["file"]
    # file_ext = os.path.splitext(file.filename)[1]
    filename = secure_filename(file.filename)
    destination = "/".join([target, filename])
    file.save(destination)
    session["uploadFilePath"] = destination
    video_chunk_data = open(destination, "r").read()
    encoded = base64.b64encode(video_chunk_data)
    response = encoded
    return response


@app.route("/remove_videodata_watchparty", methods=["POST"])
def removeVideoData():
    rawdata = request.data
    data = json.loads(rawdata)

    chunkVideo_path = "uploads/watch_party/" + data.watch_party_id + "chunk" + ".mp4"

    if os.path.exists(chunkVideo_path):
        os.remove(chunkVideo_path)
        return "done"

    return "undone"


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True, host="0.0.0.0", use_reloader=False)
