var canvas = document.getElementById('c');
var ctx = canvas.getContext('2d');
var radius=0;
var marker = document.getElementById("marker");
redMarker = document.getElementById("red");
blueMarker = document.getElementById("blue");
greenMarker = document.getElementById("green");
var redMarker;
var blueMarker;
var greenMarker;
var eraser;

var editButton = document.getElementById("edit");
var mouseDown = 0;

var markerSelected = false;
var redSelected = false;
var blueSelected = false;
var greenSelected = false;

var eraserSelected = false;

var canEdit = false;
var whiteEdits = [];
var redEdits = [];
var blueEdits = [];
var greenEdits = [];

document.body.onmousedown = function() { 
    ++mouseDown;
}
document.body.onmouseup = function() {
    --mouseDown;
}
window.onload = function() {
    ctx.fillStyle ="rgba(0, 10, 25, 0)";
};

draw = function (e) { 
    //draws a circle at (e.offsetX, e.offsetY) of radius 7.
    ctx.beginPath();
    ctx.arc(e.offsetX, e.offsetY, radius, 0,2*Math.PI);
    ctx.fill();
    //stores red and white circle data
    if(redSelected){
        console.log("(" + e.offsetX + ", " + e.offsetY + ") --- red marker");
        redEdits[redEdits.length] = [e.offsetX, e.offsetY];
    }
    if(blueSelected){
        console.log("(" + e.offsetX + ", " + e.offsetY + ") --- blue marker");
        blueEdits[redEdits.length] = [e.offsetX, e.offsetY];
    }
    if(greenSelected){
        console.log("(" + e.offsetX + ", " + e.offsetY + ") --- green marker");
        greenEdits[redEdits.length] = [e.offsetX, e.offsetY];
    }
    if(eraserSelected){
        console.log("(" + e.offsetX + ", " + e.offsetY + ") --- eraser");
        whiteEdits[whiteEdits.length] = [e.offsetX, e.offsetY];
    }
}


marker.addEventListener("click",function(e){
    ctx.fillStyle ="rgba(255, 0, 0, 1.0)";
    radius= 4;
    document.getElementById("tools").innerHTML = document.getElementById("tools").innerHTML 
                                                + "<img src='http://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Circle-green.svg/512px-Circle-green.svg.png' width='50' id='green'>" 
                                                + "<img src ='http://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Circle-red.svg/512px-Circle-red.svg.png' width='50' id='red'>" 
                                                + "<img src ='http://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Circle-blue.svg/2000px-Circle-blue.svg.png' width='50' id='blue'>";
    try{
        redMarker = document.getElementById("red");
        blueMarker = document.getElementById("blue");
        greenMarker = document.getElementById("green");
        eraser = document.getElementById("eraser");
        redMarker.addEventListener("click",function(e){
            ctx.fillStyle ="rgba(255, 0, 0, 1.0)";
            radius= 4;
            eraserSelected = false;
            markerSelected = true;
            redSelected = true;
            blueSelected = false;
            greenSelected = false;

        });
        blueMarker.addEventListener("click",function(e){
            ctx.fillStyle ="rgba(0, 0, 255, 1.0)";
            radius= 4;
            eraserSelected = false;
            markerSelected = true;
            redSelected = false;
            blueSelected = true;
            greenSelected = false;
        });
        greenMarker.addEventListener("click",function(e){
            ctx.fillStyle ="rgba(0, 255, 0, 1.0)";
            radius= 4;
            eraserSelected = false;
            markerSelected = true;
            redSelected = false;
            blueSelected = false;
            greenSelected = true;
        });
        eraser.addEventListener("click",function(e){
            ctx.fillStyle ="rgba(255, 255, 255, 1.0)";
            radius= 20;
            markerSelected = false;
            redSelected = false;
            blueSelected = false;
            greenSelected = false;
            eraserSelected = true;
        });

    }catch(e){}
});
    

editButton.addEventListener("click",function(e){
    if(!canEdit){
        document.getElementById("edit").innerHTML = "Now Editing - Click Here To Save";
    }
    else{
        document.getElementById("edit").innerHTML = "Click Here To Edit";
        //take list of coordinates and upload to the doodle database
        //------coming soon
        //then clears the red and white edits
        whiteEdits = [];
        redEdits = [];

    }
    canEdit = !canEdit;
});


canvas.addEventListener('mousemove', function(e) {
    if (mouseDown&canEdit){
        draw(e);
    }
});


