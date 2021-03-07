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

function copyToClipboard(id) {
  var tag = document.getElementById("" + id + "")
  var text = tag.innerHTML.trim()
  text = text.replace("&amp;", "&")
  var input = document.body.appendChild(document.createElement("textarea"));
  input.value = text;
  input.select();
  var status = document.execCommand("copy");
  input.parentNode.removeChild(input);
  if (status) {
    $.nok({
      message: "Success, Message Copied!",
      type: "success",
    });
  } else {
    $.nok({
      message: "Error, Message Not Copied!",
      type: "error",
    });
  }
}

function sendToGoogleSheet(act, status) {
  var inp_select = $('#select_inps')
  var inp_select_v = inp_select.val()
  $.nok({
    message: "Processing Your Request Please Wait!",
    type: "success",
  });
  $.ajax({
    type: "POST",
    crossDomain: true,
    dataType: "json",
    url: "/csv",
    data: { 'order_ids': inp_select_v, 'action': [act], 'status': status },
    success: function (res) {
      console.log(res);
      if (res.result == 'success') {
        $.nok({
          message: "Success, Sheet Created!",
          type: "success",
        });
        inp_select.val("")
      } else {
        $.nok({
          message: "Error, Sheet Not Created!",
          type: "error",
        });
        inp_select.val("")
      }
    },
    error: function (res) {
      $.nok({
        message: "API Error, Please Ask To Admin!",
        type: "error",
      });
    },
  });
}

function copyOrderDetail(status) {
  var inp_select = $('#select_inps')
  var inp_select_v = inp_select.val()
  $.nok({
    message: "Processing Your Request Please Wait!",
    type: "success",
  });
  $.ajax({
    type: "POST",
    crossDomain: true,
    dataType: "json",
    url: "/order_details",
    data: { 'order_ids': inp_select_v, 'status': status },
    success: function (res) {
      text = res.result.replace("&amp;", "&")
      var input = document.body.appendChild(document.createElement("textarea"));
      input.value = text;
      input.select();
      var status = document.execCommand("copy");
      input.parentNode.removeChild(input);
      if (status) {
        $.nok({
          message: "Success, Message Copied!",
          type: "success",
        });
      } else {
        $.nok({
          message: "Error, Message Not Copied!",
          type: "error",
        });
  }
    },
    error: function (err) {
      $.nok({
        message: "API Error, Please Ask To Admin!",
        type: "error",
      });
    },
  });
}

function copyCustomerDetail(status) {
  var inp_select = $('#select_inps')
  var inp_select_v = inp_select.val()
  $.nok({
    message: "Processing Your Request Please Wait!",
    type: "success",
  });
  $.ajax({
    type: "POST",
    crossDomain: true,
    dataType: "json",
    url: "/customer_details",
    data: { 'order_ids': inp_select_v, 'status': status },
    success: function (res) {
      text = res.result.replace("&amp;", "&")
      var input = document.body.appendChild(document.createElement("textarea"));
      input.value = text;
      input.select();
      var status = document.execCommand("copy");
      input.parentNode.removeChild(input);
      if (status) {
        $.nok({
          message: "Success, Message Copied!",
          type: "success",
        });
      } else {
        $.nok({
          message: "Error, Message Not Copied!",
          type: "error",
        });
  }
    },
    error: function (err) {
      $.nok({
        message: "API Error, Please Ask To Admin!",
        type: "error",
      });
    },
  });
}
