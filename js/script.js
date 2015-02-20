$(document).ready(function() {
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

  // function dialog_clean(elements) {
  //   faders = elements.clone();
  //   elements.css('visibility', 'hidden');
  //   elements.css('max-height', '0');
  //   setTimeout(function() { elements.remove() }, 500);
  //   // elements.animate({height: 0}, { "duration": 200, "easing": "linear", "complete": function () {
  //   //   elements.remove();
  //   // }});
  //   faders.removeClass('animated fadeInUp fadeInRight fadeInLeft');
  //   // setTimeout(function() {
  //   //   $(faders.get().reverse()).prependTo("#dialog-log-trash");
  //   // }, 1000);
  //   faders.prependTo("#dialog-log-trash");
  //   faders.addClass('animated fadeOutUp');
  //   faders.one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function(){
  //     // console.log($(this).text());
  //     $(this).remove();
  //   });
  // }

  function dialog_show(text, style, footer) {
    var log = $("#dialog-log");
    switch (style) {
      case "status":
        log.append('<p class="text-muted text-center animated fadeInUp"><i>'+text+'</i></p>');
        break
      case "robot":
        // dialog_clean($(".answer:last").prevAll().andSelf());
        // console.log("removing .answer:last");
        log.append('<blockquote class="answer animated fadeInRight"><p>'+text+'</p><footer><i>'+footer+'</i></footer></blockquote>');
        break
      case "human":
        // dialog_clean($(".question:last").prevAll().andSelf());
        // console.log("removing .question:last");
        log.append('<blockquote class="question blockquote-reverse animated fadeInLeft"><p>'+text+'</p><footer><i>'+footer+'</i></footer></blockquote>');
        break
    }
    // setTimeout(function() { $("#dialog-log").children().css("visibility","visible"); }, 200);
    // $("#dialog-log").animate({height: $("#dialog-log").get(0).scrollHeight}, 200 );
    var dialogDiv = $("#dialog-interface .panel");
    dialogDiv.animate({ scrollTop: dialogDiv.prop("scrollHeight") - dialogDiv.height() }, 500);
  }
  var socket =  new WebSocket("ws://178.62.192.111/api");
  socket.onopen = function() { 
    dialog_show("Connected to the server", "status", "");
    var data = {
      type: 'sources'
    }
    socket.send(JSON.stringify(data));
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
    console.log(event.data);
    var data = $.parseJSON(event.data);
    if (data.type == "interpretation") {
      dialog_show(data.origin, "human", 'alike: '+data.phrase+'<br> <span class="text-danger ipt-report">wrong interpretation?</span>');
      $('.ipt-report:last').data('report',event.data);
    } else if (data.type == "origin") {
      dialog_show(data.text, "human", '');
    } else if (data.type == "unknown") {
      dialog_show("Sorry, i don't know the answer.", "robot", 'already <span class="text-success">reported</span>');
    } else if (data.type == "phrase") {
      dialog_show(data.text, "robot", '');
    } else if (data.type == "sources") {
      data.modified = moment(data.modified, "x").fromNow();
      $("#update-status").html("updated "+data.modified);
      data.code.modified = moment(data.code.modified, "x").fromNow();
      data.description.modified = moment(data.description.modified, "x").fromNow();
      $("#code_python").html('<pre><code class="python">'+data.code.content+'</code></pre><p class="text-center text-muted"><i>'+data.code.filename+', last modified '+data.code.modified+'</i></p>');
      $("#code_ddl").html('<pre><code class="python">'+data.description.content+'</code></pre><p class="text-center text-muted"><i>'+data.description.filename+', last modified '+data.description.modified+'</i></p>');
      $('pre code').each(function(i, block) {
        hljs.highlightBlock(block);
      });
    }
  };

  socket.onerror = function(error) { 
    dialog_show("Error: "+error.message, "status", "");
  };

  $('#phrase-input').keypress(function (e) {
    if (e.which == 13) {
      var data = {
        type: 'phrase',
        text: $('#phrase-input').val()
      }
      socket.send(JSON.stringify(data));
      $('#phrase-input').val("");
      $('#phrase-input').tooltip('destroy');
    }
  });

  $('#dialog-log').on('click', '.ipt-report', function() {
    socket.send($(this).data("report"));
    $(this).removeClass("text-danger ipt-report").addClass("text-success").html("reported");
  });

});

