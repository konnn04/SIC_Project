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
    <li>requirements.txt: Chứa các thư viện cần thiết để chạy. Trong lúc phát triển Project, vui lòng bổ sung nếu có cài thêm thư viện mới. <b>Cài nhanh bằng: "pip install -r requirements.txt"</b></li>
    <li>src\frame_video.py: Demo tách frame khuôn mặt</li>

</ul>

<h2>2. Phân chia công việc</h2>
<ol>
    <li>Tách video thành ảnh mặt (đã cắt) (1 người) (Nhất Duy)</li>
    - Điều kiện:kích thước 128 x 128, 5frame/s (GRAYSCALE hoặc màu cũng được)\
    - Tìm từ khóa face recognition và OpenCV để hỗ trợ làm\
    <li>Tạo mô hình nhận diện khuôn mặt (Cả nhóm - nghiên cứu sau)</li>
    - MCNN \
    - face recognition \
    <li>Train</li>
    <li>Test</li>
    <li>...</li>
</ol>


<h2>3. Cách cài đặt</h2>
<i>Lưu ý: Nhớ chạy bằng môi trường ảo nha, quên là nặng máy ráng chịu. Và chừa ít nhất 6GB bộ nhớ.</i>
<ol>
    <li>
    Cài đặt các thư viện cần thiết    
    <p>
    Mở terminal từ thư mục chính, chạy <b>"python install -r requirements.txt"</b> để cài thư viện
    </p>
    </li>
    
    <li>
    Chuẩn bị dataset và mô hình FaceNet
    <p>Link Dataset: https://drive.google.com/drive/folders/1C9NSSUc2OFSMwHJAye6w0mQIkBoHpcpw?usp=sharing</p>
    <p>Link Facenet: https://drive.usercontent.google.com/download?id=1EXPBSXwTaqrSC0OhUdXNmKSh9qJUQ55-&export=download&authuser=0</p>
    <b>Giải nén rồi đặt vô theo cây thư mục như ảnh</b>
    ![Image](/image2.png)
    </li>
    <li>
    Xử lí ảnh đầu vào
    </p>
    Từ terminal, chạy <b>"python src/videoProcessing.py"</b> để bắt đầu tách frame ảnh và xử lí ảnh đầu vào. Nó sẽ tốn khá nhiều thời gian.... (Sẽ tối ưu sau)
    </p>
    </li>
    <li>
    Train phân lớp mô hình
    </p>
    Tiếp tục, chạy <b>"python src/classifier.py"</b> để bắt đầu train mô hình (Cũng không lâu lắm, sẽ tối ưu sau)
    </p>
    </li>
    <li>
    Test lên web
    </p>
    Chạy <b>"py app.py"</b> để xem thành phẩm
    </p>
    </li>
</ol>
