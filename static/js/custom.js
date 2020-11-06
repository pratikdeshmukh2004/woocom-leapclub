function makeGetRequest(path) {
  $.ajax({
    type: "GET",
    crossDomain: true,
    dataType: "json",
    url: path,
    success: function (res) {
      if (res.result == "success") {
        $.nok({
          message: "Success, Message Sent!",
          type: "success",
        });
        row = $(".wtmessage-"+res.parameteres[2].value)
        span = $('<span class="text-success">'+res.template_name+', </span>')
        row.append(span)
      } else {
        $.nok({
          message: "Error, Message Not Sent!",
          type: "error",
        });
      }
    },
    error: function (res) {
      $.nok({
        message: "API Error, Message Not Sent!",
        type: "error",
      });
    },
  });
}
