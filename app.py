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
    treatment = db.Column(db.String(100), nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    treatment_type = db.Column(db.String(100), nullable=False)

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
        appointment = Appointment(client_id=client_id, date=date, time=time, treatment_type=treatment_type)
        db.session.add(appointment)
        db.session.commit()
        return "📅 התור נשמר בהצלחה"
    return render_template('add_appointment.html', clients=clients)

@app.route('/send-whatsapp/<int:client_id>')
def send_whatsapp(client_id):
    client = Client.query.get_or_404(client_id)
    phone = client.phone
    name = client.name
    message = f"היי {name}, תורך נקבע בהצלחה!"
    return redirect(f"https://wa.me/972{phone}?text={message}")

@app.route('/calendar')
def calendar_view():
    return render_template('calendar.html')

@app.route('/appointments-json')
def appointments_json():
    appointments = Appointment.query.all()
    events = []
    for appt in appointments:
        client = Client.query.get(appt.client_id)
        events.append({
            'title': f"{client.name} - {appt.treatment_type}",
            'start': f"{appt.date}T{appt.time}"
        })
    return jsonify(events)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
