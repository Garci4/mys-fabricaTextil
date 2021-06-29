from modelo import Camion, Balanza, FabricaTextil

import matplotlib.pyplot as pyplot
import seaborn as sns
import pandas as pd
import numpy as numpy
#Distribuciones
from scipy.stats import uniform
from scipy.stats import norm
from scipy.stats import expon

class Evento:
  camion = None
  #valor del reloj cuando se crea + la demora obtenida de hacer el evento
  cuando_ocurre = None
  tipo = None


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
    self.fabricaTextil = FabricaTextil(nro_camiones)
    self.reloj = 0

  def calcular_demora_carga_camion(self, camion):
    if camion.tipo == 1:
      return 23
    if camion.tipo == 2:
      return 20
    if camion.tipo == 3:
      return 28
    if camion.tipo == 4:
      return 35 

  def calcular_pesaje_segun_tipo_camion(self, camion):
    if camion.tipo == 1:
      return norm.rvs(loc=32, scale=6.2)
    if camion.tipo == 2:
      return norm.rvs(loc=27.5, scale=4.5)
    if camion.tipo == 3:
      return norm.rvs(loc=40, scale=2.3)
    if camion.tipo == 4:
      return norm.rvs(loc=49, scale=1.4)

  #definimos cada evento
  def inicio_simulacion(self, camiones):
    #por cada camion, generar un evento que contemple el tiempo de carga de c/camion, mas el tiempo de pesaje en barraca
    #devolver lista de eventos

  def inicio_carga_camion_en_barraca(self, camiones, eventos):
    #por cada camion
    #obtener el tiempo que demora cargar el camion
    for c in range(camiones):
      c.peso = self.calcular_pesaje_segun_tipo_camion(c)



  def simular(self):
    fabrica_textil = FabricaTextil(5)
    eventos_futuros = inicio_simulacion(fabrica_textil.camiones)
    reloj = 0

    for a in range(ANIOS):
      #inicializo las variables de los tiempos para este anio
      for m in range(tope_reloj):
        while eventos_futuros != []:
          evento = eventos_futuros.pop(0) 
          reloj += evento.cuando_ocurre
          if evento.tipo == "":
            #recalcular cual es el evento futuro
            cuando ocurre = reloj + tiempo
            #meter en eventos_futuros y reordenar por cuando_ocurre
          if evento.tipo == "":
          if evento.tipo == "":
          if evento.tipo == "":
          if evento.tipo == "":
          if evento.tipo == "":
          if evento.tipo == "":

    #aca una vez terminada la sim se hace todo el proceso estadistico 
    