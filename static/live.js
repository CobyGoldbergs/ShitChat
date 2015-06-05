var ThisTag = window.location.pathname.split( '/' )[1];


var instaMessage = setInterval( $(function() {
                                  
                                $getJSON($SCRIPT_ROOT + '/_message_update',
                                         {tag: ThisTag}, function(data) {
                                         
                                         
                                         if data['new'] > 0{
                                         
                                         }
                                         }
                                         )
                                  }