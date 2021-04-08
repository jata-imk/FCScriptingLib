# -*- coding: utf-8 -*-

import sys, os
import FreeCAD, Sketcher

FREECADPATH = os.getenv('FREECADPATH')
sys.path.append(FREECADPATH) # path to your FreeCAD.so or FreeCAD.dll filE

import FabCAD #Custom Library

nameProject = "FirstSteps"
namePart = "Pieza01"
nameBody = "Cuerpo"

# Crear un nuevo documento en blanco
doc = FabCAD.nuevoDocumento(nameProject)
doc.nuevaPieza(namePart).nuevoCuerpo(nameBody).crearPlano("Planta").crearPlano("Alzado", soporte="XZ_Plane", cuerpo = nameBody).crearPlano("Vista_Lateral", "YZ_Plane", doc.cuerpos[nameBody])

sketch = FabCAD.nuevoSketch("sketch", doc, nameBody, soporte="Planta")

puntos = []
puntos.append([29.739,8.8786])
puntos.append([29.739,71.7241])
puntos.append([117.794,71.7241])
puntos.append([136.967,52.5509, 19.17, False])
puntos.append([136.967,8.8786])
puntos.append([29.739,8.8786])

sketch.crearPolilinea(puntos).extrusionAditiva("Test", 50, planoMedio = 1)

sketch02 = FabCAD.nuevoSketch("sketch02", doc, soporte = "Planta").crearPoligono(10,[50,50], 7).extrusionDeVaciado("Test02", 50, planoMedio = 1)
sketch03 = FabCAD.nuevoSketch("sketch03", doc, soporte = "Planta").crearLinea([152.934,38.4578], [102.066,1.54221]).crearArcoTresPuntos([152.934,38.4578], [102.066,1.54221], [148.132202,-3.356926])

#puntos = []
#puntos.append([152.934,38.4578])
#puntos.append([102.066,1.54221])
#puntos.append([152.934,38.4578, 35])
#
#sketch03 = FabCAD.nuevoSketch("sketch03", doc, soporte = "Planta").crearPolilinea(puntos)

sketch03.revolucionAditiva()

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
sketchTest = doc.sketch("sketchTest", False, "Alzado")

#Se cambia el objeto que se encuentra activo, esto puede lograrse de dos formas, la segunda permite el encadenamiento
doc.objetoActivo = namePart
doc.hacerActivo(namePart).crearPlano("testPieza").sketch("testSketch",False,"testPieza")

#############################################
sumaX = 0
longitudH = 20
longitudLinea = 10

#Note the use of FreeCAD original library inside the custom library wrap inside doc.base variable 
for linea in range(3):
	sketch.crearLinea( [ (2 + sumaX) , 2] , [(12 + sumaX), 12] )
	doc.base.getObject("sketch").addConstraint(Sketcher.Constraint('Distance', linea, longitudLinea)) 

	if linea > 0:
		doc.base.getObject("sketch").addConstraint(Sketcher.Constraint('Parallel',  linea -1, linea)) 
		doc.base.getObject("sketch").addConstraint(Sketcher.Constraint('Horizontal', linea - 1, 1, linea, 1)) 		
		doc.base.getObject("sketch").addConstraint(Sketcher.Constraint('DistanceX', linea - 1, 1, linea, 1, FreeCAD.Units.Quantity('{} mm'.format( longitudH )))) 

	sumaX =sumaX + 20
	longitudLinea += 10

doc.base.getObject("sketch").addConstraint(Sketcher.Constraint('Angle',0,1,-1,2, FreeCAD.Units.Quantity('135.000000 deg'))) 

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
sketch.crearRectangulo([100, 10],[140, 20]).crearRectangulo([100, 40],[140, 60]).crearCirculo([25, 50], 15).crearCirculo([150, 50], 15).crearPolilinea(puntos).crearPoligono(10).crearPoligono(12.5, [20, 100], 8).crearPoligono(15, [60, 110], 4).crearPoligono(10, [33, -17], 3).crearRanura([2,1], [8,5], 2)

sketch.crearPoligono(10, [200,200], 5)

"""
nuevoSketch.crearRectangulo([100, 10],[140, 20])
nuevoSketch.crearRectangulo([100, 40],[140, 60])

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

doc.base.recompute()