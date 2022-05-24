# Description
keypoints_3d -> vmd に変換するAPIです
flaskで動かす

# Usage
http://localhost/pythonapi/pos2vmd/ 

にPOSTでkeypoints_3dのJSONを送れば、vmdが返ってくる仕組み(にしたい)

※ webコンテナで、上のurlをこのコンテナにプロキシする

とはいえまずは、test.pyであれしてもいいかも

test.py pose.pickle
-> pose.vmd

# Setup
1. `docker build -t yk-pose . `
2. `docker run --name yk-pose-ctn -d -p 5000:5000 -it yk-pose /bin/bash`
3. `docker exec -it yk-pose-ctn bash`
4. `uwsgi --ini uwsgi/uwsgi.ini`
5. `tail -f /var/log/uwsgi/uwsgi.log`