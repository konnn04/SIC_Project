# Xử lý video thành frame, sau đó xử lý frame thành ảnh đã được xử lý.
# Đường dẫn thư mục video: dataset\raw_video

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "1"
os.environ['TF_ENABLE_ONEDNN_OPTS'] = "0"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Tắt các cảnh báo không quan trọng
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'  # Cho phép TensorFlow sử dụng GPU một cách linh hoạt
# import argparse
import tensorflow as tf
import numpy as np
import facenet
import align.detect_face
import random
from time import sleep
import cv2
import imgaug.augmenters as iaa

# VIDEO_PATH = os.path.join(os.getcwd(), 'dataset/raw_video')
FRAMES_PATH = os.path.join(os.getcwd(), 'dataset/raw_frame')
PROCESSED_PATH = os.path.join(os.getcwd(), 'dataset/processed')

SIZE = 160
MARGIN  = 32
GPU_MEMORY_FRACTION = 1.0

# def delete_directory(directory_path):
#     # Kiểm tra nếu đường dẫn tồn tại
#     if os.path.exists(directory_path):
#         for root, dirs, files in os.walk(directory_path, topdown=False):
#             for name in files:
#                 os.remove(os.path.join(root, name))
#             for name in dirs:
#                 os.rmdir(os.path.join(root, name))
#         os.rmdir(directory_path)
#         print(f"Đã xóa: {directory_path}")
#     else:
#         print(f"Không thấy thư mục: {directory_path}")

def is_face_too_tilted(det):
    # Hàm kiểm tra khuôn mặt bị nghiêng dựa trên bounding box
    x1, y1, x2, y2 = det
    width = x2 - x1
    height = y2 - y1
    aspect_ratio = width / height
    return aspect_ratio < 0.5 or aspect_ratio > 1.5  # Ngưỡng độ nghiêng có thể điều chỉnh

def is_face_within_frame(det, img_shape):
    x1, y1, x2, y2 = det
    img_height, img_width = img_shape[:2]
    return x1 >= 0 and y1 >= 0 and x2 <= img_width and y2 <= img_height

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
    return image_aug

def data_preprocessing(input_dir = FRAMES_PATH, output_dir = PROCESSED_PATH, image_size=SIZE, margin=MARGIN, random_order=False, gpu_memory_fraction=0.5, detect_multiple_faces=False):
    sleep(0.000000001)
    output_dir = os.path.expanduser(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Store some git revision info in a text file in the log directory
    src_path,_ = os.path.split(os.path.realpath(__file__))
    facenet.store_revision_info(src_path, output_dir, ' '.join(sys.argv))
    dataset = facenet.get_dataset(input_dir)    
    print('Tải mô hình phát hiện kuoon mặt...')    
    # Load MTCNN
    with tf.Graph().as_default():        
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                # Thiết lập giới hạn bộ nhớ GPU
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logical_gpus = tf.config.experimental.list_logical_devices('GPU')
                print(f"{len(gpus)} Physical GPUs, {len(logical_gpus)} Logical GPUs")
            except RuntimeError as e:
                # Xử lý lỗi nếu có
                print(e)

        # Thiết lập cấu hình phiên làm việc
        config = tf.compat.v1.ConfigProto()
        config.gpu_options.per_process_gpu_memory_fraction = gpu_memory_fraction
        config.log_device_placement = False
        
        sess = tf.compat.v1.Session(config=config)
        
        with sess.as_default():
            pnet, rnet, onet = align.detect_face.create_mtcnn(sess, None)
    
    minsize = 25 # minimum size of face
    threshold = [ 0.6, 0.7, 0.7 ]  # three steps's threshold
    factor = 0.709 # scale factor

    # Add a random key to the filename to allow alignment using multiple processes
    random_key = np.random.randint(0, high=99999)
    bounding_boxes_filename = os.path.join(output_dir, 'bounding_boxes_%05d.txt' % random_key)
    
    with open(bounding_boxes_filename, "w") as text_file:
        nrof_images_total = 0
        nrof_successfully_aligned = 0
        if random_order:
            random.shuffle(dataset)
        for cls in dataset:
            output_class_dir = os.path.join(output_dir, cls.name)
            if not os.path.exists(output_class_dir):
                os.makedirs(output_class_dir)
                if random_order:
                    random.shuffle(cls.image_paths)
            for image_path in cls.image_paths:
                nrof_images_total += 1
                filename = os.path.splitext(os.path.split(image_path)[1])[0]
                output_filename = os.path.join(output_class_dir, filename+'.png')
                print(f'Duyệt qua: '+image_path)
                if not os.path.exists(output_filename):
                    try:
                        import imageio
                        img = imageio.imread(image_path)
                    except (IOError, ValueError, IndexError) as e:
                        errorMessage = '{}: {}'.format(image_path, e)
                        print(errorMessage)
                    else:
                        if img.ndim<2:
                            print('❌"%s"' % image_path)
                            continue
                        if img.ndim == 2:
                            img = facenet.to_rgb(img)
                        img = img[:,:,0:3]
                        #Ảnh gốc và ảnh được tăng cường dữ liệu
                        augmented_img = [augment_image(img)]+[img] # Tăng cường dữ liệu
                        
                        for index_a, img in enumerate(augmented_img):
                            bounding_boxes, _ = align.detect_face.detect_face(img, minsize, pnet, rnet, onet, threshold, factor)
                            nrof_faces = bounding_boxes.shape[0]
                            if nrof_faces>0:
                                det = bounding_boxes[:,0:4]
                                det_arr = []
                                img_size = np.asarray(img.shape)[0:2]
                                if nrof_faces>1:
                                    if detect_multiple_faces:
                                        for i in range(nrof_faces):
                                            det_arr.append(np.squeeze(det[i]))
                                    else:
                                        bounding_box_size = (det[:,2]-det[:,0])*(det[:,3]-det[:,1])
                                        img_center = img_size / 2
                                        offsets = np.vstack([ (det[:,0]+det[:,2])/2-img_center[1], (det[:,1]+det[:,3])/2-img_center[0] ])
                                        offset_dist_squared = np.sum(np.power(offsets,2.0),0)
                                        index = np.argmax(bounding_box_size-offset_dist_squared*2.0) # some extra weight on the centering
                                        det_arr.append(det[index,:])
                                else:
                                    det_arr.append(np.squeeze(det))
                                #đánh dấu khuôn mặt
                                for i, det in enumerate(det_arr):
                                    if is_face_too_tilted(det) or not is_face_within_frame(det, img.shape):
                                        print('❌"%s"' % ['augment','original'][index_a])
                                        continue                                       
                                    det = np.squeeze(det)
                                    bb = np.zeros(4, dtype=np.int32)
                                    bb[0] = np.maximum(det[0]-margin/2, 0)
                                    bb[1] = np.maximum(det[1]-margin/2, 0)
                                    bb[2] = np.minimum(det[2]+margin/2, img_size[1])
                                    bb[3] = np.minimum(det[3]+margin/2, img_size[0])
                                    cropped = img[bb[1]:bb[3],bb[0]:bb[2],:]
                                    from PIL import Image
                                    cropped = Image.fromarray(cropped)
                                    # scaled = cropped.resize((image_size, image_size), Image.BILINEAR)
                                    scaled = cropped.resize((image_size, image_size), Image.BILINEAR)
                                    nrof_successfully_aligned += 1
                                    filename_base, file_extension = os.path.splitext(output_filename)
                                    if detect_multiple_faces:
                                        output_filename_n = "{}_{}_{}{}".format(filename_base, ['augment','original'][index_a],i, file_extension)
                                    else:
                                        output_filename_n = "{}_{}{}".format(filename_base,['augment','original'][index_a], file_extension)
                                    imageio.imwrite(output_filename_n, scaled)
                                    text_file.write('%s %d %d %d %d\n' % (output_filename_n, bb[0], bb[1], bb[2], bb[3]))
                                    print('✅"%s"' % ['augment','original'][index_a])
                            else:
                                print('❌"%s"' % image_path)
                                text_file.write('%s\n' % (output_filename))
                            
    print('Tổng số ảnh: %d' % nrof_images_total)
    print('Số ảnh xử lý thành công: %d' % nrof_successfully_aligned)
     

if __name__ == '__main__':
    
    data_preprocessing(gpu_memory_fraction=1.0)
    # data_preprocessing()

