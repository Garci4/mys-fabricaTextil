from modelo import Camion, Balanza, FabricaTextil

import matplotlib.pyplot as pyplot
import seaborn as sns
import pandas as pd
import numpy as numpy

import sys
import seaborn as sns

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

  DIAS = 50
  HS_TRABAJO_X_DIA = 15
  meses_contados = []
  #delta indica cuanto es el avance del reloj y reloj va a llevar el avance del tiempo
  delta = 1
  reloj = None
  avance_reloj = None
  tope_reloj = HS_TRABAJO_X_DIA * DIAS * 60
  dia_trabajo_completo = HS_TRABAJO_X_DIA * 60
  mes_trabajo_completo = dia_trabajo_completo * 10
  meses = 0
  reloj_meses = 0
  #tope_reloj = 500

  #Tiempo que toma completar un ciclo de produccion en minutos
  TIEMPO_PRODUCCION = 10
  

  '''ESTAS VARIABLES TIENEN LA CANTIDAD TOTAL DE MINUTOS QUE LAS BALANZAS ESTUVIERON OCIOSAS'''
  tmr_balanza_planta_libre = 0
  aux_tmr_balanza_planta_libre = 0

  tmr_balanza_barraca_libre = 0
  aux_tmr_balanza_barraca_libre = 0
  
  '''ACA SE ARMA LA LISTA PARA LOS GRAFICOS'''
  balanza_barraca_libre_por_mes = []
  balanza_planta_libre_por_mes = []
  
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
  
  #tabla 1
  def peso_camion_sin_carga(self, tipo_camion):
    if tipo_camion == 1:
      return 31
    if tipo_camion == 2:
      return 25
    if tipo_camion == 3:
      return 37
    if tipo_camion == 4:
      return 45 

  #tabla 2 - No se permite que el peso del camion sea menor al peso del camion sin carga
  def calcular_pesaje_segun_tipo_camion(self, tipo_camion):
    if tipo_camion == 1:
      _peso = round(norm.rvs(loc=34, scale=6.2))
      while _peso < self.peso_camion_sin_carga(tipo_camion):
        _peso = round(norm.rvs(loc=34, scale=6.2))
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

  def _balanzas_ociosas(self, avance_reloj):
    if self.fabrica_textil.balanza_barraca.balanza_esta_libre():
      print("balanza libre: ", self.fabrica_textil.balanza_barraca.balanza_esta_libre())
      self.tmr_balanza_barraca_libre += avance_reloj
      
    if self.fabrica_textil.balanza_planta.balanza_esta_libre():
      print("planta libre: ", self.fabrica_textil.balanza_planta.balanza_esta_libre())
      self.tmr_balanza_planta_libre += avance_reloj
      
  def _promedio_diario_balanzas_ociosas(self):
    dias_trabajados = self.tope_reloj/self.dia_trabajo_completo
    promedio_bb = self.tmr_balanza_barraca_libre/dias_trabajados
    promedio_bp = self.tmr_balanza_planta_libre/dias_trabajados
    return {
      'balanza_planta': promedio_bp,
      'balanza_barraca': promedio_bb
    }

  def _promedio_mensual_balanzas_ociosas(self):
    meses_trabajados = self.tope_reloj/(self.mes_trabajo_completo)
    promedio_bb = self.tmr_balanza_barraca_libre/meses_trabajados
    promedio_bp = self.tmr_balanza_planta_libre/meses_trabajados
    return {
      'balanza_planta': promedio_bp,
      'balanza_barraca': promedio_bb
    }

  '''Este m??todo guarda en las listas de abajo '''
  def _agregar_datos_estad??sticos(self):
    bplpm = self.balanza_planta_libre_por_mes
    if len(bplpm)>1:
      anterior_planta = bplpm[len(bplpm)-1]
      bplpm.append((self.reloj-self.tmr_balanza_planta_libre)-anterior_planta)
    else:
      bplpm.append(self.reloj-self.tmr_balanza_planta_libre)

    bblpm = self.balanza_barraca_libre_por_mes
    if len(bblpm)>1:
      anterior_barraca = bblpm[len(bblpm)-1]
      bblpm.append((self.reloj-self.tmr_balanza_barraca_libre)-anterior_barraca)
    else:
      bblpm.append(self.reloj-self.tmr_balanza_planta_libre)

  def _promedio_anual_balanzas_ociosas(self):
    promedio_bb = self.tmr_balanza_barraca_libre/self.tope_reloj
    promedio_bp = self.tmr_balanza_planta_libre/self.tope_reloj
    return {
      'balanza_planta': promedio_bp,
      'balanza_barraca': promedio_bb
    }

  def simular(self):
    self.eventos_futuros = self.inicio_simulacion(self.fabrica_textil.camiones)
    self.print_eventos(self.eventos_futuros)
    self.reloj = 0
    self.reloj_meses = 0
    with open('salida.txt','w') as texto:
      for a in range(1):
        #inicializo las variables de los tiempos para este anio
        while self.eventos_futuros != [] and self.tope_reloj >= self.reloj:
          e = self.eventos_futuros.pop(0)
          self.avance_reloj = (e.cuando_ocurre-self.reloj)        
          print("RELOJ: ", self.reloj)
          #Si el avance del reloj son 50 minutos y el reloj_meses se pasa de un mes reseteo reloj_meses y cuento que paso un mes 
          if self.avance_reloj < 10 and self.reloj_meses+15 > self.mes_trabajo_completo:
            print ("PASO UN MES")
            print (self.reloj_meses)
            print (self.mes_trabajo_completo)
            self.meses += 1
            self.meses_contados.append(self.meses)
            self._agregar_datos_estad??sticos()
            self.reloj_meses = 0
          self.reloj += self.avance_reloj
          self.reloj_meses += self.avance_reloj
          self._balanzas_ociosas(self.avance_reloj)   
          texto.write("-------------------------------------------------------------------------------\n")
          texto.write("RELOJ: %i\n" % self.reloj)
          texto.write("Avance Reloj: %i\n" % self.avance_reloj)
          texto.write("Reloj meses: %i\n" % self.reloj_meses)
          texto.write("Mes trabajo completo %i\n" % self.mes_trabajo_completo)
          texto.write("BP libre: %i\n" % self.tmr_balanza_planta_libre)
          texto.write("BB libre: %i\n" % self.tmr_balanza_barraca_libre)
          texto.write("producto terminado en planta: %i\n" % self.producto_terminado_en_planta)
          texto.write("materia prima en barraca: %i\n" % self.materia_prima_barraca)
          texto.write("producto terminado centro dist: %i\n" % self.producto_terminado_en_centro_dist)
          texto.write("-------------------------------------------------------------------------------\n\n")
          if e.tipo == 99:
            self.producir_producto_terminado_en_planta(self.reloj)
          if e.tipo == 1:
            c = e.camion 
            tiempo_viaje = self.calcular_tiempo_viaje_camion(c.tipo)
            _evento = Evento(c, self.reloj+tiempo_viaje, 4)
            self.agregar_evento(_evento)
          
          #no se encola porque no hay nada en la cola, pasa derecho a la balanza
          if e.tipo == 4:
            c = e.camion
            bp = self.fabrica_textil.balanza_planta
            if bp.balanza_esta_libre():
              bp.camion_a_balanza(c)
              tiempo_pesado = self.calcular_tiempo_pesaje(bp.camion_en_balanza)  
              _evento = Evento(c, self.reloj+tiempo_pesado, 6)
              self.agregar_evento(_evento)
            else:
              bp.encolar_camion(c) #evento 3, camion se encola porque la balanza esta ocupada

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
            #el camion ahora no est?? cargado
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
    texto.close()        
          
    def crear_txt(self):
      with open('estadisticas.txt','w') as texto:
        for item in self.balanza_barraca_libre_por_mes:
          texto.write("El promedio mensual de la balanza barraca ociosa mensual es %s\n" % item)
        for item in self.balanza_planta_libre_por_mes:
          texto.write("El promedio mensual de la balanza planta ociosa mensual es %s\n" % item)
        texto.close()
      #archivo_texto=open("estadisticas.txt","w")
      #archivo_texto.write('El promedio de balanza barraca ociosa diario es: ',)
      #archivo_texto.write('\nEl promedio de balanza planta ociosa diario es: ')
      #archivo_texto.write('\n--------------------------------------------------------------------------------')
      #archivo_texto.write('\nEl promedio de balanza barraca ociosa mensual es: ', (self.balanza_barraca_libre_por_mes))
      #archivo_texto.write('\nEl promedio de balanza planta ociosa mensual es: ',self.balanza_planta_libre_por_mes)
      #archivo_texto.close()

    #aca van las estad??siticas
    print (self._promedio_diario_balanzas_ociosas())
    print ("Pasaron ",self.meses," meses \n")
    print ("\nEl promedio de balanza planta ociosa mensual es: ", self.balanza_planta_libre_por_mes)
    print ("\nEl promedio de balanza barraca ociosa mensual es: ", self.balanza_barraca_libre_por_mes)
    print ("\nEl promedio de balanzas ociosas diario es: ",self._promedio_diario_balanzas_ociosas())
    print ("\nEl promedio de balanzas ociosas mensual es: ",self._promedio_mensual_balanzas_ociosas())
    print ("\nEl promedio de balanzas ociosas anual es: ",self._promedio_anual_balanzas_ociosas())

    crear_txt(self)

    #grafico de barras tiempo ocioso balanza barraca 
    pyplot.bar(range(5),self.balanza_barraca_libre_por_mes)
    pyplot.xticks(range(self.meses),self.meses_contados)
    pyplot.title("Grafico de barras balanza barraca libre por mes")
    pyplot.ylim(min(self.balanza_barraca_libre_por_mes) - 1, max(self.balanza_barraca_libre_por_mes)+1)
    pyplot.savefig('Balanza Barraca libre.pdf')
    pyplot.show()

    #grafico de barras tiempo ocioso balanza planta
    pyplot.bar(range(5),self.balanza_planta_libre_por_mes)
    pyplot.xticks(range(self.meses),self.meses_contados)
    pyplot.title("Grafico de barras balanza planta libre por mes")
    pyplot.ylim(min(self.balanza_planta_libre_por_mes) - 1, max(self.balanza_planta_libre_por_mes)+1)
    pyplot.savefig('Balanza Planta libre.pdf')
    pyplot.show()

sim = Simulacion(3)
sim.simular()

