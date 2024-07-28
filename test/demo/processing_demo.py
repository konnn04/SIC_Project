# Xử lý video thành frame, sau đó xử lý frame thành ảnh đã được xử lý.
# Đường dẫn thư mục video: dataset\raw_video

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ['TF_ENABLE_ONEDNN_OPTS'] = "0"
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
labels_augmented = ["flip", "rotate", "brightness", "noise", "original"]
augmenters = [
    iaa.Fliplr(0.5),  # Lật ảnh theo chiều ngang với xác suất 50%
    iaa.Affine(rotate=(-30, 30)),  # Xoay ảnh trong khoảng -20 đến 20 độ
    iaa.Multiply((0.4, 1.5)),  # Điều chỉnh độ sáng của ảnh
    iaa.AdditiveGaussianNoise(scale=(0, 0.15*255))  # Thêm nhiễu Gaussian
]

def augment_image(image, augmenter):
    # Áp dụng các phương pháp tăng cường dữ liệu lên ảnh
    augmented_image = augmenter(image=image)
    return augmented_image

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



def data_preprocessing(input_dir = FRAMES_PATH, output_dir = PROCESSED_PATH, image_size=SIZE, margin=MARGIN, random_order=False, gpu_memory_fraction=0.5, detect_multiple_faces=False):
    # sleep(random.random()/4)
    output_dir = os.path.expanduser(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Store some git revision info in a text file in the log directory
    src_path,_ = os.path.split(os.path.realpath(__file__))
    facenet.store_revision_info(src_path, output_dir, ' '.join(sys.argv))
    dataset = facenet.get_dataset(input_dir)    
    print('Tạo mạng lưới và các tham số cần thiết...')    
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
    
    minsize = 20 # minimum size of face
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
                            text_file.write('%s\n' % (output_filename))
                            continue
                        if img.ndim == 2:
                            img = facenet.to_rgb(img)
                        img = img[:,:,0:3]

                        augmented_img = [augment_image(img, augmenter) for augmenter in augmenters]+[img] # Tăng cường dữ liệu
                        
                        for index, img in enumerate(augmented_img):
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

                                for i, det in enumerate(det_arr):
                                    det = np.squeeze(det)
                                    bb = np.zeros(4, dtype=np.int32)
                                    bb[0] = np.maximum(det[0]-margin/2, 0)
                                    bb[1] = np.maximum(det[1]-margin/2, 0)
                                    bb[2] = np.minimum(det[2]+margin/2, img_size[1])
                                    bb[3] = np.minimum(det[3]+margin/2, img_size[0])
                                    cropped = img[bb[1]:bb[3],bb[0]:bb[2],:]
                                    from PIL import Image
                                    cropped = Image.fromarray(cropped)
                                    scaled = cropped.resize((image_size, image_size), Image.BILINEAR)
                                    nrof_successfully_aligned += 1
                                    filename_base, file_extension = os.path.splitext(output_filename)
                                    if detect_multiple_faces:
                                        output_filename_n = "{}_{}_{}{}".format(filename_base, labels_augmented[index],i, file_extension)
                                    else:
                                        output_filename_n = "{}_{}{}".format(filename_base,labels_augmented[index], file_extension)
                                    imageio.imwrite(output_filename_n, scaled)
                                    # text_file.write('%s %d %d %d %d\n' % (output_filename_n, bb[0], bb[1], bb[2], bb[3]))
                                    print('✅"%s"' % labels_augmented[index])
                            else:
                                print('❌"%s"' % image_path)
                                text_file.write('%s\n' % (output_filename))
                            
    print('Tổng số ảnh: %d' % nrof_images_total)
    print('Số ảnh xử lý thành công: %d' % nrof_successfully_aligned)
     

if __name__ == '__main__':
    
    data_preprocessing(gpu_memory_fraction=0.8)
    # data_preprocessing()

