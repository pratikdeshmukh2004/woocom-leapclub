from slack_chennels import CHANNELS


def format_mobile(mobile):
    if len(mobile)>10:
        mobile = mobile.replace(" ", "")        
    mobile = mobile[-10:]
    mobile = ("91"+mobile) if len(mobile) == 10 else mobile
    return mobile

def send_slack_message(client, channel, text):
    if len(text)==0:
        return ''
    response = client.chat_postMessage(
        channel=CHANNELS[channel],
        text=text,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                }
            }
        ]
    )
    return response

def send_slack_message_thread(client, channel, text, ttext):
    if len(text) == 0 or len(ttext) ==0:
        return ''
    response = client.chat_postMessage(
        channel=CHANNELS[channel],
        text=text,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                }
            }
        ]
    )
    t_response = client.chat_postMessage(
        channel=CHANNELS[channel],
        thread_ts=response["ts"],
        text=ttext,
        reply_broadcast=False
    )
    return response

def get_meta_data(order):
    vendor, manager, delivery_date, order_note  = "", "", "", ""
    for item in order["meta_data"]:
        if item["key"] == "wos_vendor_data":
            vendor = item["value"]["vendor_name"]
        elif item["key"] == "_wc_acof_6" and item['value'] != "":
            vendor = item["value"]
        elif item["key"] == "_wc_acof_3":
            manager = item["value"]
        elif item["key"] == "_wc_acof_7":
            order_note = item["value"]
        elif item["key"] == "_delivery_date":
            if delivery_date == "":
                delivery_date = item["value"]
        elif item["key"] == "_wc_acof_2_formatted":
            if delivery_date == "":
                delivery_date = item["value"]
    return [vendor, manager, delivery_date, order_note]
