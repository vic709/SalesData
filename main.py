import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from typing import List
from datetime import datetime
from urllib.parse import quote_plus

# 假設這些是我們之前定義的SQLAlchemy模型
from SysClass import Base, Order, Product, OrderDetails, Address


def parse_address(address_string: str) -> Address:
    parts = address_string.split(',')
    street_info = parts[0].split(' ', 1)
    state_info = parts[2].strip().split(' ')
    return Address(
        Street_Number=street_info[0],
        Street_Name=street_info[1:],
        City=parts[1].strip(),
        State=state_info[0],
        ZIP_Code=state_info[1]
    )


def read_from_excel(file_path: str, session) -> List[Order]:
    df = pd.read_excel(file_path)
    orders = []
    for _, row in df.iterrows():
        address = parse_address(row["Purchase_Address"])
        order = Order(
            Order_ID=row['Order_ID'],
            Order_Date=pd.to_datetime(row['Order_Date']),
            address=address
        )
        product = session.query(Product).filter_by(
            Product_Ean=row['Product_Ean']).first()
        if not product:
            product = Product(
                Product_Ean=row['Product_Ean'],
                Product=row['Product'],
                Category=row['Categorie'],
                Price_Each=Decimal(str(row['Price_Each'])),
                Cost_Price=Decimal(str(row['Cost_Price']))
            )
            session.add(product)

        order_detail = OrderDetails(
            order=order,
            product=product,
            Quantity_Ordered=int(row['Quantity_Ordered'])
        )
        order.add_order_detail(order_detail)
        orders.append(order)
    return orders


def write_to_database(orders: List[Order], session):
    try:
        for order in orders:
            session.add(order)
        session.commit()
        print("數據成功寫入數據庫。")
    except Exception as e:
        session.rollback()
        print(f"寫入數據時發生錯誤: {e}")


if __name__ == "__main__":
    password = quote_plus("Saa123!@#")
    username = "saa"
    host = "192.168.0.117"  # 或使用 127.0.0.1
    database = "Test_mysql"

    engine = create_engine(
        f'mysql+pymysql://{username}:{password}@{host}/{database}')

    # 創建所有定義的表（如果它們還不存在）
    Base.metadata.create_all(engine)

    # 創建會話
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 讀取Excel文件並創建訂單對象
        orders = read_from_excel('./sales_data.xlsx', session)

        # 將訂單寫入數據庫
        write_to_database(orders, session)

        # 打印一些信息
        if orders:
            print(f"訂單總金額: ${orders[0].get_total_amount()}")
            print(f"第一個商品小計: ${orders[0].order_details[0].get_subtotal()}")
            print(f"第一個商品利潤: ${
                  orders[0].order_details[0].product.get_profit_margin()}")
        else:
            print("沒有讀取到訂單數據")

    finally:
        # 關閉會話
        session.close()
