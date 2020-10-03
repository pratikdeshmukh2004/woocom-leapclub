from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig
from sshtunnel import SSHTunnelForwarder
from woocommerce import API
from sqlalchemy.dialects.postgresql import UUID
import uuid, datetime

app = Flask(__name__, instance_relative_config=True)

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
    firstname= db.Column(db.String)
    lastname= db.Column(db.String)
    city = db.Column(db.String)
    phone_number = db.Column(db.String)
    address = db.Column(db.String)
    address2 = db.Column(db.String)
    payment_method = db.Column(db.String)
    date_paid = db.Column(db.String)
    whatsapp_message = db.Column(db.Text)

def list_order_items(order_items):
    msg = ""
    for order_item in order_items:
        msg = (
                msg
                + order_item["name"]
                +" x "
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
            c_msg = c_msg + list_order_items(data["line_items"])+ "*Total Amount: "+data["total"]+"*"
            order = Orders(
                id = data["id"],
                date_created = data["date_created"],
                date_modified = data["date_modified"],
                total = data["total"],
                firstname = data["billing"]["first_name"],
                lastname = data["billing"]["last_name"],
                city = data["billing"]["city"],
                phone_number = data["billing"]["phone"],
                address = data["billing"]["address_1"],
                address2 = data["billing"]["address_2"],
                payment_method = data["payment_method"],
                date_paid = data["date_paid"],
                whatsapp_message = c_msg
            )
            db.session.add(order)
            db.session.commit()
            return {"status": "Success..."}
        else:
            return {"data": "error"}

if __name__ == "__main__":
    db.create_all()
    app.run()
