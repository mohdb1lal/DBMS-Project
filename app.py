from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
users_collection = db["users"]


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # Get the selected role

        user = users_collection.find_one(
            {"username": username, "password": password, "role": role})
        if user:
            if role == "admin":
                # Redirect to admin home
                return redirect(url_for('admin_home'))
            else:
                # Redirect to customer home
                return redirect(url_for('customer_home'))
        else:
            return "Login failed"

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # Get the selected role

        existing_user = users_collection.find_one(
            {"username": username, "role": role})

        if existing_user:
            return "User already exists"
        else:
            new_user = {"username": username,
                        "password": password, "role": role}
            users_collection.insert_one(new_user)
            return "Sign-up successful"

    return render_template('signup.html')


@app.route('/admin_home')
def admin_home():
    # Retrieve the list of customers from the database
    customers = users_collection.find({"role": "customer"})

    return render_template('admin_home.html', users=customers)


@app.route('/customer_home')
def customer_home():
    # Retrieve product information from the database
    products = db.products.find()

    return render_template('customer_home.html', products=products)


@app.route('/logout', methods=['POST'])
def logout():
    # Perform logout actions, e.g., clearing session or cookies

    # Redirect to the login page
    return redirect(url_for('login'))


@app.route('/add_product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        category = request.form['category']

        # Add the product to the database (use your MongoDB code here)
        product = {
            "name": product_name,
            "quantity": quantity,
            "price": price,
            "category": category
        }
        # Insert the product into your MongoDB collection
        db.products.insert_one(product)

    return render_template('admin_home.html')

# Route to display products for customers


if __name__ == '__main__':
    app.run(debug=True)
