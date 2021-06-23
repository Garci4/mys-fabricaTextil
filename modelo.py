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

class Balanza:
  nombre = None
  cola_camiones = []
  camion_en_balanza = None

  def __init__(self, nombre):
    self.nombre = nombre

  def encolar_camion(self):
    #aca se agrega un camion a la cola de camiones

  def desencolar_camion(self):
    #aca se quita un camion a la cola de camiones y se pone en camion_en_balanza

  def cola_es_vacia(self):
    #metodo que establece si la cola esta vacia

class FabricaTextil:
  camiones = []
  balanzas = []

  def __init__(self, max_camiones):
    self._cargar_balanzas()
    for i in range(max_camiones-1):
      tipo_camion = random.randint(1,4)
      camion = Camion(i+1, tipo_camion, 0, 1)
      self.camiones.append(camion)

  def _cargar_balanzas(self):
    balanza_planta = Balanza("Balanza Planta")
    balanza_barraca = Balanza("Balanza Barraca")
    self.balanzas.append(balanza_planta)
    self.balanzas.append(balanza_barraca)

ft = FabricaTextil(20)
print(ft.camiones[1].tipo)

