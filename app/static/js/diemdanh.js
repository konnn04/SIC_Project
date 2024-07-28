const video = document.getElementById('video');
const cam = document.getElementById('cam');
video.height = cam.offsetHeight;
video.width = cam.offsetWidth;
// Biến kiểm tra xem điểm danh có đang được bật hay không
let isAttendanceOn = false;
// Chuyển đổi camera
let currentStream = null;
// Khởi tạo socket
const socket = io();

let size = 2000;

const ping = new Audio('./static/audio/snap-sound.mp3');

function playPing() {
    ping.currentTime = 0;
    ping.play();
}

// Khởi động webcam
// navigator.mediaDevices.getUserMedia({ video: true })
//     .then(stream => {
//         currentStream = stream;
//         video.srcObject = stream;
//     })
//     .catch(err => {
//         console.error('Error accessing webcam: ', err);
//     });

function captureFrame() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imgData = canvas.toDataURL('image/jpeg');
    
    // Gửi khung hình đến server qua WebSocket
    socket.emit('frame', { image: imgData.split(',')[1] });
}

function startCapturing() {
    setInterval(() => {
        if (isAttendanceOn)
            captureFrame();
        else {
            // Xóa kết quả trên màn hình
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            text.innerText = "";
        }
    },size/1000); // Chụp và gửi khung hình mỗi giây
    console.log();
}

// Bắt đầu quá trình chụp khung hình
video.addEventListener('loadeddata', startCapturing);

const canvas = document.getElementById('canvas');
canvas.width = video.width;
canvas.height = video.height;
const ctx = canvas.getContext('2d');
const text = document.getElementById('result');
// Nhận kết quả từ server
socket.on('update_checkin_students', (data) => {
    tbody = document.getElementById('table');
    tbody.innerHTML = "";
    data.forEach((element,i) => {
        tr = document.createElement('tr');
        tr.innerHTML = `<td>${i+1}</td><td>${element.student_id}</td><td>${element.svlname} ${element.svfname}</td><td>${element.class_id}</td><td>${element.date_time}</td>`;
        tbody.appendChild(tr);
    });
})

socket.on('update_results2', (data) => {
    // console.log(data)
    if (data.update) 
        playPing()
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (data && data.persons_detected.length >0) {        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        text.innerText = ""
        data.persons_detected.forEach((e,i) => {                    
            let p = e.accuracy.toFixed(2)
            const textName = `${e.name} + ${e.name!="Unknown" ? `- Độ chính xác: ${p*100}%`:""}\n`
            text.innerText += textName
            // Vẽ hình chữ nhật và tên người được nhận diện                    
            if (p<0.9) {
                text.style.color = 'red';
            }else{
                text.style.color = 'green';
            }
            drawRectangles(ctx,e.x1,e.y1,e.x2,e.y2,e.name,p,text.style.color)
            });
    }
    else {
        console.log('No faces detected');
        text.innerText = "Không thấy khuôn mặt"
    }
});

// Vẽ hình chữ nhật và tên người được nhận diện
function drawRectangles(ctx,x1,y1,x2,y2,text,p,color){    
    ctx.strokeStyle = color; // Màu viền hình chữ nhật
    ctx.lineWidth = 2; // Độ dày của đường viền
    x1 = x1 * canvas.width;
    y1 = y1 * canvas.height;
    x2 = x2 * canvas.width;
    y2 = y2 * canvas.height;
    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
    const textX = x1;
    const textY = y2 + 20;
    ctx.fillStyle = color; // Màu chữ
    ctx.font = '16px Arial';
    if (p>0.8)
        ctx.fillText(text, textX, textY);
    else
        ctx.fillText("Không xác định", textX, textY);
}
// Khởi tạo camera mặc định và các camera khác nếu có 
function populateCameraOptions() {
    navigator.mediaDevices.enumerateDevices()
        .then(devices => {
            const videoSelect = document.getElementById('cameraSelect');
            videoSelect.innerHTML = '';
            devices.forEach(device => {
                if (device.kind === 'videoinput') {
                    const option = document.createElement('option');
                    option.value = device.deviceId;
                    option.text = device.label || `Camera ${videoSelect.length + 1}`;
                    videoSelect.appendChild(option);
                }
            });
            if (currentStream==null && videoSelect.options.length > 0) {
                switchCamera(videoSelect.options[0].value);
            }
        })
        .catch(error => {
            console.error('Không có quyền truy cập camera hoặc không phát hiện:', error);
        });
}

// Chuyển đổi camera
function switchCamera(cameraId) {
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
    }
    const constraints = {
        video: {
            deviceId: {
                exact: cameraId
            }
        },
        width: { ideal: 1920 },
        height: { ideal: 1080 }
    };
    navigator.mediaDevices.getUserMedia(constraints)
        .then(stream => {
            currentStream = stream;
            video.srcObject = stream;

            video.onloadedmetadata = () => {
                size = video.videoHeight *  video.videoWidth;
            };
        })
        .catch(error => {
            console.error('Error accessing camera:', error);
        });
}
// Bật/tắt điểm danh
document.getElementById('toggleAttendance').addEventListener('click', function() {
    isAttendanceOn = !isAttendanceOn;
    this.textContent = isAttendanceOn ? 'Tắt Điểm Danh' : 'Bật Điểm Danh';
});
// Các sự kiện khi nhấn các nút
document.getElementById('cameraSelect').addEventListener('change', function() {
    const cameraId = this.value;
    switchCamera(cameraId);
});

document.addEventListener('DOMContentLoaded', populateCameraOptions);