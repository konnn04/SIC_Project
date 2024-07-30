import cv2
import time
from src.recognition import frame_recognition, init

def capture_and_recognize():
    # Mở camera mặc định
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Không thể mở camera")
        return

    while True:
        # Lấy khung hình từ camera
        ret, frame = cap.read()
        if not ret:
            print("Không thể nhận khung hình")
            break
        # Nhận diện khuôn mặt
        result = frame_recognition(frame)
        # Hiển thị khung hình
        cv2.imshow('Camera', result['img'])
        # Chờ 1 giây
        time.sleep(0.5)
        # Nhấn 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Giải phóng tài nguyên
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    init()
    capture_and_recognize()