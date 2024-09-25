from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Order(Base):
    __tablename__ = 'Order'

    Order_ID = Column(String(6), primary_key=True)
    Order_Date = Column(DateTime, nullable=False)
    Address_ID = Column(Integer, ForeignKey(
        'Address.Address_ID'), nullable=False)

    address = relationship("Address", back_populates="orders")
    order_details = relationship("OrderDetails", back_populates="order")

    def __init__(self, Order_ID: str, Order_Date: datetime, address: 'Address') -> None:
        self.Order_ID = Order_ID
        self.Order_Date = Order_Date
        self.address = address

    def add_order_detail(self, order_detail: 'OrderDetails') -> None:
        self.order_details.append(order_detail)

    def get_total_amount(self) -> Decimal:
        return sum(detail.get_subtotal() for detail in self.order_details)


class Product(Base):
    __tablename__ = 'Product'

    Product_Ean = Column(String(13), primary_key=True)
    Product = Column(String(255), nullable=False)
    Category = Column(String(50), nullable=True)
    Price_Each = Column(Numeric(10, 2), nullable=False)
    Cost_Price = Column(Numeric(10, 2), nullable=False)

    def __init__(self, Product_Ean: str, Product: str, Category: str, Price_Each: Decimal, Cost_Price: Decimal) -> None:
        self.Product_Ean = Product_Ean
        self.Product = Product
        self.Category = Category
        self.Price_Each = Price_Each
        self.Cost_Price = Cost_Price

    def get_profit_margin(self) -> Decimal:
        return self.Price_Each - self.Cost_Price


class OrderDetails(Base):
    __tablename__ = 'OrderDetails'

    Order_ID = Column(String(6), ForeignKey(
        'Order.Order_ID'), primary_key=True)
    Product_Ean = Column(String(13), ForeignKey(
        'Product.Product_Ean'), primary_key=True)
    Quantity_Ordered = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="order_details")
    product = relationship("Product")

    def __init__(self, order: Order, product: Product, Quantity_Ordered: int) -> None:
        self.order = order
        self.product = product
        self.Quantity_Ordered = Quantity_Ordered

    def get_subtotal(self) -> Decimal:
        return self.product.Price_Each * self.Quantity_Ordered


class Address(Base):
    __tablename__ = 'Address'

    Address_ID = Column(Integer, primary_key=True, autoincrement=True)
    Street_Number = Column(String(10), nullable=False)
    Street_Name = Column(String(100), nullable=False)
    City = Column(String(50), nullable=False)
    State = Column(String(2), nullable=False)
    ZIP_Code = Column(String(10), nullable=False)

    orders = relationship("Order", back_populates="address")

    def __init__(self, Street_Number: str, Street_Name: str, City: str, State: str, ZIP_Code: str) -> None:
        self.Street_Number = Street_Number
        self.Street_Name = Street_Name
        self.City = City
        self.State = State
        self.ZIP_Code = ZIP_Code

    def get_full_address(self) -> str:
        return f"{self.Street_Number} {self.Street_Name}, {self.City}, {self.State} {self.ZIP_Code}"
