$(document).ready(function() {
  hljs.initHighlightingOnLoad();
  smoothScroll.init();
  $('[data-toggle="tooltip"]').tooltip();
  smoothScroll.init({
    speed: 500,
    easing: 'easeInOutCubic',
    updateURL: true,
    offset: 50,
    callbackBefore: function ( toggle, anchor ) {},
    callbackAfter: function ( toggle, anchor ) {}
  });
  $("#main-menu").css("margin-top", Math.max(0, 250 - $(this).scrollTop()));
  $(window).scroll(function(){
    $("#main-menu").css("margin-top", Math.max(0, 250 - $(this).scrollTop()));
  });

  function dialog_clean(elements) {
    // $( elements ).each(function( index ) {
    //   console.log( index + ": " + $( this ).text() );
    // });
    elements.remove();
    // elements.css('display', 'none');
    // elements.removeClass('animated fadeInUp fadeInRight fadeInLeft');
    // setTimeout(function() {
    //   $(elements.get().reverse()).prependTo("#dialog-log-trash");
    // }, 1000);
    // // everythin ok below
    // elements.show();
    // elements.addClass('animated fadeOutUp');
    // elements.one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function(){
    //   console.log($(this).text());
    //   $(this).remove();
    // });
  }

  function dialog_show(text, style, footer) {
    var log = $("#dialog-log");
    switch (style) {
      case "status":
        log.append('<p class="text-muted text-center animated fadeInUp"><i>'+text+'</i></p>');
        break
      case "robot":
        dialog_clean($(".answer:last").prevAll().andSelf());
        console.log("removing .answer:last");
        log.append('<blockquote class="answer animated fadeInRight"><p>'+text+'</p><footer><i>'+footer+'</i></footer></blockquote>');
        break
      case "human":
        dialog_clean($(".question:last").prevAll().andSelf());
        console.log("removing .question:last");
        log.append('<blockquote class="question blockquote-reverse animated fadeInLeft"><p>'+text+'</p><footer><i>'+footer+'</i></footer></blockquote>');
        break
    }
    // setTimeout(function() { $("#dialog-log").children().css("visibility","visible"); }, 200);
    $("#dialog-log").animate({height: $("#dialog-log").get(0).scrollHeight}, 400 );
  }
  var socket =  new WebSocket("ws://localhost:8888/api");
  socket.onopen = function() { 
    dialog_show("Connected to the server", "status", "");
  };

  socket.onclose = function(event) { 
    if (event.wasClean) {
      dialog_show("Connection was closed", "status", "");
    } else {
      dialog_show("Connection was broken", "status", "");
    }
    // dialog_show("Code: "+event.code, "status");
  };
       
  socket.onmessage = function(event) {
    // console.log(event.data);
    if (event.data.indexOf("answer: ") == 0) {
      dialog_show(event.data.substring(8), "robot", "");
    } else if (event.data.indexOf("no answer") == 0) {
      dialog_show("Sorry, i don't know the answer.", "robot", 'already <span class="text-success">reported</span>');
    }
  };

  socket.onerror = function(error) { 
    dialog_show("Error: "+error.message, "status", "");
  };

  $('#phrase-input').keypress(function (e) {
    if (e.which == 13) {
      socket.send($('#phrase-input').val());
      dialog_show($('#phrase-input').val(), "human", "original: dfdfdf<br> wrong interpretation?");
      $('#phrase-input').val("");
      $('#phrase-input').tooltip('destroy');
    }
  });

});

