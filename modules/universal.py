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