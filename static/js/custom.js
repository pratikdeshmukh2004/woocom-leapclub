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
