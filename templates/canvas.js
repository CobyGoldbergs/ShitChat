var canvas = document.getElementById('c');
var ctx = canvas.getContext('2d');
var radius=0;
var marker = document.getElementById("marker");
var eraser = document.getElementById("eraser");
var editButton = document.getElementById("edit");
var mouseDown = 0;
var markerSelected = false;
var eraserSelected = false;
var canEdit = false;
var whiteEdits = [];
var redEdits = [];
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
    if(markerSelected){
        console.log("(" + e.offsetX + ", " + e.offsetY + ") --- marker");
        redEdits[redEdits.length] = [e.offsetX, e.offsetY];
    }
    if(eraserSelected){
        console.log("(" + e.offsetX + ", " + e.offsetY + ") --- eraser");
        whiteEdits[whiteEdits.length] = [e.offsetX, e.offsetY];
    }
}

marker.addEventListener("click",function(e){
    ctx.fillStyle ="rgba(255, 0, 0, 1.0)";
    radius= 7;
    eraserSelected = false;
    markerSelected = true;
});
eraser.addEventListener("click",function(e){
    ctx.fillStyle ="rgba(255, 255, 255, 1.0)";
    radius= 20;
    markerSelected = false;
    eraserSelected = true;
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


