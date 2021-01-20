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
        var input = document.body.appendChild(document.createElement("input"));
        res = res.replace("&amp;", "&");
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
  $("#datepicker1").datepicker({
    dateFormat: "yy/mm/dd",
  });
  $("#datepicker2").datepicker({
    dateFormat: "yy/mm/dd",
  });
});
function copyText(text) {
  var input = document.body.appendChild(document.createElement("textarea"));
  input.value = text;
  input.select();
  var status = document.execCommand("copy");
  input.parentNode.removeChild(input);
  if (status) {
    $.nok({
      message: "Success, Url Copied!",
      type: "success",
    });
  } else {
    $.nok({
      message: "Error, Url Not Copied!",
      type: "error",
    });
  }
}
function CheckOutRequest(url) {
  $.nok({
    message: "Processing Your Request Please Wait!",
    type: "success",
  });
  $.ajax({
    type: "GET",
    crossDomain: true,
    dataType: "json",
    url: url,
    success: function (res) {
      console.log(res);
      if (res.result == "success") {
        $.nok({
          message: "Success, Link Generated!",
          type: "success",
        });
        var tag = $('#payment-' + res.order_id)
        console.log(typeof (res.payment.amount));
        tag.text(res.payment.receipt + " | " + (res.payment.amount / 100).toString())
        tag.attr('onclick', "copyText('" + res.short_url + "')")
        tag.attr('class', 'text-success')
      } else {
        $.nok({
          message: "Error, Link Not Generated!",
          type: "error",
        });
        var tag = $('#payment-' + res.order_id)
        tag.text(res.payment.receipt)
        tag.attr('class', 'text-danger')
      }
    },
    error: function (res) {
      $.nok({
        message: "API Error, Please Try Again!",
        type: "error",
      });
    },
  });
}
function updateSpan(order_id, template_name, color) {
  row = $(".wtmessage-" + order_id);
  span = $(
    '<span class="'+color+'">' + template_name + ", </span>"
  );
  row.append(span);
}

function SendWhatsappMessages(path) {
  $.nok({
    message: "Processing Your Request Please Wait!",
    type: "success",
  });
  $.ajax({
    type: "GET",
    crossDomain: true,
    dataType: "json",
    url: path,
    success: function (res) {
      console.log(res);
      if (["success", "PENDING", "SENT"].includes(res.result)) {
        $.nok({
          message: "Success, Message Sent!",
          type: "success",
        });
        updateSpan(res.order_id, res.template_name, 'text-success')
      } else {
        $.nok({
          message: "Error, Message Not Sent!",
          type: "error",
        });
        updateSpan(res.order_id, res.template_name, 'text-danger')
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
