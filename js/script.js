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

  function dialog_show(text, style) {
    var log = $("#dialog-log");
    switch (style) {
      case "status":
        log.append('<p class="text-muted text-center animated fadeInUp"><i>'+text+'</i></p>');
        break
      case "robot":
        log.append('<blockquote class="animated fadeInRight"><p>'+text+'</p></blockquote>');
        break
      case "human":
        log.append('<blockquote class="blockquote-reverse animated fadeInLeft"><p>'+text+'</p></blockquote>');
        break
    }
  }
  var socket =  new WebSocket("ws://localhost:8888/api");
  socket.onopen = function() { 
    dialog_show("Connected to the server", "status");
  };

  socket.onclose = function(event) { 
    if (event.wasClean) {
      dialog_show("Connection was closed", "status");
    } else {
      dialog_show("Connection was broken", "status");
    }
    // dialog_show("Code: "+event.code, "status");
  };
       
  socket.onmessage = function(event) {
    // if (event.data === "not found") {
  };

  socket.onerror = function(error) { 
    dialog_show("Error: "+error.message, "status");
  };

});

