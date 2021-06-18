from slack_chennels import CHANNELS
import concurrent.futures


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


def list_product_with_ids(wcapi, ids):
    params = {'include': ",".join(ids), 'per_page': 100}
    def get_product(params):
        product = wcapi.get("products", params=params)
        return product
    page = 1
    fproduct = wcapi.get("products", params=params)
    total_pages = int(fproduct.headers["X-WP-TotalPages"])
    p_list = []
    p = 2
    while p < total_pages+1:
        params["page"] = p
        p_list.append(params.copy())
        p += 1
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = executor.map(get_product, p_list)
    products = list(result)
    products.insert(0, fproduct)
    o_list = []
    for p in products:
        o_list.extend(p.json())
    return o_list


def list_product_list_form_orders(orders, wcapi):
    products = []
    p_d = {}
    for o in orders:
        for item in o['line_items']:
            item['product_id'] = str(item['product_id'])
            if item['product_id'] not in products:
                products.append(item['product_id'])
    products = list_product_with_ids(wcapi, products)
    for p in products:
        p_d[str(p['id'])] = p
    return p_d


def list_customers_with_wallet_balance(customers, wcapiw):
    def _get_customer_with_wallet_balance(c):
        balance = wcapiw.get("current_balance/"+str(c['id']))
        c["wallet_balance"] = float(balance.text[1:-1])
        return c
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = executor.map(_get_customer_with_wallet_balance, customers)
    return list(result)


def checkBefore(orders, conditions):
    results = {}
    for o in orders:
        vendor, manager, delivery_date, order_note,  = get_meta_data(o)
        id = str(o['id'])
        if 'paid' in conditions:
            error_t = "Order is Paid"
            if o['status'] in ['tbd-paid', 'completed'] or (o['status'] == 'processing' and o['payment_method'] in ['wallet', 'razorpay']):
                if id in results:
                    results[id].append(error_t) 
                else:
                    results[id] = [error_t]
        if 'wallet' in conditions:
            error_t = "Payment Method is already wallet"
            if o['payment_method_title'] == 'Wallet payment':
                if id in results:
                    results[id].append(error_t) 
                else:
                    results[id] = [error_t]
        if 'payment_null' in conditions:
            error_t = "Payment Method is empty"
            if o['payment_method'] == "":
                if id in results:
                    results[id].append(error_t) 
                else:
                    results[id] = [error_t]
        if 'vendor' in conditions:
            error_t = "Vendor is missing"
            if vendor == "" and o['created_via'] != 'subscription':
                if id in results:
                    results[id].append(error_t) 
                else:
                    results[id] = [error_t]
        if 'delivery_date' in conditions:
            error_t = "Delivery Date is missing"
            if delivery_date == "" and o['created_via'] != 'subscription':
                if id in results:
                    results[id].append(error_t) 
                else:
                    results[id] = [error_t]
        if 'name' in conditions:
                error_t = "Name is empty"
                if o['billing']['first_name'] == "":
                    if id in results:
                        results[id].append(error_t) 
                    else:
                        results[id] = [error_t]
        if 'mobile' in conditions:
                error_t = "Mobile number is empty"
                if o['billing']['phone'] == "":
                    if id in results:
                        results[id].append(error_t) 
                    else:
                        results[id] = [error_t]
        if 'billing_address' in conditions:
                    error_t = "Billing Address is empty"
                    if o['billing']['address_1'] == "" and o['billing']['address_2'] == "":
                        if id in results:
                            results[id].append(error_t) 
                        else:
                            results[id] = [error_t]
        if 'shipping_address' in conditions:
            error_t = "Shipping Address is empty"
            if o['shipping']['address_1'] == "" and o['shipping']['address_2'] == "":
                if id in results:
                    results[id].append(error_t) 
                else:
                    results[id] = [error_t]
        if 'pay_on' in conditions:
            error_t = "Payment method is not Pay Online On Delivery"
            if o['payment_method'] != 'cod':
                if id in results:
                    results[id].append(error_t) 
                else:
                    results[id] = [error_t]
        if 'other_status' in conditions:
            error_t = "Order status is not applicable"
            if o['status'] in ['pending', 'cancelled', 'tbd-paid', 'delivered-paid']:
                if id in results:
                    results[id].append(error_t) 
                else:
                    results[id] = [error_t]
    return results
