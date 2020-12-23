import os
import csv
import time
import datetime
import concurrent.futures
from customselectlist import list_created_via


def format_delivery_date(d):
    d_s = d.split("/")
    f_s = d_s[0]+" "
    f_s = f_s+d_s[1]
    f_s = f_s+", "
    f_s = f_s+d_s[2]
    return f_s


def filter_orders(orders, params):
    if len(params) <= 4:
        return orders
    f_orders = []
    for o in orders:
        c = {"payment_status": False, "manager": False}

        if "payment_status" in params:
            if params["payment_status"][0] != "":
                if params["payment_status"][0] == "unpaid":
                    if o["date_paid"] == None:
                        c["payment_status"] = True
                else:
                    if o["date_paid"] != None:
                        c["payment_status"] = True
            else:
                c["payment_status"] = True
        manager = ""
        for item in o["meta_data"]:
            if item["key"] == "_wc_acof_3":
                manager = item["value"]
        if "manager" in params:
            if params["manager"][0] != "":
                if manager in params["manager"]:
                    c["manager"] = True
            else:
                c["manager"] = True
        else:
            c["manager"] = True
        if c["payment_status"] and c["manager"]:
            f_orders.append(o)
    return f_orders


def list_order_items_without_refunds(order_items):
    msg = ""
    for order_item in order_items:
        msg = (
            msg
            + order_item["name"]
            + " x "
            + str(order_item["quantity"])
            + "\n"
            + "₹"
            + str(order_item["price"])
            + " x "
            + str(order_item["quantity"])
            + " = "
            + str(order_item["subtotal"])
            + "\n\n"
        )
    return msg


def list_order_refunds(order_refunds):
    msg = ""
    line_items = []
    m_list = []
    for r in order_refunds:
        for ri in r["line_items"]:
            if ri["meta_data"][0]["value"] in m_list:
                for l in line_items:
                    if l["meta_data"][0]["value"] == ri["meta_data"][0]["value"]:
                        l["quantity"] = l["quantity"] + ri["quantity"]
            else:
                line_items.append(ri)
                m_list.append(ri["meta_data"][0]["value"])
    for order_item in line_items:
        msg = (
            msg
            + order_item["name"]
            + " x "
            + str(order_item["quantity"]*-1)
            + "\n"
            + "₹"
            + str(order_item["price"])
            + " x "
            + str(order_item["quantity"]*-1)
            + " = "
            + str(order_item["subtotal"])[1:]
            + "\n\n"
        )
    if len(msg) > 0:
        msg = "We are not able to send: \n\n"+msg
    return msg


def list_order_items(order_items, refunds):
    msg = ""
    total_refunds = []
    for r in refunds:
        for ri in r["line_items"]:
            total_refunds.append(ri)
    for order_item in order_items:
        for refund in total_refunds:
            if order_item["id"] == int(refund["meta_data"][0]["value"]):
                order_item["quantity"] = order_item["quantity"] + \
                    refund["quantity"]
                order_item["total"] = float(
                    order_item["total"]) + float(refund["total"])
        if order_item["quantity"] > 0:
            msg = (
                msg
                + order_item["name"]
                + " x "
                + str(order_item["quantity"])
                + "\n"
                + "₹"
                + str(order_item["price"])
                + " x "
                + str(order_item["quantity"])
                + " = "
                + str(order_item["total"])
                + "\n\n"
            )
    return msg


def list_order_items_csv(order_items, refunds):
    msg = ""
    total_refunds = []
    for r in refunds:
        for ri in r["line_items"]:
            total_refunds.append(ri)
    for order_item in order_items:
        for refund in total_refunds:
            if order_item["id"] == int(refund["meta_data"][0]["value"]):
                order_item["quantity"] = order_item["quantity"] + \
                    refund["quantity"]
                order_item["total"] = float(
                    order_item["total"]) + float(refund["total"])
        if order_item["quantity"] > 0:
            msg = (
                msg
                + order_item["name"]
                + " x "
                + str(order_item["quantity"])
                + " = "
                + str(order_item["total"])
                + "\n\n"
            )
    return msg

def list_only_refunds(order_refunds):
    msg = ""
    for r in order_refunds:
        if len(r["line_items"]) == 0:
            msg = msg+r["reason"]+": "+r["amount"]+"\n\n"
    return msg


def get_totals(total, refunds):
    msg = str(total)
    for r in refunds:
        msg = msg+" - " + str(r["amount"])
        total = float(total) - float(r["amount"])
    if len(refunds) > 0:
        msg = msg+" = "+str(total)
    return str(total)


def get_list_to_string(l):
    list_s = ""
    for i in l:
        list_s += i
        list_s += ", "
    list_s = list_s[:-2]
    return list_s


def get_params(args):
    params = {"per_page": 50}
    if "page" in args:
        params["page"] = int(args["page"][0])
    else:
        params["page"] = 1
    if "status" in args:
        if args["status"][0] == 'subscription':
            params["status"] = "tbd-paid, tbd-unpaid"
            params["created_via"] = "subscription"
        else:
            if args["status"][0] == "tbd-paid, tbd-unpaid":
                l_c = list_created_via.copy()
                l_c.remove("subscription")
                params["created_via"] = get_list_to_string(l_c)
            params["status"] = args["status"][0]
    else:
        l_c = list_created_via.copy()
        l_c.remove("subscription")
        params["created_via"] = get_list_to_string(l_c)
        params["status"] = "tbd-paid, tbd-unpaid"
    if "order_ids" in args:
        if args["order_ids"][0] != "":
            params["include"] = args["order_ids"][0]
    if "name" in args:
        if args["name"][0] != "":
            params["search"] = args["name"][0]
    if "phone_number" in args:
        if args["phone_number"][0] != "":
            params["search"] = args["phone_number"][0]
    if "created_via" in args:
        if args['created_via'][0] != "":
            params["created_via"] = get_list_to_string(args["created_via"])
    if "vendor" in args:
        if args["vendor"][0] != "":
            params["vendor"] = get_list_to_string(args["vendor"])
    if "delivery_date" in args:
        if args["delivery_date"][0] != "":
            params["delivery_date"] = args["delivery_date"][0].replace(
                "/", "-")
    if "after" in args:
        if args["after"][0] != "":
            params["after"] = args["after"][0].replace("/", "-")+"T00:00:00"
    if "before" in args:
        if args["before"][0] != "":
            params["before"] = args["before"][0].replace("/", "-")+"T00:00:00"
    return params


def get_shipping_total(o):
    if float(o["shipping_total"]) > 0:
        return " (Including delivery charge of Rs "+o["shipping_total"]+")"
    else:
        return ""


def get_shipping_total_for_csv(o):
    if float(o["shipping_total"]) > 0:
        return " (Including Rs "+o["shipping_total"]+" delivery charge)"
    else:
        return ""


def get_orders_with_messages(orders, wcapi):
    def _get_orders_with_messages(o):
        order_refunds = []
        if len(o["refunds"]) > 0:
            order_refunds = wcapi.get("orders/"+str(o["id"])+"/refunds").json()
        c_msg = "Here are the order details:\n\n" + \
            list_order_items(o["line_items"], order_refunds) + \
            "*Total Amount: " + \
            get_totals(o["total"], order_refunds) + \
            get_shipping_total(o)+"*\n\n"
        c_msg = c_msg + \
            list_order_refunds(order_refunds) + \
            list_only_refunds(order_refunds)
        s_msg = ("Order ID: "+str(o["id"])
                 + "\n\nName: "+o["billing"]["first_name"] +
                 " "+o["billing"]["last_name"]
                 + "\nMobile: "+o["billing"]["phone"]
                 + "\nAddress: "+o["shipping"]["address_1"] + ", "+o["shipping"]["address_2"]+", "+o["shipping"]["city"]+", "+o["shipping"]["state"]+", "+o["shipping"]["postcode"] +
                 ", "+o["billing"]["address_2"]
                     + "\n\nTotal Amount: " +
                 get_totals(o["total"], order_refunds)
                     + get_shipping_total(o)
                     + "\n\n"+list_order_items(o["line_items"], order_refunds)
                     + "Payment Status: Paid To LeapClub."
                     + "\nCustomer Note: "+o["customer_note"])
        o["c_msg"] = c_msg
        o["s_msg"] = s_msg
        return o
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = executor.map(_get_orders_with_messages, orders)
    return list(result)


def get_orders_with_wallet_balance(orders, wcapiw):
    def _get_orders_with_wallet_balance(o):
        balance = wcapiw.get("current_balance/"+str(o["customer_id"]))
        o["wallet_balance"] = float(balance.text[1:-1])
        return o
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = executor.map(_get_orders_with_wallet_balance, orders)
    return list(result)


def get_csv_from_orders(orders, wcapi):
    f = open("sample.csv", "w+")
    writer = csv.DictWriter(
        f, fieldnames=["Order ID", "Customer Detail", "Total Amount", "Order Details", "Comments", "Customer Note"])
    writer.writeheader()
    for o in orders:
        wallet_payment = 0
        if len(o["fee_lines"]) > 0:
            for item in o["fee_lines"]:
                if item["name"] == "Via wallet":
                    wallet_payment = (-1)*float(item["total"])
                    break
        o["total"] = float(o["total"]) + float(wallet_payment)
        refunds = []
        if len(o["refunds"]) > 0:
            refunds = wcapi.get("orders/"+str(o["id"])+"/refunds").json()
        writer.writerow({
            "Order ID": o["id"],
            "Customer Detail": "Name: "+o["billing"]["first_name"]+" "+o["billing"]["last_name"]+"\nMobile: "+o["billing"]["phone"]
            + "\nAddress: "+o["shipping"]["address_1"] + ", "+o["shipping"]["address_2"]+", " +
            o["shipping"]["city"]+", "+o["shipping"]["state"] +
            ", "+o["shipping"]["postcode"],
            "Total Amount": get_totals(o["total"], refunds)+get_shipping_total_for_csv(o),
            "Order Details": list_order_items_csv(o["line_items"], refunds),
            "Comments": "Payment Status: Paid To Leap",
            "Customer Note": o["customer_note"]
        })
        writer.writerow({})
    f.close()
    f = open("sample.csv", "r")
    result = f.read()
    os.remove("sample.csv")
    return result


def get_csv_from_vendor_orders(orders, wcapi):
    f = open("sample.csv", "w+")
    writer = csv.DictWriter(
        f, fieldnames=["Date Created", "Delivery Date", "Order ID", "Customer Detail", "Total Order Amount", "Refund Amount", "Delivery Charge", "Order Items", "Payment Method"])
    writer.writeheader()
    for o in orders:
        refund_amount = 0
        for r in o["refunds"]:
            print(r)
            refund_amount = refund_amount + float(r["total"])
        delivery_date = ""
        for item in o["meta_data"]:
            if item["key"] == "_delivery_date":
                if delivery_date == "":
                    delivery_date = item["value"]
            elif item["key"] == "_wc_acof_2_formatted":
                if delivery_date == "":
                    delivery_date = item["value"]
        wallet_payment = 0
        if len(o["fee_lines"]) > 0:
            for item in o["fee_lines"]:
                if item["name"] == "Via wallet":
                    wallet_payment = (-1)*float(item["total"])
                    break
        o["total"] = float(o["total"]) + float(wallet_payment)
        refunds = []
        if len(o["refunds"]) > 0:
            refunds = wcapi.get("orders/"+str(o["id"])+"/refunds").json()
        writer.writerow({
            "Date Created": o["date_created"],
            "Delivery Date": delivery_date,
            "Order ID": o["id"],
            "Customer Detail":  "Name: "+o["billing"]["first_name"]+" "+o["billing"]["last_name"]+"\nMobile: "+o["billing"]["phone"]
            + "\nAddress: "+o["shipping"]["address_1"] + ", "+o["shipping"]["address_2"]+", " +
            o["shipping"]["city"]+", "+o["shipping"]["state"] +
            ", "+o["shipping"]["postcode"],
            "Total Order Amount": get_totals(o["total"], refunds)+get_shipping_total_for_csv(o),
            "Refund Amount": refund_amount*-1,
            "Delivery Charge": o["shipping_total"],
            "Order Items": list_order_items_csv(o["line_items"], refunds)+list_order_refunds(refunds),
            "Payment Method": o["payment_method_title"]
        })
        writer.writerow({})
    f.close()
    f = open("sample.csv", "r")
    result = f.read()
    os.remove("sample.csv")
    return result


def get_checkout_url(o):
    url = "https://leapclub.in/checkout/order-pay/" + \
        str(o["id"])+"/?pay_for_order=true&key="+o["order_key"]
    return url


def list_categories_with_products(products):
    main_list = {}
    d_c = []
    for p in products:
        if len(p["categories"]) > 1:
            d_c.append(p)
        for c in p["categories"]:
            if c["name"] in main_list.keys():
                main_list[c["name"]].append(p)
            else:
                main_list[c["name"]] = []
    txt = ""
    for c in main_list:
        if len(main_list[c]) > 0:
            txt = txt+"\n*"+c+"*\n\n"
            for p in main_list[c]:
                txt = txt+p["name"]+" - ₹"+p["price"]+"\n"
    return(txt)


def list_categories(wcapi):
    args = {"per_page": 100}
    categories = []
    page = 1
    while True:
        args["page"] = page
        c = wcapi.get("products/categories", params=args).json()
        categories.extend(c)
        page = page+1
        if len(c) < 100:
            break
    return categories


def list_all_orders_tbd(wcapi):
    orders = []
    page = 1
    while True:
        order = wcapi.get("orders", params={
                          "page": page, "per_page": 100, "status": "tbd-paid, tbd-unpaid"}).json()
        orders.extend(order)
        page = page+1
        if len(order) < 100:
            break
    total = []
    for o in orders:
        if o["created_via"] == "subscription":
            total.append(o)
    return total


def list_created_via_with_filter(orders):
    created_vias = []
    for o in orders:
        if o["created_via"] not in created_vias:
            created_vias.append(o["created_via"])
    return created_vias


def filter_orders_with_subscription(orders, args):
    new_list = []
    if "status" in args:
        if args["status"][0] == "subscription":
            for o in orders:
                if o["created_via"] == "subscription":
                    new_list.append(o)
        elif args["status"][0] == "tbd-paid, tbd-unpaid":
            for o in orders:
                if o["created_via"] != "subscription":
                    new_list.append(o)
        else:
            return orders
    else:
        for o in orders:
            if o["created_via"] != "subscription":
                new_list.append(o)
    return new_list


def list_orders_with_status(wcapi, params):
    def get_order(params):
        order = wcapi.get("order2", params=params)
        return order
    page = 1
    ctime = time.time()
    forder = wcapi.get("order2", params=params)
    total_pages = int(forder.headers["X-WP-TotalPages"])
    p_list = []
    p = 2
    while p < total_pages+1:
        params["page"] = p
        p_list.append(params.copy())
        p += 1
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = executor.map(get_order, p_list)
    orders = list(result)
    orders.insert(0, forder)
    o_list = []
    for o in orders:
        o_list.extend(o.json())
    return o_list
