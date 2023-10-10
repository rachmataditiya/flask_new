from random import randint
from app import db, Order, OrderDetail, Item, Package

def populate_db():
    # Create dummy data
    db.drop_all()
    db.create_all()

    for i in range(1, 11):
        new_order = Order(
            order_sn=f"210930KJDNF0{i}",
            buyer_user_id=randint(1000, 9999),
            buyer_username=f"dummy_user_{i}",
            create_time=randint(1600000000, 1700000000),
            currency="IDR",
            days_to_ship=randint(1, 7),
            total_amount=randint(1000, 9000),
            update_time=randint(1600000000, 1700000000)
        )
        db.session.add(new_order)

        new_order_detail = OrderDetail(
            checkout_shipping_carrier="Carrier_" + str(i),
            actual_shipping_fee=randint(100, 900),
            payment_method="Credit Card",
            recipient_name=f"Recipient_{i}",
            recipient_phone=f"12345678{i}",
            recipient_full_address=f"Address_{i}",
            order=new_order
        )
        db.session.add(new_order_detail)

        new_item = Item(
            item_id=randint(100000, 999999),
            item_name=f"Item_{i}",
            model_id=randint(1000, 9999),
            model_quantity_purchased=randint(1, 10),
            model_original_price=randint(1000, 9000),
            model_discounted_price=randint(500, 1000),
            weight=randint(100, 500),
            order_detail=new_order_detail
        )
        db.session.add(new_item)

        new_package = Package(
            package_number=f"PKG_{i}",
            logistics_status="Delivered",
            shipping_carrier="Carrier_" + str(i),
            order_detail=new_order_detail
        )
        db.session.add(new_package)

    db.session.commit()

if __name__ == '__main__':
    from app import app
    with app.app_context():
        populate_db()
