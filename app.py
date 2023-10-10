from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_sn = db.Column(db.String(50), unique=True, nullable=False)
    buyer_user_id = db.Column(db.Integer)
    buyer_username = db.Column(db.String(50))
    create_time = db.Column(db.Integer)
    currency = db.Column(db.String(10))
    days_to_ship = db.Column(db.Integer)
    total_amount = db.Column(db.Float)
    update_time = db.Column(db.Integer)

    details = db.relationship('OrderDetail', back_populates='order', uselist=False)

class OrderDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    checkout_shipping_carrier = db.Column(db.String(100))
    actual_shipping_fee = db.Column(db.Float)
    payment_method = db.Column(db.String(50))
    recipient_name = db.Column(db.String(100))
    recipient_phone = db.Column(db.String(20))
    recipient_full_address = db.Column(db.String(200))
    
    order = db.relationship('Order', back_populates='details')
    items = db.relationship('Item', back_populates='order_detail')
    packages = db.relationship('Package', back_populates='order_detail')

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_detail_id = db.Column(db.Integer, db.ForeignKey('order_detail.id'), nullable=False)
    item_id = db.Column(db.Integer)
    item_name = db.Column(db.String(100))
    model_id = db.Column(db.Integer)
    model_quantity_purchased = db.Column(db.Integer)
    model_original_price = db.Column(db.Float)
    model_discounted_price = db.Column(db.Float)
    weight = db.Column(db.Float)

    order_detail = db.relationship('OrderDetail', back_populates='items')

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_detail_id = db.Column(db.Integer, db.ForeignKey('order_detail.id'), nullable=False)
    package_number = db.Column(db.String(50))
    logistics_status = db.Column(db.String(50))
    shipping_carrier = db.Column(db.String(50))
    
    order_detail = db.relationship('OrderDetail', back_populates='packages')

@app.route('/api/v2/order/get_order_detail', methods=['GET'])
def get_order_detail():
    order_sn_list = request.args.get('order_sn_list')
    if not order_sn_list:
        return jsonify({"error": "Parameter order_sn_list is required"}), 400

    order_sn_array = order_sn_list.split(',')

    if len(order_sn_array) < 1 or len(order_sn_array) > 50:
        return jsonify({"error": "Number of order_sn should be between 1 and 50"}), 400

    orders = Order.query.filter(Order.order_sn.in_(order_sn_array)).all()
    order_list = []

    for order in orders:
        order_details = OrderDetail.query.filter_by(order_id=order.id).first()
        items = Item.query.filter_by(order_detail_id=order_details.id).all()
        packages = Package.query.filter_by(order_detail_id=order_details.id).all()

        # Construct the detailed order information
        detailed_order = {
            'checkout_shipping_carrier': order_details.checkout_shipping_carrier,
            'actual_shipping_fee': order_details.actual_shipping_fee,
            'buyer_user_id': order.buyer_user_id,
            'buyer_username': order.buyer_username,
            'create_time': order.create_time,
            'currency': order.currency,
            'days_to_ship': order.days_to_ship,
            'total_amount': order.total_amount,
            'update_time': order.update_time,
            'payment_method': order_details.payment_method,
            'recipient_name': order_details.recipient_name,
            'recipient_phone': order_details.recipient_phone,
            'recipient_full_address': order_details.recipient_full_address,
            'item_list': [{'item_id': item.item_id, 'item_name': item.item_name, 'model_id': item.model_id} for item in items],
            'package_list': [{'package_number': package.package_number, 'logistics_status': package.logistics_status, 'shipping_carrier': package.shipping_carrier} for package in packages]
        }

        order_list.append(detailed_order)

    response = {
        'error': '',
        'message': '',
        'response': {
            'order_list': order_list
        },
        'request_id': '971b45d6a002bfc680019320c9a685a0'
    }

    return jsonify(response)


@app.route('/api/v2/order/get_order_list', methods=['GET'])
def get_order_list():
    orders = Order.query.limit(10).all()
    order_list = [{"order_sn": order.order_sn} for order in orders]
    response = {
        "error": "",
        "message": "",
        "response": {
            "more": True,
            "next_cursor": "20",
            "order_list": order_list
        },
        "request_id": "b937c04e554847789cbf3fe33a0ad5f1"
    }
    return jsonify(response)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
