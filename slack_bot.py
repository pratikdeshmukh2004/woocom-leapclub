from custom import get_totals, get_shipping_total, list_order_items, list_orders_with_status
from  datetime import  datetime, timedelta
from customselectlist import list_created_via
from slack_chennels import CHANNELS

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
        taguser = "\n"+CHANNELS['TAG_USER_ID']
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
        + "\n`Please Egnore This Message....`"
    )
    th_s_msg = "*Order Items*\n" +list_order_items(o["line_items"], order_refunds)
    response = client.chat_postMessage(
        channel=CHANNELS['ORDER_NOTIFICATIONS'],
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
        channel=CHANNELS['ORDER_NOTIFICATIONS'],
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
        + "\n`Please Egnore This Message....`"

    )
    th_s_msg = "*Order Items*\n" +list_order_items(o["line_items"], order_refunds)
    response = client.chat_postMessage(
        channel=CHANNELS['ORDER_NOTIFICATIONS'],
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
        channel=CHANNELS['ORDER_NOTIFICATIONS'],
        thread_ts=response["ts"],
        text=th_s_msg,
        reply_broadcast=False
    )
    return response

def send_slack_for_product(client, product, topic):
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
        "*A product is Added/Updated!*\n"
    + "\n*Product Name:* "+product['name']
    + "\n*Product Categories:* "+categories
    + "\n*Shipping Class:* "+product['shipping_class']
    + "\n*Regular Price:* "+product['regular_price']
    + "\n*Product Tags:* "+tags
    + "\n*Stock Status:* "+product['stock_status']
    + "\n*Vendor:* "
    + "\n`Please Egnore This Message....`"
    )
    response = client.chat_postMessage(
        channel=CHANNELS['PRODUCT_NOTIFICATIONS'],
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

def send_slack_for_vendor_wise(client, wcapi):
    params = {"per_page": 100}
    params["status"] = 'tbd-unpaid, tbd-paid'
    params["delivery_date"] = str(datetime.utcnow().date())
    orders = list_orders_with_status(wcapi, params)
    params['delivery_date']=""
    params['created_via'] = 'subscription'
    subscriptions = list_orders_with_status(wcapi, params)
    subscriptions = list(filter(lambda o: (str(datetime.strptime(o["date_created"], '%Y-%m-%dT%H:%M:%S').date()) == str((datetime.now() - timedelta(1)).strftime('%Y-%m-%d'))), subscriptions))
    for o in orders:
        for item in o["meta_data"]:
            if item["key"] == "wos_vendor_data":
                o["vendor"] = item["value"]["vendor_name"]
            elif item["key"] == "_wc_acof_6":
                o["vendor"] = item["value"]
        if 'vendor' not in o.keys():
            o['vendor'] = ""
    vendor_list = []
    for o in orders:
        if o['vendor'].lower().replace(" ", "").replace(".", "") not in vendor_list:
            vendor_list.append(o['vendor'].lower().replace(" ", "").replace(".", ""))
    main_msg = ""
    for v in vendor_list:
        s_msg = "*Here are all the "+v+" orders to be delivered today:*\n"
        if v == "":
            s_msg = "*Here are the orders without any vendor assigned to them:*\n"
        for o in orders:
            if o['vendor'].lower().replace(" ", "").replace(".", "") == v:
                s_msg+=str(o['id'])+" - "+o['billing']['first_name']+" "+o['billing']['last_name']+" (Rs. "+o['total']+")\n"
        main_msg+=s_msg
        main_msg+="\n"
    s_msg = "*Here are the Subscriptions for today:*\n"
    for o in subscriptions:
        s_msg+=str(o['id'])+" - "+o['billing']['first_name']+" "+o['billing']['last_name']+" (Rs. "+o['total']+")\n"
    main_msg+=s_msg
    main_msg+="`Please update the status for delivery of all these orders`"
    + "\n`Please Egnore This Message....`"
    response = client.chat_postMessage(
        channel=CHANNELS['VENDOR_WISE'],
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": main_msg
                }
            }
        ]
    )
