import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movimientos.db'
db = SQLAlchemy(app)

# Modelo de datos
class Movimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20))
    cantidad = db.Column(db.Float)
    criptomoneda = db.Column(db.String(10))
    valor_euros = db.Column(db.Float)

    def __init__(self, tipo, cantidad, criptomoneda, valor_euros):
        self.tipo = tipo
        self.cantidad = cantidad
        self.criptomoneda = criptomoneda
        self.valor_euros = valor_euros

# Ruta principal
@app.route('/')
def index():
    movimientos = Movimiento.query.all()
    return render_template('index.html', movimientos=movimientos)

# Ruta para realizar una compra, venta o tradeo de criptomonedas
@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    if request.method == 'POST':
        tipo = request.form['tipo']
        cantidad = float(request.form['cantidad'])
        criptomoneda = request.form['criptomoneda']

        # Obtener el valor en euros de la criptomoneda
        valor_euros = obtener_valor_euros(criptomoneda)

        if valor_euros is None:
            return 'Error al obtener el valor en euros de la criptomoneda.'

        if tipo == 'compra':
            movimiento = Movimiento(tipo='compra', cantidad=cantidad, criptomoneda=criptomoneda, valor_euros=valor_euros)
            db.session.add(movimiento)
            db.session.commit()
        elif tipo == 'venta':
            # Verificar si hay suficiente cantidad de criptomonedas para vender
            criptos_en_stock = obtener_cantidad_criptomonedas(criptomoneda)
            if criptos_en_stock >= cantidad:
                movimiento = Movimiento(tipo='venta', cantidad=cantidad, criptomoneda=criptomoneda, valor_euros=valor_euros)
                db.session.add(movimiento)
                db.session.commit()
            else:
                return 'No tienes suficiente cantidad de criptomonedas para vender.'
        elif tipo == 'tradeo':
            # Obtener la criptomoneda a la que se realizará el tradeo (en este caso, BTC)
            criptomoneda_destino = 'btc'

            # Verificar si hay suficiente cantidad de criptomonedas para intercambiar
            criptos_en_stock = obtener_cantidad_criptomonedas(criptomoneda)
            if criptos_en_stock >= cantidad:
                # Calcular el valor en euros de la criptomoneda destino
                valor_euros_destino = obtener_valor_euros(criptomoneda_destino)
                if valor_euros_destino is None:
                    return 'Error al obtener el valor en euros de la criptomoneda destino.'

                # Calcular la cantidad de criptomonedas destino a recibir
                cantidad