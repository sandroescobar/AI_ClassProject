from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import pandas as pd 
from sqlalchemy import create_engine

app = Flask(__name__)





app.secret_key = 'your_secret_key'
print("Secret Key:", app.secret_key)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Ae9542790079'
app.config['MYSQL_DB'] = 'inventory'
app.config['SECRET_KEY'] = 'your-unique-secret-key'


mysql = MySQL(app)

engine = create_engine('mysql://root:Ae9542790079@localhost/inventory')




@app.route('/',methods=['GET', 'POST'])
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
            return render_template('dashboard.html', msg=msg)
        else:
            msg = 'Incorrect email or password'
            
    return render_template('login.html')


@app.route('/signUp', methods = ['GET', 'POST'])
def signUp():
    msg = ''
    print("mysql connection object:", mysql)

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        print(f" received sign-up request: Email = {email}, Password = {password}")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not email or not password:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts (email,password) VALUES (%s, %s)', (email, password))
            mysql.connection.commit()
            msg = 'You have successfully signed up!'
            return redirect(url_for('login'))
        
    print("there was an error stating:", msg)
    return render_template('signUp.html')



@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

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
                # 1) Read CSV into DataFrame
                df = pd.read_csv(file)

                # 2) Add a column in DF to identify which file these rows came from
                df['fileName'] = file.filename

                # 3) Rename columns to match the MySQL table exactly
                #    Make sure these EXACT names match the columns we created in MySQL
                df.rename(columns={
                    'Region': 'region',
                    'Country': 'country',
                    'Item Type': 'itemType',
                    'Sales Channel': 'saleChannel',
                    'Order Priority': 'orderPriority',   # Now we do have this column in DB
                    'Order Date': 'orderDate',
                    'Order ID': 'orderID',
                    'Ship Date': 'shipDate',             # If your DB is called 'shipDate'
                    'Units Sold': 'unitsSold',
                    'Unit Price': 'unitPrice',
                    'Unit Cost': 'unitCost',             # Now we do have this column in DB
                    'Total Revenue': 'totalRevenue',
                    'Total Cost': 'totalCost',
                    'Total Profit': 'totalProfit'
                }, inplace=True)

                # 4) Insert into DB
                #    For columns that do not exist in DB, either create them in DB or drop them from DF
                df.to_sql('csvinfo', con=engine, if_exists='append', index=False)

                return redirect(url_for('recieveInventory'))  
                # Or render_template('recieveInventory.html') if you want to show the same page
    # If GET request or no form submission yet, just show the HTML form
    return render_template('recieveInventory.html')





@app.route('/addInventory', methods = ['GET','POST'])
def addInventory():
    form_type = request.form.get('form_id')
    msg = ''
    if form_type == 'addCategory':
        categoryName = request.form['categoryField']
        print(f" received addInventory request: categoryField = {categoryName}")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM departments WHERE key_field = %s', (categoryName,))
        inventory = cursor.fetchone()
        if inventory:
            msg = 'Category already exists!'
        elif inventory == '':
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO departments (key_field) VALUES (%s)', (categoryName,))
            mysql.connection.commit()
            msg = 'You have successfully added inventory!'
            return redirect(url_for('addInventory'))
    elif form_type == 'addInventory':
        item = request.form.get('addItem')
        qty = request.form.get('quantityOfItem')
        category = request.form.get('categorySelected')

        print("Name:", item, "Qty:", qty, "Category:", category)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM items WHERE name = %s', (item,))

        inventory = cursor.fetchone()

        if inventory:
            msg = 'item already exists!'
        elif not item or not qty or not category:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO items (name, quantity, department_name) VALUES (%s, %s, %s)',(item, qty, category))
            mysql.connection.commit()
            msg = 'You have successfully added inventory!'
            return redirect(url_for('addInventory'))


    return render_template('addInventory.html')








if __name__ == "__main__":
    app.run()
