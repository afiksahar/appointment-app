from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    treatment_type = db.Column(db.String(100), nullable=False)

    client = db.relationship('Client', backref=db.backref('appointments', lazy=True))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add-client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        client = Client(name=name, phone=phone)
        db.session.add(client)
        db.session.commit()
        return redirect('/clients')
    return render_template('add_client.html')

@app.route('/clients')
def view_clients():
    clients = Client.query.all()
    return render_template('clients.html', clients=clients)

@app.route('/add-appointment', methods=['GET', 'POST'])
def add_appointment():
    clients = Client.query.all()
    if request.method == 'POST':
        client_id = request.form['client_id']
        date = request.form['date']
        time = request.form['time']
        treatment_type = request.form['treatment_type']

        appointment = Appointment(
            client_id=client_id,
            date=date,
            time=time,
            treatment_type=treatment_type
        )
        db.session.add(appointment)
        db.session.commit()

        # שליחת WhatsApp אוטומטית
        client = Client.query.get(client_id)
        phone = client.phone.replace("-", "").replace(" ", "").lstrip("0")  # הסרת קידומת מקומית
        message = f"היי {client.name}, תורך נקבע ל־{date} בשעה {time} לטיפול {treatment_type}. נתראה! 😊"
        whatsapp_url = f"https://wa.me/972{phone}?text={message}"

        return redirect(whatsapp_url)

    return render_template('add_appointment.html', clients=clients)

@app.route('/calendar')
def calendar_view():
    return render_template('calendar.html')

@app.route('/appointments-json')
def appointments_json():
    appointments = Appointment.query.all()
    data = []
    for a in appointments:
        client = Client.query.get(a.client_id)
        data.append({
            "title": f"{client.name} - {a.treatment_type}",
            "start": f"{a.date}T{a.time}"
        })
    return jsonify(data)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
