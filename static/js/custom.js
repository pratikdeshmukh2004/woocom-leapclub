$(document).ready(function () {
  $("#list_product_categories").on("submit", function (event) {
    event.preventDefault();
    console.log(event.target.shipping_class.value);
    $.NotificationApp.send(
      "Sending",
      "Please Wait For A While",
      "top-right",
      "success",
      "warning",
      10000
    );
    $.ajax({
      type: "GET",
      crossDomain: true,
      dataType: "text",
      url:
        "/list_product_categories?shipping_class=" +
        event.target.shipping_class.value,
      success: function (res) {
        console.log(res);
        var input = document.body.appendChild(
          document.createElement("input")
        );
        res = res.replace("&amp;", "&")
        input.value = res;
        input.select();
        var status = document.execCommand("copy");
        input.parentNode.removeChild(input);
        console.log(input.value);
        if (status) {
          $.NotificationApp.send(
            "Success",
            "Message Copied!",
            "top-right",
            "success",
            "success",
            10000
          );
        } else {
          console.log(status);
          $.NotificationApp.send(
            "Error",
            "Message Not Copied!",
            "top-right",
            "error",
            "error",
            10000
          );
        }
      },
      error: function (res) {
        console.log(res);
      },
    });
  });

  $("#datepicker").datepicker({
    dateFormat: "yy/mm/dd",
  });
});
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
        row = $(".wtmessage-" + res.parameteres[2].value);
        span = $(
          '<span class="text-success">' + res.template_name + ", </span>"
        );
        row.append(span);
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
