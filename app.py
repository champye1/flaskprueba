from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)
app.secret_key = 'supersecretkey'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(80), nullable=False)

class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    ram = db.Column(db.String(20), nullable=False)
    storage = db.Column(db.String(20), nullable=False)
    camera = db.Column(db.String(50), nullable=False)
    battery = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

@app.route('/')
def index():
    phones = Phone.query.all()
    return render_template('index.html', phones=phones)

@app.route('/api')
def api():
    return render_template('api.html')

@app.route('/gestion')
def gestion():
    return render_template('gestion.html')

@app.route('/educacion')
def educacion():
    return render_template('educacion.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/auth')
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('index'))
        else:
            error = 'Usuario o contraseña incorrectos.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/auth')
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        if not username or not password or not role:
            error = 'Todos los campos son obligatorios.'
        else:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                error = 'El usuario ya existe.'
            else:
                new_user = User(username=username, password=password, role=role)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
    return render_template('register.html', error=error)
@app.route('/api/add', methods=['GET', 'POST'])
def api_add():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    message = None
    if request.method == 'POST':
        # Aquí puedes procesar los datos del formulario y añadir el recurso a la base de datos
        # Por ejemplo: nombre = request.form['nombre']
        message = 'Recurso añadido correctamente (simulado).'
    return render_template('api_add.html', message=message)
def auth():
    return render_template('auth.html')

@app.route('/comparar')
def comparar():
    ids = request.args.getlist('compare')
    # Limit to only two products for comparison
    if len(ids) > 2:
        ids = ids[:2]
    phones = Phone.query.filter(Phone.id.in_(ids)).all() if ids else []
    return render_template('comparar.html', phones=phones)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password='admin123', role='admin', name='Administrador')
            db.session.add(admin_user)
            db.session.commit()
        # Add sample phones if none exist
        if Phone.query.count() == 0:
            sample_phones = [
                Phone(name='Samsung Galaxy S23', description='Flagship Samsung phone', ram='8GB', storage='256GB', camera='50MP', battery='3900mAh', price=799.99, image_url='https://fdn2.gsmarena.com/vv/pics/samsung/samsung-galaxy-s23-5g-1.jpg'),
                Phone(name='iPhone 14 Pro', description='Apple high-end phone', ram='6GB', storage='128GB', camera='48MP', battery='3200mAh', price=999.99, image_url='https://fdn2.gsmarena.com/vv/pics/apple/apple-iphone-14-pro-1.jpg'),
                Phone(name='Xiaomi 13', description='Affordable flagship', ram='8GB', storage='256GB', camera='50MP', battery='4500mAh', price=699.99, image_url='https://fdn2.gsmarena.com/vv/pics/xiaomi/xiaomi-13-1.jpg'),
                Phone(name='Google Pixel 7', description='Google phone with pure Android', ram='8GB', storage='128GB', camera='50MP', battery='4355mAh', price=599.99, image_url='https://fdn2.gsmarena.com/vv/pics/google/google-pixel-7-1.jpg'),
                Phone(name='OnePlus 11', description='Fast and smooth experience', ram='16GB', storage='256GB', camera='50MP', battery='5000mAh', price=729.99, image_url='https://fdn2.gsmarena.com/vv/pics/oneplus/oneplus-11-1.jpg'),
                Phone(name='Motorola Edge 40', description='Motorola premium phone', ram='8GB', storage='256GB', camera='50MP', battery='4400mAh', price=649.99, image_url='https://fdn2.gsmarena.com/vv/pics/motorola/motorola-edge-40-1.jpg'),
                Phone(name='Sony Xperia 1 IV', description='Sony flagship with 4K display', ram='12GB', storage='256GB', camera='12MP triple', battery='5000mAh', price=1199.99, image_url='https://fdn2.gsmarena.com/vv/pics/sony/sony-xperia-1-iv-1.jpg'),
                Phone(name='Huawei P50 Pro', description='Huawei premium camera phone', ram='8GB', storage='256GB', camera='50MP quad', battery='4360mAh', price=899.99, image_url='https://fdn2.gsmarena.com/vv/pics/huawei/huawei-p50-pro-1.jpg'),
                Phone(name='Realme GT 2 Pro', description='Affordable flagship killer', ram='12GB', storage='256GB', camera='50MP', battery='5000mAh', price=599.99, image_url='https://fdn2.gsmarena.com/vv/pics/realme/realme-gt2-pro-1.jpg'),
                Phone(name='Asus ROG Phone 6', description='Gaming powerhouse', ram='16GB', storage='512GB', camera='50MP', battery='6000mAh', price=1099.99, image_url='https://fdn2.gsmarena.com/vv/pics/asus/asus-rog-phone6-1.jpg'),
            ]
            db.session.bulk_save_objects(sample_phones)
            db.session.commit()
    app.run(debug=True, host='0.0.0.0', port=5000)