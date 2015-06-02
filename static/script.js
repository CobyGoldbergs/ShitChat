  $(function() {
    $('#name').on('input',function(){
    $.getJSON($SCRIPT_ROOT + '/_search_wall_update', {
  name: $('input[name="name"]').val(),
  }, function(data) {
  $("#one").text(data.result[0]);
  $("#two").text(data.result[1]);
  $("#three").text(data.result[2]);
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
