import plotly.express as px
import plotly.io as pio
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
from sqlalchemy import create_engine

import numpy as np

app = Flask(__name__)

# Set your secret keys
app.secret_key = 'your_secret_key'
print("Secret Key:", app.secret_key)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Ae9542790079'
app.config['MYSQL_DB'] = 'inventory'
app.config['SECRET_KEY'] = 'your-unique-secret-key'

mysql = MySQL(app)
engine = create_engine('mysql://root:Ae9542790079@localhost/inventory')


###############################################################################
# ROUTES
###############################################################################





@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s AND password = %s', (email, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            msg = 'Logged in successfully!'
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect email or password'
    return render_template('login.html')


@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    msg = ''
    print("mysql connection object:", mysql)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        print(f"Received sign-up request: Email = {email}, Password = {password}")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not email or not password:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts (email, password) VALUES (%s, %s)', (email, password))
            mysql.connection.commit()
            msg = 'You have successfully signed up!'
            return redirect(url_for('login'))
    print("There was an error stating:", msg)
    return render_template('signUp.html')



@app.route('/dashboard')
def dashboard():
    """
    1) Load data from `csvinfo`.
    2) If table is empty => pass `charts=None` => placeholders in the template.
    3) If data exists => create 5 interactive Plotly charts:
       - chart1: Top 10 Item Types by Units Sold
       - chart2: Top 10 Item Types by Total Profit
       - chart3: Monthly Units Sold
       - chart4: Monthly Total Revenue
       - chart5: Monthly Total Profit
    4) Pass `charts` dict to `dashboard.html`.
    """
    try:
        # 1. Fetch data from MySQL
        df = pd.read_sql("SELECT * FROM csvinfo", con=engine)
        if df.empty:
            # => no CSV data => show placeholders
            return render_template('dashboard.html', charts=None)

        # 2. Ensure columns are correct & parse date
        #    (Adjust the rename if your DB columns differ)
        df.rename(columns={
            'orderDate': 'OrderDate',
            'itemType': 'ItemType',
            'unitsSold': 'UnitsSold',
            'totalRevenue': 'TotalRevenue',
            'totalProfit': 'TotalProfit'
        }, inplace=True, errors='ignore')

        # Convert date to datetime
        df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')
        # Drop rows where we can't parse date
        df.dropna(subset=['OrderDate'], inplace=True)

        # Convert numeric
        for col in ['UnitsSold', 'TotalRevenue', 'TotalProfit']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 3. Create the 5 interactive Plotly charts
        #    We'll do the same logic you had in Matplotlib, but using Plotly.

        # (A) Top 10 Item Types by Total Units Sold
        top_units = (
            df.groupby("ItemType")['UnitsSold']
              .sum()
              .sort_values(ascending=False)
              .head(10)
              .reset_index()
        )
        fig1 = px.bar(top_units, x='UnitsSold', y='ItemType',
                      orientation='h', title="Top 10 Item Types by Total Units Sold")

        # IMPORTANT: Force Plotly to autosize
        fig1.update_layout(
            autosize=True,
            width=400,
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        chart1 = pio.to_html(
            fig1,
            full_html=False,
            config={
                "displayModeBar": False,
                "displaylogo": False
            }
        )




        # (B) Top 10 Item Types by Total Profit
        top_profit = (
            df.groupby("ItemType")['TotalProfit']
              .sum()
              .sort_values(ascending=False)
              .head(10)
              .reset_index()
        )
        fig2 = px.bar(top_profit, x='ItemType', y='TotalProfit',
                      title="Top 10 Item Types by Total Profit")
        fig2.update_layout(
            autosize=True,
            width=400,
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        chart2 = pio.to_html(
            fig2,
            full_html=False,
            config={
                "displayModeBar": False,
                "displaylogo": False
            }
        )









        # For the monthly time series, we need a DateTime index
        df.set_index('OrderDate', inplace=True)
        df_monthly = df.resample('ME').sum(numeric_only=True).reset_index()

        # (C) Monthly Units Sold
        fig3 = px.line(df_monthly, x='OrderDate', y='UnitsSold',
                       title='Monthly Units Sold')
        # IMPORTANT: Force Plotly to autosize
        fig3.update_layout(
            autosize=True,
            width=400,
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        chart3 = pio.to_html(
            fig3,
            full_html=False,
            config={
                "displayModeBar": False,
                "displaylogo": False
            }
        )



        # (D) Monthly Total Revenue
        fig4 = px.line(df_monthly, x='OrderDate', y='TotalRevenue',
                       title='Monthly Total Revenue')
        # IMPORTANT: Force Plotly to autosize
        fig4.update_layout(
            autosize=True,
            width=400,
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        chart4 = pio.to_html(
            fig4,
            full_html=False,
            config={
                "displayModeBar": False,
                "displaylogo": False
            }
        )


        # (E) Monthly Total Profit
        fig5 = px.line(df_monthly, x='OrderDate', y='TotalProfit',
                       title='Monthly Total Profit')
        # IMPORTANT: Force Plotly to autosize
        fig5.update_layout(
            autosize=True,
            width=400,
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        chart5 = pio.to_html(
            fig5,
            full_html=False,
            config={
                "displayModeBar": False,
                "displaylogo": False
            }
        )



        # 4. Pass the charts to the template
        charts = {
            'chart1': chart1,
            'chart2': chart2,
            'chart3': chart3,
            'chart4': chart4,
            'chart5': chart5
        }
        return render_template('dashboard.html', charts=charts)

    except Exception as e:
        print("Dashboard error:", e)
        return render_template('dashboard.html', charts=None)


@app.route('/products')
def products():
    """
    Display a list of product categories.
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Query for all departments ordered alphabetically.
    cursor.execute("SELECT key_field FROM departments ORDER BY key_field ASC")
    categories = cursor.fetchall()
    return render_template("products.html", categories=categories)


@app.route('/products/<category>')
def category_products(category):
    """
    Display all items (products) for a given category.
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Query items that belong to the selected category.
    cursor.execute("SELECT * FROM items WHERE department_name = %s ORDER BY name ASC", (category,))
    items = cursor.fetchall()
    return render_template("category_items.html", category=category, items=items)


@app.route('/recieveInventory', methods=['GET', 'POST'])
def recieveInventory():
    if request.method == 'POST':
        form_type = request.form.get('form_id')
        if form_type == 'addCsvFile':
            if 'csv_file' not in request.files:
                return "No file part in request"
            file = request.files['csv_file']
            if file.filename == '':
                return "No selected file"
            if file:
                # Read CSV into a DataFrame
                df = pd.read_csv(file)
                print("CSV file first 5 rows:")
                print(df.head())

                # Add a column to record which file the rows came from
                df['fileName'] = file.filename

                # Rename columns
                df.rename(columns={
                    'Region': 'region',
                    'Country': 'country',
                    'Item Type': 'itemType',
                    'Sales Channel': 'saleChannel',
                    'Order Priority': 'orderPriority',
                    'Order Date': 'orderDate',
                    'Order ID': 'orderID',
                    'Ship Date': 'shipDate',
                    'Units Sold': 'unitsSold',
                    'Unit Price': 'unitPrice',
                    'Unit Cost': 'unitCost',
                    'Total Revenue': 'totalRevenue',
                    'Total Cost': 'totalCost',
                    'Total Profit': 'totalProfit'
                }, inplace=True)

                print("After rename:", df.columns.tolist())
                print("Checking for null 'Order Date':", df['Order Date'].isna().sum())

                # Convert date columns to YYYY-MM-DD
                df['orderDate'] = pd.to_datetime(df['orderDate'], format='%m/%d/%Y', errors='coerce')
                df['shipDate'] = pd.to_datetime(df['shipDate'], format='%m/%d/%Y', errors='coerce')

                # Optional: drop rows with invalid date parsing
                df.dropna(subset=['orderDate', 'shipDate'], inplace=True)

                # Insert data into "csvinfo"
                df.to_sql('csvinfo', con=engine, if_exists='append', index=False)

                return redirect(url_for('recieveInventory'))
    return render_template('recieveInventory.html')



###############################################################################
# HELPER FUNCTIONS
###############################################################################


def find_or_create_department(category, cursor):
    """
    Look up a department by its key_field.
    If it doesn't exist and if the category is not empty, create it.
    """
    if not category or category.strip() == "":
        print("Empty category provided; skipping creation.")
        return None
    category = category.strip()
    cursor.execute("SELECT * FROM departments WHERE key_field = %s", (category,))
    dept = cursor.fetchone()
    if not dept:
        print(f"Creating new department for category: '{category}'")
        cursor.execute("INSERT INTO departments (key_field) VALUES (%s)", (category,))
        mysql.connection.commit()
        cursor.execute("SELECT * FROM departments WHERE key_field = %s", (category,))
        dept = cursor.fetchone()
    return dept


def process_csv_records(batch_size=500):
    """
    Process a batch of unprocessed CSV records in csvinfo.
    This function updates the departments table and inserts into items
    based on the 'itemType' field from csvinfo.
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = "SELECT * FROM csvinfo WHERE imported = 0 OR imported IS NULL LIMIT %s"
    cursor.execute(query, (batch_size,))
    records = cursor.fetchall()
    if not records:
        print("No unprocessed CSV records found.")
        return
    for record in records:
        category_raw = record.get('itemType')
        category = category_raw.strip() if category_raw else ""
        print(f"Processing record id {record.get('id')}: raw category='{category_raw}' trimmed to '{category}'")
        if category == "":
            print(f"Skipping record {record.get('id')} because itemType is empty after trimming.")
            continue
        # For this example, we use itemType as both the item name and category.
        item_name = category
        quantity = record.get('unitsSold')
        # Ensure the department exists in the departments table.
        find_or_create_department(category, cursor)
        # Insert record into items table.
        cursor.execute(
            "INSERT INTO items (name, quantity, department_name) VALUES (%s, %s, %s)",
            (item_name, quantity, category)
        )
        # Mark record as processed.
        cursor.execute("UPDATE csvinfo SET imported = 1 WHERE id = %s", (record.get('id'),))
        print(f"Processed CSV record id {record.get('id')} with category '{category}'.")
    mysql.connection.commit()


###############################################################################
# ADD INVENTORY ROUTE
###############################################################################


@app.route('/addInventory', methods=['GET', 'POST'])
def addInventory():
    # Process a batch of CSV records to update departments.
    try:
        process_csv_records()
    except Exception as e:
        print("Error in process_csv_records:", e)
    # Retrieve all departments for the dropdown menu.
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM departments")
    categories = cursor.fetchall()

    form_type = request.form.get('form_id')
    msg = ''
    if form_type == 'addCategory':
        categoryName = request.form['categoryField']
        print(f"Received addInventory request: categoryField = {categoryName}")
        cursor.execute('SELECT * FROM departments WHERE key_field = %s', (categoryName,))
        inventory = cursor.fetchone()
        if inventory:
            msg = 'Category already exists!'
        elif categoryName == '':
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO departments (key_field) VALUES (%s)', (categoryName,))
            mysql.connection.commit()
            msg = 'You have successfully added the category!'
            return redirect(url_for('addInventory'))
    elif form_type == 'addInventory':
        item = request.form.get('addItem')
        qty = request.form.get('quantityOfItem')
        category = request.form.get('categorySelected')
        print("Name:", item, "Qty:", qty, "Category:", category)
        cursor.execute('SELECT * FROM items WHERE name = %s', (item,))
        inventory = cursor.fetchone()
        if inventory:
            msg = 'Item already exists!'
        elif not item or not qty or not category:
            msg = 'Please fill out all fields!'
        else:
            cursor.execute(
                'INSERT INTO items (name, quantity, department_name) VALUES (%s, %s, %s)',
                (item, qty, category)
            )
            mysql.connection.commit()
            msg = 'You have successfully added the inventory item!'
            return redirect(url_for('addInventory'))
    return render_template('addInventory.html', msg=msg, categories=categories)


###############################################################################
# GET CATEGORIES ENDPOINT (optional for JS fetch)
###############################################################################


@app.route('/getCategories')
def getCategories():
    """
    Return a JSON list of all distinct category names (key_field)
    from the departments table.
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT key_field FROM departments")
    rows = cursor.fetchall()
    categories = [row['key_field'] for row in rows if row['key_field'].strip() != ""]
    print("Fetched categories from DB:", categories)
    return jsonify(categories)


###############################################################################
# MAIN
###############################################################################


if __name__ == "__main__":
    app.run()
