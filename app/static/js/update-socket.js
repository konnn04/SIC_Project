document.addEventListener("DOMContentLoaded", function() {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    
    socket.on('connect', function() {
        // socket.emit('my_event', {data: 'I\'m connected!'});
        console.log('Socket connected');
    });
    socket.on('update_results', function(data) {
        let p = data.accuracy.toFixed(2)
        const text = document.getElementById('result');
        if (p<0.8) {
            text.style.color = 'red';
        }else{
            text.style.color = 'green';
        }
        text.innerText = `Tên: ${data.name} - Độ chính xác: ${p*100}%`
        console.log(`Tên: ${data.name} - Độ chính xác: ${data.accuracy}%`);
    });

    
});
