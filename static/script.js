  $(function() {
    $('#name').on('input',function(){
    $.getJSON($SCRIPT_ROOT + '/_search_wall_update', {
  name: $('input[name="name"]').val(),
  }, function(data) {
  if (data.result[0]){
      $('#search-ac').show();
      $("#one").text(data.result[0]['name']);
      var link = "wall/" + data.result[0]['wall_id'];
      $("#one").attr("href", link)
      if (data.result[1]['name']){
	  $("#two").text(data.result[1]['name']);
	  var link = "wall/" + data.result[1]['wall_id'];
	  $("#two").attr("href", link)
	  if (data.result[2]['name']){
	      $("#three").text(data.result[2]['name']);
	      var link = "wall/" + data.result[2]['wall_id'];
	      $("#three").attr("href", link)
	  }
	  else{
	      $("#three").text(data.result[2]['name']);
	      $("#search-ac").css({'height': "45px"});
	  }
      }
      else{
	  $("#two").text(data.result[1]['name']);
	  $("#search-ac").css({'height': "30px"});
      }
  }
  else {
  $('#search-ac').hide();
  }
  });
  return false;
  });
  });


  $(function() {
    $('#friend').on('input',function(){
    $.getJSON($SCRIPT_ROOT + '/_email_search', {
  name: $('input[name="friend"]').val(),
  }, function(data) {
  $("#friend_one").text(data.result[0]);
  $("#friend_two").text(data.result[1]);
  $("#friend_three").text(data.result[2]);
  });
  return false;
  });
  });
