document.addEventListener('DOMContentLoaded', function() {
    const multiplyScale = 1.2;
    let scale = 1, panning = false, pointX = 0, pointY = 0;
    let start = { 
        x: 0, 
        y: 0 
    };
    function setTransform() {
        zoom.style.transform = "translate(" + pointX + "px, " + pointY + "px) scale(" + scale + ")";
    }

    const zoom = document.getElementById("zoom");
    
    zoom.onmousedown = function (e) {
        e.preventDefault();
        start = { 
            x: e.clientX - pointX, 
            y: e.clientY - pointY 
        };
        panning = true;
    }

    zoom.onmouseup = function (e) {
        panning = false;
    }

    zoom.onmousemove = function (e) {
        e.preventDefault();
        if (!panning) {
            return;
        }
        pointX = (e.clientX - start.x);
        pointY = (e.clientY - start.y);
        setTransform();
    }

    zoom.onwheel = function (e) {
        e.preventDefault();
        let xs = (e.clientX - pointX) / scale;
        let ys = (e.clientY - pointY) / scale;
        let delta = (e.wheelDelta ? e.wheelDelta : -e.deltaY);

        if (delta > 0) {
            scale *= multiplyScale
        } 
        else {
            scale /= multiplyScale;
        }

        pointX = e.clientX - xs * scale;
        pointY = e.clientY - ys * scale;
        setTransform();
    }
})