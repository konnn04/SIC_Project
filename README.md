<h1>HỆ THỐNG ĐIỂM DANH BẰNG KHUÔN MẶT (MCMM)</h1>
<h2>1. Giới thiệu</h2>
<p>Là một dự án nhóm xây dựng mô hình nhận diện khuôn mặt qua webcam thực tế, đa khuôn mặt</p>
<h3>Cấu trúc thư mục</h3>

![Image](/image.png)



Với:
<ul>
    <li>dataset: Thư mục chứ dataset để huấn luyện</li>
    <li>dataset/raw_video: Thư mục chứ các thư mục chứa video train, tên thư mục đánh dấu là tên nhãn của người đó</li>
    <li>dataset/raw: Thư mục chứ ảnh đã tách frame (Có thể không cần thiết)</li>
    <li>dataset/processed: Thư mục chứ thư mục ảnh đã qua xử lý (Cắt ảnh mặt, xoay,...)</li>
    <li>models: Thư mục chứ model đã huấn luyện xuất ra</li>
    <li>src: Chứa source code của bạn</li>
    <li>requirements.txt: Chứa các thư viện cần thiết để chạy. Trong lúc phát triển Project, vui lòng bổ sung nếu có cài thêm thư viện mới. <b>Cài nhanh bằng: "pip install -r requirements-dev.txt"</b></li>
    <li>src\frame_video.py: Demo tách frame khuôn mặt</li>

</ul>

<h2>2. Phân chia công việc</h2>
1. Tách video thành ảnh mặt (đã cắt) (1 người) (Nhất Duy)
- Điều kiện:kích thước 128 x 128, 5frame/s (GRAYSCALE hoặc màu cũng được)
- Tìm từ khóa face recognition và OpenCV để hỗ trợ làm
2. Tạo mô hình nhận diện khuôn mặt (Cả nhóm - nghiên cứu sau)
- MCNN 
- face recognition
3. Train
4. Test
5. Triển khai viết webapp
6. Xây database lưu người
<h2>3. Lộ trình</h2>
<h1><b>TÁCH ẢNH</b> -> VIẾT MÔ HÌNH -> TRAIN -> TEST -> TỐI ƯU -> XÂY DỰNG DATABASE -> VIẾT WEBAPP</h1>
