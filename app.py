#pip install waitress
#pip install flask-marshmallow
#pip install -U flask-sqlalchemy marshmallow-sqlalchemy
from waitress import serve
from MySQLdb import DataError, IntegrityError
from flask import Flask, request, json
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from sqlalchemy import and_, func , or_, not_
from datetime import datetime
from datetime import date
from datetime import timedelta
from sqlalchemy import exc
from sqlalchemy.exc import IntegrityError
#pip install pyjwt
import jwt
from flask_marshmallow import Marshmallow, exceptions
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/dbpython"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET'] = 'ASDASDFBTGHDFJKGHDFJ56'
db = SQLAlchemy(app)
ma = Marshmallow(app)


def error_middelware(route): #va a levantar una funcion que va a ser una ruta
    def inner(*args, **kwargs): #va a tener una funcion interna que va a recibir argumentos y argumentos de clave
        try:
            return route(*args, **kwargs) # intenta retornar esta funcion utilizando los mismos argumentos
        except AttributeError:
            return {"status": 404, "message": "No existe el valor buscado"}
        except exceptions.ValidationError:
            return {"status": 500, "message": "Valor invalido revise la clave"}
        except IntegrityError: 
            return {"status": 500, "message": "El usuario ya existe"}
    inner.__name__ = route.__name__
    return inner

def error_reserva(route):
    def inner(*args, **kwargs): #va a tener una funcion interna que va a recibir argumentos y argumentos de clave
        try:
            return route(*args, **kwargs) # intenta retornar esta funcion utilizando los mismos argumentos
        except AttributeError:
            return {"status": 404, "message": "No existe la habitacion ingresada"}
    inner.__name__ = route.__name__
    return inner
def error(route):
    def inner(*args, **kwargs): #va a tener una funcion interna que va a recibir argumentos y argumentos de clave
        try:
            return route(*args, **kwargs) # intenta retornar esta funcion utilizando los mismos argumentos
        except ValueError:
            return {"status": 404, "message": "Falla por formato de fecha incorrecto."}
    inner.__name__ = route.__name__
    return inner

def error_ingresodatos(route):
    def inner(*args, **kwargs): #va a tener una funcion interna que va a recibir argumentos y argumentos de clave
        try:
            return route(*args, **kwargs) # intenta retornar esta funcion utilizando los mismos argumentos
        except :
            return {"status": 404, "message": "Error al ingresar los datos, vuelva a intentar"}
    inner.__name__ = route.__name__
    return inner

#verifica que el usuario se encuentre autenticado
def autenticacion(route):
    def inner(*args, **kwargs):
        try:
            token = request.headers['Authorization'][7:] #con el 7: se recortan las primeras 7 letras de lo que hay guardado
            payload =jwt.decode(token, app.config['JWT_SECRET'], algorithms=["HS256"])

            return route(*args, **kwargs)
        except jwt.InvalidSignatureError:
            return {"status": 400, "message":"Token invalido"}
        except KeyError:
            return {"status": 400, "message":"Token inexistente"}
        except jwt.DecodeError:
            return {"status": 400, "message":"Token corrupto"}
    inner.__name__ = route.__name__
    return inner
#verifica que el usuario sea un emplado
def esEmpleado(route): #va a levantar una funcion que va a ser una ruta
    def inner(*args, **kwargs): #va a tener una funcion interna que va a recibir argumentos y argumentos de clave
        try:
            token = request.headers['Authorization'][7:] #con el 7: se recortan las primeras 7 letras de lo que hay guardado
            payload =jwt.decode(token, app.config['JWT_SECRET'], algorithms=["HS256"])
            if payload['rol'] == 'empleado':
                return route(*args, **kwargs)
            else:
                return {"status": 400, "message":"Solo los empleados tienen acceso"}
        except jwt.InvalidSignatureError:
            return {"status": 400, "message":"Token invalido"}
        except KeyError:
            return {"status": 400, "message":"Token inexistente"}
        except jwt.DecodeError:
            return {"status": 400, "message":"Token corrupto"}
    inner.__name__ = route.__name__
    return inner


#verifica que el usuario sea un Cliente
def esCliente(route): #va a levantar una funcion que va a ser una ruta
    def inner(*args, **kwargs): #va a tener una funcion interna que va a recibir argumentos y argumentos de clave
        try:
            token = request.headers['Authorization'][7:] #con el 7: se recortan las primeras 7 letras de lo que hay guardado
            payload =jwt.decode(token, app.config['JWT_SECRET'], algorithms=["HS256"])
            if payload['rol'] == 'cliente':
                return route(*args, **kwargs)
            else:
                return {"status": 400, "message":"Solo los clientes pueden realizar esta tarea"}
        except jwt.InvalidSignatureError:
            return {"status": 400, "message":"Token invalido"}
        except KeyError:
            return {"status": 400, "message":"Token inexistente"}
        except jwt.DecodeError:
            return {"status": 400, "message":"Token corrupto"}
    inner.__name__ = route.__name__
    return inner

def obtener_nombre_usuario():
    token = request.headers['Authorization'][7:] #con el 7: se recortan las primeras 7 letras de lo que hay guardado
    payload =jwt.decode(token, app.config['JWT_SECRET'], algorithms=["HS256"])
    return payload["name"]
class Usuario(db.Model):

    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(25), unique=True, nullable=False)
    clave = db.Column(db.String(50),nullable=False)
    nick = db.Column(db.String(20), nullable=False)
    rol = db.Column(db.String(20), nullable=False) #para identificar si es cliente o empleado
    reservas = db.relationship('Reserva', backref='usuario', lazy = True)

    def __init__(self,name, clave, nick, rol ):
        self.name =name
        self.clave = clave
        self.nick = nick
        self.rol = rol

class Habitacion(db.Model):
    __tablename__ = 'habitaciones'
    id = db.Column(db.Integer, primary_key=True)
    precio = db.Column(db.Integer)
    condicion = db.Column(db.String(20))
    reservas = db.relationship('Reserva', backref='Habitacion', lazy = True)

    def __init__(self,precio,condicion):
        self.precio = precio
        self.condicion = condicion

class Reserva(db.Model):
    __tablename__ = 'reservas'
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    habitacion = db.Column(db.Integer,db.ForeignKey('habitaciones.id'))
    fechaEntrada = db.Column(db.DateTime,nullable=False)
    fechaSalida = db.Column(db.DateTime,nullable=False)


    def __init__(self,cliente, habitacion , fechaEntrada, fechaSalida):
        self.cliente = cliente
        self.habitacion = habitacion
        self.fechaEntrada = fechaEntrada
        self.fechaSalida = fechaSalida


class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta():
        model = Usuario
        include_fk = True
        load_instance = True #convierte autom en obj
        load_only = ("clave",)

class ReservaSchema(ma.SQLAlchemyAutoSchema):
    class Meta():
        model = Reserva
        include_fk = True
        load_instance = True #convierte autom en obj

class HabitacionSchema(ma.SQLAlchemyAutoSchema):
    class Meta():
        model = Habitacion
        include_fk = True
        load_instance = True #convierte autom en obj

    reservas= ma.Nested(  ReservaSchema, many=True)

class SoloHabitacionSchema(ma.SQLAlchemyAutoSchema):
    class Meta():
        model = Habitacion
        include_fk = True
        load_instance = True #convierte autom en obj

@app.route('/init')
def iniciar():
    db.create_all()
    return 'ok'

@app.route('/')
def saludo():
    return 'Hello world'


@app.route('/usuarios', methods=['POST'])
@error_middelware
@esEmpleado
def crear_usuario(): #nos van a pasar los datos en json  y va a devolver un diccionario

        request.json
        sUsuario = UsuarioSchema(partial=True)
        usu = sUsuario.load(request.json)
    #name = request.json['name']
    #clave = request.json['clave']
    #nick = request.json['nick']
    #rol = request.json['rol']

    #usu = Usuario(name,clave, nick, rol ) #creo el objeto Usuario
    
        db.session.add(usu) #lo agrego a la base de datos
        db.session.commit() # guarda los cambios en base de datos
        return {"status": 200, "message": "Usuario creado correctamente."} #retorna un status 200 que significa que esta todo OK
   

@app.route("/usuarios", methods=["GET"])
@esEmpleado
def listar_usuarios():
    sUsuarios = UsuarioSchema(many=True)
    return { "results": sUsuarios.dump( Usuario.query.all())}

#@app.route("/usuarios/<int:id>", methods=["GET"])
#@esEmpleado
#@error_middelware
#def traer_usuario(id):
#    usu = Usuario.query.get(id)
#   return {"name": usu.name, "nick":usu.nick }
@app.route("/usuarios/<int:id>", methods=["GET"])
@esEmpleado
@error_middelware
def traer_usuario(id):
    usu = Usuario.query.get(id)
    #return {"name": usu.name, "nick":usu.nick }
    return UsuarioSchema().dump(usu)

@app.route('/usuarios/<int:id>', methods=['DELETE'])
@error_ingresodatos
@esEmpleado
def eliminar_usuario(id):
        usu = Usuario.query.get(id)
        db.session.delete(usu)
        db.session.commit()
        return {"status": 200, "message":" Usuario eliminado"}


@app.route('/usuarios/<int:id>', methods=['PUT'])
@esEmpleado
@error_ingresodatos
def modificar_usuario(id):
    #name = request.json['name']
    #clave = request.json['clave']
    #nick = request.json['nick']
    #rol = request.json['rol']
    #usu:Usuario =Usuario.query.get(id)
    #usu.name = name
    #usu.clave =clave
    #usu.nick = nick
    #usu.rol = rol
    #db.session.commit()
    if Usuario.query.filter_by(id=id).update(values=request.json):
        db.session.commit()
        return {"status": 200, "message":" Usuario modificado."}
    else:
        return {"status": 400, "message":" El id del usuario no existe."}


@app.route('/login', methods=['POST'])
def login():
    name = request.json["name"]
    clave = request.json["clave"]  #esto sirve para clave no encriptadas 
    result = Usuario.query.filter_by(name=name, clave=clave)
    if result.count() > 0:
        usu = Usuario.query.filter_by(name=name).first()
        usu = Usuario.query.get(usu.id)
        if usu.clave == clave:
            return crear_token({"name" : usu.name, "nick":usu.nick, "rol":usu.rol}) #guardo el name y el rol en el payload
        else:
            return {"status": 404, "message":"Credenciales invalidas (se intento, muchachos)"}
    else:
        return  {"status": 404, "message":"Credenciales invalidas"}
def crear_token(payload):
    return jwt.encode(payload,app.config['JWT_SECRET'] )


@app.route('/who', methods=['GET']) # '/who' para sabewr quien esta conectado
def muestra_headers():
    try:
        token = request.headers['Authorization'][7:] #con el 7: se recortan las primeras 7 letras de lo que hay guardado
        payload =jwt.decode(token, app.config['JWT_SECRET'], algorithms=["HS256"])
    except jwt.InvalidSignatureError:
        return {"status": 404, "message":"Token invalido"}
    return payload


########## HABITACIONES ###########
@app.route('/habitaciones', methods=['POST'])
@esEmpleado
def crear_habitacion():
    try:
        request.json
        sHabitacion = HabitacionSchema(partial=True)
        habitacion = sHabitacion.load(request.json)
    #precio = request.json['precio']
    #condicion = request.json['condicion']
    #habitacion = Habitacion(precio, condicion) #creo el objeto Habitacion
        if habitacion.precio >= 0:
            db.session.add(habitacion) #lo agrego a la base de datos
            db.session.commit() # guarda los cambios en base de datos
            return {"status": 200} #retorna un status 200 que significa que esta todo OK
        elif habitacion.precio < 0:
            return {"status":400, "message":"No puede crear una habitacion con precio negativo."}
        #elif habitacion.precio == str:
        #    return {"status":400, "message":"El precio ingresado debe ser de tipo numerico."}
    except ValidationError:
        return {"status":400, "message":"El precio ingresado debe ser de tipo numérico"}








#lista todas las habitaciones
@app.route("/habitaciones", methods=["GET"])
@esEmpleado
def listar_todas_las_habitaciones():
    sHabitaciones =HabitacionSchema(many=True)
    return { "results": sHabitaciones.dump( Habitacion.query.all())}

#trae habitacion por id
@app.route("/habitaciones/<int:id>", methods=["GET"])
@esEmpleado
def trer_habitacion(id):
    hab = Habitacion.query.get(id)
    if hab :
        return HabitacionSchema().dump(hab)
    else: 
         return {"status": 400, "message":"El ID ingresado es incorrecto."}


#lista solo las habitaciones disponibles
@app.route("/habitacionesDisponibles", methods=["GET"])
@esEmpleado
def listar_habitaciones_disponibles():
    condicion="activa"
    sHabitaciones =HabitacionSchema(many=True)
    return { "results": sHabitaciones.dump(Habitacion.query.filter_by(condicion=condicion))}

#modifica el precio de la habitacion
@app.route('/habitaciones/<int:id>', methods=['PUT'])
@esEmpleado
@error_ingresodatos
def modificar_precio(id):
    precio=request.json['precio']
    if  float(precio) > 0:
        if Habitacion.query.filter_by(id=id).update(values=request.json):
            db.session.commit()
            return {"status": 200, "message":"Precio actualizado."}
        else:
            return {"status": 400, "message":"El ID ingresado es incorrecto."}
    else:
        return {"status": 400, "message":"Precio ingresado incorrecto."}


#marca como disponible una habitacion

#modifica la condicion de la habitacion
##### 'disponible' para activa y 'ocupada' para inactiva
@app.route('/habitaciones/disponibilidad/<int:id>', methods=['PUT'])
@esEmpleado
@error_ingresodatos
def modificar_condicion(id):
    if Habitacion.query.filter_by(id=id).update(values=request.json):
            db.session.commit()
            return {"status": 200, "message":"Condicion actualizada"}
    else:
            return {"status": 400, "message":"El ID ingresado es incorrecto."}
######## Reservas ############

@app.route('/reservas', methods=['POST'])
@error
@error_reserva
@autenticacion
@esCliente
def crear_reserva():
    name= obtener_nombre_usuario()
    usu = Usuario.query.filter_by(name=name).first()
    usu = Usuario.query.get(usu.id)
    #idUsuario = request.json['cliente']
    idHabitacion = request.json['habitacion']
    fechaEntrada = request.json['fechaEntrada']
    fechaSalida = request.json['fechaSalida']
    if datetime.strptime(fechaEntrada, "%Y-%m-%d") <= datetime.strptime(fechaSalida, "%Y-%m-%d"):
        hab = Habitacion.query.get(idHabitacion)
        if hab.condicion == "inactiva":
            mensaje = {"status":400, "message":"La habitacion se encuentra inactiva hasta nuevo aviso."}
        else:
            rExistentes = Reserva.query.filter(Reserva.habitacion == idHabitacion).all()
            diaN = datetime.strptime(fechaEntrada, "%Y-%m-%d")
            cantDiasNR = (datetime.strptime(fechaSalida, "%Y-%m-%d")-diaN).days
            listaDiasNR = []

            listaDiasNR2 = generarListaDias(cantDiasNR, listaDiasNR, diaN)
            libre2 = compararDiasDeReservas(rExistentes, listaDiasNR2)

            if libre2==False:
                mensaje = {"status":200, "message":"La habitacion no se encuentra disponible en al menos una de las fechas elegidas."}
            else:
                reserva = Reserva(usu.id, idHabitacion, fechaEntrada, fechaSalida) #creo el objeto Reserva
                db.session.add(reserva) #lo agrego a la base de datos
                db.session.commit() # guarda los cambios en base de datos
                mensaje = {"status":200, "message":"Reserva realizada."} #retorna un status 200 que significa que esta todo OK

        return mensaje
    else:
        return {"status":400, "message":"Falla por incongruencia de fechas."}
def generarListaDias(cantDias, listaDias, diaN2):
    for diaNR in range(0,cantDias+1):
            listaDias.append(diaN2) #va completando la lista de dias
            diaN2 = diaN2 + timedelta(days=1)
    return listaDias

def compararDiasDeReservas(rExistentes2, listaDiasNR2):
    libre = True
    for reservaE in rExistentes2:
            diaE = reservaE.fechaEntrada
            cantDiasRE = (reservaE.fechaSalida-diaE).days
            for diaRE in range(0,cantDiasRE+1):
                if diaE in listaDiasNR2:
                    libre = False
                diaE = diaE + timedelta(days=1)
    return libre



#lista todas las reservas
@app.route("/reservas", methods=["GET"])
@esEmpleado
def listar_todas_las_reservas():
    sReservas =ReservaSchema(many=True)
    return { "results": sReservas.dump( Reserva.query.all())}

@app.route("/reservas/<int:id>", methods=["GET"])
@esEmpleado
def traer_reservas(id):
    sReservas =ReservaSchema(many=True)
    if  sReservas.dump( Reserva.query.filter_by(habitacion=id).all()):
        return { "results": sReservas.dump( Reserva.query.filter_by(habitacion=id).all())}
    else:
        return {"status": 400, "message":"El ID ingresado es incorrecto."}



########### BUSQUEDA ############
#por precio#
@app.route('/habitacion/precio/<int:precio>', methods=['GET'])
@esCliente
def buscarprecio(precio):
    condi = "activa"
    habitaciones = SoloHabitacionSchema(many=True)
    return { "results": habitaciones.dump(Habitacion.query.filter(and_(Habitacion.precio < precio , Habitacion.condicion == condi)).all())}






    

"""
@app.route('/buscarHabitaciones', methods=['GET'])
def buscar_habitaciones_por_rango_de_fecha():

    fechaE=request.json["fechaEntrada"]
    fechaS=request.json["fechaSalida"]
    sReservas =ReservaSchema(many=True)
    return { "results": sReservas.dump(Reserva.query.filter(or_(Reserva.fechaSalida < fechaE ,Reserva.fechaEntrada > fechaS))) }
"""



#por rango de fechas#
@app.route('/buscarhabitaciones/rango', methods=['GET'])
@error
@esCliente
def buscar_habitaciones_por_rango_de_fecha():

    fechaE=request.json["fechaEntrada"]
    fechaS=request.json["fechaSalida"]
    sReservas =ReservaSchema(many=True)
    if datetime.strptime(fechaE, "%Y-%m-%d") <= datetime.strptime(fechaS, "%Y-%m-%d"):
        if  datetime.strptime(fechaE, '%Y-%m-%d') and datetime.strptime(fechaS, '%Y-%m-%d') :

            qHabitacionesOcupadas = db.session.query(Reserva.habitacion).filter(not_(or_
            (Reserva.fechaSalida < fechaE, Reserva.fechaEntrada > fechaS)))

            query= Habitacion.query.filter(and_(Habitacion.id.not_in(qHabitacionesOcupadas),
            Habitacion.condicion != "inactiva"))

            return {"results" :sReservas.dump (query.all())}
    else:
        return {"status":400, "message":"Falla por incongruencia de fechas."}



#traer por dia Disponibles y Ocupadas por separado#
@app.route('/buscarhabitaciones/dia', methods=['GET'])
@error
@esCliente
def traerHabitacionesPorDisponibilidad():
    
    fecha=request.json["fecha"]
    if  datetime.strptime(fecha, '%Y-%m-%d'):
        sReservas =ReservaSchema(many=True)

        qHabitacionesOcupadas = db.session.query(Reserva.habitacion).filter((and_
    (Reserva.fechaEntrada <= fecha, Reserva.fechaSalida >= fecha)))

        qOcupadas = Habitacion.query.filter(and_(Habitacion.id.in_ (qHabitacionesOcupadas),
        Habitacion.condicion != "inactiva"))

        qDisponibles = Habitacion.query.filter(and_(Habitacion.id.not_in (qHabitacionesOcupadas),
        Habitacion.condicion != "inactiva"))

        return {"results": { "Habitaciones disponibles" :sReservas.dump (qDisponibles.all()),"Habitaciones ocupadas" :sReservas.dump (qOcupadas.all()) }}


if __name__ == "__main__":
    #app.run(debug=True, port=5000)
    serve(app, host='0.0.0.0', port=5000)