console.log("HELLO");
var strings = ["Hi", "How are you?", "good"];

var block = d3.select("#block");
//for(var i = 0; i < strings.length; i++){
//    block.text(strings[0]);
//}

function send(message){
    block.append("").text(message);
    document.getElementById('textbox1').value = "";
    objDiv = document.getElementById("block");
    objDiv.scrollTop = objDiv.scrollHeight;
}