
# -*- coding: utf-8 -*-
#
# pos2vmd.py - convert joint position data to VMD

from __future__ import print_function

from PyQt5.QtGui import QQuaternion, QVector3D
from VmdWriter import VmdBoneFrame, VmdInfoIk, VmdShowIkFrame
import numpy as np

def positions_to_frames(pos, vis, frame_num=0, center_enabled=False, head_rotation=None):
    """convert positions to bone frames"""
    frames = []
    if len(pos) < 17:
        return frames
    
    # センター
    if center_enabled:
        bf = VmdBoneFrame()
        bf.name = b'\x83\x5a\x83\x93\x83\x5e\x81\x5b' # 'センター'
        bf.frame = frame_num
        bf.position = pos[7]
        frames.append(bf)

    # 上半身
    bf = VmdBoneFrame()
    bf.name = b'\x8f\xe3\x94\xbc\x90\x67' # '上半身'
    bf.frame = frame_num
    direction = pos[8] - pos[7]
    up = QVector3D.crossProduct(direction, (pos[14] - pos[11])).normalized()
    upper_body_orientation = QQuaternion.fromDirection(direction, up)
    initial = QQuaternion.fromDirection(QVector3D(0, 1, 0), QVector3D(0, 0, 1))
    bf.rotation = upper_body_orientation * initial.inverted()
    frames.append(bf)
    upper_body_rotation = bf.rotation
    
    # 下半身
    bf = VmdBoneFrame()
    bf.name = b'\x89\xba\x94\xbc\x90\x67' # '下半身'
    bf.frame = frame_num
    direction = pos[0] - pos[7]
    up = QVector3D.crossProduct(direction, (pos[4] - pos[1]))
    lower_body_orientation = QQuaternion.fromDirection(direction, up)
    initial = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(0, 0, 1))
    bf.rotation = lower_body_orientation * initial.inverted()
    lower_body_rotation = bf.rotation
    frames.append(bf)

    # 首は回転させず、頭のみ回転させる
    # 頭
    bf = VmdBoneFrame()
    bf.name = b'\x93\xaa' # '頭'
    bf.frame = frame_num
    if head_rotation is None:
        # direction = pos[10] - pos[9]
        direction = pos[10] - pos[8]
        up = QVector3D.crossProduct((pos[9] - pos[8]), (pos[10] - pos[9]))
        orientation = QQuaternion.fromDirection(direction, up)
        initial_orientation = QQuaternion.fromDirection(QVector3D(0, 1, 0), QVector3D(1, 0, 0))
        rotation = orientation * initial_orientation.inverted()
        bf.rotation = upper_body_rotation.inverted() * rotation
    else:
        bf.rotation = upper_body_rotation.inverted() * head_rotation
    frames.append(bf)
        
    # 左腕
    bf = VmdBoneFrame()
    bf.name = b'\x8d\xb6\x98\x72' # '左腕'
    bf.frame = frame_num
    direction = pos[12] - pos[11]
    up = QVector3D.crossProduct((pos[12] - pos[11]), (pos[13] - pos[12]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(1.73, -1, 0), QVector3D(1, 1.73, 0))
    rotation = orientation * initial_orientation.inverted()
    # 左腕ポーンの回転から親ボーンの回転を差し引いてbf.rotationに格納する。
    # upper_body_rotation * bf.rotation = rotation なので、
    bf.rotation = upper_body_rotation.inverted() * rotation
    left_arm_rotation = bf.rotation # 後で使うので保存しておく
    if vis[6]: # 左ひじが見えているなら
        frames.append(bf)
    
    # 左ひじ
    bf = VmdBoneFrame()
    bf.name = b'\x8d\xb6\x82\xd0\x82\xb6' # '左ひじ'
    bf.frame = frame_num
    direction = pos[13] - pos[12]
    up = QVector3D.crossProduct((pos[12] - pos[11]), (pos[13] - pos[12]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(1.73, -1, 0), QVector3D(1, 1.73, 0))
    rotation = orientation * initial_orientation.inverted()
    # 左ひじポーンの回転から親ボーンの回転を差し引いてbf.rotationに格納する。
    # upper_body_rotation * left_arm_rotation * bf.rotation = rotation なので、
    bf.rotation = left_arm_rotation.inverted() * upper_body_rotation.inverted() * rotation
    # bf.rotation = (upper_body_rotation * left_arm_rotation).inverted() * rotation # 別の表現
    if vis[6] and vis[7]: # 左ひじと左手首が見えているなら
        frames.append(bf)

    
    # 右腕
    bf = VmdBoneFrame()
    bf.name = b'\x89\x45\x98\x72' # '右腕'
    bf.frame = frame_num
    direction = pos[15] - pos[14]
    up = QVector3D.crossProduct((pos[15] - pos[14]), (pos[16] - pos[15]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(-1.73, -1, 0), QVector3D(1, -1.73, 0))
    rotation = orientation * initial_orientation.inverted()
    bf.rotation = upper_body_rotation.inverted() * rotation
    right_arm_rotation = bf.rotation
    if vis[3]: # 右ひじが見えているなら
        frames.append(bf)
    
    # 右ひじ
    bf = VmdBoneFrame()
    bf.name = b'\x89\x45\x82\xd0\x82\xb6' # '右ひじ'
    bf.frame = frame_num
    direction = pos[16] - pos[15]
    up = QVector3D.crossProduct((pos[15] - pos[14]), (pos[16] - pos[15]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(-1.73, -1, 0), QVector3D(1, -1.73, 0))
    rotation = orientation * initial_orientation.inverted()
    bf.rotation = right_arm_rotation.inverted() * upper_body_rotation.inverted() * rotation
    if vis[3] and vis[4]: # 右ひじと右手首が見えているなら
        frames.append(bf)

    # 左足
    bf = VmdBoneFrame()
    bf.name = b'\x8d\xb6\x91\xab' # '左足'
    bf.frame = frame_num
    direction = pos[5] - pos[4]
    up = QVector3D.crossProduct((pos[5] - pos[4]), (pos[6] - pos[5]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(-1, 0, 0))
    rotation = orientation * initial_orientation.inverted()
    bf.rotation = lower_body_rotation.inverted() * rotation
    left_leg_rotation = bf.rotation
    if vis[12]: # 左ひざが見えているなら
        frames.append(bf)
    
    # 左ひざ
    bf = VmdBoneFrame()
    bf.name = b'\x8d\xb6\x82\xd0\x82\xb4' # '左ひざ'
    bf.frame = frame_num
    direction = pos[6] - pos[5]
    up = QVector3D.crossProduct((pos[5] - pos[4]), (pos[6] - pos[5]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(-1, 0, 0))
    rotation = orientation * initial_orientation.inverted()
    bf.rotation = left_leg_rotation.inverted() * lower_body_rotation.inverted() * rotation
    if vis[12] and vis[13]: # 左ひざと左足首が見えているなら
        frames.append(bf)

    # 右足
    bf = VmdBoneFrame()
    bf.name = b'\x89\x45\x91\xab' # '右足'
    bf.frame = frame_num
    direction = pos[2] - pos[1]
    up = QVector3D.crossProduct((pos[2] - pos[1]), (pos[3] - pos[2]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(-1, 0, 0))
    rotation = orientation * initial_orientation.inverted()
    bf.rotation = lower_body_rotation.inverted() * rotation
    right_leg_rotation = bf.rotation
    if vis[9]: # 右ひざが見えているなら
        frames.append(bf)
    
    # 右ひざ
    bf = VmdBoneFrame()
    bf.name = b'\x89\x45\x82\xd0\x82\xb4' # '右ひざ'
    bf.frame = frame_num
    direction = pos[3] - pos[2]
    up = QVector3D.crossProduct((pos[2] - pos[1]), (pos[3] - pos[2]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(-1, 0, 0))
    rotation = orientation * initial_orientation.inverted()
    bf.rotation = right_leg_rotation.inverted() * lower_body_rotation.inverted() * rotation
    if vis[9] and vis[10]: # 右ひざと右足首が見えているなら
        frames.append(bf)

    return frames

def make_showik_frames():
    frames = []
    sf = VmdShowIkFrame()
    sf.show = 1
    sf.ik.append(VmdInfoIk(b'\x8d\xb6\x91\xab\x82\x68\x82\x6a', 0)) # '左足ＩＫ'
    sf.ik.append(VmdInfoIk(b'\x89\x45\x91\xab\x82\x68\x82\x6a', 0)) # '右足ＩＫ'
    sf.ik.append(VmdInfoIk(b'\x8d\xb6\x82\xc2\x82\xdc\x90\xe6\x82\x68\x82\x6a', 0)) # '左つま先ＩＫ'
    sf.ik.append(VmdInfoIk(b'\x89\x45\x82\xc2\x82\xdc\x90\xe6\x82\x68\x82\x6a', 0)) # '右つま先ＩＫ'
    frames.append(sf)
    return frames

def convert_position(pose_3d):
    positions = []
    if pose_3d is None:
        return positions
    
    # TODO: Multi person support
    pose = pose_3d[0]
    for j in range(pose.shape[1]):
        q = QVector3D(pose[0, j], pose[2, j], pose[1, j])
        positions.append(q)
    return positions


def convert_position_mmpose(keypoints_3d):
    positions = []
    if keypoints_3d is None:
        return positions
    
    pose = keypoints_3d # この時点で、[[x,y,z],[x,y,z]...]
    for point in pose:
        q = QVector3D(point[0]*-1, point[2], point[1]) # 
        positions.append(q)
    return positions

def dict2array(d):
    keys = ['x', 'y', 'z']
    a = np.empty(0)
    for key in keys:
        a = np.append(a, d[key])
    return a # x,y,zの順の配列が帰る

def convert_position_mediapipe(points_mp):

    # 返すモノ
    positions = []

    if points_mp is None:
        return positions

    # print(points_mp[24])
    # > [{'x': -0.03426040709018707, 'y': -0.6185110807418823, 'z': -0.173828125, 'score': 0.9999817609786987, 'name': 'nose'}, ..]

    # dictだと扱いにくいのでarrayに(numpyのarray)
    points_mp_array = []
    for pm in points_mp:
        points_mp_array.append( dict2array(pm) )

    # 17点のpointsに変換
    points = []
    
    points.append( (points_mp_array[24] + points_mp_array[23]) / 2 )
    points.append( points_mp_array[23] )
    points.append( points_mp_array[25] )
    points.append( points_mp_array[27] )
    points.append( points_mp_array[24] )
    points.append( points_mp_array[26] )
    points.append( points_mp_array[28] )
    points.append([]) # 7
    points.append( (points_mp_array[12] + points_mp_array[11]) / 2 )
    points.append([]) # 9
    points.append( points_mp_array[0] )
    points.append( points_mp_array[12] )
    points.append ( points_mp_array[14] )
    # points.append( points_mp_array[16] ) # 13
    points.append( (points_mp_array[20] + points_mp_array[18]) / 2 ) # 13
    points.append( points_mp_array[11] )
    points.append( points_mp_array[13] )
    # points.append( points_mp_array[15] ) # 16
    points.append( (points_mp_array[19] + points_mp_array[17]) / 2 ) # 16

    points[7] = (points[0] + points[8]) / 2
    #points[9] = ( points[8] + (points_mp_array[10] + points_mp_array[9]) / 2 ) / 2
    points[9] = ( points[8] + points_mp_array[0] ) / 2

    #print(points)

    # QVector3Dに変換
    for point in points:
        positions.append( QVector3D(point[0], point[1]*-1, point[2]*-1) )

    return positions