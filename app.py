from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig
from sshtunnel import SSHTunnelForwarder
from woocommerce import API
from sqlalchemy.dialects.postgresql import UUID
from custom import filter_orders, list_order_items, list_order_refunds, list_only_refunds
from flask_datepicker import datepicker
from werkzeug.datastructures import ImmutableMultiDict
import uuid
import datetime
import pprint


app = Flask(__name__, instance_relative_config=True)
datepicker(app)

app.config.from_object(DevelopmentConfig)
db = SQLAlchemy(app)
wcapi = API(
    url="http://box2364.temp.domains/~leapclub/",
    consumer_key="ck_785fefd21aa061e99511b6fe01a69671aa289100",
    consumer_secret="cs_35e700a4c2f1b325470f5f64d676608a3e892c6d",
    version="wc/v3"
)


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow())
    date_modified = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow())
    total = db.Column(db.Float)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    city = db.Column(db.String)
    phone_number = db.Column(db.String)
    address = db.Column(db.String)
    address2 = db.Column(db.String)
    payment_method = db.Column(db.String)
    date_paid = db.Column(db.String)
    whatsapp_message = db.Column(db.Text)


@app.route("/", methods=["GET", "POST"])
def webhooks():
    if request.method == "GET":
        page = request.args.get("page", 1, type=int)
        orders = Orders.query.paginate(page=page, per_page=50)
        return render_template("orders.html", orders=orders)
    else:
        data = request.get_json()
        if data != []:
            c_msg = "Hi - Your order is on the way.\n\nPlease check whether you are satisfied with the quality of items when you receive them. Feel free to Whatsapp me here if you have any queries.\n\nI hope you will like them. Looking forward to your feedback. :)\n\n\nHere are the order details:\n\n"
            c_msg = c_msg + list_order_items_without_refunds(
                data["line_items"], o["id"]) + "*Total Amount: "+data["total"]+"*"
            order = Orders(
                id=data["id"],
                date_created=data["date_created"],
                date_modified=data["date_modified"],
                total=data["total"],
                firstname=data["billing"]["first_name"],
                lastname=data["billing"]["last_name"],
                city=data["billing"]["city"],
                phone_number=data["billing"]["phone"],
                address=data["billing"]["address_1"],
                address2=data["billing"]["address_2"],
                payment_method=data["payment_method"],
                date_paid=data["date_paid"],
                whatsapp_message=c_msg
            )
            db.session.add(order)
            db.session.commit()
            return {"status": "Success..."}
        else:
            return {"data": "error"}


@app.route("/orders")
def woocom_orders():
    args = request.args.to_dict(flat=False)
    new_ids = []
    if "order_id" in args:
        for i in args["order_id"]:
            new_ids.append(int(i))
    args["order_id"] = new_ids
    orders = wcapi.get("orders").json()
    f_orders = filter_orders(orders, args)
    for o in f_orders:
        order_refunds = []
        if len(o["refunds"]) > 0:
            order_refunds = wcapi.get("orders/"+str(o["id"])+"/refunds").json()
        c_msg = "Here are the order details:\n\n" + \
            list_order_items(o["line_items"], order_refunds) + \
            "*Total Amount: "+o["total"]+"*\n\n"
        if len(o["refunds"]) > 0:
            c_msg = c_msg+ \
                list_order_refunds(order_refunds)+list_only_refunds(order_refunds)
        s_msg = ("Order ID: "+str(o["id"])
                 + "\n\nName: "+o["billing"]["first_name"] +
                 " "+o["billing"]["last_name"]
                 + "\nMobile: "+o["billing"]["phone"]
                 + "\n\nAddress: "+o["billing"]["address_1"] +
                 ", "+o["billing"]["address_2"]
                 + "\n\nTotal Amount: "+str(o["total"])
                 + "\n\n"+list_order_items(o["line_items"], order_refunds)
                 + "Payment Status: Paid To LeapClub.")
        o["c_msg"] = c_msg
        o["s_msg"] = s_msg
    if type(orders) == list:
        for o in orders:
            refunds = 0
            for r in o["refunds"]:
                refunds = refunds + float(r["total"])
            o["total_refunds"] = refunds*-1
            o["total"] = float(o["total"])
        return render_template("woocom_orders.html", orders=f_orders, query=args)
    else:
        return orders


if __name__ == "__main__":
    db.create_all()
    app.run()
