  $(function() {
    $('#name').on('input',function(){
    $.getJSON($SCRIPT_ROOT + '/_search_wall_update', {
  name: $('input[name="name"]').val(),
  }, function(data) {
  if (data.result[0]['name']){
      console.log("show");
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
	      $("#search-ac").css({'height': "95px"});
	  }
	  else{
	      $("#three").text(data.result[2]['name']);
	      $("#search-ac").css({'height': "65px"});
	  }
      }
      else{
	  $("#two").text(data.result[1]['name']);
	  $("#search-ac").css({'height': "35px"});
      }
  }
      else {
	  console.log("hide")
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
  if (data.result[0]['email']){
      console.log("in");
      $('#search-ac-friend').show();
      $("#friend_one").text(data.result[0]['email']);
      var link = "messages/" + data.result[0]['id'];
      $("#friend_one").attr("href", link)
      if (data.result[1]['email']){
	  $("#friend_two").text(data.result[1]['email']);
	  var link = "messages/" + data.result[1]['id'];
	  $("#friend_two").attr("href", link)
	  if (data.result[2]['email']){
	      $("#friend_three").text(data.result[2]['email']);
	      var link = "messages/" + data.result[2]['id'];
	      $("#friend_three").attr("href", link)
	      $("#search-ac-friend").css({'height': "90px"});
	  }
	  else{
	      $("#friend_three").text(data.result[2]['email']);
	      $("#search-ac-friend").css({'height': "60px"});
	  }
      }
      else{
	  $("#friend_two").text(data.result[1]['email']);
	  $("#search-ac-friend").css({'height': "30px"});
      }
  }
      else {
	  $('#search-ac-friend').hide();
      };
  });
	return false;
    });
  });
