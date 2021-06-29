from modelo import Camion, Balanza, FabricaTextil

import sys

#Distribuciones
from scipy.stats import uniform
from scipy.stats import norm
from scipy.stats import expon

TIPO_EVENTO = {
  '1': 'fin carga camion en barraca/inicio tiempo viaje',
  '2': 'inicio carga camion en barraca',
  '3': 'fin de viaje a balanza planta/se encola o pasa derecho a balanza',
  '4': '4',
  '5': '5',
  '6': '6',
  '7': '7',
}

class Evento:
  camion = None
  #valor del reloj cuando se crea + la demora obtenida de hacer el evento
  cuando_ocurre = None
  tipo = None

  def __init__(self, camion, cuando_ocurre, tipo):
    self.camion = camion
    self.cuando_ocurre = cuando_ocurre
    self.tipo = tipo

class Simulacion:

  fabrica_textil = None

  DIAS = 300
  HS_TRABAJO_X_DIA = 15
  #delta indica cuanto es el avance del reloj y reloj va a llevar el avance del tiempo
  delta = 1
  reloj = None
  tope_reloj = HS_TRABAJO_X_DIA * DIAS * 60
  
  tmr_balanzas_libres = None
  tmr_espera_camiones_en_cola = None
  nro_puntos_criticos_alcanzados = None

  #esta lista de eventos tiene que estar ordenada segun cuando_ocurre de menor a mayor
  eventos_futuros = []

  def __init__(self, nro_camiones):
    self.fabrica_textil = FabricaTextil(nro_camiones)
    self.reloj = 0

  #tabla 3
  def calcular_demora_carga_camion(self, tipo_camion):
    if tipo_camion == 1:
      return 23
    if tipo_camion == 2:
      return 20
    if tipo_camion == 3:
      return 28
    if tipo_camion == 4:
      return 35 

  #tabla 2
  def calcular_pesaje_segun_tipo_camion(self, tipo_camion):
    if tipo_camion == 1:
      return norm.rvs(loc=32, scale=6.2)
    if tipo_camion == 2:
      return norm.rvs(loc=27.5, scale=4.5)
    if tipo_camion == 3:
      return norm.rvs(loc=40, scale=2.3)
    if tipo_camion == 4:
      return norm.rvs(loc=49, scale=1.4)

  #definimos cada evento
  def inicio_simulacion(self, camiones):
    #por cada camion, generar un evento que contemple el tiempo de carga de c/camion, mas el tiempo de pesaje en barraca
    #devolver lista de eventos
    demora_total = 0
    eventos = []
    for c in camiones:
      c.peso = self.calcular_pesaje_segun_tipo_camion(c.tipo)
      demora = self.calcular_demora_carga_camion(c.tipo)
      demora_total += demora
      print ("camion: %i -- peso: %i -- demora: %i --- Demora total: %i" % (c.nro_camion, c.peso, demora, demora_total))
      e = Evento(c, demora_total, 1)
      print ("evento cuando ocurre: %i -- tipo: %i" % (e.cuando_ocurre, e.tipo))
      eventos.append(e)
    
    return eventos

  #Recibe un tipo de camion y devuelve su tiempo de viaje
  def calcular_tiempo_viaje_camion(self, tipo_camion):
    if tipo_camion == 1:
      return round(norm.rvs(loc=29, scale=5.1))
    if tipo_camion == 2:
      return round(norm.rvs(loc=30, scale=6.4))
    if tipo_camion == 3:
      return round(norm.rvs(loc=35, scale=8))
    if tipo_camion == 4:
      return round(norm.rvs(loc=38, scale=12.3))

  ''' reloj += evento.cuando_ocurre
          if evento.tipo == "":
            #recalcular cual es el evento futuro
            cuando ocurre = reloj + tiempo
            #meter en eventos_futuros y reordenar por cuando_ocurre
          if evento.tipo == "":
          if evento.tipo == "":
          if evento.tipo == "":
          if evento.tipo == "":
          if evento.tipo == "":
          if evento.tipo == "":'''
  def simular(self):
    self.eventos_futuros = self.inicio_simulacion(self.fabrica_textil.camiones)
    self.reloj = 0
    for a in range(1):
      #inicializo las variables de los tiempos para este anio
      for m in range(self.tope_reloj):
        while self.eventos_futuros != []:
          e = self.eventos_futuros.pop(0)
          self.reloj += e.cuando_ocurre
          if e.tipo == 1:
            c = e.camion 
            tiempo_viaje = self.calcular_tiempo_viaje_camion(c.tipo)
            #print ("tiempo de viaje de evento camion %i = %i" % (c.nro_camion, tiempo_viaje))
            _evento = Evento(c, self.reloj+tiempo_viaje, 3)
            print (_evento.cuando_ocurre)
            print (_evento)
            self.eventos_futuros.append(_evento)
            print ("antes")
            print (self.eventos_futuros)
            self.eventos_futuros.sort(key=lambda x: x.cuando_ocurre, reverse=False)
            print ("desp")
            print (self.eventos_futuros)
            #print (_evento.cuando_ocurre) 



sim = Simulacion(3)
sim.simular()