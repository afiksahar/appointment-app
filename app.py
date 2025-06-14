from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'
db = SQLAlchemy(app)

# מודל לקוחות
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    treatment = db.Column(db.String(100))

# מודל תורים
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    treatment_type = db.Column(db.String(100))

# מסך הבית
@app.route('/')
def home():
    return render_template('index.html')

# הוספת לקוח
@app.route('/add-client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        treatment = request.form['treatment']
        new_client = Client(name=name, phone=phone, treatment=treatment)
        db.session.add(new_client)
        db.session.commit()
        return "🎉 לקוחה נוספת בהצלחה"
    return render_template('add_client.html')

# רשימת לקוחות
@app.route('/clients')
def view_clients():
    clients = Client.query.all()
    return render_template('clients.html', clients=clients)

# קביעת תור
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

# שליחת הודעת וואטסאפ
@app.route('/send-whatsapp/<int:client_id>')
def send_whatsapp(client_id):
    client = Client.query.get(client_id)
    if client:
        message = f"היי {client.name}, נקבע לך תור לטיפול {client.treatment}."
        number = client.phone.replace("-", "").replace(" ", "")
        return redirect(f"https://wa.me/972{number[1:]}?text={message}")
    return "לקוחה לא נמצאה"

if __name__ == '__main__':
    app.run(debug=True)
