
particlesJS("particles-js", {
    "particles": {
        "number": {
            "value": 100,
            "density": { "enable": true, "value_area": 800 }
        },
        "color": { "value": "#00ffcc" }, /* Màu xanh công nghệ */
        "shape": { "type": "circle" },
        "opacity": {
            "value": 0.6,
            "random": true
        },
        "size": {
            "value": 3,
            "random": true
        },
        "line_linked": {
            "enable": true,
            "distance": 150,
            "color": "#00ffcc",
            "opacity": 0.3,
            "width": 1
        },
        "move": {
            "enable": true,
            "speed": 1, /* Tốc độ di chuyển vừa phải, mượt mà */
            "direction": "none",
            "out_mode": "out"
        }
    },
    "interactivity": {
        "detect_on": "canvas",
        "events": {
            "onhover": {
                "enable": true,
                "mode": "grab" /* Hút các đường nối khi di chuột qua */
            },
            "onclick": {
                "enable": false,
                "mode": "none" /* Thêm hạt khi click */
            }
        },
        "modes": {
            "grab": { "distance": 140, "line_linked": { "opacity": 0.8 } }
        }
    },
    "retina_detect": true
});