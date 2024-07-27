import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ['TF_ENABLE_ONEDNN_OPTS'] = "0"
import src.recognition as rec

from app import app, socketio

if __name__ == '__main__':
    rec.init()
    socketio.run(app, debug=True)