from flask import Flask, render_template, request, url_for, redirect, jsonify, make_response, g, session
from flask_sqlalchemy import SQLAlchemy
from sshtunnel import SSHTunnelForwarder
from woocommerce import API
from sqlalchemy.dialects.postgresql import UUID
from custom import filter_orders, list_order_items, get_params, get_orders_with_messages, get_csv_from_orders, get_checkout_url, list_categories_with_products, list_categories, get_orders_with_wallet_balance, list_all_orders_tbd, list_created_via_with_filter
from flask_datepicker import datepicker
from werkzeug.datastructures import ImmutableMultiDict
from datetime import datetime
from template_broadcast import TemplatesBroadcast, vendor_type
import uuid
import json
import requests
import csv
import os
import ast
import time
from datetime import datetime, timedelta
app = Flask(__name__, instance_relative_config=True)
datepicker(app)

app.config.from_pyfile("config.py")

db = SQLAlchemy(app)
wcapi = API(
    url=app.config["WOOCOMMERCE_API_URL"],
    consumer_key=app.config["WOOCOMMERCE_API_CUSTOMER_KEY"],
    consumer_secret=app.config["WOOCOMMERCE_API_CUSTOMER_SECRET"],
    version="wc/v3",
    timeout=15
)

# wcapiw = API(
#     url=app.config["WOOCOMMERCE_API_URL"],
#     consumer_key=app.config["WOOCOMMERCE_API_CUSTOMER_KEY_WALLET"],
#     consumer_secret=app.config["WOOCOMMERCE_API_CUSTOMER_SECRET_WALLET"],
#     version="wp/v2",
#     timeout=15
# )


class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return f'<User: {self.email}>'


users = []
users.append(User(email=app.config["ADMIN_EMAIL"],
                  password=app.config["ADMIN_PASSWORD"]))


@app.errorhandler(404)
def invalid_route(e):
    return redirect(url_for("products"))


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [x for x in users if x.email == session['user_id']]
        if len(user) > 0:
            g.user = user[0]


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    args = request.args.to_dict(flat=False)
    if "error" in args:
        error = args["error"][0]
    if request.method == 'POST':
        session.pop('user_id', None)
        email = request.form['email']
        password = request.form['password']
        user = [x for x in users if x.email == email]
        if len(user) > 0:
            user = user[0]
            if user.password == password:
                session['user_id'] = email
                return redirect(url_for('woocom_orders'))
            else:
                error = "Invalid User Password!"
        else:
            error = "You do not have accesss. Please contact To Admin!"
        return redirect(url_for('login', error=error))
    if "user_id" in session:
        return redirect(url_for("woocom_orders"))
    else:
        return render_template('login.html', error=error)


class wtmessages(db.Model):
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    order_id = db.Column(db.Integer)
    time_sent = db.Column(db.DateTime, default=datetime.utcnow())
    template_name = db.Column(db.String)
    broadcast_name = db.Column(db.String)
    status = db.Column(db.String)


@app.route("/orders")
def woocom_orders():
    if not g.user:
        return redirect(url_for('login'))
    args = request.args.to_dict(flat=False)
    new_ids = []
    if "order_ids" in args:
        for i in args["order_ids"]:
            new_ids.append(int(i))
    args["order_ids"] = new_ids
    if "w_status" in args:
        is_w = True
        w_status = args["w_status"]
    else:
        is_w = False
        w_status = ""
    params = get_params(args)
    params["page"] = request.args.get("page", 1, type=int)
    start_time = time.time()
    if "status" in args:
        if args["status"][0] == 'subscription':
            params["status"] = "subscription"
            orders = list_all_orders_tbd(wcapi)
        else:
            orders = wcapi.get("orders", params=params).json()
    else:
        orders = wcapi.get("orders", params=params).json()
    fetch_time = time.time()
    print("Time to fetch orders: " + str(fetch_time-start_time))
    f_orders = filter_orders(orders, args)
    filter_time = time.time()
    print("Time to filer:", str(filter_time-fetch_time))
    vendors = []
    managers = []
    wtmessages_list = {}
    orders = get_orders_with_messages(f_orders, wcapi)
    # fetch_time = time.time()
    # orders = get_orders_with_wallet_balance(orders, wcapiw)
    # wallet_fetch_time = time.time()
    # print("Time to Fetch Wallet Balance Of All Orders:", str(wallet_fetch_time-fetch_time))
    for o in orders:
        refunds = 0
        for r in o["refunds"]:
            refunds = refunds + float(r["total"])
        o["total_refunds"] = refunds*-1
        o["total"] = float(o["total"])
        wt_messages = wtmessages.query.filter_by(order_id=o["id"]).all()
        wtmessages_list[o["id"]] = wt_messages
        vendor = ""
        manager = ""
        delivery_date = ""
        wallet_payment = 0
        for item in o["meta_data"]:
            if item["key"] == "wos_vendor_data":
                vendor = item["value"]["vendor_name"]
            elif item["key"] == "_wc_acof_6":
                vendor = item["value"]
            elif item["key"] == "_wc_acof_3":
                manager = item["value"]
            elif item["key"] == "_delivery_date":
                if delivery_date == "":
                    delivery_date = item["value"]
            elif item["key"] == "_wc_acof_2_formatted":
                if delivery_date == "":
                    delivery_date = item["value"]

        if len(o["fee_lines"]) > 0:
            for item in o["fee_lines"]:
                if "wallet" in item["name"].lower():
                    wallet_payment = (-1)*float(item["total"])

        if vendor not in vendors:
            vendors.append(vendor)
        if manager not in managers:
            managers.append(manager)
        if vendor in vendor_type.keys():
            o["vendor_type"] = vendor_type[vendor]
        else:
            o["vendor_type"] = ""
        o["vendor"] = vendor
        o["delivery_date"] = delivery_date
        o["manager"] = manager
        o["wallet_payment"] = wallet_payment
        o["total"] = float(o["total"]) + float(o["wallet_payment"])
        o["checkout_url"] = get_checkout_url(o)
    list_created_via = list_created_via_with_filter(orders)
    data_time = time.time()
    print("Calculating additional columns" + str(data_time-filter_time))
    message_time = time.time()
    print("Create message time" + str(message_time-data_time))
    return render_template("woocom_orders.html", json=json, orders=orders, query=args, nav_active=params["status"], is_w=is_w, w_status=w_status, managers=managers, vendors=vendors, wtmessages_list=wtmessages_list, c_page=params["page"], user=g.user, list_created_via=list_created_via)


def send_whatsapp_msg(args, mobile, name):
    url = app.config["WATI_URL"]+"/api/v1/sendTemplateMessage/" + mobile
    if name in TemplatesBroadcast.keys():
        template_name = TemplatesBroadcast[name][args["vendor_type"]]["template"]
        broadcast_name = TemplatesBroadcast[name][args["vendor_type"]]["broadcast"]
    else:
        return {"result": "error", "info": "Please Select Valid Button."}
    parameters_s = "["
    args["name"] = args["c_name"]
    args["order_note"] = "No changes to the order" if args["order_note"] == '' else args["order_note"]
    for d in args:
        parameters_s = parameters_s + \
            '{"name":"'+str(d)+'", "value":"'+str(args[d])+'"},'
    parameters_s = parameters_s[:-1]
    parameters_s = parameters_s+"]"
    payload = {
        "template_name": template_name,
        "broadcast_name": broadcast_name,
        "parameters": parameters_s
    }
    headers = {
        'Authorization': app.config["WATI_AUTHORIZATION"],
        'Content-Type': 'application/json',
    }

    response = requests.request(
        "POST", url, headers=headers, data=json.dumps(payload))

    result = json.loads(response.text.encode('utf8'))
    if result["result"] != "success":
        result["broadcast_name"] = broadcast_name
        result["template_name"] = template_name
    return result


@app.route("/send_whatsapp_msg/<string:name>")
def send_whatsapp(name):
    if not g.user:
        return redirect(url_for('login'))
    args = request.args.to_dict(flat=True)
    if len(args) > 0:
        if "status" in args:
            nav_active = args["status"]
        else:
            nav_active = "any"
        mobile_number = args["mobile_number"].strip(" ")
        mobile_number = mobile_number[-10:]
        mobile_number = (
            "91"+mobile_number) if len(mobile_number) == 10 else mobile_number
        result = send_whatsapp_msg(args, mobile_number, name)
        if result["result"] == "success":
            new_wt = wtmessages(order_id=args["order_id"], template_name=result["template_name"], broadcast_name=result[
                                "broadcast"]["broadcastName"], status="success", time_sent=datetime.utcnow())
        else:
            new_wt = wtmessages(order_id=args["order_id"], template_name=result["template_name"], broadcast_name=result[
                                "broadcast_name"], status="failed", time_sent=datetime.utcnow())
        db.session.add(new_wt)
        db.session.commit()
        if nav_active != "any":
            return redirect(url_for("woocom_orders", status=nav_active, message_sent=args["order_id"], page=args["page"][0]))
        else:
            return redirect(url_for("woocom_orders", message_sent=args["order_id"], page=args["page"][0]))


@app.route('/csv', methods=["POST"])
def download_csv():
    if not g.user:
        return redirect(url_for('login'))
    data = request.form.to_dict(flat=False)
    orders = wcapi.get("orders", params=get_params(data)).json()
    csv_text = get_csv_from_orders(orders, wcapi)
    filename = str(datetime.utcnow())+"-" + data["status"][0]+".csv"
    response = make_response(csv_text)
    if "," in filename:
        filename = filename.replace(",", "-")
    cd = 'attachment; filename='+filename
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'

    return response


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route("/products")
def products():
    if not g.user:
        return redirect(url_for('login'))
    args = request.args.to_dict(flat=True)
    if "page" in args:
        page = args["page"]
    else:
        page = 1
    args["stock_status"] = "instock"
    args["per_page"] = 50
    products = wcapi.get("products", params=args).json()
    total_categories = list_categories(wcapi)
    print(len(total_categories))
    return render_template("products/index.html", user=g.user, products=products, params=args, total_categories=total_categories, page=int(page))


@app.route("/list_product_categories")
def list_product_categories():
    if not g.user:
        return redirect(url_for('login'))
    args = request.args.to_dict(flat=True)
    args["stock_status"] = "instock"
    args["per_page"] = 100
    total_products = []
    page = 1
    while True:
        args["page"] = page
        products = wcapi.get("products", params=args).json()
        total_products.extend(products)
        page = page+1
        if len(products) < 100:
            break
    list_categories = list_categories_with_products(total_products)
    filename = str(datetime.utcnow())+"-" + "categories-text.txt"
    response = make_response(list_categories)
    cd = 'attachment; filename='+filename
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'
    return response


@app.route("/list_product_categories_by_c")
def list_product_categories_by_c():
    if not g.user:
        return redirect(url_for('login'))
    args = request.args.to_dict(flat=False)
    args["stock_status"] = "instock"
    args["per_page"] = 100
    total_products = []
    for c in args["categories"]:
        page = 1
        args["category"] = str(c)
        while True:
            args["page"] = page
            products = wcapi.get("products", params=args).json()
            total_products.extend(products)
            page = page+1
            if len(products) < 100:
                break
    list_categories = list_categories_with_products(total_products)
    filename = str(datetime.utcnow())+"-" + "categories-text.txt"
    response = make_response(list_categories)
    cd = 'attachment; filename='+filename
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'
    return response


@app.route("/new_order", methods=["GET", "POST"])
def new_order():
    o = request.get_json()
    customer_number = o["billing"]["phone"]
    mobile_numbers = ["919325837420", "919517622867"]
    print("\n\nEvent aaya hai........................."+str(o["id"]))
    params = {}
    vendor = ""
    delivery_date = ""
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
    print(delivery_date)
    if vendor in vendor_type.keys():
        vendor_type1 = vendor_type[vendor]
    else:
        vendor_type1 = ""
    checkout_url = str(o["id"])+"/?pay_for_order=true&key="+str(o["order_key"])
    wallet_payment = 0
    if len(o["fee_lines"]) > 0:
        for item in o["fee_lines"]:
            if "wallet" in item["name"].lower():
                wallet_payment = (-1)*float(item["total"])
    o["total"] = float(o["total"]) + float(wallet_payment)
    params["c_name"] = o["billing"]["first_name"]
    params["order_id"] = o["id"]
    params["order_note"] = o["customer_note"]
    params["total_amount"] = float(o["total"])
    params["delivery_date"] = delivery_date
    params["payment_method"] = o["payment_method_title"]
    params["delivery_charge"] = o["shipping_total"]
    params["items_amount"] = float(o["total"])-float(o["shipping_total"])
    params["order_key"] = o["order_key"]
    params["vendor_type"] = vendor_type1
    params["seller"] = vendor
    params["url_post_pay"] = checkout_url
    od = datetime.fromisoformat(o["date_created"])
    cd = datetime.now()
    nd = (cd - timedelta(minutes=15)).isoformat()
    nd = datetime.fromisoformat(nd)
    if o["status"] == "processing" and o["created_via"] == "checkout" and vendor and od > nd:
        for num in mobile_numbers:
            print("sent to : "+num)
            if o["date_paid"] != None:
                result = send_whatsapp_msg(params, num, "order_prepay")
            else:
                result = send_whatsapp_msg(params, num, "order_postpay")
    else:
        return {"Result": "Please Enter Valid Detal..."}
    if result["result"] == "success":
        new_wt = wtmessages(order_id=params["order_id"], template_name=result["template_name"], broadcast_name=result[
                            "broadcast"]["broadcastName"], status="success", time_sent=datetime.utcnow())
    else:
        new_wt = wtmessages(order_id=params["order_id"], template_name=result["template_name"], broadcast_name=result[
                            "broadcast_name"], status="failed", time_sent=datetime.utcnow())
    db.session.add(new_wt)
    db.session.commit()
    print("Done")
    return {"Result": "Success No Error..."}


if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True)
