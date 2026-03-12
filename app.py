from flask import Flask, request, jsonify, send_file
import subprocess
import requests
import os
import uuid

app = Flask(__name__)

@app.route('/')
def home():
    return "Zingaloo Video Maker Running!"

@app.route('/create-video', methods=['POST'])
def create_video():
    data = request.json
    audio_url = data['audio_url']
    job_id = str(uuid.uuid4())[:8]
    audio_file = f"/tmp/{job_id}.mp3"
    video_file = f"/tmp/{job_id}.mp4"

    # Download audio
    r = requests.get(audio_url)
    with open(audio_file, 'wb') as f:
        f.write(r.content)

    # Create video using ffmpeg
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', 'color=c=#EA580C:size=1920x1080:rate=30',
        '-i', audio_file,
        '-shortest',
        '-vf', "drawtext=text='ZINGALOO':fontsize=120:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-pix_fmt', 'yuv420p',
        video_file
    ]
    subprocess.run(cmd, check=True)

    return jsonify({"status": "success", "job_id": job_id})

@app.route('/get-video/<job_id>', methods=['GET'])
def get_video(job_id):
    video_file = f"/tmp/{job_id}.mp4"
    if os.path.exists(video_file):
        return send_file(video_file, mimetype='video/mp4')
    return jsonify({"error": "not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
