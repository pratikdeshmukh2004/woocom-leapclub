$(document).ready(function () {
  $("#list_product_categories").on("submit", function (event) {
    event.preventDefault();
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
        var input = document.body.appendChild(document.createElement("input"));
        res = res.replace("&amp;", "&");
        input.value = res;
        input.select();
        var status = document.execCommand("copy");
        input.parentNode.removeChild(input);
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
  $('[data-toggle="tooltip"]').tooltip()
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

function updateSpan(order_id, template_name, color) {
  row = $(".wtmessage-" + order_id);
  span = $(
    '<span class="' + color + '">' + template_name + ", </span>"
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
      if (["success", "PENDING", "SENT", true].includes(res.result)) {
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
    timeout: 900000,
    data: { 'order_ids': inp_select_v, 'action': [act], 'status': status },
    success: function (res) {
      if (res.result == 'success') {
        delivery_dates_text = ""
        delivery_date_msg = ""
        for (var d of Object.keys(res.delivery_dates)) {
          dt = d
          if (d == '') {
            dt = "No Date"
          }
          delivery_dates_text += (dt + " : " + res.delivery_dates[d]['count'].toString() + " orders <br>")
        }
        if (Object.keys(res.delivery_dates).length > 1) {
          delivery_date_msg = "There are orders with different delivery date or no delivery date. Please change it now."
        }
        status_text = ""
        status_msg = ""
        for (var d of Object.keys(res.status_list)) {
          status_text += (d + " : " + res.status_list[d]['count'].toString() + " orders <br>")
        }
        if (Object.keys(res.status_list).length > 1) {
          status_msg = "There are orders with different status. Please change all orders to To Be Delivered. "
        }
        Swal.fire({
          html: `
<b>`+ res.total_o + ` orders added to Google Sheet <a target='blank' href='` + res.ssUrl + `'>` + res.ssName + `</a></b><br/><br/>
<div style='text-align: left'><b>Delivery Dates</b><br/>
`+ delivery_dates_text + `<br>
`+ delivery_date_msg + `</div><br/><br/>
<div style='text-align: left'><b>Status</b><br/>
`+ status_text + `<br>
`+ status_msg + `</div>
            `,
          width: 700,
          backdrop: `
              rgba(0,0,123,0.4)
            `
        })
      } else {
        $.nok({
          message: "Error, Sheet Not Created!",
          type: "error",
        });
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
      if (res.result == 'missing'){
        if (res.missings.delivery_date && res.missings.vendor){
          Swal.fire({
            icon:"warning",
            title: "Vendor and Delivery date is missing. Please add it before copying order details."
          })
        }else if(res.missings.delivery_date){
          Swal.fire({
            icon:"warning",
            title: "Delivery date is missing. Please add it before copying order derails"
          })
        }else{
          Swal.fire({
            icon:"warning",
            title: "Vendor is missing. Please add it before copying order details."
          })
        }
        return ""
      }
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
        if (text.length > 0) {
          Swal.fire({
            html: `
        <pre>
        <div style='text-align: left;'>
<b class='text-danger'>There are some problem in flask panel, please copy manualy</b>

`+ text + `
</pre>
</div>
        `,
            width: 700,
            backdrop: `
          rgba(0,0,123,0.4)
        `
          })
        } else {
          $.nok({
            message: "Error, Message Not Copied!",
            type: "error",
          });
        }
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

function copyOrderDetailMini(status) {
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
    url: "/order_details_mini",
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
        if (text.length > 0) {
          Swal.fire({
            html: `
        <pre>
        <div style='text-align: left;'>
<b class='text-danger'>There are some problem in flask panel, please copy manualy</b>

`+ text + `
</pre>
</div>
        `,
            width: 700,
            backdrop: `
          rgba(0,0,123,0.4)
        `
          })
        } else {
          $.nok({
            message: "Error, Message Not Copied!",
            type: "error",
          });
        }
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
        if (text.length > 0) {
          Swal.fire({
            html: `
        <pre>
        <div style='text-align: left;'>
<b class='text-danger'>There are some problem in flask panel, please copy manualy</b>

`+ text + `
</pre>
</div>
        `,
            width: 700,
            backdrop: `
          rgba(0,0,123,0.4)
        `
          })
        } else {
          $.nok({
            message: "Error, Message Not Copied!",
            type: "error",
          });
        }
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

function copySupplierMessage(status) {
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
    url: "/supplier_messages",
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
        if (text.length > 0) {
          Swal.fire({
            html: `
        <pre>
        <div style='text-align: left;'>
<b class='text-danger'>There are some problem in flask panel, please copy manualy</b>

`+ text + `
</pre>
</div>
        `,
            width: 700,
            backdrop: `
          rgba(0,0,123,0.4)
        `
          })
        } else {
          $.nok({
            message: "Error, Message Not Copied!",
            type: "error",
          });
        }
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



function changeOrderStatus(status) {
  var inp_select = $('#select_inps')
  var inp_select_v = inp_select.val()
  Swal.fire({
    title: `Do you want to change order status to `+status+` for `+inp_select_v.length.toString()+` orders? (Yes / No)`,
    showDenyButton: true,
    confirmButtonText: `Yes`,
    denyButtonText: `No`,
  }).then((result) => {
    if (result.isConfirmed) {
      $.nok({
        message: "Processing Your Request Please Wait!",
        type: "success",
      });
      $.ajax({
        type: "POST",
        crossDomain: true,
        dataType: "json",
        url: "/change_order_status",
        data: { 'order_ids': inp_select_v, "status": status },
        success: function (res) {
          if (res.result == 'success') {
            trtext = ""
            for (var o of res.result_list) {
              trtext += `
                  <tr>
                    <td><p>`+ o.order_id + " ( " + o.name + ` ) </p></td>
                    <td><p>`+ o.status + `</p></td>
                    <td><p>`+ o.message + `</p></td>
                    <td><p>`+ o.refund + `</p></td>
                  </tr>
              `
            }
            Swal.fire({
              html: `
                <table class='table'>
                  <thead>
                  <tr>
                    <th><b>Order ID ( Name )</b></th>  
                    <th><b>Result</b></th>  
                    <th><b>Message</b></th>  
                    <th><b>Refund</b></th>  
                  </tr>  
                  </thead>
                  <tbody>
                  `+ trtext + `
                  </tbody>
                </table>
              `,
              width: 700,
              backdrop: `
                rgba(0,0,123,0.4)
              `
            }).then(() => {
              location.reload()
            })
          }
          else if (res.result == 'paid'){
            trtext = ""
            for (var o of res.result_list) {
              trtext += `
                  <tr>
                    <td><p>`+ o.id + " ( " + o.billing.first_name + ` ) </p></td>
                    <td><p>`+ o.status + `</p></td>
                  </tr>
              `
            }
            Swal.fire({
              title: "You Selected Paid Orders Please Try Again",
              html: `
                <table class='table'>
                  <thead>
                  <tr>
                    <th><b>Order ID ( Name )</b></th>  
                    <th><b>Status</b></th>  
                  </tr>  
                  </thead>
                  <tbody>
                  `+ trtext + `
                  </tbody>
                </table>
              `,
              width: 700,
              backdrop: `
                rgba(0,0,123,0.4)
              `
            })
          }
          else {
            $.nok({
              message: "Error, Order Status Not Changed Please Check Order ID!",
              type: "error",
            });
          }
        }
      })
    }
  })
}

function copyToClipboard(id) {
  $.nok({
    message: "Please Wait For a While, Generating Message ....",
    type: "success",
  });
  $.ajax({
    type: "GET",
    crossDomain: true,
    dataType: "json",
    url: "/get_copy_messages/" + id.toString(),
    success: function (res) {
      if (res.status == 'missing'){
        if (res.missings.delivery_date && res.missings.vendor){
          Swal.fire({
            icon:"warning",
            title: "Vendor and Delivery date is missing. Please add it before copying order details."
          })
        }else if(res.missings.delivery_date){
          Swal.fire({
            icon:"warning",
            title: "Delivery date is missing. Please add it before copying order derails"
          })
        }else{
          Swal.fire({
            icon:"warning",
            title: "Vendor is missing. Please add it before copying order details."
          })
        }
        return ""
      }
      else if (res.status == 'success') {
        var input = document.body.appendChild(document.createElement("textarea"));
        input.value = res.text;
        input.select();
        var status = document.execCommand("copy");
        input.parentNode.removeChild(input);
        if (status) {
          $.nok({
            message: "Success, Message Copied!",
            type: "success",
          });
        } else {
          if (res.text.length > 0) {
            Swal.fire({
              html: `
          <pre>
          <div style='text-align: left;'>
<b class='text-danger'>There are some problem in flask panel, please copy manualy</b>

`+ res.text + `
</pre>
</div>
          `,
              width: 700,
              backdrop: `
            rgba(0,0,123,0.4)
          `
            })
          } else {
            $.nok({
              message: "Error, Message Not Copied!",
              type: "error",
            });
          }
        }
      } else {
        $.nok({
          message: "Error, Message Not Copied!",
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
      if (res.result == 'check') {
        o_str = ""
        for (var o of res.orders) {
          o_str += '<tr>'
          o_str += '<td>' + o['id'] + '</td>'
          o_str += '<td>' + o['status'] + '</td>'
          o_str += '<td>' + o['total'] + '</td>'
          o_str += '</tr>'
        }
        Swal.fire({
          html: `
        <b>Follow orders of `+ res.orders[0]['billing']['first_name'] + " " + res.orders[0]['billing']['last_name'] + ` are unpaid. Do you want to generate payment for a single order?</b>
          <table class='table'>
            <thead>
            <tr>
              <th><b>Order ID</b></th>  
              <th><b>Status</b></th>  
              <th><b>Amount</b></th>  
            </tr>  
            </thead>
            <tbody>
            `+ o_str + `
            </tbody>
          </table>
        `,
          width: 700,
          backdrop: `
          rgba(0,0,123,0.4)
        `,
          confirmButtonText: 'Yes',
          cancelButtonText: 'No',
          showCancelButton: true,
        }).then((result) => {
          if (result.isConfirmed) {
            $.ajax({
              type: "GET",
              crossDomain: true,
              dataType: "json",
              url: url + "?check=true",
              success: function (res) {
                if (res.result == "success") {
                  $.nok({
                    message: res.text,
                    type: "success",
                  });
                  var tag = $('#payment-' + res.order_id)
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
              }
            })
          }
        })
      }
      else if (res.result == "success") {
        $.nok({
          message: res.text,
          type: "success",
        });
        var tag = $('#payment-' + res.order_id)
        tag.text(res.payment.receipt + " | " + (res.payment.amount / 100).toString())
        tag.attr('onclick', "copyText('" + res.short_url + "')")
        tag.attr('class', 'text-success')
      } else if (res.result == 'paid') {
        Swal.fire({
          title: 'The order is already paid. Payment link cannot be generated.',
          icon: 'warning',
        })
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


function genSubscriptionLink(id) {
  Swal.fire({
    title: 'Enter amount',
    input: 'text',
    inputAttributes: {
      autocapitalize: 'off'
    },
    showCancelButton: true,
    confirmButtonText: 'Generate',
    showLoaderOnConfirm: true,
    preConfirm: (amount) => {
      return ($.ajax({
        type: "GET",
        crossDomain: true,
        dataType: "json",
        url: "/genSubscriptionLink/" + id + "/" + amount,
        success: function (res) {
          if (res.result == "success") {
            console.log(res);
            return res
          } else {
            Swal.showValidationMessage(
              `Please enter valid amount.`
            )
          }
        }
      }))
    },
    allowOutsideClick: () => !Swal.isLoading()
  }).then((res) => {
    if (res.isConfirmed) {
      res = res.value
      if (res.result == "success") {
        Swal.fire({
          title: "Success, Link Generated!",
          icon: "success",
        });
        var tag = $('#payment-' + res.data.id)
        tag.text(res.data.receipt + " | " + (res.data.amount / 100).toString())
        tag.attr('onclick', "copyText('" + res.data.short_url + "')")
        tag.attr('class', 'text-success')
      } else {
        Swal.fire({
          title: "Error, Link Not Generated!",
          icon: "error",
        });
        var tag = $('#payment-' + res.data.id)
        tag.text(res.data.receipt)
        tag.attr('class', 'text-danger')
      }
    }
  })
}

function genSubscriptionLink2(id, amount) {
  Swal.fire({
    title: 'Processing Your Request....',
    showConfirmButton: false,
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading()
    },
  })

  $.ajax({
    type: "GET",
    crossDomain: true,
    dataType: "json",
    url: "/genSubscriptionLink/" + id + "/" + parseInt(amount).toString(),
    success: function (res) {
      if (res.result == "success") {
        Swal.fire({
          title: "Success, Link Generated!",
          icon: "success",
        });
        var tag = $('#payment-' + res.data.id)
        tag.text(res.data.receipt + " | " + (res.data.amount / 100).toString())
        tag.attr('onclick', "copyText('" + res.data.short_url + "')")
        tag.attr('class', 'text-success')
      } else {
        Swal.fire({
          title: "Error, Link Not Generated!",
          icon: "error",
        });
        var tag = $('#payment-' + res.data.id)
        tag.text(res.data.receipt)
        tag.attr('class', 'text-danger')
      }
    }
  })
}

function genMulSubscriptionLinks() {
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
    url: "/genMulSubscriptionLink",
    data: { 'order_ids': inp_select_v },
    success: function (res) {
      new_tr = ""
      for (var c of res.results) {
        if (c.result == 'success') {
          for (var id of c.order_ids) {
            var tag = $('#payment-' + id.toString())
            tag.text(c.receipt + " | " + (c.amount / 100).toString())
            tag.attr('onclick', "copyText('" + c.short_url + "')")
            tag.attr('class', 'text-success')
          }
          new_tr += `
          <tr>
            <td><p>`+ c.mobile.toString() + `</p></td>
            <td><p>`+ (c.amount / 100).toString() + `</p></td>
            <td><p>`+ c.receipt + `</p></td>
            <td><button class='btn btn-success btn-sm' title='Click To Copy Payment Link' onclick="copyText('`+ c.short_url + `')">Copy Link</button></td>
          </tr>`
        } else {
          new_tr += `
          <tr class='table-danger'>
            <td><p>`+ c.mobile.toString() + `</p></td>
            <td><p>`+ (c.amount / 100).toString() + `</p></td>
            <td><p>`+ c.receipt + `</p></td>
          </tr>`
        }
      }
      Swal.fire({
        html: `
          <table class='table'>
            <thead>
            <tr>
              <th><b>Mobile</b></th>  
              <th><b>Amount</b></th>  
              <th><b>Receipt</b></th>  
            </tr>  
            </thead>
            <tbody>
            `+ new_tr + `
            </tbody>
          </table>
        `,
        width: 700,
        backdrop: `
          rgba(0,0,123,0.4)
        `,
        confirmButtonColor: '#FF3232',
        confirmButtonText: 'Close'
      })
    }
  })
}


function copyLinkedOrders() {
  var inp_select = $('#select_inps')
  var inp_select_v = inp_select.val()
  $.nok({
    message: "Please Wait For a While, Generating Message ....",
    type: "success",
  });
  $.ajax({
    type: "POST",
    crossDomain: true,
    dataType: "json",
    url: "/copy_linked_orders",
    data: { 'order_ids': inp_select_v },
    success: function (res) {
      if (res.status == 'success') {
        var input = document.body.appendChild(document.createElement("textarea"));
        input.value = res.text;
        input.select();
        var status = document.execCommand("copy");
        input.parentNode.removeChild(input);
        if (status) {
          $.nok({
            message: "Success, Message Copied!",
            type: "success",
          });
        } else {
          if (res.text.length > 0) {
            Swal.fire({
              html: `
          <pre>
          <div style='text-align: left;'>
<b class='text-danger'>There are some problem in flask panel, please copy manualy</b>

`+ res.text + `
</pre>
</div>
          `,
              width: 700,
              backdrop: `
            rgba(0,0,123,0.4)
          `
            })
          } else {
            $.nok({
              message: "Error, Message Not Copied!",
              type: "error",
            });
          }
        }
      } else {
        $.nok({
          message: "Error, Message Not Copied!",
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



function sendWMessages(name) {
  var inp_select = $('#select_inps')
  var inp_select_v = inp_select.val()
  Swal.fire({
    title: `Do you want to send `+name+` message for `+inp_select_v.length.toString()+` orders? (Yes / No)`,
    showDenyButton: true,
    confirmButtonText: `Yes`,
    denyButtonText: `No`,
  }).then((result) => {
    if (result.isConfirmed) {
      Swal.fire({
        title: 'Processing Your Request....',
        showConfirmButton: false,
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading()
        },
      })
      $.ajax({
        type: "POST",
        crossDomain: true,
        dataType: "json",
        url: "/send_whatsapp_messages/" + name,
        data: { 'order_ids': inp_select_v },
        success: function (res) {
          if (res.result == 'success') {
            trtext = ""
            for (var o of res.results) {
              console.log(o);
              if (["success", "PENDING", "SENT", true].includes(o.result)) {
                updateSpan(o.order_id, o.template_name, 'text-success')
              } else {
                updateSpan(o.order_id, o.template_name, 'text-danger')
              }
              button = `<td onclick="sendWPaymentLink('` + o.order_id + "','" + o.phone_number + "','" + o.vendor_type + `')"><button class='btn btn-sm btn-success'>Send Payment Link</button></td>`
              if (!o.button) {
                button = ""
              }
              trtext += `
                  <tr>
                    <td><p>`+ o.customer_name + " ( " + o.phone_number + ` ) </p></td>
                    <td><p>`+ o.order_id + `</p></td>
                    <td><p>`+ o.result + `</p></td>
                    <td><p>`+ o.payment_status + `</p></td>
                    `+ button + `
                  </tr>
              `
            }
            Swal.fire({
              html: `
              <b>Group orders by customer:</b>
                <table class='table'>
                  <thead>
                  <tr>
                    <th><b>Name (Mobile)</b></th>  
                    <th><b>Order IDS</b></th>  
                    <th><b>Result</b></th>  
                    <th><b>Paid/Unpaid</b></th>  
                  </tr>  
                  </thead>
                  <tbody>
                  `+ trtext + `
                  </tbody>
                </table>
              `,
              width: 1000,
              backdrop: `
                rgba(0,0,123,0.4)
              `,
              allowOutsideClick: false
            })
          }
          else {
            $.nok({
              message: "Error, Messages not sent!",
              type: "error",
            });
          }
        }
      })
    }
  })
}
function sendWPaymentLink(id, phone_number, order_type) {
  console.log(id, phone_number, order_type);
  $.nok({
    message: "Processing Your Request Please Wait!",
    type: "success",
  });
  $.ajax({
    type: "POST",
    crossDomain: true,
    dataType: "json",
    url: "/send_payment_link_wt/" + id,
    data: { 'mobile_number': phone_number, 'order_type': order_type },
    success: function (res) {
      if (["success", "PENDING", "SENT", true].includes(res.result)) {
        $.nok({
          message: "Success, Payment Link Sent!",
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

function CheckOutRequest(url) {
  Swal.fire({
      title: 'Processing Your Request....',
      showConfirmButton: false,
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading()
      },
    })
  $.ajax({
    type: "GET",
    crossDomain: true,
    dataType: "json",
    url: url,
    success: function (res) {
      if (res.result == 'check') {
        o_str = ""
        for (var o of res.orders) {
          o_str += '<tr>'
          o_str += '<td>' + o['id'] + '</td>'
          o_str += '<td>' + o['status'] + '</td>'
          o_str += '<td>' + o['total'] + '</td>'
          o_str += '</tr>'
        }
        Swal.fire({
          html: `
        <b>Follow orders of `+ res.orders[0]['billing']['first_name'] + " " + res.orders[0]['billing']['last_name'] + ` are unpaid. Do you want to generate payment for a single order?</b>
          <table class='table'>
            <thead>
            <tr>
              <th><b>Order ID</b></th>  
              <th><b>Status</b></th>  
              <th><b>Amount</b></th>  
            </tr>  
            </thead>
            <tbody>
            `+ o_str + `
            </tbody>
          </table>
        `,
          width: 700,
          backdrop: `
          rgba(0,0,123,0.4)
        `,
          confirmButtonText: 'Yes',
          showCancelButton: true,
          cancelButtonText: 'No'
        }).then((result) => {
          if (result.isConfirmed) {
            if (url.includes('?')){
              CheckOutRequest(url + "&check=true")
            }else{
              CheckOutRequest(url + "?check=true")
            }
          }
        })
      }
      else if (res.result == "success") {
        Swal.fire({
          title: res.text,
          icon: 'success'
        })
        var tag = $('#payment-' + res.order_id)
        tag.text(res.payment.receipt + " | " + (res.payment.amount / 100).toString())
        tag.attr('onclick', "copyText('" + res.short_url + "')")
        tag.attr('class', 'text-success')
      } 
      else if (res.result == 'paid') {
        Swal.fire({
          title: 'The order is already paid. Payment link cannot be generated.',
          icon: 'warning'
        })
      }
      else if (res.result == 'balance') {
        Swal.fire({
          html: '<h4>Wallet balance is '+res.balance+'. Total payable amount is '+res.total+'. Do you want to pay by wallet instead of generating payment link?</h4>',
          icon: 'warning',
          confirmButtonText: 'Generate Payment Link',
          cancelButtonText: 'Pay By Wallet',
          showCancelButton: true,
          cancelButtonColor: '#4BB543',
          confirmButtonColor: '#4BB543',
          width: 700
        }).then((result) => {
          if (!result.isConfirmed) {
            if (url.includes('?')){
              CheckOutRequest(url + "&balance=add")
            }else{
              CheckOutRequest(url + "?balance=add")
            }
          }else{
            if (url.includes('?')){
              CheckOutRequest(url + "&balance=no")
            }else{
              CheckOutRequest(url + "?balance=no")
            }
          }
        })
      } 
      else if (res.result == 'wallet') {
        Swal.fire({
          html: '<h4>Wallet balance is '+res.balance+'. Total payable amount is '+res.total+'. Do you want to deduct '+res.balance+' from wallet and generate payment link of '+(parseFloat(res.total)-parseFloat(res.balance)).toString()+'?</h4>',
          icon: 'warning',
          confirmButtonText: 'Generate Payment Link Of '+(parseFloat(res.total)-parseFloat(res.balance)).toString(),
          cancelButtonText: 'Generate Payment Link Of '+res.total,
          showCancelButton: true,
          cancelButtonColor: '#4BB543',
          confirmButtonColor: '#4BB543',
          width: 700
        }).then((result) => {
          if (result.isConfirmed) {
            if (url.includes('?')){
              CheckOutRequest(url + "&wallet_remove=add")
            }else{
              CheckOutRequest(url + "?wallet_remove=add")
            }
          }else{
            if (url.includes('?')){
              CheckOutRequest(url + "&wallet_remove=no")
            }else{
              CheckOutRequest(url + "?wallet_remove=no")
            }
          }
        })
      } 
      else if (res.result == 'wallet_add') {
        Swal.fire({
          html: '<h4>Wallet balance is - '+res.balance+'. Total payable amount is '+res.total+'. Do you want to generate payment link of '+(parseFloat(res.total)-parseFloat(res.balance)).toString()+'?</h4>',
          icon: 'warning',
          confirmButtonText: 'Generate Payment Link Of '+(parseFloat(res.total)-parseFloat(res.balance)).toString(),
          cancelButtonText: 'Generate Payment Link Of '+res.total,
          showCancelButton: true,
          cancelButtonColor: '#4BB543',
          confirmButtonColor: '#4BB543',
          width: 700
        }).then((result) => {
          if (result.isConfirmed) {
            if (url.includes('?')){
              CheckOutRequest(url + "&wallet_add=add")
            }else{
              CheckOutRequest(url + "?wallet_add=add")
            }
          }else{
            if (url.includes('?')){
              CheckOutRequest(url + "&wallet_add=no")
            }else{
              CheckOutRequest(url + "?wallet_add=no")
            }
          }
        })
      } 
      else if (res.result == 'success_s') {
        Swal.fire({
          title: 'Success!',
          icon: 'success'
        })
      }
      else if (res.result == 'error_s') {
        Swal.fire({
          title: res.error,
          icon: 'error'
        })
      }
      else {
        Swal.fire({
          title: 'Something went wrong..',
          icon: 'error'
        })
        var tag = $('#payment-' + res.order_id)
        tag.text(res.payment.receipt)
        tag.attr('class', 'text-danger')
      }
    },
    error: function (res) {
      Swal.fire({
      title: 'Something went wrong..',
      icon: 'error'
    })
    },
  });
}


function payByWallet(inp_s_v){
  console.log(inp_s_v)
var inp_select = $('#select_inps')
var ischecked = ''
if (inp_s_v == undefined){
  var inp_select_v = inp_select.val()
}else{
  var inp_select_v = inp_s_v
  ischecked = "?check=true"
}
Swal.fire({
    title: 'Processing Your Request....',
    showConfirmButton: false,
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading()
    },
})
$.ajax({
  type: "POST",
  crossDomain: true,
  dataType: "json",
  url: "/payByWallet"+ischecked,
  data: { 'ids': inp_select_v },
  success: function (res) {
    if (res.result == 'paid'){
      trs = ""
      for (var o of res.orders) {
        trs += '<tr>'
        trs += '<td>' + o['id'] + '</td>'
        trs += '<td>' + o['billing']['first_name'] + '</td>'
        trs += '<td>' + o['total'] + '</td>'
        trs += '<td>' + o['status'] + '</td>'
        trs += '</tr>'
      }
      Swal.fire({
        icon: "warning",
        html: `
        <h4>Following orders are already paid. Please remove them from selection:</h4>
        <table class='table'>
          <thead>
          <tr>
            <th>Order ID</th>
            <th>Name</th>
            <th>Amount</th>
            <th>Status</th>
          <tr>
          </thead>
          <tbody>
            `+trs+`
          </tbody>
        <table>
        `,
        width: 900
      })
    }
    else if (res.result == 'balance'){
      trs = ""
      for (var c of res.customers) {
        trs += '<tr>'
        trs += '<td>' + c['name']+" (" +c['mobile']+ ')</td>'
        trs += '<td>' + c['order_ids'] + '</td>'
        trs += '<td>' + c['total'] + '</td>'
        trs += '<td>' + c['wallet_balance'] + '</td>'
        trs += '</tr>'
      }
      Swal.fire({
        icon: "warning",
        html: `
        <h4>Following customers have insufficient balance. Please remove them from selection:</h4>
        <table class='table'>
          <thead>
          <tr>
            <th>Name (Mobile)</th>
            <th>Order IDS</th>
            <th>Amount</th>
            <th>Wallet Balance</th>
          <tr>
          </thead>
          <tbody>
            `+trs+`
          </tbody>
        <table>
        `,
        width: 900
      })
    }
    else if (res.result == 'success'){
      trs = ""
      for (var c of res.customers) {
        trs += '<tr>'
        trs += '<td>' + c['name']+" (" +c['mobile']+ ')</td>'
        trs += '<td>' + c['order_ids'] + '</td>'
        trs += '<td>' + c['total'] + '</td>'
        trs += '<td>' + c['wallet_balance'] + '</td>'
        trs += '<td>' + c['status'] + '</td>'
        if (c['status'] =='success'){
          trs += '<td><button class="btn btn-sm btn-success">button</button></td>'
        }
        trs += '</tr>'
      }
      Swal.fire({
        icon: "success",
        html: `
        <table class='table'>
          <thead>
          <tr>
            <th>Name (Mobile)</th>
            <th>Order ID</th>
            <th>Amount Paid</th>
            <th>Current Balance</th>
            <th>Result</th>
          <tr>
          </thead>
          <tbody>
            `+trs+`
          </tbody>
        <table>
        `,
        width: 1100
      }).then(()=>{
        location.reload()
      })
    }
    else if (res.result == 'check'){
      trs = ""
      for (var c of res.customers) {
        trs += '<tr>'
        trs += '<td>' + c['name']+" (" +c['mobile']+ ')</td>'
        trs += '<td>' + c['order_ids'] + '</td>'
        trs += '<td>' + c['total'] + '</td>'
        trs += '<td>' + c['wallet_balance'] + '</td>'
        trs += '</tr>'
      }
      Swal.fire({
        icon: "warning",
        html: `
        <h4>Do you want to pay for these orders by wallet? (Yes / No)</h4>
        <table class='table'>
          <thead>
          <tr>
            <th>Name (Mobile)</th>
            <th>Order ID</th>
            <th>Total Amount</th>
            <th>Current Balance</th>
          <tr>
          </thead>
          <tbody>
            `+trs+`
          </tbody>
        <table>
        `,
        width: 1100,
        confirmButtonText: 'Yes &rarr;',
        cancelButtonText: 'No',
        showCancelButton: true,
      }).then((result) => {
        if (result.isConfirmed) {
          payByWallet(inp_select_v)
        }
      })
    }else{
      Swal.fire({
        icon: "error",
        title: "Got Error Please Recheck Orders!"
      })
    }
  },
  error: function () {
    Swal.fire({
      icon: "error",
      title: "Got Error Please Recheck Orders!"
    })
  }
})

}



function gen_multipayment(id, c_id, amount, name, phone, balance, type){
  $.ajax({
  type: "POST",
  crossDomain: true,
  dataType: "json",
  url: "/gen_multipayment",
  data: { 'order_ids': id, 'amount': amount, 'name': name, 'phone': phone,'balance': balance, 'type': type , 'customer_id': c_id},
  success: function (res){
    if (res.result == 'success' || res.result == 'already'){
      $('#status-'+c_id).append('<b class="text-success ml-2 mr-1">'+res.result+'</b>')
      $('#status-'+c_id).append(`<b>Link: '`+res.short_url+`'</b>`)

    }else{
      $('#status-'+c_id).append('<b class="text-danger ml-2">Error</b>')

    }

  },
  error: function (){
    $('#status-'+c_id).append('<b class="text-danger ml-2">Error</b>')
  }
})
}

function genMultipleLinks() {
var inp_select = $('#select_inps')
var inp_select_v = inp_select.val()
Swal.fire({
  showConfirmButton: false,
  allowOutsideClick: false,
  didOpen: () => {
    Swal.showLoading()
  },
})  
$.ajax({
  type: "POST",
  crossDomain: true,
  dataType: "json",
  url: "/multiple_links",
  data: { 'order_ids': inp_select_v },
  success: function (res) {
    if (res.status == 'paid'){
      trs = ""
      for (var o of res.orders) {
        trs += '<tr>'
        trs += '<td>' + o['id'] + '</td>'
        trs += '<td>' + o['billing']['first_name'] + '</td>'
        trs += '<td>' + o['total'] + '</td>'
        trs += '<td>' + o['status'] + '</td>'
        trs += '</tr>'
      }
      Swal.fire({
        icon: "warning",
        html: `
        <h4>Following orders are already paid. Please remove them from selection:</h4>
        <table class='table'>
          <thead>
          <tr>
            <th>Order ID</th>
            <th>Name</th>
            <th>Amount</th>
            <th>Status</th>
          <tr>
          </thead>
          <tbody>
            `+trs+`
          </tbody>
        <table>
        `,
        width: 900
      })
    }
    else if (res.status == 'vendor'){
      trs = ""
      for (var o of res.orders) {
        trs += '<tr>'
        trs += '<td>' + o['id'] + '</td>'
        trs += '<td>' + o['billing']['first_name'] + '</td>'
        trs += '<td>' + o['total'] + '</td>'
        trs += '<td>' + o['status'] + '</td>'
        trs += '</tr>'
      }
      Swal.fire({
        icon: "warning",
        html: `
        <h4>Following orders are without vendor. Please assign them vendor:</h4>
        <table class='table'>
          <thead>
          <tr>
            <th>Order ID</th>
            <th>Name</th>
            <th>Amount</th>
            <th>Status</th>
          <tr>
          </thead>
          <tbody>
            `+trs+`
          </tbody>
        <table>
        `,
        width: 900
      })
    }
    else if (res.status == 'popup'){
      trs = ""
      for (var o of res.customers) {
        btns = ''
        var o_ids = "["+o.order_id+"]"
        if (o.pbw){
          btns = '<button onclick="payByWallet('+o_ids+')" class="btn btn-success btn-sm mr-1 mt-2">Pay by wallet</button>'
        }else if (o.genl || o.genm){
          var type = 'add'
          if (o.genm){
            type = 'remove'
          }
          btns = `<button onclick="gen_multipayment('`+o.order_id+`','`+o.customer_id+`', '`+(parseFloat(o.total)-parseFloat(o.wallet_balance))+`','`+o.name+`','`+o.phone+`','`+o.wallet_balance+`','`+type+`')" class="btn mt-2 btn-success btn-sm mr-1">Generate Payment Link of `+(parseFloat(o.total)-parseFloat(o.wallet_balance)).toString()+`</button>`
        }
        trs += '<tr>'
        trs += '<td>' + o['name']+' ('+o['phone'] + ')</td>'
        trs += '<td>' + o['order_id'] + '</td>'
        trs += '<td>' + o['total'] + '</td>'
        trs += '<td>' + o['wallet_balance'] + '</td>'
        trs += `<td><button onclick="gen_multipayment('`+o.order_id+`','`+o.customer_id+`', '`+o.total+`','`+o.name+`','`+o.phone+`')" class="btn mt-2 btn-success btn-sm mr-1">Generate Payment Link of `+o.total+`</button>`+btns+`</td>`
        trs += '<td style="display: flex;" id="status-'+o.customer_id+'"></td>'
        trs += '</tr>'
      }
    $('#exampleModal').modal({
      show: true
    })
    $(".modal-body").html(`
    <table class='table'>
          <thead>
          <tr>
            <th>Customer</th>
            <th>Order ID</th>
            <th>Amount</th>
            <th>Wallet Balance</th>
            <th></th>
            <th>Status</th>
          <tr>
          </thead>
          <tbody>
            `+trs+`
          </tbody>
        <table>
    `)
    Swal.fire({
      showConfirmButton: false,
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading()
      },
      timer: 500
    })
    }
  },
  error: function (err){
    Swal.fire({
      title: "Error in Flask Panel. Or Please Select Correct Orders.",
      icon: "error"
    })
  }
})
}

