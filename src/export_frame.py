
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from concurrent.futures import ThreadPoolExecutor

import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "0"
# os.environ['TF_ENABLE_ONEDNN_OPTS'] = "0"
# import argparse
import cv2

VIDEO_PATH = os.path.join(os.getcwd(), 'dataset/raw_video')
FRAMES_PATH = os.path.join(os.getcwd(), 'dataset/raw_frame') 

FRAME_COUNT = 150
MARGIN  = 32
GPU_MEMORY_FRACTION = 1.0
MAX_WORKERS = os.cpu_count()  # Giới hạn số luồng

def extract_frames_from_videos(video_dir=VIDEO_PATH, output_dir=FRAMES_PATH, frame_count=FRAME_COUNT):
    for label in os.listdir(video_dir):
        label_path = os.path.join(video_dir, label)
        if not os.path.isdir(label_path):
            continue
        
        for video_file in os.listdir(label_path):
            video_path = os.path.join(label_path, video_file)
            if not video_file.endswith(('.mp4', '.avi', '.mov')):
                continue
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"Không thể mở video {video_path}.")
                continue
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))            
            if total_frames < 200:
                frame_indices = list(range(total_frames))  # Lấy tất cả các frame nếu ít hơn 200
            else:
                frame_indices = [int(total_frames * i / frame_count) for i in range(frame_count)]

            extracted_frame_count = 0

            def save_frame(frame, output_path):
                cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])

            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = []
                for idx, frame_idx in enumerate(frame_indices):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                    ret, frame = cap.read()
                    if not ret:
                        continue
                    
                    
                    output_label_dir = os.path.join(output_dir, label)
                    os.makedirs(output_label_dir, exist_ok=True)
                    output_path = os.path.join(output_label_dir, f"frame_{idx}.jpg")
                    futures.append(executor.submit(save_frame, frame, output_path))
                    extracted_frame_count+=1

                for future in futures:
                    future.result()
            
            cap.release()
            print(f"Đã trích xuất {extracted_frame_count} khung hình vào {output_label_dir}.")

if __name__ == "__main__":
    extract_frames_from_videos()