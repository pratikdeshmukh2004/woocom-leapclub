import requests, json

def send_whatsapp_message_text(url,mobile, auth, text):
      url = url+"/api/v1/sendSessionMessage/" + \
            mobile + "?messageText="+text
      headers = {
            'Authorization': auth,
            'Content-Type': 'application/json',
      }
      response = requests.request(
            "POST", url, headers=headers)
      result = json.loads(response.text.encode('utf8'))
      if result["result"] in ["success", "PENDING", "SENT", True]:
            return True
      else:
            return False
