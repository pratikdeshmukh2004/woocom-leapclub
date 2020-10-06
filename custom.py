def filter_orders(orders, params):
    if len(params) <= 1:
        return orders
    f_orders = []
    for o in orders:
        c = {"status": False, "payment_status": False,
             "phone_number": False, "name": False, "order_id": False}
        if "status" in params:
            if params["status"][0] != "":
                if params["status"][0] == o["status"]:
                    c["status"] = True
            else:
                c["status"] = True

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
                if params["name"][0] in (o["billing"]["first_name"] + " " + o["billing"]["last_name"]):
                    c["name"] = True
            else:
                c["name"] = True
        if "order_id" in params:
            if params["order_id"] != []:
                if o["id"] in params["order_id"]:
                    c["order_id"] = True
            else:
                c["order_id"] = True
        if c["status"] and c["payment_status"] and c["phone_number"] and c["name"] and c["order_id"]:
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
    if len(msg)>0:
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
                order_item["quantity"] = order_item["quantity"] + refund["quantity"]
                order_item["total"] = float(order_item["total"]) + float(refund["total"])
        if order_item["quantity"]>0:
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

def list_only_refunds(order_refunds):
    msg = ""
    for r in order_refunds:
        if len(r["line_items"])==0:
            msg = msg+r["reason"]+": "+r["amount"]+"\n\n"
    return msg