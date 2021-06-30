from modelo import Camion, Balanza, FabricaTextil

import sys

#Distribuciones
from scipy.stats import uniform
from scipy.stats import norm
from scipy.stats import expon

TIPO_EVENTO = {
  '1': 'fin carga camion en barraca/inicio tiempo viaje',
  '2': 'inicio carga camion en barraca',
  '3': 'fin de viaje a balanza planta/se encola',
  '4': 'fin de viaje a balanza planta/pasa derecho a balanza', 
  '5': 'esta encolado y pasa a balanza',
  '6': 'fin de pesado en planta/inicio descarga en planta',
  '7': 'fin de descarga en planta/...',
  '8': ''
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
  materia_prima_ciclo_prod = 0  
  producto_terminado = 0

  def __init__(self, nro_camiones):
    self.fabrica_textil = FabricaTextil(nro_camiones)
    self.reloj = 0

  def agregar_evento(self, _evento):
    self.eventos_futuros.append(_evento)
    self.eventos_futuros.sort(key=lambda x: x.cuando_ocurre, reverse=False)

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

  #definimos eventos iniciales de la simulacion
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

  #recibe un camion y devuelve el tiempo que tarda en pesarse en planta
  def calcular_tiempo_pesaje_en_planta(self, camion):
    return norm.rvs(loc=10, scale=3)

  def peso_camion_sin_carga(self, tipo_camion):
    if tipo_camion == 1:
      return 31
    if tipo_camion == 2:
      return 25
    if tipo_camion == 3:
      return 37
    if tipo_camion == 4:
      return 45 

  #metodo que imprime la lista de eventos en un formato que nos gusta
  def print_eventos(self, eventos):
          for i in eventos:
            if i.camion is not None:
              print("camion: %i - evento: %i - ocurre en: %i" %(i.camion.nro_camion, i.tipo, i.cuando_ocurre))
            else:
              print("99999999999 evento: %i - ocurre en: %i" %(i.tipo, i.cuando_ocurre))

  def producir_producto_terminado(self, ahora):
    if self.materia_prima_ciclo_prod >= 1.1:
      self.materia_prima_ciclo_prod -= 1.1
      demora = expon.rvs(scale=5)
      print("demora %i" % (demora))
      self.producto_terminado += 1
      print ("reloj: ", ahora)
      _evento = Evento(None, ahora+demora, 99)
      self.agregar_evento(_evento)

  def se_esta_produciendo(self):
    for i in self.eventos_futuros:
      if i.tipo == 99:
        return True
      else:
        return False

  def simular(self):
    self.eventos_futuros = self.inicio_simulacion(self.fabrica_textil.camiones)
    self.reloj = 0
    for a in range(1):
      #inicializo las variables de los tiempos para este anio
      for m in range(self.tope_reloj):
        while self.eventos_futuros != []:
          e = self.eventos_futuros.pop(0)
          self.reloj += (e.cuando_ocurre-self.reloj)
          if e.tipo == 99:
            self.producir_producto_terminado(self.reloj)
            print("este ocurre en: ", e.cuando_ocurre)
          if e.tipo == 1:
            c = e.camion 
            tiempo_viaje = self.calcular_tiempo_viaje_camion(c.tipo)
            print ("tiempo de viaje de evento camion %i = %i" % (c.nro_camion, tiempo_viaje))
            bp = self.fabrica_textil.balanza_planta
            if bp.balanza_esta_libre():
              _evento = Evento(c, self.reloj+tiempo_viaje, 4)
            else:
              _evento = Evento(c, self.reloj+tiempo_viaje, 3)
            self.agregar_evento(_evento)
            #print (_evento.cuando_ocurre) 
          if e.tipo == 2:
            break
          
          #se encola en la balanza de planta  
          if e.tipo == 3:
            c = e.camion
            bp = self.fabrica_textil.balanza_planta
            bp.encolar_camion(c)
          
          #no se encola porque no hay nada en la cola, pasa derecho a la balanza
          if e.tipo == 4:
            c = e.camion
            bp = self.fabrica_textil.balanza_planta
            bp.camion_a_balanza(c)
            tiempo_pesado = self.calcular_tiempo_pesaje_en_planta(bp.camion_en_balanza)
            _evento = Evento(c, self.reloj+tiempo_pesado, 6)
            self.agregar_evento(_evento)
         
          #está encolado y es su turno para pesarse
          if e.tipo == 5:
            c = e.camion
            bp = self.fabrica_textil.balanza_planta
            bp.camion_a_balanza(c)
            tiempo_pesado = self.calcular_tiempo_pesaje_en_planta(bp.camion_en_balanza) 
            _evento = Evento(c, self.reloj+tiempo_pesado, 6)
            self.agregar_evento(_evento)
          
          #fin de pesado en planta y pasa a descargar en planta
          #libero la balanza
          if e.tipo == 6:
            c = e.camion
            bp = self.fabrica_textil.balanza_planta
            if bp.cola_es_vacia() == False:
              _evento = Evento(bp.desencolar_camion(), self.reloj, 5)
              self.agregar_evento(_evento)
            tiempo_descarga = self.calcular_demora_carga_camion(c.tipo)
            _evento = Evento(c, self.reloj+tiempo_descarga, 7)
            self.agregar_evento(_evento)

          #fin de descarga en planta
          if e.tipo == 7:
            #la carga del camion pasa al inventario de la planta para ciclo de prod
            materia_prima_descargada = e.camion.peso - self.peso_camion_sin_carga(e.camion.tipo)
            self.materia_prima_ciclo_prod += materia_prima_descargada
            print ("camion %i evento: %i - materia prima: %i - RELOJ: %i" % (e.camion.nro_camion, e.tipo, self.materia_prima_ciclo_prod, self.reloj))
            if not self.se_esta_produciendo():
              self.producir_producto_terminado(self.reloj)
            #el camion ahora no está cargado
            e.camion.peso = self.peso_camion_sin_carga(e.camion.tipo)
            e.camion.estado = e.camion.ESTADO_CAMION[1]

          self.print_eventos(self.eventos_futuros)
          print("corte")


sim = Simulacion(3)
sim.simular()