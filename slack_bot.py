from custom import get_totals, get_shipping_total, list_order_items


def send_slack_message(client, wcapi, o):
    vendor = ""
    delivery_date = ""
    payment_status = "Paid"
    if o["date_paid"] == None:
        payment_status = "Unpaid"
    for item in o["meta_data"]:
        if item["key"] == "wos_vendor_data":
            vendor = item["value"]["vendor_name"]
        elif item["key"] == "_wc_acof_6":
            vendor = item["value"]
        elif item["key"] == "_delivery_date":
            if delivery_date == "":
                delivery_date = item["value"]
        elif item["key"] == "_wc_acof_2_formatted":
            if delivery_date == "":
                delivery_date = item["value"]
    if len(o["refunds"]) > 0:
        order_refunds = wcapi.get("orders/"+str(o["id"])+"/refunds").json()
    else:
        order_refunds = []
    
    taguser = ""
    if o['created_via'] == "checkout" and vendor == "Mr. Dairy":
        taguser = "\n<@U01FQP200FR>"
    s_msg = (
        "*Order ID: "+str(o["id"])
        + "*\nName: "+o["billing"]["first_name"] + " " +
        o["billing"]["last_name"] + " | Mobile: "+o["billing"]["phone"]
        + "\nAddress: "+o["shipping"]["address_1"] + ", "+o["shipping"]["address_2"]+", "+o["shipping"]["city"] +
        ", "+o["shipping"]["state"]+", " +
        o["shipping"]["postcode"] + ", "+o["billing"]["address_2"]
        + "\nPayment Status: " +
        payment_status +
        " | Payment Method: "+o["payment_method_title"]
        + "\nDelivery Date: "+delivery_date+" | Vendor: "+vendor
        + "\nTotal Amount: " +
        get_totals(o["total"], order_refunds)
        + " | Delivery Charge: "+o["shipping_total"]
        + "\nStatus: "+ o['status']
        + " | Created_via: "+ o['created_via']
        + "\nCustomer Notes: "+ o["customer_note"]
        + taguser
    )
    th_s_msg = "*Order Items*\n" +list_order_items(o["line_items"], order_refunds)
    response = client.chat_postMessage(
        channel="flask-bot",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": s_msg
                }
            }
        ]
    )
    t_response = client.chat_postMessage(
        channel="flask-bot",
        thread_ts=response["ts"],
        text=th_s_msg,
        reply_broadcast=False
    )
    return response

def send_slack_message_calcelled(client, wcapi, o):
    vendor = ""
    delivery_date = ""
    payment_status = "Paid"
    if o["date_paid"] == None:
        payment_status = "Unpaid"
    for item in o["meta_data"]:
        if item["key"] == "wos_vendor_data":
            vendor = item["value"]["vendor_name"]
        elif item["key"] == "_wc_acof_6":
            vendor = item["value"]
        elif item["key"] == "_delivery_date":
            if delivery_date == "":
                delivery_date = item["value"]
        elif item["key"] == "_wc_acof_2_formatted":
            if delivery_date == "":
                delivery_date = item["value"]
    if len(o["refunds"]) > 0:
        order_refunds = wcapi.get("orders/"+str(o["id"])+"/refunds").json()
    else:
        order_refunds = []
    s_msg = (
        "*Order ID: "+str(o["id"])
        + " HAS BEEN CANCELLED*\nName: "+o["billing"]["first_name"] + " " +
        o["billing"]["last_name"] + " | Mobile: "+o["billing"]["phone"]
        + "\nAddress: "+o["shipping"]["address_1"] + ", "+o["shipping"]["address_2"]+", "+o["shipping"]["city"] +
        ", "+o["shipping"]["state"]+", " +
        o["shipping"]["postcode"] + ", "+o["billing"]["address_2"]
        + "\nPayment Status: " +
        payment_status +
        " | Payment Method: "+o["payment_method_title"]
        + "\nDelivery Date: "+delivery_date+" | Vendor: "+vendor
        + "\nTotal Amount: " +
        get_totals(o["total"], order_refunds)
        + " | Delivery Charge: "+o["shipping_total"]
    )
    th_s_msg = "*Order Items*\n" +list_order_items(o["line_items"], order_refunds)
    response = client.chat_postMessage(
        channel="orders-notifications",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": s_msg
                }
            }
        ]
    )
    t_response = client.chat_postMessage(
        channel="orders-notifications",
        thread_ts=response["ts"],
        text=th_s_msg,
        reply_broadcast=False
    )
    return response

def send_slack_for_product(client, product):
    categories = ""
    tags = ""
    for c in product['categories']:
        categories+=c['name']
        categories+=", "
    for t in product['tags']:
        tags+=c['name']
        tags+=", "
    categories = categories[:-2]
    tags = tags[:-2]
    s_msg = (
        "*Product Name:* "+product['name']
    + "\n*Product Categories:* "+categories
    + "\n*Shipping Class:* "+product['shipping_class']
    + "\n*Regular Price:* "+product['regular_price']
    + "\n*Product Tags:* "+tags
    + "\n*Stock Status:* "+product['stock_status']
    + "\n*Vendor:* "+""
    )
    response = client.chat_postMessage(
        channel="flask-bot",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": s_msg
                }
            }
        ]
    )
    return response