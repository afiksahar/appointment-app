from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appointments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    appointments = db.relationship('Appointment', backref='client', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    treatment = db.Column(db.String(100), nullable=False)

@app.route('/')
def index():
    return render_template('calendar.html')

@app.route('/add-client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        new_client = Client(name=name, phone=phone)
        db.session.add(new_client)
        db.session.commit()
        return redirect('/clients')
    return render_template('add_client.html')

@app.route('/add-appointment', methods=['GET', 'POST'])
def add_appointment():
    clients = Client.query.all()
    if request.method == 'POST':
        client_id = request.form['client_id']
        date = request.form['date']
        time = request.form['time']
        treatment = request.form['treatment']
        new_appt = Appointment(client_id=client_id, date=date, time=time, treatment=treatment)
        db.session.add(new_appt)
        db.session.commit()
        return redirect('/')
    return render_template('add_appointment.html', clients=clients)

@app.route('/clients')
def clients():
    all_clients = Client.query.all()
    return render_template('clients.html', clients=all_clients)

@app.route('/appointments-json')
def appointments_json():
    appts = Appointment.query.all()
    data = []
    for a in appts:
        data.append({
            "title": f"{a.client.name} - {a.treatment}",
            "start": f"{a.date}T{a.time}"
        })
    return jsonify(data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
