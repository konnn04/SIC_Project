# Xử lý video thành frame, sau đó xử lý frame thành ảnh đã được xử lý.
# Đường dẫn thư mục video: dataset\raw_video

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os

# import argparse
import tensorflow as tf
import numpy as np
import facenet
from deepface import DeepFace
from time import sleep
import imgaug.augmenters as iaa
from PIL import Image

# VIDEO_PATH = os.path.join(os.getcwd(), 'dataset/raw_video')
FRAMES_PATH = os.path.join(os.getcwd(), 'dataset/raw_frame')
PROCESSED_PATH = os.path.join(os.getcwd(), 'dataset/processed')

SIZE = 160
MARGIN  = 32
GPU_MEMORY_FRACTION = 1.0

def augment_image(image):
    # Tạo chuỗi các phép biến đổi
    seq = iaa.Sequential([
        iaa.Fliplr(0.5),  # Lật ảnh theo chiều ngang
        iaa.Affine(rotate=(-15, 15)),  # Xoay ảnh 45 độ
        iaa.MultiplyBrightness((0.6, 1.4)),  # Độ sáng thay đổi ngẫu nhiên
        # iaa.AdditiveGaussianNoise(scale=(0, 0.08*255))  # Thêm nhiễu Gaussian
    ])
    # Thực hiện tất cả các phép biến đổi trên ảnh
    image_aug = seq(image=image)
    return [image]+[image_aug]

def data_preprocessing(input_dir = FRAMES_PATH, output_dir = PROCESSED_PATH, image_size=SIZE, margin=MARGIN, gpu_memory_fraction=0.5):
    sleep(0.000000001)
    output_dir = os.path.expanduser(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Store some git revision info in a text file in the log directory
    src_path, _ = os.path.split(os.path.realpath(__file__))
    facenet.store_revision_info(src_path, output_dir, ' '.join(sys.argv))
    dataset = facenet.get_dataset(input_dir)
    print('Tải mô hình phát hiện khuôn mặt...')

    # Load DeepFace detector
    detector_backend = 'mtcnn'  # 'ssd', 'opencv', 'mtcnn', 'dlib'

    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            tf.config.experimental.set_virtual_device_configuration(
                gpus[0],
                [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=gpu_memory_fraction * 1024)]
            )
        except RuntimeError as e:
            print(e)
    print()
    for object in dataset:
        print('Xử lý dữ liệu cho:', object.name)
        for i, image_path in enumerate(object.image_paths):
            print('  Xử lý ảnh %d/%d: %s' % (i, len(object.image_paths), image_path))
            img_aug = augment_image(np.array(Image.open(image_path)))
            for (j, img) in enumerate(img_aug):
                faces = DeepFace.extract_faces(img_path=img, detector_backend=detector_backend, enforce_detection=False)
                if len(faces) > 0:
                    img = faces[0]["face"]
                    img = Image.fromarray((img * 255).astype(np.uint8))
                    img = img.convert('RGB')
                    img = img.resize((image_size, image_size),Image.Resampling.LANCZOS)
                    output_dir_path = os.path.join(output_dir, object.name)
                    if not os.path.exists(output_dir_path):
                        os.makedirs(output_dir_path)
                    output_file_path = os.path.join(output_dir_path, str(j) + "_" + os.path.basename(image_path))
                    img.save(output_file_path)

        print(object.image_paths)
    print('Hoàn thành xử lý dữ liệu.')

if __name__ == '__main__':
    
    data_preprocessing(gpu_memory_fraction=1.0)
    # data_preprocessing()

