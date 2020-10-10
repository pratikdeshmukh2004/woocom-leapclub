from flask import Flask, render_template, request, url_for, redirect, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sshtunnel import SSHTunnelForwarder
from woocommerce import API
from sqlalchemy.dialects.postgresql import UUID
from custom import filter_orders, list_order_items, list_order_refunds, list_only_refunds, get_totals, get_params, get_orders_with_messages, list_order_items_csv
from flask_datepicker import datepicker
from werkzeug.datastructures import ImmutableMultiDict
from datetime import datetime
import uuid
import json
import requests
import csv
import os


app = Flask(__name__, instance_relative_config=True)
datepicker(app)

app.config.from_pyfile("config.py")

# db = SQLAlchemy(app)
wcapi = API(
    url=app.config["WOOCOMMERCE_API_URL"],
    consumer_key=app.config["WOOCOMMERCE_API_CUSTOMER_KEY"],
    consumer_secret=app.config["WOOCOMMERCE_API_CUSTOMER_SECRET"],
    version="wc/v3"
)


# class Orders(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date_created = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow())
#     date_modified = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow())
#     total = db.Column(db.Float)
#     firstname = db.Column(db.String)
#     lastname = db.Column(db.String)
#     city = db.Column(db.String)
#     phone_number = db.Column(db.String)
#     address = db.Column(db.String)
#     address2 = db.Column(db.String)
#     payment_method = db.Column(db.String)
#     date_paid = db.Column(db.String)
#     whatsapp_message = db.Column(db.Text)


# @app.route("/", methods=["GET", "POST"])
# def webhooks():
#     if request.method == "GET":
#         page = request.args.get("page", 1, type=int)
#         orders = Orders.query.paginate(page=page, per_page=50)
#         return render_template("orders.html", orders=orders)
#     else:
#         data = request.get_json()
#         if data != []:
#             c_msg = "Hi - Your order is on the way.\n\nPlease check whether you are satisfied with the quality of items when you receive them. Feel free to Whatsapp me here if you have any queries.\n\nI hope you will like them. Looking forward to your feedback. :)\n\n\nHere are the order details:\n\n"
#             c_msg = c_msg + list_order_items_without_refunds(
#                 data["line_items"], o["id"]) + "*Total Amount: "+data["total"]+"*"
#             order = Orders(
#                 id=data["id"],
#                 date_created=data["date_created"],
#                 date_modified=data["date_modified"],
#                 total=data["total"],
#                 firstname=data["billing"]["first_name"],
#                 lastname=data["billing"]["last_name"],
#                 city=data["billing"]["city"],
#                 phone_number=data["billing"]["phone"],
#                 address=data["billing"]["address_1"],
#                 address2=data["billing"]["address_2"],
#                 payment_method=data["payment_method"],
#                 date_paid=data["date_paid"],
#                 whatsapp_message=c_msg
#             )
#             db.session.add(order)
#             db.session.commit()
#             return {"status": "Success..."}
#         else:
#             return {"data": "error"}
@app.route("/", methods=["GET", "POST"])
def webhooks():
    return redirect(url_for("woocom_orders"))


@app.route("/orders")
def woocom_orders():
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
    orders = wcapi.get("orders", params=params).json()
    f_orders = filter_orders(orders, args)
    orders = get_orders_with_messages(f_orders, wcapi)
    for o in orders:
        refunds = 0
        for r in o["refunds"]:
            refunds = refunds + float(r["total"])
        o["total_refunds"] = refunds*-1
        o["total"] = float(o["total"])
    return render_template("woocom_orders.html", orders=orders, query=args, nav_active=params["status"], is_w=is_w, w_status=w_status)


def send_whatsapp_msg(order):
    url = "https://live-server-54.wati.io/api/v1/sendTemplateMessage/" + \
        order["billing"]["phone"]

    payload = {
        "template_name": "order_intro_2308",
        "broadcast_name": "order_ack",
        "parameters": "[{'name':'name', 'value':'"+order["billing"]["first_name"]+" " + order["billing"]["last_name"]+"'},{'name':'manager', 'value':'Pratik'}]"
    }
    headers = {
        'Authorization': app.config["WATI_AUTHORIZATION"],
        'Content-Type': 'application/json',
        'Cookie': '__cfduid=d4f3524497b15c8e8434c2cb0cf4d47601602064478'
    }

    response = requests.request(
        "POST", url, headers=headers, data=json.dumps(payload))

    return json.loads(response.text.encode('utf8'))


@app.route("/send_whatsapp_msg/<string:order_id>")
def send_whatsapp(order_id):
    args = request.args.to_dict(flat=False)
    if "status" in args:
        nav_active = args["status"][0]
    else:
        nav_active = "any"
    order = wcapi.get("orders/"+order_id).json()
    result = send_whatsapp_msg(order)
    if result["result"] == "success":
        w_status = "Message Sent."
    else:
        w_status = "Message Not Sent."
    if nav_active != "any":
        return redirect(url_for("woocom_orders", w_status=w_status, status=nav_active))
    else:
        return redirect(url_for("woocom_orders", w_status=w_status))


def get_csv_from_orders(orders):
    f = open("sample.csv", "w+")
    writer = csv.DictWriter(
        f, fieldnames=["Order ID", "Customer Detail", "Total Amount", "Order Details", "Comments"])
    writer.writeheader()
    for o in orders:
        refunds = []
        if len(o["refunds"])>0:
            refunds = wcapi.get("orders/"+str(o["id"])+"/refunds").json()
        writer.writerow({
            "Order ID": o["id"],
            "Customer Detail": "Name: "+o["billing"]["first_name"]+" "+o["billing"]["last_name"]+"\nMobile: "+o["billing"]["phone"]+"\nAddress: "+o["billing"]["address_1"]+", "+o["billing"]["address_2"],
            "Total Amount": get_totals(o["total"], refunds),
            "Order Details": list_order_items_csv(o["line_items"], refunds),
            "Comments": "Payment Status: Paid To Leap"
        })
        writer.writerow({})
    f.close()
    f = open("sample.csv", "r")
    result = f.read()
    os.remove("sample.csv")
    return result


@app.route('/csv', methods=["POST"])
def download_csv():
    data = request.form.to_dict(flat=False)
    orders = wcapi.get("orders", params=get_params(data)).json()
    csv_text = get_csv_from_orders(orders)
    filename = str(datetime.utcnow())+"-" + data["status"][0]+".csv"
    response = make_response(csv_text)
    cd = 'attachment; filename='+filename
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'

    return response


if __name__ == "__main__":
    # db.create_all()
    app.run()
