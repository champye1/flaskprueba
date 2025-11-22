from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

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
    # Nuevos campos para registro más completo
    last_name = db.Column(db.String(80), nullable=False, default='')
    email = db.Column(db.String(120), nullable=False, default='')
    address = db.Column(db.String(255), nullable=False, default='')

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
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        if not all([username, password, confirm, first_name, last_name, email, address]):
            error = 'Todos los campos son obligatorios.'
        elif password != confirm:
            error = 'Las contraseñas no coinciden.'
        elif '@' not in email:
            error = 'Correo inválido.'
        else:
            existing_user = User.query.filter_by(username=username).first()
            existing_email = User.query.filter_by(email=email).first()
            if existing_user:
                error = 'El nombre de usuario ya existe.'
            elif existing_email:
                error = 'El correo ya está registrado.'
            else:
                full_name = f"{first_name} {last_name}".strip()
                new_user = User(username=username, password=password, role='user', name=full_name, last_name=last_name, email=email, address=address)
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

# --- API REST (JSON) ---
# Implementación y uso del API REST:
# - Endpoints:
#   * GET /api/phones -> lista todos los teléfonos en JSON (200)
#   * GET /api/phones/<id> -> detalle de un teléfono (200 o 404 si no existe)
#   * POST /api/phones -> crea un teléfono (201). Requiere rol admin (403 si no autorizado).
#   * PUT /api/phones/<id> -> actualiza parcialmente un teléfono (200). Requiere rol admin.
#   * DELETE /api/phones/<id> -> elimina un teléfono (200). Requiere rol admin.
# - Autenticación y permisos: se usa la sesión de Flask; las operaciones de escritura requieren session['role']=='admin'.
# - Validaciones: 'name' y 'description' obligatorios; 'price' debe ser numérico; errores devuelven JSON con códigos adecuados (400/403/404).
# - Respuestas: se usa 'jsonify' y códigos HTTP (200/201/400/403/404).
# - Ejemplos:
#   - Listado: fetch('/api/phones').then(r => r.json())
#   - Curl crear (como admin): curl -X POST http://127.0.0.1:5000/api/phones -H "Content-Type: application/json" -d '{"name":"Nuevo","description":"Desc","ram":"8GB","storage":"128GB","camera":"50MP","battery":"4500mAh","price":599.99,"image_url":"https://..."}'
# - Propósito: desacoplar el catálogo de las vistas HTML y permitir consumo desde frontend/scripts o integraciones.
def phone_to_dict(p: Phone):
    return {
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'ram': p.ram,
        'storage': p.storage,
        'camera': p.camera,
        'battery': p.battery,
        'price': p.price,
        'image_url': p.image_url,
    }

@app.route('/api/phones', methods=['GET'])
def api_phones_list():
    phones = Phone.query.order_by(Phone.id.desc()).all()
    return jsonify([phone_to_dict(p) for p in phones]), 200

@app.route('/api/phones/<int:phone_id>', methods=['GET'])
def api_phone_detail(phone_id):
    phone = Phone.query.get(phone_id)
    if not phone:
        return jsonify({'error': 'not_found'}), 404
    return jsonify(phone_to_dict(phone)), 200

@app.route('/api/phones', methods=['POST'])
def api_phone_create():
    # Solo admin puede crear
    if session.get('role') != 'admin':
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    description = (data.get('description') or '').strip()
    ram = (data.get('ram') or '').strip()
    storage = (data.get('storage') or '').strip()
    camera = (data.get('camera') or '').strip()
    battery = (data.get('battery') or '').strip()
    image_url = (data.get('image_url') or '').strip()
    price_raw = data.get('price')
    try:
        price = float(price_raw) if price_raw is not None else 0.0
    except (ValueError, TypeError):
        return jsonify({'error': 'invalid_price'}), 400
    if not name or not description:
        return jsonify({'error': 'name_and_description_required'}), 400
    phone = Phone(name=name, description=description, ram=ram, storage=storage, camera=camera, battery=battery, price=price, image_url=image_url)
    db.session.add(phone)
    db.session.commit()
    return jsonify(phone_to_dict(phone)), 201

@app.route('/api/phones/<int:phone_id>', methods=['PUT'])
def api_phone_update(phone_id):
    # Solo admin puede editar
    if session.get('role') != 'admin':
        return jsonify({'error': 'forbidden'}), 403
    phone = Phone.query.get(phone_id)
    if not phone:
        return jsonify({'error': 'not_found'}), 404
    data = request.get_json(silent=True) or {}
    # Actualización parcial
    for field in ['name', 'description', 'ram', 'storage', 'camera', 'battery', 'image_url']:
        value = data.get(field)
        if isinstance(value, str):
            setattr(phone, field, value.strip())
    if 'price' in data:
        try:
            phone.price = float(data['price'])
        except (ValueError, TypeError):
            return jsonify({'error': 'invalid_price'}), 400
    db.session.commit()
    return jsonify(phone_to_dict(phone)), 200

@app.route('/api/phones/<int:phone_id>', methods=['DELETE'])
def api_phone_delete(phone_id):
    # Solo admin puede borrar
    if session.get('role') != 'admin':
        return jsonify({'error': 'forbidden'}), 403
    phone = Phone.query.get(phone_id)
    if not phone:
        return jsonify({'error': 'not_found'}), 404
    db.session.delete(phone)
    db.session.commit()
    return jsonify({'status': 'deleted', 'id': phone_id}), 200

# --- CRUD de Teléfonos ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/phones')
def phones_list():
    phones = Phone.query.order_by(Phone.id.desc()).all()
    return render_template('phones_list.html', phones=phones)

@app.route('/phones/<int:phone_id>')
def phone_detail(phone_id):
    phone = Phone.query.get_or_404(phone_id)
    return render_template('phone_detail.html', phone=phone)

@app.route('/phones/new', methods=['GET', 'POST'])
@admin_required
def phone_create():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        ram = request.form.get('ram', '').strip()
        storage = request.form.get('storage', '').strip()
        camera = request.form.get('camera', '').strip()
        battery = request.form.get('battery', '').strip()
        image_url = request.form.get('image_url', '').strip()
        price_raw = request.form.get('price', '0').strip()
        try:
            price = float(price_raw)
        except ValueError:
            price = 0.0
        if not name or not description:
            error = 'Nombre y descripción son obligatorios.'
            return render_template('phone_form.html', phone=None, action='create', error=error)
        new_phone = Phone(name=name, description=description, ram=ram, storage=storage, camera=camera, battery=battery, price=price, image_url=image_url)
        db.session.add(new_phone)
        db.session.commit()
        return redirect(url_for('phone_detail', phone_id=new_phone.id))
    return render_template('phone_form.html', phone=None, action='create')

@app.route('/phones/<int:phone_id>/edit', methods=['GET', 'POST'])
@admin_required
def phone_edit(phone_id):
    phone = Phone.query.get_or_404(phone_id)
    if request.method == 'POST':
        phone.name = request.form.get('name', phone.name).strip()
        phone.description = request.form.get('description', phone.description).strip()
        phone.ram = request.form.get('ram', phone.ram).strip()
        phone.storage = request.form.get('storage', phone.storage).strip()
        phone.camera = request.form.get('camera', phone.camera).strip()
        phone.battery = request.form.get('battery', phone.battery).strip()
        phone.image_url = request.form.get('image_url', phone.image_url).strip()
        price_raw = request.form.get('price', str(phone.price)).strip()
        try:
            phone.price = float(price_raw)
        except ValueError:
            pass
        db.session.commit()
        return redirect(url_for('phone_detail', phone_id=phone.id))
    return render_template('phone_form.html', phone=phone, action='edit')

@app.route('/phones/<int:phone_id>/delete', methods=['POST'])
@admin_required
def phone_delete(phone_id):
    phone = Phone.query.get_or_404(phone_id)
    db.session.delete(phone)
    db.session.commit()
    return redirect(url_for('phones_list'))

# Utilidad admin: reiniciar catálogo y crear 2 teléfonos nuevos
@app.route('/admin/reset_phones', methods=['GET', 'POST'])
@admin_required
def admin_reset_phones():
    try:
        # Borrar todos los teléfonos
        Phone.query.delete()
        db.session.commit()

        # Crear dos nuevos teléfonos de ejemplo
        new_phones = [
            Phone(name='Samsung Galaxy S24', description='Nuevo flagship Samsung', ram='8GB', storage='256GB', camera='50MP', battery='4000mAh', price=899.99, image_url='https://fdn2.gsmarena.com/vv/pics/samsung/samsung-galaxy-s24-1.jpg'),
            Phone(name='iPhone 15 Pro', description='Nuevo high-end Apple', ram='8GB', storage='256GB', camera='48MP', battery='3500mAh', price=1199.99, image_url='https://fdn2.gsmarena.com/vv/pics/apple/apple-iphone-15-pro-1.jpg'),
        ]
        db.session.bulk_save_objects(new_phones)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'reset_failed'}), 500

    # Volver a la lista de teléfonos
    return redirect(url_for('phones_list'))

# Página informativa solo para administradores
@app.route('/admin/info')
@admin_required
def admin_info():
    return render_template('admin_info.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Asegurar columnas nuevas en SQLite si ya existía la tabla
        try:
            conn = db.engine.connect()
            cols = {row[1] for row in conn.execute(text("PRAGMA table_info(user)")).fetchall()}
            for col, ddl in [("last_name", "TEXT"), ("email", "TEXT"), ("address", "TEXT")]:
                if col not in cols:
                    conn.execute(text(f"ALTER TABLE user ADD COLUMN {col} {ddl} NOT NULL DEFAULT ''"))
            # Enforce that there can only be ONE admin user in the table
            # SQLite supports partial unique indexes; this guarantees a single row with role='admin'
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ux_single_admin ON user(role) WHERE role='admin'"))
            conn.close()
        except Exception:
            pass
        # Create default admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password='admin123', role='admin', name='Administrador', last_name='', email='admin@example.com', address='Oficina')
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