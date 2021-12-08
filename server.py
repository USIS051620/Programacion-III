from urllib import parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import cv2
import numpy as np

import crudpaciente
import crudproveedor
import crudmedicamentos
import crudturnos
import crudespecialidades
import crudpersonal
import crudrecetas
import inteligencia

crudproveedor = crudproveedor.curdproveedor()
crudpaciente = crudpaciente.curdpacientes()
crudmedicamentos = crudmedicamentos.curdmedicamento()
crudturnos = crudturnos.curdturno()
crudespecialidades = crudespecialidades.curdespecialidad()
crudpersonal = crudpersonal.curdpersonal()
crudrecetas = crudrecetas.curdreceta()
inteligencia = inteligencia.manejarRostros()

class crud:
    def administrar_paciente(self, datos):
        id = 0
        if datos['accion'] == 'nuevo':
            sql = 'INSERT INTO pacientes (idPaciente, DUI, NIT, Nombre, Sexo, Telefono, Correo, Direccion, FechaNacimiento, Foto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            id = self.auto_increment('pacientes')
            valores = (id, datos['dui'], datos['nit'], datos['nombre'], datos['sexo'], datos['telefono'], datos['correo'], datos['direccion'], datos['fechaNacimiento'], 'icon/pacientes/perfil'+str(id)+'.jpg')
            resultado = self.ejecutar_sql(sql, valores)
            if resultado == True:
                mensaje = 'Paciente registrado exitosamente'
            else:
                mensaje = 'Error al registrar paciente'
        elif datos['accion'] == 'editar':
            sql = 'UPDATE pacientes SET DUI = %s, NIT = %s, Nombre = %s, Sexo = %s, Telefono = %s, Correo = %s, Direccion = %s, FechaNacimiento = %s WHERE idPaciente = %s'
            valores = (datos['dui'], datos['nit'], datos['nombre'], datos['sexo'], datos['telefono'], datos['correo'], datos['direccion'], datos['fechaNacimiento'], datos['id'])
            resultado = self.ejecutar_sql(sql, valores)
            if resultado == True:
                mensaje = 'Paciente editado exitosamente'
            else:
                mensaje = 'Error al editar paciente'

        datos = {'respuesta': resultado, 'mensaje': mensaje, 'id': id}
        return datos

    def permitir_entrada(self, usuario):
        return True

class servidorBasico(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
            return SimpleHTTPRequestHandler.do_GET(self)

        elif self.path == '/consultar-paciente':
            resp = crudpaciente.consultar_paciente()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(dict(resp=resp)).encode('utf-8'))

        elif self.path == '/consultar-personal':
            resp = crudpersonal.consultar_personal()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(dict(resp=resp)).encode('utf-8'))

        elif self.path == '/consultar-proveedor':
            resp = crudproveedor.consultar_proveedor()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(dict(resp=resp)).encode('utf-8'))

        elif self.path == '/consultar-medicamento':
            resp = crudmedicamentos.consultar_medicamento()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(dict(resp=resp)).encode('utf-8'))

        elif self.path == '/consultar-turno':
            resp = crudturnos.consultar_turno()
            for hora in resp:
                hora['HoraInicio'] = str(hora['HoraInicio'])
                hora['HoraSalida'] = str(hora['HoraSalida'])
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(dict(resp=resp)).encode('utf-8'))

        elif self.path == '/consultar-especialidad':
            resp = crudespecialidades.consultar_especialidad()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(dict(resp=resp)).encode('utf-8'))

        elif self.path == '/consultar-receta':
            resp = crudrecetas.consultar_receta()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(dict(resp=resp)).encode('utf-8'))
            
        else:
            return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        data = data.decode('utf-8')
        data = parse.unquote(data)
        data = json.loads(data)

        if self.path == '/paciente':
            resultado = crudpaciente.administrar_paciente(data)
            print(resultado)
            if data['accion'] == 'nuevo' or data['accion'] == 'modificar' and resultado == 'Registro procesado con exito':
                foto = data['foto']
                matriz = np.array([np.fromstring(foto, np.uint8, sep=',')])
                matriz = matriz.reshape(200, 200, 3)
                if data['accion'] == 'nuevo':
                    id = resultado[1]
                    resultado = resultado[0]
                else:
                    id = data['id']

                inteligencia.guardar_rostro('icon/pacientes/', matriz, id)

        if self.path == '/personal':
            resultado = crudpersonal.administrar_personal(data)
            print(resultado)
            if data['accion'] == 'nuevo' or data['accion'] == 'modificar' and resultado == 'Registro procesado con exito':
                matriz = data['foto']
                matriz = np.array([np.fromstring(foto, np.uint8, sep=',')])
                matriz = matriz.reshape(200, 200, 3)
                if data['accion'] == 'nuevo':
                    id = resultado[1]
                    resultado = resultado[0]
                else:
                    id = data['id']

                inteligencia.guardar_rostro('icon/pacientes/', matriz, id)

        elif self.path == '/iniciar_sesion':
            resultado = crudpaciente.identificar(data['dui'])
            print(resultado)
            id = int(resultado[0]['idPaciente'])
            if resultado != False:
                foto = data['imagen']
                matriz = np.array([])
                matriz = np.fromstring(foto, np.uint8, sep=',')
                matriz = matriz.reshape(200, 200, 3)

                comparar = inteligencia.iniciar_sesion('icon/pacientes/', matriz, id)

                if comparar == True:
                    resultado = True
                else:
                    resultado = False
            else:
                resultado = False

        elif self.path == '/proveedor':
            resultado = crudproveedor.administrar_proveedor(data)

        elif self.path == '/medicamento':
            resultado = crudmedicamentos.administrar_medicamento(data)

        elif self.path == '/turno':
            resultado = crudturnos.administrar_turno(data)

        elif self.path == '/especialidad':
            resultado = crudespecialidades.administrar_especialidad(data)

        elif self.path == '/receta':
            resultado = crudrecetas.administrar_receta(data)

        elif self.path == '/admintir':
            resultado = crud.permitir_entrada(data)
            
            
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(dict(resultado=resultado)).encode('utf-8'))

print('Servidor iniciado en el puerto 3008')
servidor = HTTPServer(('localhost', 3008), servidorBasico)
servidor.serve_forever()