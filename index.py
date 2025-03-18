from flask import Flask, render_template, request, redirect, url_for, session
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'BeBrA'

cart = []

def get_books():
    response = requests.get("http://127.0.0.1:8000/books")
    if response.status_code == 200:
        return response.json()
    
@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route("/auth/reader", methods=["POST"])
def auth():
    if request.method == "POST":
        name = request.form['name']
        password = request.form['password']

        response = requests.post(f"http://127.0.0.1:8000/api/reader/SignIn?name={name}&password={password}")
        if response.status_code == 200:
            session['user'] = name
            return redirect(url_for('index'))
    return "Ошибка авторизации", 401

@app.route("/auth")
def index_auth():
    return render_template("auth.html")

@app.route("/", methods=["GET", "POST"])
def index():
    books = get_books()
    user = session.get('user')
    return render_template("index.html", user=user, books=books)

@app.route("/cart", methods=["GET"])
def show_cart():
    user = session.get('user')  # Получаем имя пользователя из сессии
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    return render_template("cart.html", user=user, cart_items=cart, total_price=total_price)

@app.route("/add_to_cart/<int:book_id>", methods=["POST"])
def add_to_cart(book_id):
    books = get_books()
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        cart_item = next((item for item in cart if item['id'] == book_id), None)
        if cart_item:
            cart_item['quantity'] += 1
        else:
            cart.append({
                'id': book_id,
                'name': book['name'],
                'author': book['author'],
                'price': book['price'],
                'quantity': 1
            })
    return redirect(url_for('show_cart'))

@app.route("/remove_from_cart/<int:book_id>", methods=["POST"])
def remove_from_cart(book_id):
    global cart
    cart = [item for item in cart if item['id'] != book_id]
    return redirect(url_for('show_cart'))

@app.route("/checkout", methods=["POST"])
def checkout():
    global cart
    user = session.get('user')  # Получаем имя пользователя из сессии
    if cart and user:
        for item in cart:
            today = datetime.today()
            plane_date = today + timedelta(weeks=2)

            json_data = {
                "book": item['name'],
                "reader": user,  # Используем имя пользователя из сессии
                "drop_date": today.date().isoformat(),
                "plan_get_date": plane_date.date().isoformat(),
                "real_get_date": None,
                "book_lost": False,
                "summ": item['price'] * item['quantity'],
                "date_summ": today.date().isoformat()
            }

            response = requests.post("http://127.0.0.1:8000/inssue", json=json_data)
            if response.status_code != 200:
                return f"Ошибка при оформлении заказа для книги '{item['name']}'", 500

        cart = []
        return redirect(url_for('show_cart'))
    return redirect(url_for('show_cart'))

if __name__ == "__main__":
    app.run(debug=True)
