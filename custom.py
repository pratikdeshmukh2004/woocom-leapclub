import os
import csv


def filter_orders(orders, params):
    if len(params) <= 4:
        return orders
    f_orders = []
    for o in orders:
        c = {"payment_status": False,
             "phone_number": False, "name": False, "vendor": False, "manager": False}

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
        if "phone_number" in params:
            if params["phone_number"][0] != "":
                if params["phone_number"][0] in o["billing"]["phone"]:
                    c["phone_number"] = True
            else:
                c["phone_number"] = True
        if "name" in params:
            if params["name"][0] != "":
                if params["name"][0].lower() in (o["billing"]["first_name"] + " " + o["billing"]["last_name"]).lower():
                    c["name"] = True
            else:
                c["name"] = True
        vendor = ""
        manager = ""
        for item in o["meta_data"]:
            if item["key"] == "wos_vendor_data":
                vendor = item["value"]["vendor_name"]
            elif item["key"] == "_wc_acof_6":
                vendor = item["value"]
            elif item["key"] == "_wc_acof_3":
                manager = item["value"]
        if "vendor" in params:
            if vendor in params["vendor"]:
                c["vendor"] = True
        else:
            c["vendor"] = True
        if "manager" in params:
            if manager in params["manager"]:
                c["manager"] = True
        else:
            c["manager"] = True
        if c["payment_status"] and c["phone_number"] and c["name"] and c["vendor"] and c["manager"]:
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


def get_params(args):
    params = {"per_page": 50}
    if "status" in args:
        params["status"] = args["status"][0]
    else:
        params["status"] = "tbd-paid, tbd-unpaid"
    if "order_ids" in args:
        id_text = ""
        for id in args["order_ids"]:
            id_text = id_text+str(id)+", "
        params["include"] = id_text[:-2]
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
    for o in orders:
        order_refunds = []
        if len(o["refunds"]) > 0:
            order_refunds = wcapi.get("orders/"+str(o["id"])+"/refunds").json()
        c_msg = "Here are the order details:\n\n" + \
            list_order_items(o["line_items"], order_refunds) + \
            "*Total Amount: " + \
                get_totals(o["total"], order_refunds) + \
            get_shipping_total(o)+"*\n\n"+"Customer Note: "+o["customer_note"]
        if len(o["refunds"]) > 0:
            c_msg = c_msg + \
                list_order_refunds(order_refunds) + \
                list_only_refunds(order_refunds)
        s_msg = ("Order ID: "+str(o["id"])
                 + "\n\nName: "+o["billing"]["first_name"] +
                 " "+o["billing"]["last_name"]
                 + "\nMobile: "+o["billing"]["phone"]
                 + "\nAddress: "+o["shipping"]["address_1"] +", "+o["shipping"]["address_2"]+", "+o["shipping"]["city"]+", "+o["shipping"]["state"]+", "+o["shipping"]["postcode"] +
                 ", "+o["billing"]["address_2"]
                 + "\n\nTotal Amount: "+get_totals(o["total"], order_refunds)
                 + get_shipping_total(o)
                 + "\n\n"+list_order_items(o["line_items"], order_refunds)
                 + "Payment Status: Paid To LeapClub."
                 + "\nCustomer Note: "+o["customer_note"])
        o["c_msg"] = c_msg
        o["s_msg"] = s_msg
    return orders


def get_csv_from_orders(orders, wcapi):
    f = open("sample.csv", "w+")
    writer = csv.DictWriter(
        f, fieldnames=["Order ID", "Customer Detail", "Total Amount", "Order Details", "Comments", "Customer Note"])
    writer.writeheader()
    for o in orders:
        wallet_payment = 0
        if len(o["fee_lines"])>0:
            for item in o["fee_lines"]:
                if item["name"] == "Via wallet":
                    wallet_payment = (-1)*float(item["total"])
                    break
        o["total"]  = float(o["total"]) + float(wallet_payment)
        refunds = []
        if len(o["refunds"]) > 0:
            refunds = wcapi.get("orders/"+str(o["id"])+"/refunds").json()
        writer.writerow({
            "Order ID": o["id"],
            "Customer Detail": "Name: "+o["billing"]["first_name"]+" "+o["billing"]["last_name"]+"\nMobile: "+o["billing"]["phone"]
            + "\nAddress: "+o["shipping"]["address_1"] +", "+o["shipping"]["address_2"]+", "+o["shipping"]["city"]+", "+o["shipping"]["state"]+", "+o["shipping"]["postcode"],
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
