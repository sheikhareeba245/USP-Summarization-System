// Flash messages auto hide
setTimeout(function() {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(function(flash) {
        flash.style.opacity = '0';
        flash.style.transition = 'opacity 0.5s';
        setTimeout(() => flash.remove(), 500);
    });
}, 3000);
