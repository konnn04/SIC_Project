import os  # Thao tác với hệ thống file và thư mục.
import cv2 as cv  # Thư viện OpenCV để xử lý ảnh và video.
import torch  # Thư viện PyTorch để tính toán tensor và sử dụng GPU.
from facenet_pytorch import MTCNN  # Gói phần mềm MTCNN để phát hiện khuôn mặt.
from datetime import datetime  

# Đường dẫn chứa các thư mục ảnh sau khi chụp
output_directory = r"dataset\raw"

# Đường dẫn chứa các folder video quay
video_directory = r"dataset\raw_video"

# Tạo thư mục nếu chưa có
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

pathvideo = []  # Danh sách chứa đường dẫn tới các video.
label = []      # Danh sách chứa nhãn của các video (tên thư mục chứa video).
pathfolder = []  # Danh sách chứa đường dẫn tới các thư mục chứa video.
indexfolder = 0  # Biến đếm cho thư mục.

# Duyệt qua tất cả các thư mục và video trong video_directory
for i in os.listdir(video_directory): 
    label.append(i)  # Thêm tên thư mục vào danh sách nhãn.
    path1 = os.path.join(video_directory, i)  # Tạo đường dẫn đầy đủ tới thư mục con.
    pathfolder.append(path1)  # Thêm đường dẫn thư mục vào danh sách pathfolder.

    for j in os.listdir(path1):  # Duyệt qua tất cả các file trong thư mục con.
        path2 = os.path.join(path1, j)  # Tạo đường dẫn đầy đủ tới file video.
        pathvideo.append(path2)  # Thêm đường dẫn video vào danh sách pathvideo.

# Khởi tạo MTCNN
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')  # Sử dụng GPU nếu có, ngược lại sử dụng CPU.
mtcnn = MTCNN(keep_all=True, device=device)  # Khởi tạo MTCNN để phát hiện khuôn mặt.

# Hàm cắt khuôn mặt và lưu lại
def extract_faces_from_video(video_path, output_path, num_images=20, size=(128, 128)):
    print(f"Đang xử lý video: {video_path}")
    cap = cv.VideoCapture(video_path)  # Mở video
    if not cap.isOpened():  # Kiểm tra nếu không thể mở video.
        print(f"Không thể mở video: {video_path}")
        return

    count = 0  # Đếm số lượng hình ảnh khuôn mặt đã cắt
    leap = 1  # Sử dụng để giảm số lần chụp ảnh (cứ mỗi 2 frame mới chụp 1 lần)

    while count < num_images:
        ret, frame = cap.read()  # Đọc từng frame của video
        if not ret:  # Kiểm tra nếu không còn frame nào để đọc hoặc lỗi đọc video.
            print("Không còn frame nào để đọc hoặc lỗi đọc video.")
            break  # Thoát nếu không còn frame nào để đọc

        if leap % 2 == 0:  # Chỉ xử lý mỗi 2 frame.
            boxes, _ = mtcnn.detect(frame)  # Phát hiện khuôn mặt trong frame.
            if boxes is not None:  # Kiểm tra nếu phát hiện được khuôn mặt.
                for box in boxes:
                    bbox = list(map(int, box.tolist()))  # Lấy tọa độ của hộp khuôn mặt.
                    face = frame[bbox[1]:bbox[3], bbox[0]:bbox[2]]  # Cắt khuôn mặt ra từ frame
                    if face.size != 0:  # Kiểm tra nếu khuôn mặt không rỗng.
                        try:
                            face = cv.resize(face, size)  # Thay đổi kích thước khuôn mặt về 128x128
                            cv.imwrite(os.path.join(output_path, f'face_{count}.jpg'), face)  # Lưu hình ảnh khuôn mặt
                            print(f"Đã lưu ảnh khuôn mặt {count + 1}/{num_images} từ video: {video_path}")
                            count += 1  # Tăng bộ đếm số lượng hình ảnh khuôn mặt

                            if count >= num_images:  # Kiểm tra nếu đã đạt đến số lượng hình ảnh khuôn mặt cần cắt.
                                print(f"Hoàn thành việc cắt {num_images} ảnh khuôn mặt từ video: {video_path}")
                                break  # Thoát nếu đã đạt đến số lượng hình ảnh khuôn mặt cần cắt
                        except Exception as e:
                            print(f"Error processing frame: {str(e)}")  # In ra lỗi nếu có ngoại lệ
        leap += 1  # Tăng leap để giảm tần suất chụp ảnh

    cap.release()  # Đóng video

# Thực hiện cắt và lưu hình ảnh khuôn mặt từ video
for video_path in pathvideo:
    video_name = os.path.splitext(os.path.basename(video_path))[0]  # Tên video (không bao gồm đuôi file)
    output_path = os.path.join(output_directory, video_name)  # Đường dẫn để lưu hình ảnh khuôn mặt

    if not os.path.exists(output_path):
        os.makedirs(output_path)  # Tạo thư mục lưu hình ảnh khuôn mặt nếu chưa tồn tại
        print(f"Tạo thư mục: {output_path}")

    extract_faces_from_video(video_path, output_path,200)  # Thực hiện cắt và lưu hình ảnh khuôn mặt từ video

print("Hoàn thành quá trình xử lý tất cả các video.")