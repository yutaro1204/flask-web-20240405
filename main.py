from flask import Flask, render_template, session, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from typing import List
import logging
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email
import bcrypt

app = Flask(__name__)

# ログ設定
log_handler = logging.FileHandler('server.log')
log_handler.setLevel(logging.DEBUG)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(log_handler)
werkzeug = logging.getLogger('werkzeug')
werkzeug.setLevel(logging.DEBUG)
werkzeug.addHandler(log_handler)

# ここでは公式ドキュメントにもある secret_key をそのまま使って公開していますが、
# 実際の運用では secret_key は公開しないでください
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:postgres@postgres/postgres'
db = SQLAlchemy()
db.init_app(app)

migrate = Migrate()
migrate.init_app(app, db)

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

class SignUpForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(min=1, max=20)])
    email = StringField('email', validators=[InputRequired(), Email()])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=20)])

class SignInForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email()])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=20)])

class SignOutForm(FlaskForm):
    pass

@app.route("/sign_up", methods=('GET', 'POST'))
def sign_up():
    form = SignUpForm(request.form)
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        salt = bcrypt.gensalt(rounds=12, prefix=b'2b')
        hashpw = bcrypt.hashpw(password.encode('utf8'), salt)
        user = User(name=name, email=email, password=hashpw.decode('utf8'))
        db.session.add(user)
        db.session.commit()
        session['email'] = user.email
        return redirect(url_for('products'))
    return render_template('sign_up.html', form=form)

@app.route("/sign_in", methods=('GET', 'POST'))
def sign_in():
    form = SignInForm(request.form)
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one()
        if bcrypt.checkpw(password.encode('utf8'), user.password.encode('utf8')):
            session['email'] = user.email
            return redirect(url_for('products'))
    return render_template('sign_in.html', form=form)

@app.post("/sign_out")
def sign_out():
    if 'email' in session:
        session.pop('email', None)
        return redirect(url_for('sign_in'))
    form = SignOutForm(request.form)
    products = db.session.query(Product).all()
    return render_template('products.html', products=products, form=form)

@app.route("/products")
def products():
    if 'email' in session:
        form = SignOutForm(request.form)
        products = db.session.query(Product).all()
        return render_template('products.html', products=products, form=form)
    return redirect(url_for('sign_in'))

@app.route("/transactions")
def transactions():
    if 'email' in session:
        purchase_transactions = db.session.query(PurchaseTransaction).all()
        return render_template('transactions.html', transactions=purchase_transactions)
    return redirect(url_for('sign_in'))

@app.route("/products/<product_id>")
def product(product_id):
    if 'email' in session:
        product = db.session.execute(db.select(Product).filter_by(id=product_id)).scalar_one()
        in_cart = False
        if 'cart' in session and product_id in session['cart']:
            in_cart = True
        return render_template('products.html', product=product, in_cart=in_cart)
    return redirect(url_for('sign_in'))

@app.post("/purchase/<product_id>")
def purchase(product_id):
    if 'email' in session:
        user = db.session.execute(db.select(User).filter_by(id=2)).scalar_one()
        product = db.session.execute(db.select(Product).filter_by(id=product_id)).scalar_one()
        if user and product:
            purchase_transaction = PurchaseTransaction(user=user, product=product)
            db.session.add(purchase_transaction)
            db.session.commit()
        return render_template('success.html', product=product)
    return redirect(url_for('sign_in'))

@app.post('/add_cart')
def add_cart():
    if 'email' in session:
        cart_items = []
        if 'cart' in session:
            cart_items = session['cart']
        if request.form['product_id'] not in cart_items:
            cart_items.append(request.form['product_id'])
        session['cart'] = cart_items
        return redirect(url_for('cart'))
    return redirect(url_for('sign_in'))

@app.post('/remove_cart')
def remove_cart():
    if 'email' in session:
        if 'cart' in session:
            cart_items = session['cart']
            cart_items.remove(request.form['product_id'])
            session['cart'] = cart_items
        return redirect(url_for('cart'))
    return redirect(url_for('sign_in'))

@app.route("/cart")
def cart():
    if 'email' in session:
        products = []
        if 'cart' in session:
            cart_items = session['cart']
            app.logger.info(cart_items)
            products = db.session.query(Product).filter(Product.id.in_(cart_items)).all()
        return render_template('cart.html', products=products)
    return redirect(url_for('sign_in'))
