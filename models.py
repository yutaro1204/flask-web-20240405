from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from typing import List
from . import db

class Product(db.Model):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(20), nullable=False)
    price: Mapped[int] = mapped_column(db.Integer, nullable=False)
    purchase_transactions: Mapped[List['PurchaseTransaction']] = db.relationship(back_populates='product', cascade='all, delete-orphan')
    created: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    def __repr__(self) -> str:
        return f'Product(id={self.id!r}, name={self.name!r}, price={self.price!r}, created={self.created!r}, updated={self.updated!r})'

class User(db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)
    purchase_transactions: Mapped[List['PurchaseTransaction']] = db.relationship(back_populates='user', cascade='all, delete-orphan')
    created: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    def __repr__(self) -> str:
        return f'User(id={self.id!r}, name={self.name!r}, email={self.email!r}, password={self.password!r}, created={self.created!r}, updated={self.updated!r})'

class PurchaseTransaction(db.Model):
    __tablename__ = 'purchase_transactions'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(db.ForeignKey('products.id'))
    user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
    product: Mapped['Product'] = db.relationship(back_populates='purchase_transactions')
    user: Mapped['User'] = db.relationship(back_populates='purchase_transactions')
    created: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    def __repr__(self) -> str:
        return f'PurchaseTransaction(id={self.id!r}, product_id={self.product_id!r}, user_id={self.user_id!r} created={self.created!r}, updated={self.updated!r})'
