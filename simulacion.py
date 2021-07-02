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
  '7': 'fin de descarga mat prima en planta/ carga de prod terminado',
  '8': 'fin viaje a centro distribucion'
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

  def __str__(self, camion):
    if camion is not None:
      return ("E -> Ocurre en: %i - Tipo %i - Camion %i" % (self.cuando_ocurre, self.tipo, self.camion.nro_camion))
    else:  
      return ("E -> Ocurre en: %i - Tipo %i" % (self.cuando_ocurre, self.tipo))

class Simulacion:

  fabrica_textil = None

  DIAS = 300
  HS_TRABAJO_X_DIA = 15
  #delta indica cuanto es el avance del reloj y reloj va a llevar el avance del tiempo
  delta = 1
  reloj = None
  tope_reloj = HS_TRABAJO_X_DIA * DIAS * 60
  #tope_reloj = 500

  #Tiempo que toma completar un ciclo de produccion en minutos
  TIEMPO_PRODUCCION = 10
  
  tmr_balanzas_libres = None
  tmr_espera_camiones_en_cola = None
  nro_puntos_criticos_alcanzados = None

  #esta lista de eventos tiene que estar ordenada segun cuando_ocurre de menor a mayor
  eventos_futuros = []
  materia_prima_ciclo_prod = 0  
  #asumimos que empieza con 30000 toneladas
  materia_prima_barraca = 30000
  producto_terminado_en_planta = 30
  producto_terminado_en_centro_dist = 0

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

  def peso_camion_sin_carga(self, tipo_camion):
    if tipo_camion == 1:
      return 31
    if tipo_camion == 2:
      return 25
    if tipo_camion == 3:
      return 37
    if tipo_camion == 4:
      return 45 

  #tabla 2
  def calcular_pesaje_segun_tipo_camion(self, tipo_camion):
    if tipo_camion == 1:
      _peso = round(norm.rvs(loc=32, scale=6.2))
      while _peso < self.peso_camion_sin_carga(tipo_camion):
        _peso = round(norm.rvs(loc=32, scale=6.2))
      return _peso
    if tipo_camion == 2:
      _peso = round(norm.rvs(loc=27.5, scale=4.5))
      while _peso < self.peso_camion_sin_carga(tipo_camion):
        _peso = round(norm.rvs(loc=27.5, scale=4.5))
      return _peso
    if tipo_camion == 3:
      _peso = round(norm.rvs(loc=40, scale=2.3))
      while _peso < self.peso_camion_sin_carga(tipo_camion):
        _peso = round(norm.rvs(loc=40, scale=2.3))
      return _peso
    if tipo_camion == 4:
      _peso = round(norm.rvs(loc=49, scale=1.4))
      while _peso < self.peso_camion_sin_carga(tipo_camion):
        _peso = round(norm.rvs(loc=49, scale=1.4))
      return _peso

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
      e = Evento(c, demora_total, 1)
      print ("INICIO SIMULACION")
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
  def calcular_tiempo_pesaje(self, camion):
    return round(norm.rvs(loc=10, scale=3))

  #metodo que imprime la lista de eventos en un formato que nos gusta
  def print_eventos(self, eventos):
    for i in eventos:
      print (i.__str__(i.camion))

  def producir_producto_terminado_en_planta(self, ahora):
    if self.materia_prima_ciclo_prod >= 1.1:
      self.materia_prima_ciclo_prod -= 1.1
      demora = round(expon.rvs(scale=5)) + self.TIEMPO_PRODUCCION
      self.producto_terminado_en_planta += 1
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
    self.print_eventos(self.eventos_futuros)
    self.reloj = 0
    for a in range(1):
      #inicializo las variables de los tiempos para este anio
      while self.eventos_futuros != [] and self.tope_reloj >= self.reloj:
        e = self.eventos_futuros.pop(0)
        self.reloj += (e.cuando_ocurre-self.reloj)
        print("-------------------------------------------------------------------------------")
        print("RELOJ: ", self.reloj)
        print("producto terminado en planta: ", self.producto_terminado_en_planta)
        print("materia prima en barraca: ", self.materia_prima_barraca)
        print("producto terminado centro dist: ", self.producto_terminado_en_centro_dist)
        print("-------------------------------------------------------------------------------")
        if e.tipo == 99:
          self.producir_producto_terminado_en_planta(self.reloj)
        if e.tipo == 1:
          c = e.camion 
          tiempo_viaje = self.calcular_tiempo_viaje_camion(c.tipo)
          bp = self.fabrica_textil.balanza_planta
          _evento = Evento(c, self.reloj+tiempo_viaje, 4)
          self.agregar_evento(_evento)
          #print (_evento.cuando_ocurre) 
        
        #no se encola porque no hay nada en la cola, pasa derecho a la balanza
        if e.tipo == 4:
          c = e.camion
          bp = self.fabrica_textil.balanza_planta
          if bp.balanza_esta_libre() :
            bp.camion_a_balanza(c)
            tiempo_pesado = self.calcular_tiempo_pesaje(bp.camion_en_balanza)  
            _evento = Evento(c, self.reloj+tiempo_pesado, 6)
            self.agregar_evento(_evento)
          else:
            bp.encolar_camion(c)

        #fin de pesado en planta y pasa a descargar en planta
        #libero la balanza
        if e.tipo == 6:
          c = e.camion
          bp = self.fabrica_textil.balanza_planta
          bp.camion_en_balanza = None
          if bp.cola_es_vacia() == False:
            _evento = Evento(bp.desencolar_camion(), self.reloj, 4)
            self.agregar_evento(_evento)
          tiempo_descarga = self.calcular_demora_carga_camion(c.tipo)
          _evento = Evento(c, self.reloj+tiempo_descarga, 7)
          self.agregar_evento(_evento)

        #fin de descarga materia prima en planta / carga de prod terminado en planta
        if e.tipo == 7:
          #la carga del camion pasa al inventario de la planta para ciclo de prod
          materia_prima_descargada = e.camion.peso - self.peso_camion_sin_carga(e.camion.tipo)
          self.materia_prima_ciclo_prod += materia_prima_descargada
          if not self.se_esta_produciendo():
            self.producir_producto_terminado_en_planta(self.reloj)
          #el camion ahora no está cargado
          e.camion.peso = self.peso_camion_sin_carga(e.camion.tipo)

          #ahora el camion debe cargarse con producto terminado
          _peso_nuevo = self.calcular_pesaje_segun_tipo_camion(e.camion.tipo)
          #cptc = cantidad producto terminado a cargar
          cptc = _peso_nuevo - e.camion.peso
          if cptc <= self.producto_terminado_en_planta:
            self.producto_terminado_en_planta -= cptc
            e.camion.peso = _peso_nuevo
          else:
            cptc = self.producto_terminado_en_planta
            self.producto_terminado_en_planta = 0
            e.camion.peso += cptc              

          #ahora el camion parte al centro de distribucion
          tiempo_viaje = self.calcular_tiempo_viaje_camion(e.camion.tipo)
          _evento = Evento(e.camion, self.reloj+tiempo_viaje, 8)
          self.agregar_evento(_evento)

        #Fin de viaje al centro de dist / inicio de descarga de producto terminado
        if e.tipo == 8:
          c = e.camion
          tiempo_descarga = self.calcular_demora_carga_camion(c.tipo)
          _evento = Evento(c, self.reloj+tiempo_descarga, 9)
          self.agregar_evento(_evento)
        
        #fin de descarga del camion / inicio de viaje a la barraca
        if e.tipo == 9:
          c = e.camion
          self.producto_terminado_en_centro_dist += c.peso - self.peso_camion_sin_carga(c.tipo)
          c.peso = self.peso_camion_sin_carga(c.tipo)
          tiempo_viaje = self.calcular_tiempo_viaje_camion(c.tipo)
          bb = self.fabrica_textil.balanza_barraca
          _evento = Evento(c, self.reloj+tiempo_viaje, 11)
          self.agregar_evento(_evento)
       
        #no se encola porque no hay nada en la cola de la barraca, pasa derecho a la balanza
        if e.tipo == 11:
          c = e.camion
          bb = self.fabrica_textil.balanza_barraca
          if bb.balanza_esta_libre():
            bb.camion_a_balanza(c)
            tiempo_pesado = self.calcular_tiempo_pesaje(bb.camion_en_balanza)
            _evento = Evento(c, self.reloj+tiempo_pesado, 13)
            self.agregar_evento(_evento)
          else:
            bb.encolar_camion(c)

        #fin de pesado e inicio de carga en la barraca de materia prima
        if e.tipo == 13:
          c = e.camion
          bb = self.fabrica_textil.balanza_barraca
          bb.camion_en_balanza = None
          if bb.cola_es_vacia() == False:
            _evento = Evento(bb.desencolar_camion(), self.reloj, 11)
            self.agregar_evento(_evento)
          _nuevo_peso = self.calcular_pesaje_segun_tipo_camion(c.tipo)
          cantidad_materia_prima = _nuevo_peso - c.peso
          if cantidad_materia_prima <= self.materia_prima_barraca:
            self.materia_prima_barraca -= cantidad_materia_prima
            c.peso = _nuevo_peso
          else:
            c.peso += self.materia_prima_barraca
            self.materia_prima_barraca = 0
          tiempo_carga = self.calcular_demora_carga_camion(c.tipo)
          _evento = Evento(c, self.reloj+tiempo_carga, 14)
          self.agregar_evento(_evento)

        if e.tipo == 14:
          c = e.camion
          tiempo_descarga = self.calcular_demora_carga_camion(c.tipo)
          _evento = Evento(c, self.reloj+tiempo_descarga, 1)
          self.agregar_evento(_evento)

        self.print_eventos(self.eventos_futuros)
        print("corte")


sim = Simulacion(20)
sim.simular()