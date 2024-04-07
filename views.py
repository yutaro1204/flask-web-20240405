from flask import Blueprint, render_template, session, request, redirect, url_for
import bcrypt
from werkzeug.exceptions import Unauthorized, NotFound, InternalServerError
from .forms import SignUpForm, SignInForm, SignOutForm
from .models import User, Product, PurchaseTransaction
from . import db

bp = Blueprint("views", __name__)

@bp.route("/sign_up", methods=('GET', 'POST'))
def sign_up():
    try:
        if 'email' in session:
            return redirect(url_for('views.products'))

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
            return redirect(url_for('views.products'))

        return render_template('sign_up.html', form=form)
    except Exception as e:
        return render_template('sign_up.html', form=form, e=e)

@bp.route("/sign_in", methods=('GET', 'POST'))
def sign_in():
    try:
        if 'email' in session:
            return redirect(url_for('views.products'))

        form = SignInForm(request.form)
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one()

            if user is None:
                raise Unauthorized

            if bcrypt.checkpw(password.encode('utf8'), user.password.encode('utf8')):
                session['email'] = user.email
                return redirect(url_for('views.products'))
            else:
                raise Unauthorized

        return render_template('sign_in.html', form=form)
    except Exception as e:
        return render_template('sign_in.html', form=form, e=e)

@bp.post("/sign_out")
def sign_out():
    try:
        if 'email' in session:
            session.pop('email', None)
            return redirect(url_for('views.sign_in'))

        form = SignOutForm(request.form)
        products = db.session.query(Product).all()
        return render_template('products.html', products=products, form=form)
    except Exception as e:
        raise InternalServerError from e

@bp.route("/products")
def products():
    if 'email' in session:
        form = SignOutForm(request.form)
        products = db.session.query(Product).all()
        return render_template('products.html', products=products, form=form)

    return redirect(url_for('views.sign_in'))

@bp.route("/transactions")
def transactions():
    if 'email' in session:
        purchase_transactions = db.session.query(PurchaseTransaction).all()
        return render_template('transactions.html', transactions=purchase_transactions)

    return redirect(url_for('views.sign_in'))

@bp.route("/products/<product_id>")
def product(product_id):
    if 'email' in session:
        product = db.session.execute(db.select(Product).filter_by(id=product_id)).scalar_one()

        if product is None:
            raise NotFound

        in_cart = False
        if 'cart' in session and product_id in session['cart']:
            in_cart = True

        return render_template('products.html', product=product, in_cart=in_cart)

    return redirect(url_for('views.sign_in'))

@bp.post("/purchase/<product_id>")
def purchase(product_id):
    try:
        if 'email' in session:
            user = db.session.execute(db.select(User).filter_by(id=2)).scalar_one()
            product = db.session.execute(db.select(Product).filter_by(id=product_id)).scalar_one()

            if user and product:
                purchase_transaction = PurchaseTransaction(user=user, product=product)
                db.session.add(purchase_transaction)
                db.session.commit()
            else:
                raise NotFound

            return render_template('success.html', product=product)

        return redirect(url_for('views.sign_in'))
    except Exception as e:
        raise InternalServerError from e

@bp.post('/add_cart')
def add_cart():
    try:
        if 'email' in session:
            cart_items = []

            if 'cart' in session:
                cart_items = session['cart']

            if request.form['product_id'] not in cart_items:
                cart_items.append(request.form['product_id'])

            session['cart'] = cart_items
            return redirect(url_for('views.cart'))

        return redirect(url_for('views.sign_in'))
    except Exception as e:
        raise InternalServerError from e

@bp.post('/remove_cart')
def remove_cart():
    try:
        if 'email' in session:

            if 'cart' in session:
                cart_items = session['cart']
                cart_items.remove(request.form['product_id'])
                session['cart'] = cart_items

            return redirect(url_for('views.cart'))

        return redirect(url_for('views.sign_in'))
    except Exception as e:
        raise InternalServerError from e

@bp.route("/cart")
def cart():
    if 'email' in session:
        products = []

        if 'cart' in session:
            cart_items = session['cart']
            products = db.session.query(Product).filter(Product.id.in_(cart_items)).all()

        return render_template('cart.html', products=products)

    return redirect(url_for('views.sign_in'))
