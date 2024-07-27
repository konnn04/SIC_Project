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
import align.detect_face
import random
from time import sleep
import cv2

VIDEO_PATH = os.path.join(os.getcwd(), 'dataset/raw_video')
FRAMES_PATH = os.path.join(os.getcwd(), 'dataset/raw_frame')
PROCESSED_PATH = os.path.join(os.getcwd(), 'dataset/processed')

SIZE = 160
MARGIN  = 32
GPU_MEMORY_FRACTION = 1.0
DELETE_FRAME_EXPORT = True


def delete_directory(directory_path):
    # Kiểm tra nếu đường dẫn tồn tại
    if os.path.exists(directory_path):
        for root, dirs, files in os.walk(directory_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(directory_path)
        print(f"Đã xóa: {directory_path}")
    else:
        print(f"Không thấy thư mục: {directory_path}")

def extract_frames_from_videos(video_dir = VIDEO_PATH, output_dir  = FRAMES_PATH, processed_dir=PROCESSED_PATH, frames_per_second=10, delete_frame_export=DELETE_FRAME_EXPORT):
    for label in os.listdir(video_dir):
        label_path = os.path.join(video_dir, label)        
        # Kiểm tra nếu label_path là thư mục
        if os.path.isdir(label_path):
            # Tạo thư mục đầu ra cho nhãn nếu chưa tồn tại
            label_output_dir = os.path.join(output_dir, label)
            if not os.path.exists(label_output_dir):
                os.makedirs(label_output_dir)                
            # Duyệt qua tất cả các video trong thư mục nhãn
            for video_file in os.listdir(label_path):
                video_path = os.path.join(label_path, video_file)                
                # Kiểm tra nếu video_path là file
                if os.path.isfile(video_path):
                    print(f"Đang xử lý: {video_path}")
                    extract_frames(video_path, label_output_dir, frames_per_second)
    print("Đã xong. Đến bước xử lý!")
    
    data_preprocessing(output_dir, processed_dir, SIZE, MARGIN, random_order=True, gpu_memory_fraction=GPU_MEMORY_FRACTION, detect_multiple_faces=False)
    if delete_frame_export:
        delete_directory(FRAMES_PATH)

def extract_frames(video_path, output_folder, frames_per_second=10):
    video_capture = cv2.VideoCapture(video_path)
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    interval = fps // frames_per_second
    frame_count = 0
    extracted_frame_count = 0
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        if frame_count % interval == 0:
            frame_filename = os.path.join(output_folder, f"frame_{extracted_frame_count:04d}.jpg")
            cv2.imwrite(frame_filename, frame)
            extracted_frame_count += 1
        frame_count += 1
    video_capture.release()
    print(f"Đã trích xuất {extracted_frame_count} khung hình từ {video_path} vào {output_folder}.")


def data_preprocessing(input_dir = FRAMES_PATH, output_dir = PROCESSED_PATH, image_size=SIZE, margin=MARGIN, random_order=False, gpu_memory_fraction=1.0, detect_multiple_faces=False):
    sleep(random.random())
    output_dir = os.path.expanduser(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Store some git revision info in a text file in the log directory
    src_path,_ = os.path.split(os.path.realpath(__file__))
    facenet.store_revision_info(src_path, output_dir, ' '.join(sys.argv))
    dataset = facenet.get_dataset(input_dir)    
    print('Tạo mạng lưới và các tham số cần thiết...')    
    with tf.Graph().as_default():
        # gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
        sess = tf.compat.v1.Session()
        # config=tf.ConfigProto()
        # gpu_options=gpu_options, log_device_placement=False
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
                print(f'✅'+image_path)
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
                                    output_filename_n = "{}_{}{}".format(filename_base, i, file_extension)
                                else:
                                    output_filename_n = "{}{}".format(filename_base, file_extension)
                                imageio.imwrite(output_filename_n, scaled)
                                text_file.write('%s %d %d %d %d\n' % (output_filename_n, bb[0], bb[1], bb[2], bb[3]))
                        else:
                            print('❌"%s"' % image_path)
                            text_file.write('%s\n' % (output_filename))
                            
    print('Tổng số ảnh: %d' % nrof_images_total)
    print('Số ảnh xử lý thành công: %d' % nrof_successfully_aligned)
     

if __name__ == '__main__':
    extract_frames_from_videos()

