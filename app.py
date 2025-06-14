from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
import urllib.parse  # לשליחת WhatsApp

# הגדרת האפליקציה
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# הגדרת מסד נתונים
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'clients.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# טבלת לקוחות
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    treatment = db.Column(db.String(100), nullable=False)

# טבלת תורים
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    treatment_type = db.Column(db.String(100), nullable=False)
    client = db.relationship('Client', backref=db.backref('appointments', lazy=True))

# יצירת הטבלאות במסד הנתונים
with app.app_context():
    db.create_all()

# דף הבית – מעביר לדף הוספת לקוחה
@app.route('/')
def index():
    return redirect('/add-client')

# הוספת לקוחה
@app.route('/add-client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        treatment = request.form['treatment']
        new_client = Client(name=name, phone=phone, treatment=treatment)
        db.session.add(new_client)
        db.session.commit()
        return 'לקוחה נוספה בהצלחה 🎉'
    return render_template('add_client.html')

# רשימת לקוחות
@app.route('/clients')
def clients():
    all_clients = Client.query.all()
    return render_template('clients.html', clients=all_clients)

# קביעת תור
@app.route('/add-appointment', methods=['GET', 'POST'])
def add_appointment():
    clients = Client.query.all()
    if request.method == 'POST':
        client_id = request.form['client_id']
        date = request.form['date']
        time = request.form['time']
        treatment_type = request.form['treatment_type']
        new_appointment = Appointment(client_id=client_id, date=date, time=time, treatment_type=treatment_type)
        db.session.add(new_appointment)
        db.session.commit()
        return f'התוּר נשמר בהצלחה 📅 <br><a href="/send-whatsapp/{new_appointment.id}">שלח WhatsApp ללקוחה</a>'
    return render_template('add_appointment.html', clients=clients)

# שליחת הודעת WhatsApp (קישור)
@app.route('/send-whatsapp/<int:appointment_id>')
def send_whatsapp(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    client = appointment.client

    # הודעת וואטסאפ
    message = f"שלום {client.name}, נקבע תור עבורך בתאריך {appointment.date} בשעה {appointment.time} עבור טיפול {appointment.treatment_type}."
    encoded_msg = urllib.parse.quote(message)

    # עיבוד מספר טלפון לפורמט בינלאומי (למשל: 0501234567 -> 972501234567)
    raw_phone = client.phone.replace("-", "").replace(" ", "").strip()
    if raw_phone.startswith("0"):
        raw_phone = "972" + raw_phone[1:]

    # הפנייה ל-WhatsApp
    return redirect(f"https://wa.me/{raw_phone}?text={encoded_msg}")


    message = f"שלום {client.name}, נקבע תור עבורך בתאריך {appointment.date} בשעה {appointment.time} עבור טיפול {appointment.treatment_type}."
    phone = client.phone.replace("-", "").strip()  # להסיר מקפים
    encoded_msg = urllib.parse.quote(message)

    return redirect(f"https://wa.me/{phone}?text={encoded_msg}")

# הפעלת האפליקציה
if __name__ == '__main__':
    app.run(debug=True)
