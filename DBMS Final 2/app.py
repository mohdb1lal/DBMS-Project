from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from bson import ObjectId  # Import ObjectId
import os


app = Flask(__name__)

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
users_collection = db["users"]

# Define the folder where uploaded product images will be stored
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure a secret key for session management
# Replace with a strong, random secret key
app.secret_key = '123'


@app.route('/')
def login_selection():
    return render_template('login_selection.html')


@app.route('/redirect_login', methods=['POST'])
def redirect_login():
    role = request.form['role']
    if role == 'admin':
        return redirect(url_for('admin_login'))
    elif role == 'customer':
        return redirect(url_for('customer_login'))
    else:
        return "Invalid role selected."


@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')


@app.route('/signup_admin', methods=['GET', 'POST'])
def signup_admin():
    if request.method == 'POST':
        username = request.form['username']
        role = 'admin'

        existing_user = users_collection.find_one(
            {"username": username, "role": "admin"})

        if existing_user:
            return "User already exists"
        else:
            new_user = {"username": username, "role": 'admin'}
            users_collection.insert_one(new_user)
            return "Admin sign-up successful"

    return render_template('signup_admin.html')


@app.route('/customer_login')
def customer_login():
    return render_template('customer_login.html')


@app.route('/signup_customer', methods=['GET', 'POST'])
def signup_customer():
    if request.method == 'POST':
        username = request.form['username']
        role = 'customer'

        existing_user = users_collection.find_one(
            {"username": username, "role": 'customer'})

        if existing_user:
            return "User already exists"
        else:
            new_user = {"username": username, "role": 'customer'}
            users_collection.insert_one(new_user)
            return "Customer sign-up successful"

    return render_template('signup_customer.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']

        user = users_collection.find_one({"username": username, "role": role})

        if user:
            # Store user details in session
            session['username'] = username
            session['role'] = role

            if role == "admin":
                return redirect(url_for('admin_home'))
            else:
                return redirect(url_for('customer_home'))
        else:
            return "Login failed"

    return render_template('login.html')


@app.route('/admin_home')
def admin_home():
    # Check if the user is logged in
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    # Retrieve the list of customers from the database
    customers = users_collection.find({"role": "customer"})

    return render_template('admin_home.html', users=customers)


@app.route('/manage_product', methods=['GET', 'POST'])
def manage_product():
    if request.method == 'GET':
        # Add your code to retrieve and display products
        products = db.products.find()
        return render_template('manage_product.html', products=products)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'delete':
            # Perform deletion logic using the product ID
            product_id = request.form.get('product_id')
            db.products.delete_one({"_id": ObjectId(product_id)})
            # Redirect to the product management page or render a refreshed view
            return redirect(url_for('manage_product'))

        if action == 'update':
            # Perform update logic using the product ID and form data
            product_id = request.form.get('product_id')
            updated_product_data = {
                "name": request.form['updated_product_name'],
                "quantity": int(request.form['updated_quantity']),
                "price": float(request.form['updated_price']),
                "category": request.form['updated_category'],
                # Update image path or handle new image upload
            }
            db.products.update_one({"_id": ObjectId(product_id)}, {
                                   "$set": updated_product_data})
            # Redirect to the product management page or render a refreshed view
            return redirect(url_for('manage_product'))

    return render_template('manage_product.html')


@app.route('/customer_home')
def customer_home():
    # Check if the user is logged in
    if 'username' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))

    # Retrieve product information from the database
    products = db.products.find()

    return render_template('customer_home.html', products=products)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))


@app.route('/add_product', methods=['POST'])
def add_product():
    # Check if the user is logged in as an admin
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        product_name = request.form['product_name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        category = request.form['category']

        # Handle image file upload
        if 'image' in request.files:
            image_file = request.files['image']

            if image_file.filename != '':
                # Secure the filename to prevent path traversal
                filename = secure_filename(image_file.filename)
                # Save the image to the specified folder
                image_path = os.path.join(
                    app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)
            else:
                # Provide a default image path if no image is uploaded
                image_path = 'static/images/default.jpg'

            # Add the product to the database
            product = {
                "name": product_name,
                "quantity": quantity,
                "price": price,
                "category": category,
                "image": image_path
            }
            db.products.insert_one(product)

    return redirect(url_for('admin_home'))


if __name__ == '__main__':
    app.run(debug=True)
