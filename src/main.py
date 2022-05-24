from flask import Flask, request, url_for
from pos2vmd import positions_to_frames, make_showik_frames, convert_position, convert_position_mmpose, convert_position_mediapipe
from VmdWriter import VmdWriter
import pickle
import requests

app = Flask(__name__)

@app.route('/pyapi/pos2vmd', methods=['POST', 'GET'])
def pos2vmd():

    print("pos2vmd started.")

    json = request.get_json()

    vmd_file_path = "temp.vmd"

    # ↓------------変換ここから--------------↓

    center_enabled=False

    bone_frames = []
    frame_num = 0

    positions_list = []
    visibility = [True,  True,  True,  True,  True,  True,  True,  True,  True, True,  True,  True,  True,  True]
    visibility_list = []

    i = 0
    for frame in json:
        # keypoints_3d = frame['keypoints3D'] # p.htmlで使用
        keypoints_3d = frame # p_cam.htmlで使用
        positions = convert_position_mediapipe(keypoints_3d) # positionsをQVector3Dの配列に変換
        positions_list.append(positions)
        visibility_list.append(visibility)
        print("frame ", i, ":", positions)
        i = i+1

    # VMD化(フレームごとにfor)
    for positions, visibility in zip(positions_list, visibility_list):
        #print("p-v: ", positions, visibility) # この時点でQVector3Dの配列, booleanの配列 になっている必要あり
        if positions is None:
            frame_num += 1
            continue
        bf = positions_to_frames(positions, visibility, frame_num, center_enabled)
        bone_frames.extend(bf)
        frame_num += 1

    showik_frames = make_showik_frames()
    writer = VmdWriter()
    writer.write_vmd_file(vmd_file_path, bone_frames, showik_frames)

    # ↑------------変換ここまで--------------↑


    # cookieの取得＆再セット
    session_id = request.cookies.get('_cookie', None)
    print("session id: ", session_id)
    cookies = {'_cookie': session_id}

    # room_idの取得
    room_id = request.args.get('room_id')

    url = 'http://ap:6000/api/upload'
    vmd_file = open(vmd_file_path, 'rb')
    data = {
        'room_id': room_id,
        'file_type': 'motion'
    }
    files = {'file-input': (
        'upload.vmd',
        vmd_file
     )}
    req = requests.post(url, files=files, data=data, cookies=cookies)

    if req.status_code == 200:
        return "ok", 200
    else:
        return "ng", 500

if __name__ == "__main__":
    app.run()