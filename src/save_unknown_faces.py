import os
import cv2
import torch
from facenet_pytorch import MTCNN
import pickle
import numpy as np
import tensorflow as tf

UNKNOWN_FACES_DIR = os.path.join('unknown_faces')
MODEL_PATH = os.path.join('models')
EMBEDDINGS_FILE = os.path.join('unknown_faces', 'embeddings.pkl')
IMAGE_SIZE = (128, 128)  # Update this size if needed
NUM_IMAGES = 20

# Khởi tạo MTCNN
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(keep_all=True, device=device)

def capture_unknown_faces(num_images=NUM_IMAGES):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Không thể mở camera")
        return []

    image_paths = []
    count = 0
    leap = 1  # Sử dụng để giảm số lần chụp ảnh (cứ mỗi 2 frame mới chụp 1 lần)

    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            print("Không thể nhận khung hình từ camera")
            break

        if leap % 2 == 0:  # Chỉ xử lý mỗi 2 frame.
            boxes, _ = mtcnn.detect(frame)
            if boxes is not None:
                for box in boxes:
                    bbox = list(map(int, box.tolist()))
                    face = frame[bbox[1]:bbox[3], bbox[0]:bbox[2]]
                    if face.size != 0:
                        try:
                            face = cv2.resize(face, IMAGE_SIZE)
                            face_path = os.path.join(UNKNOWN_FACES_DIR, f'face_{count}.jpg')
                            cv2.imwrite(face_path, face)
                            image_paths.append(face_path)
                            print(f"Đã lưu ảnh khuôn mặt {count + 1}/{num_images}")
                            count += 1

                            if count >= num_images:
                                print(f"Hoàn thành việc cắt {num_images} ảnh khuôn mặt")
                                break
                        except Exception as e:
                            print(f"Error processing frame: {str(e)}")

        # Hiển thị khung hình hiện tại
        cv2.imshow('Camera', frame)

        # Thêm độ trễ nhỏ để hiển thị khung hình
        cv2.waitKey(1)

        leap += 1

    cap.release()
    cv2.destroyAllWindows()
    return image_paths

# Tạo thư mục nếu chưa có
if not os.path.exists(UNKNOWN_FACES_DIR):
    os.makedirs(UNKNOWN_FACES_DIR)

# Gọi hàm để chụp và lưu ảnh khuôn mặt
capture_unknown_faces()