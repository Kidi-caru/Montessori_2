from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "Montessori3D_2026"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "montessori"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def login():
    if "login" in session:
        return redirect("/dashboard")
    return render_template("login.html")


@app.route("/validar", methods=["POST"])
def validar():
    usuario = request.form["usuario"]
    password = request.form["password"]

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario=%s", (usuario,))
    cuenta = cursor.fetchone()
    cursor.close()

    if cuenta:
        password_correcta = False
        if cuenta["password"].startswith("pbkdf2:sha256:") or cuenta["password"].startswith("scrypt:"):
            password_correcta = check_password_hash(cuenta["password"], password)
        else:
            password_correcta = (cuenta["password"] == password)

        if password_correcta:
            session["login"] = True
            session["id"] = cuenta["id"]
            session["usuario"] = cuenta["usuario"]
            session["nombre"] = cuenta["nombre"]
            flash("Bienvenido al sistema.")
            return redirect("/dashboard")

    flash("Usuario o contraseña incorrectos")
    return redirect("/")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if "login" in session:
        return redirect("/dashboard")

    if request.method == "POST":
        nombre = request.form["nombre"]
        usuario = request.form["usuario"]
        password = request.form["password"]

        password_hashed = generate_password_hash(password)

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario=%s", (usuario,))
        if cursor.fetchone():
            cursor.close()
            flash("El nombre de usuario ya está registrado.")
            return redirect("/registro")

        cursor.execute(
            "INSERT INTO usuarios(nombre, usuario, password) VALUES(%s, %s, %s)",
            (nombre, usuario, password_hashed)
        )
        mysql.connection.commit()
        cursor.close()

        flash("Registro exitoso. Ahora puedes iniciar sesión.")
        return redirect("/")

    return render_template("registro.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente")
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    if "login" not in session:
        return redirect("/")

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT COUNT(*) total FROM productos")
    total_productos = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) total FROM clientes")
    total_clientes = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) total FROM proveedores")
    total_proveedores = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(total), 0) total FROM ventas")
    total_ventas = cursor.fetchone()["total"]
    cursor.close()

    return render_template(
        "dashboard.html",
        productos=total_productos,
        clientes=total_clientes,
        proveedores=total_proveedores,
        ventas=total_ventas
    )

@app.route("/inventario")
def inventario():
    if "login" not in session:
        return redirect("/")

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT productos.*, categorias.nombre AS categoria
        FROM productos
        INNER JOIN categorias ON productos.categoria_id = categorias.id
        ORDER BY productos.id DESC
    """)
    productos = cursor.fetchall()

    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()
    cursor.close()

    return render_template("inventario.html", productos=productos, categorias=categorias)


@app.route("/guardar_producto", methods=["POST"])
def guardar_producto():
    if "login" not in session:
        return redirect("/")

    codigo = request.form.get("codigo")
    nombre = request.form.get("nombre")
    categoria = request.form.get("categoria")
    material = request.form.get("material", "")
    color = request.form.get("color", "")
    descripcion = request.form.get("descripcion", "")

    try:
        largo = float(request.form.get("largo", 0))
        ancho = float(request.form.get("ancho", 0))
        alto = float(request.form.get("alto", 0))
        precio = float(request.form.get("precio", 0))
        stock = int(request.form.get("stock", 0))
    except ValueError:
        flash("Error: Revisa que el precio, stock y dimensiones sean datos numéricos válidos.")
        return redirect("/inventario")

    imagen = request.files.get("imagen")
    nombre_imagen = ""

    if imagen and imagen.filename != "":
        nombre_imagen = secure_filename(imagen.filename)
        ruta_destino = os.path.join(app.config["UPLOAD_FOLDER"], nombre_imagen)
        imagen.save(ruta_destino)

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO productos(
            codigo, nombre, categoria_id, material, color,
            largo, ancho, alto, precio, stock, descripcion, imagen
        )
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (codigo, nombre, categoria, material, color, largo, ancho, alto, precio, stock, descripcion, nombre_imagen))

    mysql.connection.commit()
    cursor.close()

    flash("Producto registrado correctamente.")
    return redirect("/inventario")

@app.route("/editar_producto/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    if "login" not in session:
        return redirect("/")

    cursor = mysql.connection.cursor()

    if request.method == "POST":
        codigo = request.form.get("codigo")
        nombre = request.form.get("nombre")
        categoria = request.form.get("categoria")
        material = request.form.get("material", "")
        color = request.form.get("color", "")
        descripcion = request.form.get("descripcion", "")

        try:
            largo = float(request.form.get("largo", 0))
            ancho = float(request.form.get("ancho", 0))
            alto = float(request.form.get("alto", 0))
            precio = float(request.form.get("precio", 0))
            stock = int(request.form.get("stock", 0))
        except ValueError:
            cursor.close()
            flash("Error: Verifica que precio, stock y dimensiones sean valores numéricos.")
            return redirect(f"/editar_producto/{id}")

        imagen = request.files.get("imagen")

        if imagen and imagen.filename != "":
            nombre_imagen = secure_filename(imagen.filename)
            ruta_destino = os.path.join(app.config["UPLOAD_FOLDER"], nombre_imagen)
            imagen.save(ruta_destino)

            cursor.execute("""
                UPDATE productos
                SET codigo=%s, nombre=%s, categoria_id=%s, material=%s, color=%s,
                    largo=%s, ancho=%s, alto=%s, precio=%s, stock=%s, descripcion=%s, imagen=%s
                WHERE id=%s
            """, (codigo, nombre, categoria, material, color, largo, ancho, alto, precio, stock, descripcion, nombre_imagen, id))
        else:
            cursor.execute("""
                UPDATE productos
                SET codigo=%s, nombre=%s, categoria_id=%s, material=%s, color=%s,
                    largo=%s, ancho=%s, alto=%s, precio=%s, stock=%s, descripcion=%s
                WHERE id=%s
            """, (codigo, nombre, categoria, material, color, largo, ancho, alto, precio, stock, descripcion, id))

        mysql.connection.commit()
        cursor.close()
        flash("Producto actualizado correctamente.")
        return redirect("/inventario")

    cursor.execute("SELECT * FROM productos WHERE id=%s", (id,))
    producto = cursor.fetchone()

    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()
    cursor.close()

    return render_template("editar_producto.html", producto=producto, categorias=categorias)

@app.route("/eliminar_producto/<int:id>")
def eliminar_producto(id):
    if "login" not in session:
        return redirect("/")

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM productos WHERE id=%s", (id,))
    mysql.connection.commit()
    cursor.close()

    flash("Producto eliminado correctamente.")
    return redirect("/inventario")


@app.route("/buscar_producto")
def buscar_producto():
    if "login" not in session:
        return redirect("/")

    buscar = request.args.get("buscar", "")
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT productos.*, categorias.nombre AS categoria
        FROM productos
        INNER JOIN categorias ON productos.categoria_id = categorias.id
        WHERE productos.nombre LIKE %s
        ORDER BY productos.nombre
    """, ("%" + buscar + "%",))
    productos = cursor.fetchall()

    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()
    cursor.close()

    return render_template("inventario.html", productos=productos, categorias=categorias)

@app.route("/muebles")
def muebles():
    if "login" not in session:
        return redirect("/")
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT * FROM productos WHERE categoria_id = 1")
    productos = cursor.fetchall()
    cursor.close()
    return render_template("muebles.html", productos=productos)


@app.route("/comedores")
def comedores():
    if "login" not in session:
        return redirect("/")
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM productos WHERE categoria_id = 2")
    productos = cursor.fetchall()
    cursor.close()
    return render_template("comedores.html", productos=productos)


@app.route("/basecamas")
def basecamas():
    if "login" not in session:
        return redirect("/")
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM productos WHERE categoria_id = 3")
    productos = cursor.fetchall()
    cursor.close()
    return render_template("basecamas.html", productos=productos)


@app.route("/colchones")
def colchones():
    if "login" not in session:
        return redirect("/")
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM productos WHERE categoria_id = 4")
    productos = cursor.fetchall()
    cursor.close()
    return render_template("colchones.html", productos=productos)

@app.route("/clientes")
def clientes():
    if "login" not in session:
        return redirect("/")
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM clientes ORDER BY id DESC")
    clientes = cursor.fetchall()
    cursor.close()
    return render_template("clientes.html", clientes=clientes)


@app.route("/guardar_cliente", methods=["POST"])
def guardar_cliente():
    if "login" not in session:
        return redirect("/")
    nombre = request.form["nombre"]
    telefono = request.form["telefono"]
    correo = request.form["correo"]
    direccion = request.form["direccion"]

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO clientes(nombre, telefono, correo, direccion) VALUES(%s,%s,%s,%s)", 
                   (nombre, telefono, correo, direccion))
    mysql.connection.commit()
    cursor.close()

    flash("Cliente registrado correctamente.")
    return redirect("/clientes")


@app.route("/editar_cliente/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    if "login" not in session:
        return redirect("/")
    cursor = mysql.connection.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]
        correo = request.form["correo"]
        direccion = request.form["direccion"]

        cursor.execute("""
            UPDATE clientes SET nombre=%s, telefono=%s, correo=%s, direccion=%s WHERE id=%s
        """, (nombre, telefono, correo, direccion, id))
        mysql.connection.commit()
        cursor.close()
        flash("Cliente actualizado correctamente.")
        return redirect("/clientes")

    cursor.execute("SELECT * FROM clientes WHERE id=%s", (id,))
    cliente = cursor.fetchone()
    cursor.close()
    return render_template("editar_cliente.html", cliente=cliente)


@app.route("/eliminar_cliente/<int:id>")
def eliminar_cliente(id):
    if "login" not in session:
        return redirect("/")
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM clientes WHERE id=%s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash("Cliente eliminado.")
    return redirect("/clientes")

@app.route("/proveedores")
def proveedores():
    if "login" not in session:
        return redirect("/")
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM proveedores ORDER BY id DESC")
    proveedores = cursor.fetchall()
    cursor.close()
    return render_template("proveedores.html", proveedores=proveedores)


@app.route("/guardar_proveedor", methods=["POST"])
def guardar_proveedor():
    if "login" not in session:
        return redirect("/")
    empresa = request.form["empresa"]
    contacto = request.form["contacto"]
    telefono = request.form["telefono"]
    correo = request.form["correo"]
    direccion = request.form["direccion"]

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO proveedores(empresa, contacto, telefono, correo, direccion) VALUES(%s,%s,%s,%s,%s)", 
                   (empresa, contacto, telefono, correo, direccion))
    mysql.connection.commit()
    cursor.close()
    flash("Proveedor registrado correctamente.")
    return redirect("/proveedores")


@app.route("/editar_proveedor/<int:id>", methods=["GET", "POST"])
def editar_proveedor(id):
    if "login" not in session:
        return redirect("/")
    cursor = mysql.connection.cursor()

    if request.method == "POST":
        empresa = request.form["empresa"]
        contacto = request.form["contacto"]
        telefono = request.form["telefono"]
        correo = request.form["correo"]
        direccion = request.form["direccion"]

        cursor.execute("""
            UPDATE proveedores SET empresa=%s, contacto=%s, telefono=%s, correo=%s, direccion=%s WHERE id=%s
        """, (empresa, contacto, telefono, correo, direccion, id))
        mysql.connection.commit()
        cursor.close()
        flash("Proveedor actualizado.")
        return redirect("/proveedores")

    cursor.execute("SELECT * FROM proveedores WHERE id=%s", (id,))
    proveedor = cursor.fetchone()
    cursor.close()
    return render_template("editar_proveedor.html", proveedor=proveedor)


@app.route("/eliminar_proveedor/<int:id>")
def eliminar_proveedor(id):
    if "login" not in session:
        return redirect("/")
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM proveedores WHERE id=%s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash("Proveedor eliminado.")
    return redirect("/proveedores")

@app.route("/ventas")
def ventas():
    if "login" not in session:
        return redirect("/")

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT ventas.id, clientes.nombre AS cliente, productos.nombre AS producto, 
               detalle_ventas.cantidad, ventas.total, ventas.fecha
        FROM ventas
        INNER JOIN clientes ON ventas.cliente_id = clientes.id
        LEFT JOIN detalle_ventas ON ventas.id = detalle_ventas.venta_id
        LEFT JOIN productos ON detalle_ventas.producto_id = productos.id
        ORDER BY ventas.id DESC
    """)
    ventas = cursor.fetchall()

    cursor.execute("SELECT * FROM clientes ORDER BY nombre")
    clientes = cursor.fetchall()

    cursor.execute("SELECT * FROM productos ORDER BY nombre")
    productos = cursor.fetchall()
    cursor.close()

    return render_template("ventas.html", ventas=ventas, clientes=clientes, productos=productos)


@app.route("/guardar_venta", methods=["POST"])
def guardar_venta():
    if "login" not in session:
        return redirect("/")

    cliente_id = request.form["cliente"]
    producto_id = request.form["producto"]
    cantidad = int(request.form["cantidad"])

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM productos WHERE id=%s", (producto_id,))
    datos = cursor.fetchone()

    if datos is None:
        cursor.close()
        flash("Producto no encontrado.")
        return redirect("/ventas")

    stock = datos["stock"]
    if cantidad > stock:
        cursor.close()
        flash("No hay suficiente inventario disponible.")
        return redirect("/ventas")

    precio = float(datos["precio"])
    subtotal = precio * cantidad

    cursor.execute("INSERT INTO ventas(cliente_id, total) VALUES(%s,%s)", (cliente_id, subtotal))
    mysql.connection.commit()
    id_venta = cursor.lastrowid

    cursor.execute("""
        INSERT INTO detalle_ventas(venta_id, producto_id, cantidad, precio, subtotal)
        VALUES(%s,%s,%s,%s,%s)
    """, (id_venta, producto_id, cantidad, precio, subtotal))

    cursor.execute("UPDATE productos SET stock = stock - %s WHERE id=%s", (cantidad, producto_id))
    mysql.connection.commit()
    cursor.close()

    flash("Venta registrada correctamente.")
    return redirect("/ventas")

@app.route("/reportes")
def reportes():
    if "login" not in session:
        return redirect("/")

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT COUNT(*) total FROM productos")
    total_productos = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) total FROM clientes")
    total_clientes = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) total FROM proveedores")
    total_proveedores = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(total), 0) total FROM ventas")
    total_ventas = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT productos.nombre, categorias.nombre AS categoria, productos.stock
        FROM productos
        INNER JOIN categorias ON productos.categoria_id = categorias.id
        WHERE productos.stock <= 5
        ORDER BY productos.stock ASC
    """)
    stock_bajo = cursor.fetchall()
    cursor.close()

    return render_template(
        "reportes.html",
        total_productos=total_productos,
        total_clientes=total_clientes,
        total_proveedores=total_proveedores,
        total_ventas=total_ventas,
        stock_bajo=stock_bajo
    )


@app.route("/spaceview")
@app.route("/spaceview/<int:id>")
def spaceview(id=None):
    if "login" not in session:
        return redirect("/")

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM productos ORDER BY nombre")
    productos = cursor.fetchall()

    producto_seleccionado = None
    if id:
        cursor.execute("SELECT * FROM productos WHERE id=%s", (id,))
        producto_seleccionado = cursor.fetchone()
    
    cursor.close()

    return render_template("spaceview.html", productos=productos, producto_seleccionado=producto_seleccionado)


@app.route("/comparar_espacio", methods=["POST"])
def comparar_espacio():
    if "login" not in session:
        return redirect("/")

    producto_id = request.form["producto"]
    habitacion = request.form["habitacion"]
    espacio_largo = float(request.form["espacio_largo"])
    espacio_ancho = float(request.form["espacio_ancho"])
    espacio_alto = float(request.form["espacio_alto"])

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM productos WHERE id=%s", (producto_id,))
    producto = cursor.fetchone()

    cursor.execute("SELECT * FROM productos ORDER BY nombre")
    productos = cursor.fetchall()
    cursor.close()

    if producto:
        largo_m = float(producto["largo"])
        ancho_m = float(producto["ancho"])
        alto_m = float(producto["alto"])

        if espacio_largo >= largo_m and espacio_ancho >= ancho_m and espacio_alto >= alto_m:
            resultado = f"✅ El producto '{producto['nombre']}' SÍ cabe holgadamente en el espacio '{habitacion}'."
        else:
            resultado = f"❌ El producto '{producto['nombre']}' NO cabe en '{habitacion}'. Revisa las dimensiones."
    else:
        resultado = "⚠️ Producto no encontrado para comparar."

    return render_template(
        "spaceview.html",
        productos=productos,
        producto_seleccionado=producto,
        resultado=resultado
    )


if __name__ == "__main__":
    app.run(debug=True)