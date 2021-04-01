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
nuevoSketch = doc.nuevoSketch("sketch", doc.cuerpos[nameBody], doc.planos["Planta"])

docTest = FabCAD.nuevoDocumento()
sketchTest = doc.nuevoSketch("sketchTest", False, "Alzado")

doc.hacerActivo(namePart).crearPlano("testPieza").nuevoSketch("testSketch",False,"testPieza")

"""

doc = FabCAD.nuevoDocumento(nameProject)

# Crea una nueva pieza vinculada al documento que acabamos de crear y un nuevo cuerpo sin vinculos a ninguna pieza
doc.nuevaPieza(namePart) 
cuerpo = doc.nuevoCuerpo(nameBody)

# Se vincula el cuerpo previamente creado a la pieza creada al inicio
#TODO Crear metodo de clase para vincular objetos del documento a traves del MethodChaining
doc.base.Pieza01.addObject(doc.cuerpos[nameBody])

# Se crean los planos de Planta, Alzado y Vista Lateral vinculados a los planos base la PIEZA
doc.crearPlano("Planta") 				#Creacion de plano con solo 2 argumentos
doc.crearPlano("Alzado", soporte="XZ_Plane", cuerpo = nameBody) 	#Creacion de plano mediante diccionario
doc.crearPlano("Vista_Lateral", "YZ_Plane", doc.cuerpos[nameBody]) 	#Sin diccionario y con objeto
"""

#############################################
sumaX = 0
longitudH = 20
longitudLinea = 10

#Note the use of FreeCAD original library inside the custom library wrap inside doc.base variable 
for linea in range(3):
	nuevoSketch.crearLinea( [ (2 + sumaX) , 2] , [(12 + sumaX), 12] )
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

#HACK Poder añadir un arco si la longitud de la lista es 3 [x,y, radio]
puntos.append([69,48,30])

puntos.append([69,48])
puntos.append([74,38])
puntos.append([83,60])

#Uso desquiciado del method chaining xD
nuevoSketch.crearRectangulo([100, 10],[140, 20]).crearRectangulo([100, 40],[140, 60]).crearCirculo([25, 50], 15).crearCirculo([150, 50], 15).crearPolilinea(puntos).crearPoligono(10).crearPoligono(12.5, [20, 100], 8).crearPoligono(15, [60, 110], 4).crearPoligono(10, [33, -17], 3)
nuevoSketch.crearRanura([2,1], [8,5], 2)
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

# TODO Leer libro de solidworks para basar la documentación de FreeCAD 0.19

"""
doc.base.recompute()