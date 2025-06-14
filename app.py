from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import webbrowser

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'
db = SQLAlchemy(app)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    treatment = db.Column(db.String(100))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    treatment_type = db.Column(db.String(100))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add-client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        treatment = request.form['treatment']
        client = Client(name=name, phone=phone, treatment=treatment)
        db.session.add(client)
        db.session.commit()
        return "🎉 לקוחה נוספה בהצלחה"
    return render_template('add_client.html')

@app.route('/clients')
def clients():
    all_clients = Client.query.all()
    return render_template('clients.html', clients=all_clients)

@app.route('/add-appointment', methods=['GET', 'POST'])
def add_appointment():
    clients = Client.query.all()
    if request.method == 'POST':
        client_id = request.form['client']
        date = request.form['date']
        time = request.form['time']
        treatment_type = request.form['treatment_type']
        appointment = Appointment(client_id=client_id, date=date, time=time, treatment_type=treatment_type)
        db.session.add(appointment)
        db.session.commit()
        return redirect(url_for('send_whatsapp', appointment_id=appointment.id))
    return render_template('add_appointment.html', clients=clients)

@app.route('/send-whatsapp/<int:appointment_id>')
def send_whatsapp(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    client = Client.query.get(appointment.client_id)
    msg = f"נקבע לך תור לטיפול {appointment.treatment_type} בתאריך {appointment.date} בשעה {appointment.time}"
    phone = client.phone.replace("-", "").replace(" ", "")
    if phone.startswith("0"):
        phone = "972" + phone[1:]
    url = f"https://wa.me/{phone}?text={msg}"
    return redirect(url)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
