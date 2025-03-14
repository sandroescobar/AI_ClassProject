from flask import Flask, render_template



app = Flask(__name__)


@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/recieveInventory')
def recieveInventory():
    return render_template('recieveInventory.html')




if __name__ == "__main__":
    app.run()
