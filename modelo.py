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

class FabricaTextil:
  camiones = []

  def __init__(self, max_camiones):
    for i in range(max_camiones-1):
      tipo_camion = random.randint(1,4)
      camion = Camion(i+1, tipo_camion, 0, 1)
      self.camiones.append(camion)


ft = FabricaTextil(20)
print(ft.camiones[1].tipo)

