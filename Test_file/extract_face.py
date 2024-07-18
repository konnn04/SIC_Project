from facenet_pytorch import MTCNN
import cv2
# from PIL import Image
import torch
import os
from concurrent.futures import ThreadPoolExecutor

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

# def extract_face(input_path = 'Project\\SIC_Project\\Face recognition data\\Dataset',output_path = 'Project\\SIC_Project\\Face recognition data\\NewData'):
#     images,label = [],[]
#     lbl = 0
#     mtcnn = MTCNN(margin = 20,keep_all = False,post_process = False,device = device)
#     for folder_name in os.listdir(input_path):
#         lbl = lbl + 1
#         p = f'{input_path}\\{folder_name}'
#         for file in os.listdir(p):
#             cap = cv2.VideoCapture(f'{p}\\{file}')
#             count = 1
#             leap = 1
#             outFolder = f'{output_path}\\{folder_name}'
#             if not os.path.exists(outFolder):
#                 os.makedirs(outFolder)
#             while cap.isOpened() and count <= 50:
#                 isSuccess,frame = cap.read()
#                 if mtcnn(frame) is not None and leap%2:
#                     filePath = os.path.join(outFolder,f'{count}.jpg')
#                     face_img = mtcnn(frame,save_path = filePath)
#                     count = count + 1
#                 leap += 1
#             cap.release()
#             cv2.destroyAllWindows()

def process_video(file, p, output_path, folder_name, mtcnn):
    cap = cv2.VideoCapture(f'{p}\\{file}')
    count = 1
    leap = 1
    outFolder = f'{output_path}\\{folder_name}'
    if not os.path.exists(outFolder):
        os.makedirs(outFolder)
    while cap.isOpened() and count <= 50:
        isSuccess, frame = cap.read()
        if not isSuccess:
            break
        if mtcnn(frame) is not None and leap % 2:
            filePath = os.path.join(outFolder, f'{count}.jpg')
            face_img = mtcnn(frame, save_path=filePath)
            count += 1
        leap += 1
    cap.release()

def extract_face(input_path='dataset/raw_video', output_path='Test_file/processed'):
    mtcnn = MTCNN(margin=20, keep_all=False, post_process=False, device=device)
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for folder_name in os.listdir(input_path):
            p = f'{input_path}\\{folder_name}'
            for file in os.listdir(p):
                executor.submit(process_video, file, p, output_path, folder_name, mtcnn)

if __name__ == '__main__':
    extract_face()