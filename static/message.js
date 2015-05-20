console.log("HELLO");


var block = d3.select("#block");


function send(message, user){
    var d = new Date();
    date = d.toLocaleString()
    
    
                    
    block.append("p").style("font-size", "12").text(message);
    
    
    document.getElementById('textbox1').value = "";
    objDiv = document.getElementById("block");
    objDiv.scrollTop = objDiv.scrollHeight;
}

