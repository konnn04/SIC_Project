document.addEventListener('DOMContentLoaded', function() {
    let resizeTimeout;

    function adjustBackgroundSize() {
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;
        const imageAspectRatio = 16 / 9; // Giả sử tỷ lệ khung hình 16:9, điều chỉnh nếu cần
        const windowAspectRatio = windowWidth / windowHeight;

        if (windowAspectRatio > imageAspectRatio) {
            document.body.style.backgroundSize = '100% auto';
        } else {
            document.body.style.backgroundSize = 'auto 100%';
        }
    }

    function debouncedAdjustBackgroundSize() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(adjustBackgroundSize, 100);
    }

    window.addEventListener('resize', debouncedAdjustBackgroundSize);
    adjustBackgroundSize(); // Điều chỉnh ban đầu
});