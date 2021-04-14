# -*- coding: utf-8 -*-

import sys, os

FREECADPATH = os.getenv('FREECADPATH')
sys.path.append(FREECADPATH) # path to your FreeCAD.so or FreeCAD.dll filE

import FreeCAD, Sketcher
import FabCAD 				#Custom Library

nameProject = "FirstSteps"
namePart = "Pieza01"
nameBody = "Cuerpo"

# Crear un nuevo documento en blanco
doc = FabCAD.nuevoDocumento(nameProject)
doc.nuevaPieza(namePart).nuevoCuerpo(nameBody).crearPlano("Planta").crearPlano("Alzado", soporte="XZ_Plane", cuerpo = nameBody).crearPlano("Vista_Lateral", "YZ_Plane", doc.cuerpos[nameBody])

#Aclarar que estos planos se crean para que haya una referencia global en la pieza

sketch = FabCAD.nuevoSketch("sketch", doc, nameBody, soporte="Planta")

puntos = []
puntos.append([29.739,8.8786])
puntos.append([29.739,71.7241])
puntos.append([117.794,71.7241])
puntos.append([136.967,52.5509, 19.17, False])
puntos.append([136.967,8.8786])
puntos.append([29.739,8.8786])

sketch.crearPolilinea(puntos).extrusionAditiva("Test", 50, planoMedio = 1)

sketch02 = FabCAD.nuevoSketch("sketch02", doc, soporte = "Planta")
sketch02.crearPoligono(10,[50,50], 7).extrusionDeVaciado("Test02", 50, planoMedio = 1)

sketch03 = FabCAD.nuevoSketch("sketch03", doc, soporte = "Planta")
sketch03.crearLinea([152.934,38.4578], [102.066,1.54221]).crearArcoTresPuntos([152.934,38.4578], [102.066,1.54221], [148.132202,-3.356926]).revolucionAditiva()

sketch04 = FabCAD.nuevoSketch("sketch04", doc, soporte = "Planta")
sketch04.crearPolilinea([[71.5256,-5.78647], [71.5256,23.524], [89.308,8.86878], [71.5256,-5.78647]]).revolucionDeVaciado()

#Se crea un plano con un offset de 25mm para que quede en la superficie de la primer extrusion
#ya que aqui empezara una operacion de extrusion de saliente recubierta
doc.crearPlano("basePrisma", "Planta", nameBody, offsets=[0,0,25])
doc.crearPlano("techoPrisma", "Planta", nameBody, offsets=[0,0,75])

sketch05 = FabCAD.nuevoSketch("sketch05", doc, nameBody, soporte="basePrisma").crearRectanguloEsquinas([86.294,39.2519],[112.215,65.1726])
sketch06 = FabCAD.nuevoSketch("sketch06", doc, nameBody, soporte="techoPrisma").crearRectanguloEsquinas([92.2162,52.2524],[105.737,53.3337])

sketch05.recubrir(sketch06)

doc.crearPlano("inicioCorteRecubierto", "Vista_Lateral", nameBody, offsets=[0,0,155], rotaciones=[22.5, -45, 0])
doc.crearPlano("mitadCorteRecubierto", "Vista_Lateral", nameBody, offsets=[0,0,155], rotaciones=[90, 0, 0])
doc.crearPlano("finCorteRecubierto", "Vista_Lateral", nameBody, offsets=[0,0,155], rotaciones=[-22.5, -45, 0])

sketch07 = FabCAD.nuevoSketch("sketch07", doc, nameBody, soporte="inicioCorteRecubierto").crearCirculo([-3.2,-25], 7.5)
sketch08 = FabCAD.nuevoSketch("sketch08", doc, nameBody, soporte="mitadCorteRecubierto").crearCirculo([16.296404,-19.677139], 6.5)
sketch09 = FabCAD.nuevoSketch("sketch09", doc, nameBody, soporte="finCorteRecubierto").crearCirculo([-3.2,25], 5.5)

sketch07.recubrirCorte([sketch08, sketch09])

doc.nuevoSketch("perfilBarrido", soporte = "Planta").dibujos["perfilBarrido"].crearPoligono(4, [0,0], lados = 3).corteConducido("sketch")

sketch10 = FabCAD.nuevoSketch("sketch10", doc, nameBody, soporte="basePrisma")
sketch10.copiarGeometriaCroquis("sketch")

doc.crearPlano("fondoPieza", "Planta", nameBody, offsets=[0,0,-25])
sketch11 = FabCAD.nuevoSketch("sketch11", doc, nameBody, soporte="fondoPieza")
sketch11.copiarGeometriaCroquis("sketch")

sketch12 = FabCAD.nuevoSketch("sketch12",doc,False,soporte="Planta").crearCirculo(radio=2.5).salienteConducida(sketch10)
sketch13 = FabCAD.nuevoSketch("sketch13",doc,False,soporte="Planta").crearCirculo(radio=2.5).salienteConducida(sketch11, nombreExtrusion="salienteConducida02")

from FabCAD.mallado import Mallas

Mallas().exportarEnSTL(doc.cuerpos[nameBody])

#puntos = []
#puntos.append([152.934,38.4578])
#puntos.append([102.066,1.54221])
#puntos.append([152.934,38.4578, 35])

#sketch03 = FabCAD.nuevoSketch("sketch03", doc, soporte = "Planta").crearPolilinea(puntos).revolucionAditiva()

"""
doc = FabCAD.nuevoDocumento(nameProject)

# Crea una nueva pieza vinculada al documento que acabamos de crear y un nuevo cuerpo sin vinculos a ninguna pieza
pieza = FabCAD.nuevaPieza(doc, namePart) 
cuerpo = FabCAD.nuevoCuerpo(doc, nameBody)

#COMPLETADO Crear metodo de clase para vincular objetos del documento a traves del MethodChaining
# Se vincula el cuerpo previamente creado a la pieza creada al inicio
doc.vincularObjetos(pieza, cuerpo)

# Se crean los planos de Planta, Alzado y Vista Lateral vinculados a los planos base la PIEZA
doc.crearPlano("Planta") 											#Creacion de plano con solo 2 argumentos
doc.crearPlano("Alzado", soporte="XZ_Plane", cuerpo = nameBody) 	#Creacion de plano mediante diccionario
doc.crearPlano("Vista_Lateral", "YZ_Plane", doc.cuerpos[nameBody]) 	#Sin diccionario y con objeto

nuevoSketch = doc.nuevoSketch("sketch", doc.cuerpos[nameBody], doc.planos["Planta"])
"""

#Creacion de nuevos documentos al mismo tiempo
docTest = FabCAD.nuevoDocumento()
docTest.nuevaPieza(namePart).nuevoCuerpo(nameBody).crearPlano("Planta").crearPlano("Alzado", soporte="XZ_Plane", cuerpo = nameBody).crearPlano("Vista_Lateral", "YZ_Plane", docTest.cuerpos[nameBody]).nuevoSketch("sketchTest", False, "Alzado")

sketchTest = docTest.dibujos["sketchTest"]

"""
#Se cambia el objeto que se encuentra activo, esto puede lograrse de dos formas, la segunda permite el encadenamiento
doc.objetoActivo = namePart
doc.hacerActivo(namePart).crearPlano("testPieza").sketch("testSketch",False,"testPieza")
"""

#############################################
sumaX = 0
longitudH = 20
longitudLinea = 10

#Note the use of FreeCAD original library inside the custom library wrap inside doc.base variable 
for linea in range(3):
	sketchTest.crearLinea( [ (2 + sumaX) , 2] , [(12 + sumaX), 12] )
	docTest.base.getObject("sketchTest").addConstraint(Sketcher.Constraint('Distance', linea, longitudLinea)) 

	if linea > 0:
		docTest.base.getObject("sketchTest").addConstraint(Sketcher.Constraint('Parallel',  linea -1, linea)) 
		docTest.base.getObject("sketchTest").addConstraint(Sketcher.Constraint('Horizontal', linea - 1, 1, linea, 1)) 		
		docTest.base.getObject("sketchTest").addConstraint(Sketcher.Constraint('DistanceX', linea - 1, 1, linea, 1, FreeCAD.Units.Quantity('{} mm'.format( longitudH )))) 

	sumaX =sumaX + 20
	longitudLinea += 10

docTest.base.getObject("sketchTest").addConstraint(Sketcher.Constraint('Angle',0,1,-1,2, FreeCAD.Units.Quantity('135.000000 deg'))) 

puntos = []

puntos.append([47,40])
puntos.append([54,55])
puntos.append([64,33])

#COMPLETADO Poder añadir un arco si la longitud de la lista es 3 [x,y, radio]
puntos.append([69,48,30])

puntos.append([69,48])
puntos.append([74,38])
puntos.append([83,60])

#Uso desquiciado del method chaining xD
sketchTest.crearRectanguloEsquinas([100, 10],[140, 20]).crearRectanguloEsquinas([100, 40],[140, 60]).crearCirculo([25, 50], 15).crearCirculo([150, 50], 15).crearPolilinea(puntos).crearPoligono(10).crearPoligono(12.5, [20, 100], 8).crearPoligono(15, [60, 110], 4).crearPoligono(10, [33, -17], 3).crearRanura([2,1], [8,5], 2)
sketchTest.crearPoligono(10, [200,200], 5)

"""
nuevoSketch.crearRectanguloEsquinas([100, 10],[140, 20])
nuevoSketch.crearRectanguloEsquinas([100, 40],[140, 60])

nuevoSketch.crearCirculo([25, 50], 15)
nuevoSketch.crearCirculo([150, 50], 15)

puntos = []

puntos.append([47,40])
puntos.append([54,55])
puntos.append([64,33])
puntos.append([69,48])
puntos.append([74,38])
puntos.append([83,60])

nuevoSketch.crearPolilinea(puntos)

nuevoSketch.crearPoligono(10)
nuevoSketch.crearPoligono(12.5, [20, 100], 8)
nuevoSketch.crearPoligono(15, [60, 110], 4)
nuevoSketch.crearPoligono(10, [33, -17], 3)
"""

# TODO Leer libro de solidworks para basar la documentación de FreeCAD 0.19
# Test para actualizacion del analisis de seguridad de LGMT
# HACK Idea: Poder crear lineas con solo un punto y definiendo su longitud y angulo de inclinacion
# e ir agregando mas geometria que pueda ser creada de esta forma como rectangulos (Un punto y alto y ancho),
# arcos (un punto, Perimetro +- para direccion y angulo de inicio)

# TODO Preguntar acerca de la posibilidad de agregar colores a los objetos aunque esto sea unicamente util
# para la interfaz grafica y la libreria este hecha para servir sin esta.

doc.base.recompute()