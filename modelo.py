import random

class Camion:
  nro_camion = 0
  tipo = 0
  peso = 0
  estado = 0

  TIPO_CAMION = [1,2,3,4]

  ESTADO_CAMION = {
    1: 'Sin Carga',
    2: 'Reabasteciendo',
    3: 'Para Produccion',
    4: 'Producto Terminado'
  }

  def __init__(self, nro_camion = 0, tipo = 0, peso = 0, estado = ESTADO_CAMION[1]):
    self.nro_camion = nro_camion
    if tipo in range(1,5):
      self.tipo = self.TIPO_CAMION[tipo-1]
    self.peso = peso
    if estado in range(1,5):
      self.estado = self.ESTADO_CAMION[estado]

  
  def __str__(self):
    return ("Camion %i -> tipo %i - peso %i" % (self.nro_camion, self.tipo, self.peso))

  def __repr__(self):
    return ("Camion %i -> tipo %i - peso %i" % (self.nro_camion, self.tipo, self.peso))

  '''def cargar_pesos_sin_carga(self):
    #aca se cargan los pesos de cada camión segun el tipo que le toco. Ver tabla 2'''

class Balanza:  
  def __init__(self, nombre):
    self.nombre = nombre
    self.cola_camiones = []
    self.camion_en_balanza = None


  def encolar_camion(self, camion):
    #aca se agrega un camion a la cola de camiones
    self.cola_camiones.append(camion)

  def desencolar_camion(self):
    #aca se retorna el primer camion de la cola de camiones
    try:
      return self.cola_camiones.pop(0)
    except:
      print("La cola está vacía")
      return None

  def cola_es_vacia(self):
    #metodo que indica si la cola esta vacia
    return self.cola_camiones == []

  def balanza_esta_libre(self):
    return self.camion_en_balanza == None

  def camion_a_balanza(self, camion):
    self.camion_en_balanza = camion


class FabricaTextil:
  camiones = []
  balanza_planta = None
  balanza_barraca = None

  def __init__(self, max_camiones):
    self.balanza_planta = Balanza("Balanza Planta")
    self.balanza_barraca = Balanza("Balanza Barraca")
    for i in range(max_camiones):
      
      tipo_camion = random.randint(1,4) 

      camion = Camion(i+1, tipo_camion, 0, 1)
      self.camiones.append(camion)


