from custom import get_totals, get_shipping_total, list_order_items
def send_slack_message(client, wcapi, o):
    if len(o["refunds"]) > 0:
            order_refunds = wcapi.get("orders/"+str(o["id"])+"/refunds").json()
    else:
        order_refunds = []
    s_msg = ("Order ID: "+str(o["id"])
             + "\n\nName: "+o["billing"]["first_name"] +
             " "+o["billing"]["last_name"]
             + "\nMobile: "+o["billing"]["phone"]
             + "\nAddress: "+o["shipping"]["address_1"] + ", "+o["shipping"]["address_2"]+", "+o["shipping"]["city"]+", "+o["shipping"]["state"]+", "+o["shipping"]["postcode"] +
             ", "+o["billing"]["address_2"]
             + "\n\n*Total Amount: " +
             get_totals(o["total"], order_refunds)
             + get_shipping_total(o)
             + "*\n\n"+list_order_items(o["line_items"], order_refunds)
                     + "Payment Status: "+o["payment_method_title"])
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
    return s_msg
