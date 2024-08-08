const import_btn = document.getElementById('import')
const delete_btn = document.getElementById('delete')
const camera_layer = document.getElementById('camera')
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const capture = document.getElementById('capture');
const process_box = Array.from(document.getElementsByClassName('process'))[0];
const process = document.getElementById('process');
const cam = document.getElementById('cam');


const ctx = canvas.getContext('2d');

let currentStream = null;
let uploading = false;
let ratio = 1;

const socket = io();


document.getElementById('cameraSelect').addEventListener('change', function() {
    const cameraId = this.value;
    switchCamera(cameraId);
});

import_btn.addEventListener('click', function() {
    camera_layer.classList.toggle('show')
    populateCameraOptions();
})

socket.on('update_result', function(data) {    
    console.log(data);
    if (uploading) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (data['error']) {
            console.log(data['error']);
        }else{
            if (data.progress == 1) {
                alert('Đã xong');
                location.reload();
            }
            process.style.width = data.progress*process_box.offsetWidth + 'px';
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawRectangles(ctx,data.bb[0],data.bb[1],data.bb[2],data.bb[3]);
        }
    }
})

capture.addEventListener('click', function() {
    if (uploading) {
        capture.innerText = 'Bắt đầu quay';
        uploading = false;
    }else{
        capture.innerText = 'Dừng quay';
        uploading = true;
    }    
})

setInterval(()=>{
   if (uploading) {
        const canva2 = document.createElement('canvas');
        canva2.width = video.videoWidth;
        canva2.height = video.videoHeight;
        const ctx = canva2.getContext('2d');
        ctx.drawImage(video, 0, 0, canva2.width, canva2.height);
        const imgData = canva2.toDataURL('image/jpeg');    
        // Gửi khung hình đến server qua WebSocket
        socket.emit('upload', { image: imgData.split(',')[1] });
    }
},100)

async function populateCameraOptions() {
    await navigator.mediaDevices.getUserMedia({ video: true });
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

        })
        .catch(error => {
            console.error('Error accessing camera:', error);
        });
    cam.style.aspectRatio = video.width / video.height;
    cam.style.width = video.width + 'px';
    video.width = cam.offsetWidth;
    video.height = cam.offsetHeight;
    canvas.width = video.width;
    canvas.height = video.height;
}

window.addEventListener('resize', function() {
    cam.style.aspectRatio = video.width / video.height;
    cam.style.width = video.width + 'px';
    video.width = cam.offsetWidth;
    video.height = cam.offsetHeight;
    canvas.width = video.width;
    canvas.height = video.height;
})

function drawRectangles(ctx,x1,y1,x2,y2){    
    ctx.strokeStyle = "#ff0"; // Màu viền hình chữ nhật
    ctx.lineWidth = 2; // Độ dày của đường viền
    x1 = x1 * canvas.width;
    y1 = y1 * canvas.height;
    x2 = x2 * canvas.width;
    y2 = y2 * canvas.height;
    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
}

if (status != 'none') {
    import_btn.style.display = 'none'
}

window.onload = ()=>{
    delete_btn.style.display = 'none'
}

