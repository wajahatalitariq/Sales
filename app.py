from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json
import uuid
import qrcode
from io import BytesIO

app = Flask(__name__, static_folder="app/static", template_folder="app/templates")
app.secret_key = 'salestracker2023'
CORS(app)

# Database setup
DB_PATH = 'app/database/sales.db'

# Data files
ITEMS_FILE = 'data/items.json'
SALES_FILE = 'data/sales.json'
USERS_FILE = 'data/users.json'
INVESTMENT_FILE = 'data/investment.json'
PENDING_ORDERS_FILE = 'data/pending_orders.json'

def init_db():
    # Create the directory if it doesn't exist
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
    
    # Only initialize if the database doesn't exist
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Create items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                price REAL NOT NULL,
                description TEXT
            )
        ''')
        
        # Create sales table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                amount REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                user_id TEXT NOT NULL,
                options TEXT,
                FOREIGN KEY (item_id) REFERENCES items (id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Insert authorized users
        cursor.execute('INSERT INTO users (user_id) VALUES (?)', ('01-135231-091',))
        cursor.execute('INSERT INTO users (user_id) VALUES (?)', ('01-135231-041',))
        
        # Insert menu items from the image
        items = [
            ('Golgappay 8 in Plate', 200, '8 pieces per plate'),
            ('Golgappay 12 in Plate', 250, '12 pieces per plate'),
            ('Mint Margarita', 130, 'Refreshing mint drink'),
            ('Chat in Bag', 250, 'Select your combo - Noodles, Onion, Tomato, Boiled Corn, Lemon, Chilli garlic sauce, Mayo sauce, Corrian'),
            ('Classic Butter Corn', 100, 'Boiled Flavoured Corn - Classic Butter'),
            ('Masaa Masti Corn', 150, 'Boiled Flavoured Corn - Masaa Masti'),
            ('Super Corn Chaat', 200, 'Boiled Flavoured Corn - Super Corn Chaat'),
            ('Garlic Powder Topping', 10, 'Extra topping'),
            ('Cheese Powder Topping', 30, 'Extra topping')
        ]
        
        for item in items:
            cursor.execute('INSERT INTO items (name, price, description) VALUES (?, ?, ?)', item)
        
        # Setting initial investment
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        cursor.execute('INSERT INTO settings (key, value) VALUES (?, ?)', 
                      ('initial_investment', '21000'))
        
        conn.commit()
        conn.close()

# Initialize database
if not os.path.exists(os.path.dirname(DB_PATH)):
    os.makedirs(os.path.dirname(DB_PATH))
init_db()

# Initialize data files if they don't exist
def initialize_data_files():
    # Create data directory if it doesn't exist
    try:
        if not os.path.exists('data'):
            os.makedirs('data')
    except Exception as e:
        print(f"Error creating data directory: {e}")
    
    try:
        # ALWAYS recreate the items file with the correct prices
        with open(ITEMS_FILE, 'w') as f:
            json.dump([
                {
                    "id": 1,
                    "name": "Golgappay 8 in Plate",
                    "price": 200,
                    "description": "8 crispy puris filled with spicy water and potatoes"
                },
                {
                    "id": 2,
                    "name": "Golgappay 12 in Plate",
                    "price": 250,
                    "description": "12 crispy puris filled with spicy water and potatoes"
                },
                {
                    "id": 3,
                    "name": "Mint Margarita",
                    "price": 130,
                    "description": "Refreshing mint drink with lemon and soda"
                },
                {
                    "id": 4,
                    "name": "Chat in Bag",
                    "price": 250,
                    "description": "Mix of ingredients served in a bag with sauces"
                },
                {
                    "id": 5,
                    "name": "Classic Butter Corn",
                    "price": 100,
                    "description": "Sweet corn with butter and spices"
                },
                {
                    "id": 6,
                    "name": "Masaa Masti Corn",
                    "price": 150,
                    "description": "Spicy corn with masala and lemon"
                },
                {
                    "id": 7,
                    "name": "Super Corn Chaat",
                    "price": 200,
                    "description": "Corn with chaat masala, onions and sauce"
                },
                {
                    "id": 8,
                    "name": "Garlic Powder Topping",
                    "price": 10,
                    "description": "Extra garlic powder topping"
                },
                {
                    "id": 9,
                    "name": "Cheese Powder Topping",
                    "price": 30,
                    "description": "Extra cheese powder topping"
                }
            ], f, indent=4)
    except Exception as e:
        print(f"Error creating items file: {e}")
    
    try:
        # Sales data
        if not os.path.exists(SALES_FILE):
            with open(SALES_FILE, 'w') as f:
                json.dump([], f, indent=4)
        
        # Users data
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'w') as f:
                json.dump([
                    {
                        "id": 1,
                        "username": "01-135231-091",
                        "password": generate_password_hash("ali2525W")
                    },
                    {
                        "id": 2,
                        "username": "01-135231-041",
                        "password": generate_password_hash("ali2525W")
                    }
                ], f, indent=4)
        
        # ALWAYS recreate the investment file with the correct amount
        with open(INVESTMENT_FILE, 'w') as f:
            json.dump({"initial_investment": 21000}, f, indent=4)
            
        # Pending orders data
        if not os.path.exists(PENDING_ORDERS_FILE):
            with open(PENDING_ORDERS_FILE, 'w') as f:
                json.dump([], f, indent=4)
    except Exception as e:
        print(f"Error creating other data files: {e}")

# Initialize data files
initialize_data_files()

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('dashboard.html')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    print(f"Login attempt - Username: {username}, Password: {password[:1]}***")
    
    if not username or not password:
        print("Missing username or password")
        return render_template('login.html', error="Please enter both admin ID and password")
    
    try:
        # First try direct admin login for these specific credentials
        if username == "01-135231-091" and password == "ali2525W":
            print("Direct login successful")
            session['user_id'] = 1
            session['username'] = username
            return redirect(url_for('index'))
            
        if username == "01-135231-041" and password == "ali2525W":
            print("Direct login successful")
            session['user_id'] = 2
            session['username'] = username
            return redirect(url_for('index'))
        
        # If direct login fails, try the JSON file
        print("Trying JSON file login")
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
            print(f"Loaded users: {users}")
        
        for user in users:
            if user['username'] == username:
                print(f"Found user: {user['username']}")
                if check_password_hash(user['password'], password):
                    print("Password match")
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    return redirect(url_for('index'))
                else:
                    print("Password mismatch")
                    return render_template('login.html', error="Invalid password")
        
        print("User not found")
        return render_template('login.html', error="Admin ID not found")
    except Exception as e:
        print(f"Login error: {e}")
        return render_template('login.html', error=f"Login error: {str(e)}")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/items')
def get_items():
    with open(ITEMS_FILE, 'r') as f:
        items = json.load(f)
    return jsonify(items)

@app.route('/api/sales', methods=['GET', 'POST'])
def handle_sales():
    if request.method == 'GET':
        # Get sales data
        try:
            with open(SALES_FILE, 'r') as f:
                sales = json.load(f)
            return jsonify(sales)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading sales file: {e}")
            # Create empty sales file if it doesn't exist or is corrupted
            with open(SALES_FILE, 'w') as f:
                json.dump([], f, indent=4)
            return jsonify([])
    else:
        # Add new sales
        try:
            new_sales = request.json
            
            if not new_sales:
                return jsonify({"status": "error", "message": "No sales data provided"}), 400
            
            # Load existing sales
            try:
                with open(SALES_FILE, 'r') as f:
                    sales = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error reading sales file: {e}. Creating new file.")
                sales = []
            
            # Add new sales with timestamp and ID
            for sale in new_sales:
                sale_obj = {
                    'id': str(uuid.uuid4()),
                    'name': sale['item'],
                    'quantity': sale['quantity'],
                    'amount': sale['amount'],
                    'options': sale['options'],
                    'timestamp': datetime.now().isoformat()
                }
                sales.append(sale_obj)
            
            # Save updated sales data
            with open(SALES_FILE, 'w') as f:
                json.dump(sales, f, indent=4)
            
            return jsonify({"status": "success"})
        except Exception as e:
            print(f"Error adding sales: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/summary')
def get_summary():
    try:
        # Get investment data
        with open(INVESTMENT_FILE, 'r') as f:
            investment_data = json.load(f)
        initial_investment = investment_data.get('initial_investment', 0)
        
        # Get sales data
        try:
            with open(SALES_FILE, 'r') as f:
                sales = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading sales file: {e}")
            sales = []

        # Calculate total sales
        total_sales = sum(sale['amount'] for sale in sales)
        
        # Calculate remaining investment
        remaining_investment = max(0, initial_investment - total_sales)
        
        # Calculate percent recouped
        percent_recouped = (total_sales / initial_investment) * 100 if initial_investment > 0 else 0

        # Calculate sales by item
        sales_by_item = {}
        for sale in sales:
            if sale['name'] in sales_by_item:
                sales_by_item[sale['name']]['qty'] += sale['quantity']
                sales_by_item[sale['name']]['amount'] += sale['amount']
            else:
                sales_by_item[sale['name']] = {
                    'qty': sale['quantity'],
                    'amount': sale['amount']
                }

        sales_by_item_list = [{
            'name': item,
            'qty': data['qty'],
            'amount': data['amount']
        } for item, data in sales_by_item.items()]

        # Sort by amount descending
        sales_by_item_list = sorted(sales_by_item_list, key=lambda x: x['amount'], reverse=True)

        return jsonify({
            'initial_investment': initial_investment,
            'total_sales': total_sales,
            'remaining_investment': remaining_investment,
            'percent_recouped': percent_recouped,
            'sales_by_item': sales_by_item_list
        })
    except Exception as e:
        print(f"Error getting summary: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/user')
def get_user():
    if 'user_id' in session:
        # Check if username exists in session, if not use user_id as fallback
        username = session.get('username', f"User-{session['user_id']}")
        return jsonify({
            'id': session['user_id'],
            'username': username
        })
    return jsonify({})

# QR Code functionality
@app.route('/qrcode')
def generate_qr():
    """Generate QR code for ordering"""
    # Generate the URL for the customer order page
    base_url = request.host_url.rstrip('/')
    order_url = f"{base_url}/customer-order"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(order_url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png', download_name='order_qrcode.png')

@app.route('/customer-order')
def customer_order_page():
    """Customer order page accessed via QR code"""
    return render_template('customer_order.html')

@app.route('/api/customer-order', methods=['POST'])
def submit_customer_order():
    """API endpoint to submit a customer order"""
    try:
        customer_name = request.json.get('customerName')
        order_items = request.json.get('items')
        
        if not customer_name or not order_items:
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Create a unique order ID
        order_id = str(uuid.uuid4())
        
        # Create new order
        new_order = {
            'id': order_id,
            'customerName': customer_name,
            'items': order_items,
            'status': 'pending',
            'timestamp': datetime.now().isoformat(),
            'totalAmount': sum(item['amount'] for item in order_items)
        }
        
        # Load existing pending orders
        try:
            if os.path.exists(PENDING_ORDERS_FILE):
                with open(PENDING_ORDERS_FILE, 'r') as f:
                    pending_orders = json.load(f)
            else:
                pending_orders = []
        except Exception:
            pending_orders = []
        
        # Add new order
        pending_orders.append(new_order)
        
        # Save updated pending orders
        with open(PENDING_ORDERS_FILE, 'w') as f:
            json.dump(pending_orders, f, indent=4)
        
        return jsonify({'success': True, 'orderId': order_id})
    except Exception as e:
        print(f"Error submitting order: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pending-orders')
def get_pending_orders():
    """Get all pending orders"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401
        
    try:
        if os.path.exists(PENDING_ORDERS_FILE):
            with open(PENDING_ORDERS_FILE, 'r') as f:
                pending_orders = json.load(f)
        else:
            pending_orders = []
            
        return jsonify(pending_orders)
    except Exception as e:
        print(f"Error getting pending orders: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/approve-order/<order_id>', methods=['POST'])
def approve_order(order_id):
    """Approve a pending order"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401
        
    try:
        # Load pending orders
        if os.path.exists(PENDING_ORDERS_FILE):
            with open(PENDING_ORDERS_FILE, 'r') as f:
                pending_orders = json.load(f)
        else:
            return jsonify({'error': 'No pending orders found'}), 404
            
        # Find the order to approve
        order_to_approve = None
        updated_pending_orders = []
        
        for order in pending_orders:
            if order['id'] == order_id:
                order_to_approve = order
                order_to_approve['status'] = 'approved'
                order_to_approve['approvedBy'] = session.get('username', f"User-{session['user_id']}")
                order_to_approve['approvedAt'] = datetime.now().isoformat()
            else:
                updated_pending_orders.append(order)
                
        if not order_to_approve:
            return jsonify({'error': 'Order not found'}), 404
            
        # Update pending orders list
        with open(PENDING_ORDERS_FILE, 'w') as f:
            json.dump(updated_pending_orders, f, indent=4)
            
        # Load existing sales
        with open(SALES_FILE, 'r') as f:
            sales = json.load(f)
            
        # Add approved items to sales
        for item in order_to_approve['items']:
            sale_obj = {
                'id': str(uuid.uuid4()),
                'name': item['item'],
                'quantity': item['quantity'],
                'amount': item['amount'],
                'options': item.get('options', ''),
                'timestamp': datetime.now().isoformat(),
                'customerName': order_to_approve['customerName']
            }
            sales.append(sale_obj)
            
        # Save updated sales
        with open(SALES_FILE, 'w') as f:
            json.dump(sales, f, indent=4)
            
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error approving order: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reject-order/<order_id>', methods=['POST'])
def reject_order(order_id):
    """Reject a pending order"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401
        
    try:
        # Load pending orders
        if os.path.exists(PENDING_ORDERS_FILE):
            with open(PENDING_ORDERS_FILE, 'r') as f:
                pending_orders = json.load(f)
        else:
            return jsonify({'error': 'No pending orders found'}), 404
            
        # Find and remove the order
        updated_pending_orders = [order for order in pending_orders if order['id'] != order_id]
        
        if len(updated_pending_orders) == len(pending_orders):
            return jsonify({'error': 'Order not found'}), 404
            
        # Update pending orders list
        with open(PENDING_ORDERS_FILE, 'w') as f:
            json.dump(updated_pending_orders, f, indent=4)
            
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error rejecting order: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/deal-menu')
def deal_menu():
    return render_template('deal_menu.html')

@app.route('/api/clear-sales', methods=['POST'])
def clear_sales():
    """Clear all sales history and reset summary data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401
        
    try:
        # Clear sales data
        with open(SALES_FILE, 'w') as f:
            json.dump([], f, indent=4)
        
        # Reset investment data to original value
        with open(INVESTMENT_FILE, 'r') as f:
            investment_data = json.load(f)
            
        # Keep the original investment amount but reset other stats
        with open(INVESTMENT_FILE, 'w') as f:
            json.dump({
                'initial_investment': investment_data['initial_investment']
            }, f, indent=4)
            
        return jsonify({'success': True, 'message': 'Sales history and summary cleared'})
    except Exception as e:
        print(f"Error clearing sales data: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 