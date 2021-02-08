from flask import Flask, render_template, request, url_for, redirect, jsonify, make_response, g, session
from flask_sqlalchemy import SQLAlchemy
from sshtunnel import SSHTunnelForwarder
from woocommerce import API
from sqlalchemy.dialects.postgresql import UUID
from custom import filter_orders, list_order_items, get_params, get_orders_with_messages, get_csv_from_orders, get_checkout_url, list_categories_with_products, list_categories, get_orders_with_wallet_balance, list_all_orders_tbd, list_created_via_with_filter, filter_orders_with_subscription, list_orders_with_status, get_csv_from_vendor_orders, get_list_to_string, get_total_from_line_items, update_order_status, get_csv_from_products
from werkzeug.datastructures import ImmutableMultiDict
from template_broadcast import TemplatesBroadcast, vendor_type
from customselectlist import list_created_via, list_vendor
import uuid
import json
import requests
import csv
import os
import ast
import concurrent.futures
import time
import razorpay
from datetime import datetime, timedelta
from pytz import timezone
from slack import WebClient
from slack_bot import send_slack_message, send_slack_message_calcelled

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile("config.py")
db = SQLAlchemy(app)

wcapi = API(
    url=app.config["WOOCOMMERCE_API_URL"],
    consumer_key=app.config["WOOCOMMERCE_API_CUSTOMER_KEY"],
    consumer_secret=app.config["WOOCOMMERCE_API_CUSTOMER_SECRET"],
    version="wc/v3",
    timeout=15
)

wcapi_write = API(
    url=app.config["WOOCOMMERCE_API_URL"],
    consumer_key=app.config["WOOCOMMERCE_API_CUSTOMER_KEY_WRITE"],
    consumer_secret=app.config["WOOCOMMERCE_API_CUSTOMER_SECRET_WRITE"],
    version="wc/v3",
    timeout=15
)

wcapis = API(
    url=app.config["WOOCOMMERCE_API_URL"],
    consumer_key=app.config["WOOCOMMERCE_API_CUSTOMER_KEY"],
    consumer_secret=app.config["WOOCOMMERCE_API_CUSTOMER_SECRET"],
    version="wc/v1",
    timeout=15
)

wcapiw = API(
    url=app.config["WOOCOMMERCE_API_URL"],
    consumer_key=app.config["WOOCOMMERCE_API_CUSTOMER_KEY_WALLET"],
    consumer_secret=app.config["WOOCOMMERCE_API_CUSTOMER_SECRET_WALLET"],
    version="wp/v2",
    timeout=15
)

client = WebClient(
    token=app.config["SLACK_APP_TOKEN"]
)

razorpay_client = razorpay.Client(
    auth=(app.config["RAZORPAY_ID"], app.config["RAZORPAY_SECRET"]))


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
    return redirect(url_for("woocom_orders"))


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


class PaymentLinks(db.Model):
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    order_id = db.Column(db.Integer)
    receipt = db.Column(db.String)
    payment_link_url = db.Column(db.String)
    contact = db.Column(db.String)
    status = db.Column(db.String)
    name = db.Column(db.String)
    created_at = db.Column(db.String)
    amount = db.Column(db.Float)



@app.route("/orders")
def woocom_orders():
    if not g.user:
        return redirect(url_for('login'))
    args = request.args.to_dict(flat=False)
    params = get_params(args)
    if "created_via" in params:
        args["created_via"] = params["created_via"]
    t_orders = time.time()
    orders = wcapi.get("order2", params=params).json()
    print("Time To Fetch Total Orders: "+str(time.time()-t_orders))
    orders = filter_orders(orders, args)
    managers = []
    wtmessages_list = {}
    payment_links = {}
    t_refunds = time.time()
    orders = get_orders_with_messages(orders, wcapi)
    print("Time To Fetch Total Refunds: "+str(time.time()-t_refunds))
    for o in orders:
        wallet_payment = 0
        refunds = 0
        for r in o["refunds"]:
            refunds = refunds + float(r["total"])
        o["total_refunds"] = refunds*-1
        o["total"] = float(o["total"])
        wt_messages = wtmessages.query.filter_by(order_id=o["id"]).all()
        payment_link = PaymentLinks.query.filter_by(order_id=o["id"]).all()
        if len(payment_link)>0:
            payment_link = payment_link[-1]
        else:
            payment_link = ''
        payment_links[o["id"]] = payment_link
        wtmessages_list[o["id"]] = wt_messages
        vendor, manager, delivery_date, order_note,  = "", "", "", ""
        for item in o["meta_data"]:
            if item["key"] == "wos_vendor_data":
                vendor = item["value"]["vendor_name"]
            elif item["key"] == "_wc_acof_6":
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
        if len(o["fee_lines"]) > 0:
            for item in o["fee_lines"]:
                if "wallet" in item["name"].lower():
                    wallet_payment = (-1)*float(item["total"])

        if manager not in managers:
            managers.append(manager)
        if vendor in vendor_type.keys():
            o["vendor_type"] = vendor_type[vendor]
        else:
            o["vendor_type"] = ""
        o["vendor"] = vendor
        o["delivery_date"] = delivery_date
        o["order_note"] = order_note
        o["manager"] = manager
        o["wallet_payment"] = wallet_payment
        o["total"] = float(o["total"]) + float(o["wallet_payment"])
        o["checkout_url"] = get_checkout_url(o)
    if "status" in args:
        if args["status"][0] == "subscription":
            params["status"] = "subscription"
    return render_template("woocom_orders.html", json=json, orders=orders, query=args, nav_active=params["status"], managers=managers, vendors=list_vendor, wtmessages_list=wtmessages_list, user=g.user, list_created_via=list_created_via, page=params["page"], payment_links=payment_links)


def send_whatsapp_msg(args, mobile, name):
    url = app.config["WATI_URL"]+"/api/v1/sendTemplateMessage/" + mobile
    if name in TemplatesBroadcast.keys():
        template_name = TemplatesBroadcast[name][args["vendor_type"]]["template"]
        broadcast_name = TemplatesBroadcast[name][args["vendor_type"]]["broadcast"]
    else:
        return {"result": "error", "info": "Please Select Valid Button."}
    parameters_s = "["
    if "c_name" in args:
        args["name"] = args["c_name"]
    if "order_note" in args:
        if args["order_note"] == "":
            args["order_note"] = "No changes to the order"
    else:
        args["order_note"] = "No changes to the order"
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
        if result["result"] in ["success", "PENDING", "SENT"]:
            new_wt = wtmessages(order_id=args["order_id"], template_name=result["template_name"], broadcast_name=result[
                                "broadcast"]["broadcastName"], status="success", time_sent=datetime.utcnow())
        else:
            new_wt = wtmessages(order_id=args["order_id"], template_name=result["template_name"], broadcast_name=result[
                                "broadcast_name"], status="failed", time_sent=datetime.utcnow())
        db.session.add(new_wt)
        db.session.commit()
        result['order_id'] = str(args['order_id'])
        return jsonify(result)


@app.route('/csv', methods=["POST"])
def download_csv():
    if not g.user:
        return redirect(url_for('login'))
    data = request.form.to_dict(flat=False)
    params = get_params(data)
    params["include"] = get_list_to_string(data["order_ids"])
    orders = wcapi.get("orders", params=params).json()
    if data["action"][0] == "order_sheet":
        csv_text = get_csv_from_orders(orders, wcapi)
        filename = str(datetime.utcnow())+"-" + \
            data["status"][0]+"-Product-Sheet.csv"
    elif data["action"][0] == "product_sheet":
        csv_text = get_csv_from_products(orders, wcapi)
        filename = str(datetime.utcnow())+"-" + "Product-Sheet.csv"
    else:
        csv_text = get_csv_from_vendor_orders(orders, wcapi)
        filename = str(datetime.utcnow())+"-" + \
            data["status"][0]+"-Vendor-Order-Sheet.csv"
    response = make_response(csv_text)
    if "," in filename:
        filename = filename.replace(",", "-")
    cd = 'attachment; filename='+filename
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'
    return response


@app.route("/download_vendor_order_csv", methods=["POST"])
def download_vendor_order_csv():
    if not g.user:
        return redirect(url_for('login'))
    data = request.form.to_dict(flat=False)
    params = {"per_page": 100}
    params["include"] = get_list_to_string(data["order_ids"])
    orders = list_orders_with_status(wcapi, params)
    csv_text = get_csv_from_vendor_orders(orders, wcapi)
    filename = str(datetime.utcnow())+"-Vendor-Order-Sheet.csv"
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


def update_wati_contact_attributs(o):
    mobile_number = o["billing"]["phone"].strip(" ")
    mobile_number = mobile_number[-10:]
    mobile_number = (
        "91"+mobile_number) if len(mobile_number) == 10 else mobile_number
    url = app.config["WATI_URL"] + \
        "/api/v1/updateContactAttributes/" + mobile_number
    vendor = ""
    for item in o["meta_data"]:
        if item["key"] == "wos_vendor_data":
            vendor = item["value"]["vendor_name"]
        elif item["key"] == "_wc_acof_6":
            vendor = item["value"]
    args = {}
    args['last_order_date'] = o["date_created"]
    args['city'] = o["shipping"]["city"]
    args["last_order_amount"] = get_total_from_line_items(o["line_items"])
    args["last_order_vendor"] = vendor
    day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    week_day = datetime.strptime(
        o["date_created"], '%Y-%m-%dT%H:%M:%S').weekday()
    args["weekly_reminder"] = day_name[week_day]
    parameters_s = "["
    for d in args:
        parameters_s = parameters_s + \
            '{"name":"'+str(d)+'", "value":"'+str(args[d])+'"},'
    parameters_s = parameters_s[:-1]
    parameters_s = parameters_s+"]"
    payload = {"customParams": json.loads(parameters_s)}
    headers = {
        'Authorization': app.config["WATI_AUTHORIZATION"],
        'Content-Type': 'application/json',
    }

    response = requests.request(
        "POST", url, headers=headers, data=json.dumps(payload))

    result = json.loads(response.text.encode('utf8'))
    if result["result"]:
        return True


@app.route("/new_order", methods=["GET", "POST"])
def new_order():
    if request.method == "GET":
        return "Plese Use Get Method..."
    o = request.get_json()
    if o == None:
        return "Please Enter Valid Detail...."
    customer_number = _format_mobile_number(o["billing"]["phone"])
    mobile_numbers = [customer_number]
    params = {}
    vendor = ""
    delivery_date = ""
    order_note = ""
    for item in o["meta_data"]:
        if item["key"] == "wos_vendor_data":
            vendor = item["value"]["vendor_name"]
        elif item["key"] == "_wc_acof_6":
            vendor = item["value"]
        elif item["key"] == "_wc_acof_7":
            order_note = item["value"]
        elif item["key"] == "_delivery_date":
            if delivery_date == "":
                delivery_date = item["value"]
        elif item["key"] == "_wc_acof_2_formatted":
            if delivery_date == "":
                delivery_date = item["value"]
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
    params["order_note"] = order_note
    params["total_amount"] = float(o["total"])
    params["delivery_date"] = delivery_date
    params["payment_method"] = o["payment_method_title"]
    params["delivery_charge"] = o["shipping_total"]
    params["items_amount"] = float(o["total"])-float(o["shipping_total"])
    params["order_key"] = o["order_key"]
    params["vendor_type"] = vendor_type1
    params["seller"] = vendor
    params["url_post_pay"] = checkout_url
    od = datetime.strptime(o["date_created"], '%Y-%m-%dT%H:%M:%S')
    cd = datetime.now(tz=timezone('Asia/Kolkata')).replace(tzinfo=None)
    nd = (cd - timedelta(minutes=5))
    # Sending Whatsapp Template Message....
    if request.headers["x-wc-webhook-topic"] == "order.updated":
        if (o["status"] == "processing") and (o["created_via"] == "checkout") and vendor and (od > nd):
            for num in mobile_numbers:
                if o["date_paid"] != None:
                    result = send_whatsapp_msg(params, num, "order_prepay")
                else:
                    result = send_whatsapp_msg(params, num, "order_postpay")

            if result["result"] in ["success", "PENDING", "SENT"]:
                new_wt = wtmessages(order_id=params["order_id"], template_name=result["template_name"], broadcast_name=result[
                                    "broadcast"]["broadcastName"], status="success", time_sent=datetime.utcnow())
            else:
                new_wt = wtmessages(order_id=params["order_id"], template_name=result["template_name"], broadcast_name=result[
                                    "broadcast_name"], status="failed", time_sent=datetime.utcnow())
            db.session.add(new_wt)
            db.session.commit()

        # End Whatsapp Template Message.....
        # Sending Slack Message....
        if (o["status"] in ["processing", "tdb-paid", "tdb-unpaid"]) and (o["created_via"] in ["admin", "checkout"]) and (od > nd):
            s_msg = send_slack_message(client, wcapi, o)
            update_wati_contact_attributs(o)

        if (o["status"] == "cancelled"):
            s_msg = send_slack_message_calcelled(client, wcapi, o)
        # End Slack Message....

    if request.headers["x-wc-webhook-topic"] == "order.created":
        if (o["created_via"] == "admin"):
            s_msg = send_slack_message(client, wcapi, o)
            update_wati_contact_attributs(o)

    return {"Result": "Success No Error..."}


def _format_mobile_number(number):
    mobile_number = number.strip(" ").replace(" ", "")
    mobile_number = mobile_number[-10:]
    mobile_number = (
        "91"+mobile_number) if len(mobile_number) == 10 else mobile_number
    return mobile_number


@app.route("/vendor_order_sheet")
def vendor_order_sheet():
    if not g.user:
        return redirect(url_for('login'))
    args = request.args.to_dict(flat=False)
    params = get_params(args)
    params["per_page"] = 100
    if "status" in args:
        params["status"] = get_list_to_string(args["status"])
    t_orders = time.time()
    if len(args) > 0:
        orders = list_orders_with_status(wcapi, params)
    else:
        orders = []
    print("Time To Fetch Total Orders: "+str(time.time()-t_orders))
    orders = filter_orders(orders, args)
    managers = []
    wtmessages_list = {}
    for o in orders:
        wallet_payment = 0
        refunds = 0
        for r in o["refunds"]:
            refunds = refunds + float(r["total"])
        o["total_refunds"] = refunds*-1
        o["total"] = float(o["total"])
        wt_messages = wtmessages.query.filter_by(order_id=o["id"]).all()
        wtmessages_list[o["id"]] = wt_messages
        vendor, manager, delivery_date, order_note,  = "", "", "", ""
        for item in o["meta_data"]:
            if item["key"] == "wos_vendor_data":
                vendor = item["value"]["vendor_name"]
            elif item["key"] == "_wc_acof_6":
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
        if len(o["fee_lines"]) > 0:
            for item in o["fee_lines"]:
                if "wallet" in item["name"].lower():
                    wallet_payment = (-1)*float(item["total"])

        if manager not in managers:
            managers.append(manager)
        if vendor in vendor_type.keys():
            o["vendor_type"] = vendor_type[vendor]
        else:
            o["vendor_type"] = ""
        o["vendor"] = vendor
        o["delivery_date"] = delivery_date
        o["order_note"] = order_note
        o["manager"] = manager
        o["wallet_payment"] = wallet_payment
        o["total"] = float(o["total"]) + float(o["wallet_payment"])
        o["checkout_url"] = get_checkout_url(o)
    if "status" in args:
        if args["status"][0] == "subscription":
            params["status"] = "subscription"
    return render_template("vendor-order-sheet/index.html", json=json, orders=orders, query=args, nav_active=params["status"], managers=managers, vendors=list_vendor, wtmessages_list=wtmessages_list, user=g.user, list_created_via=list_created_via, page=params["page"])


def get_subscription_wallet_balance(subscriptions):
    def _get_orders_with_wallet_balance(o):
        balance = wcapiw.get("current_balance/"+str(o["customer_id"]))
        o["wallet_balance"] = float(balance.text[1:-1])
        return o
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = executor.map(_get_orders_with_wallet_balance, subscriptions)
    return list(result)


@app.route("/subscriptions")
def subscriptions():
    if not g.user:
        return redirect(url_for('login'))
    args = request.args.to_dict(flat=True)
    if "order" in args:
        if args["order"] == 'ASC':
            order = 'DSC'
        else:
            order = 'ASC'
    else:
        order = 'ASC'
    if "page" in args:
        page = int(args["page"])
    else:
        page = 1
    args["per_page"] = 50
    t_orders = time.time()
    subscriptions = wcapis.get("subscriptions", params=get_params_subscriptions(args)).json()
    print("Time To Fetch Total Subscriptions: "+str(time.time()-t_orders))
    t_orders = time.time()
    subscriptions = get_subscription_wallet_balance(subscriptions)
    print("Time To Fetch Total Wallet Balance: "+str(time.time()-t_orders))
    subscriptions = sort_subscriptions(subscriptions, args, order)
    return render_template("subscriptions/index.html", user=g.user, subscriptions=subscriptions, page=page, order=order)

def get_params_subscriptions(args):
    params = {"per_page": 50}
    if "page" in args:
        params["page"] = args["page"]
    return params

def sort_subscriptions(subscriptions, args, order):
    if "sort" in args:
        if order == "ASC":
            return sorted(subscriptions, key = lambda i: i['wallet_balance'],reverse=True)
        else:
            return sorted(subscriptions, key = lambda i: i['wallet_balance'],reverse=False)
    else:
        return subscriptions


@app.route("/send_session_message/<string:order_id>")
def send_session_message(order_id):
    if not g.user:
        return redirect(url_for('login'))
    order = wcapi.get("orders/"+order_id).json()
    mobile_number = order["billing"]["phone"]
    order = get_orders_with_messages([order], wcapi)
    mobile_number = mobile_number[-10:]
    mobile_number = (
        "91"+mobile_number) if len(mobile_number) == 10 else mobile_number
    url = app.config["WATI_URL"]+"/api/v1/sendSessionMessage/" + \
        mobile_number + "?messageText="+order[0]["c_msg"]
    headers = {
        'Authorization': app.config["WATI_AUTHORIZATION"],
        'Content-Type': 'application/json',
    }
    ctime = time.time()
    response = requests.request(
        "POST", url, headers=headers)
    print("Time To Send Session Message - ", time.time()-ctime)
    result = json.loads(response.text.encode('utf8'))
    if result["result"] in ["success", "PENDING", "SENT"]:
        new_wt = wtmessages(order_id=order[0]["id"], template_name="order_detail",
                            broadcast_name="order_detail", status="success", time_sent=datetime.utcnow())
    else:
        new_wt = wtmessages(order_id=order[0]["id"], template_name="order_detail",
                            broadcast_name="order_detail", status="failed", time_sent=datetime.utcnow())
    db.session.add(new_wt)
    db.session.commit()
    result["template_name"] = 'order_detail'
    result["parameteres"] = [{'name': 'order_id', 'value': str(order_id)}]
    return jsonify(result)


@app.route("/gen_payment_link/<string:order_id>")
def gen_payment_link(order_id):
    if not g.user:
        return redirect(url_for('login'))
    page = request.args.get('page', 0)
    o = wcapi.get("orders/"+order_id).json()
    payment_links = PaymentLinks.query.filter_by(order_id=o["id"]).all()
    wallet_payment = 0
    if len(o["fee_lines"]) > 0:
        for item in o["fee_lines"]:
            if "wallet" in item["name"].lower():
                wallet_payment = (-1)*float(item["total"])
    data = {
        "amount": (float(get_total_from_line_items(o["line_items"]))+float(o["shipping_total"])-wallet_payment-float(get_total_from_line_items(o["refunds"])*-1))*100,
        "receipt": "Leap "+str(o["id"])+"-"+str(len(payment_links)+1),
        "customer": {
            "name": o["shipping"]["first_name"] + " " + o["shipping"]["last_name"],
            "contact": o["billing"]["phone"]
        },
        "type": "link",
        "view_less": 1,
        "currency": "INR",
        "description": "Thank you for making a healthy and sustainable choice",
        "reminder_enable": False,
        "callback_url": "https://leapclub.in/",
        "callback_method": "get",
        "sms_notify": False,
        'email_notify': False
    }
    try:
        invoice = razorpay_client.invoice.create(data=data)
        status = "success"
        short_url = invoice['short_url']
        new_payment_link = PaymentLinks(order_id=o["id"], receipt=data["receipt"], payment_link_url=invoice['short_url'], contact=o["billing"]["phone"], name=data["customer"]['name'], created_at=invoice["created_at"], amount=data['amount'], status=status)
    except:
        status = "failed"
        short_url = ""
        new_payment_link = PaymentLinks(order_id=o["id"], receipt=data["receipt"], payment_link_url="", contact=o["billing"]["phone"], name=data["customer"]['name'], created_at="", amount=data['amount'], status=status)
    db.session.add(new_payment_link)
    db.session.commit()
    return jsonify({"result": status, 'payment':data, "short_url": short_url, "order_id": order_id})


@app.route("/razorpay", methods=["GET", "POST"])
def razorpay():
    if request.method == "GET":
        return "Plese Use POST Method..."
    e = request.get_json()
    if len(e)>0:
        if e["event"] == "invoice.paid":
            mobile = e['payload']['payment']['entity']['contact']
            order_id = e['payload']['order']['entity']['receipt'][5:].split("-")[0]
            invoice_id = e['payload']['invoice']['entity']['id']
            order = wcapi.get("orders/"+order_id)
            print(order, "ORDER.........................")
            if order.status_code == 200:
                order = order.json()
                name = order['billing']['first_name']
                vendor_name = ""
                vendor_t = 'any'
                for item in order["meta_data"]:
                    if item["key"] == "wos_vendor_data":
                        vendor_name = item["value"]["vendor_name"]
                    elif item["key"] == "_wc_acof_6":
                        vendor_name = item["value"]
                if vendor_name in vendor_type.keys():
                    vendor_t = vendor_type[vendor_name]
                update_order_status(order, invoice_id, wcapi_write)
                if order['status'] in ['tbd-unpaid', 'delivered-unpaid']:
                    msg = send_whatsapp_msg({'vendor_type': vendor_t, "c_name": name}, mobile, 'payment_received')
            return("Done")
        else:
            return "Payment.Paid"
    else:
        return "Please enter valid detail..."

@app.route("/new_customer", methods=['POST', 'GET'])
def new_customer():
    if request.method == "GET":
        return "Plese Use POST Method..."
    e = request.get_json()
    if e:
        print(e['meta_data'], "Meta Data.....")
        print(e, "JSON Data.....")
        print(request.headers)
        is_new = list(filter(lambda i: (i['key'] == 'wc_last_active'), e['meta_data']))
        if len(is_new)>0:
            digits_phone = ""
            name = e['first_name']
            for i in e['meta_data']:
                if i['key'] == 'digits_phone_no':
                    digits_phone = "+91" + i['value']
                    break
            # digits_phone = "919325837420"
            msg = send_whatsapp_msg({'vendor_type': "any", "c_name": name}, digits_phone, 'new-signup')
    return e

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
