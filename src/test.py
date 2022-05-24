# 動作確認済み

from pos2vmd import positions_to_frames, make_showik_frames, convert_position, convert_position_mmpose
from VmdWriter import VmdWriter
import pickle

center_enabled=False
vmd_file = "res.vmd"

bone_frames = []
frame_num = 0

positions_list = []
visibility = [True,  True,  True,  True,  True,  True,  True,  True,  True, True,  True,  True,  True,  True]
visibility_list = []

with open('pose.pickle', 'rb') as p:
    l = pickle.load(p)

for j in range(len(l)):
    keypoints_3d = l[j][0]['keypoints_3d']
    positions = convert_position_mmpose(keypoints_3d) # positionsをQVector3Dの配列に変換
    positions_list.append(positions)
    visibility_list.append(visibility)

# VMD化(フレームごとにfor)
for positions, visibility in zip(positions_list, visibility_list):
    print("p-v: ", positions, visibility) # この時点でQVector3Dの配列, booleanの配列 になっている必要あり
    if positions is None:
        frame_num += 1
        continue
    bf = positions_to_frames(positions, visibility, frame_num, center_enabled)
    bone_frames.extend(bf)
    frame_num += 1

showik_frames = make_showik_frames()
writer = VmdWriter()
writer.write_vmd_file(vmd_file, bone_frames, showik_frames)