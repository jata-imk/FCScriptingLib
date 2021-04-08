import math

import FreeCAD as App
import Sketcher, Part, PartDesign

import FabCAD.base
from FabCAD.utilidades import extraerString

class Dibujo: 
    #COMPLETADO Comprobar si en realidad estas propiedades se actualiza hasta ejecutar cada metodo
    #Se tuvo que crear metodos en lugar de propiedades para devolver siempre el valor correcto

    def __init__(self, nombreDibujo, doc, cuerpo, soporte = "XY_Plane", modoDeAdjuncion = "FlatFace"):
        """Constructor de la clase Dibujo"""
        self.doc = doc
        self.nombre = nombreDibujo

        if cuerpo is False:
            stringCuerpo = self.doc.objetoActivo
        else:
            stringCuerpo = extraerString(cuerpo)
       
        self.padre = stringCuerpo
        
        #Se crea y agrega el sketch como una propiedad del objeto original
        self.doc.base.getObject(stringCuerpo).newObject('Sketcher::SketchObject',nombreDibujo)
        self.doc.dibujos[nombreDibujo] = self
        self.doc.addExtern("Dibujo", self.nombre)
        self.base = self.doc.base.getObject(nombreDibujo)

        #Cuerpo del metodo
        self.base.Support = [(self.doc.base.getObject(extraerString(soporte)),'')]
        self.base.MapMode = modoDeAdjuncion

    def listaGeometria(self):
        return self.base.Geometry

    def contGeometria(self):
        return self.base.GeometryCount

    def contRestricciones(self):
        return self.base.ConstraintCount

    def convertirUnidades(self,stringConversion):
        return App.Units.Quantity(stringConversion)

    def datosGeometricosRecta(self, puntoUno, puntoDos):
        """
        Dados dos puntos, este metodo devuelve datos geometricos de una recta tales como:

        1. Pendiente
        2. Angulo en radianes
        3. Angulo en grados
        4. Longitud
        5. Punto Medio
        """
        #Pendiente, radianes y grados
        try:
            m = (puntoDos[1]-puntoUno[1])/(puntoDos[0]-puntoUno[0])
            rad = math.atan(m)
            deg = math.degrees(rad)
        except ZeroDivisionError:
            m = "Indeterminada"
            rad = math.pi
            deg = 90

        #Longitud
        l = math.dist(puntoUno, puntoDos)
        puntoMedio = [((puntoUno[0]+puntoDos[0])/2), ((puntoUno[1]+puntoDos[1])/2)]

        return [m, rad, deg, l, puntoMedio]
    
    def conmutarRestricciones(self):
        for i in range (self.contRestricciones()):
            self.base.toggleActive(i)

        return self

    def bloquearPunto(self, index, punto, coordenadas = [0,0], temporal = False):
        self.base.addConstraint(Sketcher.Constraint('DistanceX',index,punto,-1,1,-coordenadas[0]))
        self.base.addConstraint(Sketcher.Constraint('DistanceY',index,punto,-1,1,-coordenadas[1]))

        if temporal is True:
            self.base.delConstraint(self.base.ConstraintCount-1)
            self.base.delConstraint(self.base.ConstraintCount-1)

        return self
        
    def geometriaPunto(self, coordenadas = [0,0]):
        return Part.Point(App.Vector(coordenadas[0],coordenadas[1],0))

    def crearPunto(self, coordenadas = [0,0]):
        """
        The Point tool creates a point in the current sketch, which can be used for 
        constructing geometry elements. The point is always an construction element
        """
        geometriaPunto = self.geometriaPunto(coordenadas)
        self.doc.base.getObject(self.nombre).addGeometry(geometriaPunto)

        return self

    def geometriaLinea(self, puntoInicial = ['x','y'], puntoFinal = ['x','y']):
        return Part.LineSegment(App.Vector(puntoInicial[0],puntoInicial[1],0),App.Vector(puntoFinal[0],puntoFinal[1]))
    
    def crearLinea(self, puntoInicial = ['x','y'], puntoFinal = ['x','y'], constructiva=False):
        """Dibuja una linea dados dos puntos"""
        geometriaLinea = self.geometriaLinea(puntoInicial, puntoFinal)
        self.doc.base.getObject(self.nombre).addGeometry(geometriaLinea, constructiva)

        return self

    def crearLineaCentro(self, centro = [0,0], esquina = [0,0], constructiva = False):
        """
        A midpoint-to-midpoint placement of two straight lines can be achieved by creating a new Sketcher
        CreatePoint.svg Point and using two Sketcher ConstrainSymmetric.svg Symmetric constraints so 
        that it lies on the midpoint of both lines.
        """
        contGeometria = self.contGeometria()

        esquinaOpuestaX = centro[0] - (esquina[0] - centro[0])
        esquinaOpuestaY = centro[1] - (esquina[1] - centro[1])

        geometriaLinea = self.geometriaLinea([esquinaOpuestaX, esquinaOpuestaY], esquina)
        geometriaPunto = self.geometriaPunto(centro)

        self.doc.base.getObject(self.nombre).addGeometry(geometriaLinea, constructiva)
        self.doc.base.getObject(self.nombre).addGeometry(geometriaPunto, False)

        self.doc.base.getObject(self.nombre).addConstraint(Sketcher.Constraint('Symmetric',contGeometria,1,contGeometria,2,contGeometria + 1,1))

        return self
        
    #COMPLETADO Eliminar el parametro 'constructiva' de los metodos de las geometrias
    def geometriaCirculo(self, centro = [0 , 0], radio = 0):
        return (Part.Circle(App.Vector(centro[0], centro[1], 0),App.Vector(0,0,1), radio))

    def geometriaArco(self, centro = [0, 0], radio = 1, angulos = [0,0]):
        return (Part.ArcOfCircle(Part.Circle(App.Vector(centro[0],centro[1],0),App.Vector(0,0,1),radio),angulos[0],angulos[1]))

    def crearArco(self, centro = [0, 0], radio = 1, angulos = [0,90], unidadMedida = "deg", constructiva = False):
        """
        Esta herramienta dibuja un arco seleccionando tres datos: el centro, el radio y los
        ángulo de inicio y fin del arco. 
        """
        #Conversión de grados a radianes por defecto activada
        if unidadMedida == "deg":
            angulos = [self.convertirUnidades(f"({angulo}*pi/180) deg") for angulo in angulos]

        geometriaArco = self.geometriaArco(centro,radio,angulos)
        self.doc.base.getObject(self.nombre).addGeometry(geometriaArco,constructiva)

        return self
        
    #COMPLETADO Terminar de implementar la teoria del arco para obtener todos sus datos
    #Teoria obtenida de:
    #https://es.wikihow.com/encontrar-la-ecuación-de-una-recta
    #https://es.wikipedia.org/wiki/Intersección_de_dos_rectas
    def crearArcoTresPuntos(self, puntoInicial = [0, 0], puntoFinal = [0,0], puntoArco = [0,0], constructiva = False):
        """
        Esta herramienta dibuja un arco seleccionando tres puntos: el punto inicial, el punto final y
        un punto entre los dos anteriores
        """
        #Centros de cada linea, servirán para obtener la ecuacion de la recta tangente a esta linea
        centroP1P2 = [((puntoInicial[0] + puntoArco[0])/2), ((puntoInicial[1] + puntoArco[1])/2)]
        centroP2P3 = [((puntoArco[0] + puntoFinal[0])/2), ((puntoArco[1] + puntoFinal[1])/2)]

        #Se obtienela inclinacion en radianes de las dos lineas formadas por los tres puntos
        rad12 = self.datosGeometricosRecta(puntoInicial,puntoArco)[1]
        rad23 = self.datosGeometricosRecta(puntoArco,puntoFinal)[1]

        #Datos para la formula de intersección de dos rectas
        A = math.tan(rad12-(math.pi/2))
        B = math.tan(rad23-(math.pi/2))
        C = (-A * centroP1P2[0])  + centroP1P2[1]
        D = (-B * centroP2P3[0])  + centroP2P3[1]

        posCentro = [(D - C) / (A - B)]
        posCentro.append(A*posCentro[0]+(-A*centroP1P2[0] +centroP1P2[1]))

        #Obtención de los angulos para el arco
        geoDataAnguloUno = self.datosGeometricosRecta(posCentro, puntoFinal)
        geoDataAnguloDos = self.datosGeometricosRecta(posCentro, puntoInicial)

        angulos = [0,0]

        #     X_CENTRO        X_FINAL
        if (posCentro[0] < puntoFinal[0]):
            #     Y_CENTRO        Y_FINAL
            if (posCentro[1] < puntoFinal[1]):
                angulos[0] = geoDataAnguloUno[1]
            else:
                angulos[0] = geoDataAnguloUno[1]
        else:
            #     Y_CENTRO        Y_FINAL
            if (posCentro[1] < puntoFinal[1]):
                angulos[0] = math.pi+geoDataAnguloUno[1]
            else:
                angulos[0] = -(math.pi-geoDataAnguloUno[1])

        #     X_CENTRO        X_INICIAL
        if (posCentro[0] < puntoInicial[0]):
            #     Y_CENTRO        Y_INICIAL
            if (posCentro[1] < puntoInicial[1]):
                angulos[1] = geoDataAnguloDos[1]
            else:
                angulos[1] = geoDataAnguloDos[1]
        else:
            #     Y_CENTRO        Y_INICIAL
            if (posCentro[1] < puntoInicial[1]):
                angulos[1] = math.pi+geoDataAnguloDos[1]
            else:
                angulos[1] = -(math.pi-geoDataAnguloDos[1])

        radio = math.dist(posCentro, puntoFinal)

        #Obtenidos todos los datos se crea el arco en FreeCAD
        arcoBase = self.geometriaArco(posCentro,radio,angulos)
        self.doc.base.getObject(self.nombre).addGeometry(arcoBase,constructiva)

        return self
        
    def crearCirculo(self, centro = [0 , 0], radio = 0, constructiva = False):
        """Dibuja una circulo con los datos de centro y longitud de radio"""
        geometriaCirculo = self.geometriaCirculo(centro, radio)

        self.doc.base.getObject(self.nombre).addGeometry(geometriaCirculo,constructiva)

        return self

    #COMPLETADO Metodo de elipse terminado
    def geometriaElipse(self, centro = [0,0], radioMayor = [0,2], radioMenor = [1,0]):
        return (Part.Ellipse(App.Vector(radioMayor[0], radioMayor[1],0),App.Vector(radioMenor[0], radioMenor[1],0),App.Vector(centro[0],centro[1],0)))

    def crearElipse(self, centro = [0,0], radioMayor = [0,2], radioMenor = [1,0], constructiva = False):
        geometriaElipse = self.geometriaElipse(centro, radioMayor, radioMenor)
        self.doc.base.getObject(self.nombre).addGeometry(geometriaElipse,False)

        return self

    def crearRectangulo(self, puntoInicial = [0,0], puntoFinal = [0, 0]):
        """Dibuja un rectangulo dados dos puntos"""
        contGeometria = self.contGeometria()

        geoList = []
        geoList.append(Part.LineSegment(App.Vector(puntoInicial[0],puntoFinal[1],0),App.Vector(puntoFinal[0],puntoFinal[1],0)))
        geoList.append(Part.LineSegment(App.Vector(puntoFinal[0],puntoFinal[1],0),App.Vector(puntoFinal[0],puntoInicial[1],0)))
        geoList.append(Part.LineSegment(App.Vector(puntoFinal[0],puntoInicial[1],0),App.Vector(puntoInicial[0],puntoInicial[1],0)))
        geoList.append(Part.LineSegment(App.Vector(puntoInicial[0],puntoInicial[1],0),App.Vector(puntoInicial[0],puntoFinal[1],0)))

        self.doc.base.getObject(self.nombre).addGeometry(geoList, False)

        conList = []
        conList.append(Sketcher.Constraint('Coincident', (contGeometria    ),  2,(contGeometria + 1), 1))
        conList.append(Sketcher.Constraint('Coincident', (contGeometria + 1),  2,(contGeometria + 2), 1))
        conList.append(Sketcher.Constraint('Coincident', (contGeometria + 2),  2,(contGeometria + 3), 1))
        conList.append(Sketcher.Constraint('Coincident', (contGeometria + 3),  2,(contGeometria    ), 1))

        conList.append(Sketcher.Constraint('Horizontal', (contGeometria    )))
        conList.append(Sketcher.Constraint('Horizontal', (contGeometria + 2)))
        conList.append(Sketcher.Constraint('Vertical',   (contGeometria + 1)))
        conList.append(Sketcher.Constraint('Vertical',   (contGeometria + 3)))

        self.doc.base.getObject(self.nombre).addConstraint(conList)

        return self

    def crearPolilinea (self, puntos, constructiva = False):
        """Esta herramiento crea segmentos continuos de lineas conectadas por sus vertices """
        for i in range(len(puntos)-1):
            if len(puntos[i]) == 2:
                if len(puntos[i+1]) == 2:
                    self.crearLinea(puntos[i], puntos[i+1])

                    if i != 0:
                        self.base.addConstraint(Sketcher.Constraint('Coincident', (self.contGeometria()-1), 1, (self.contGeometria() - 2), 2))

                elif len(puntos[i+1]) >= 3:
                    #Esto quiere decir que el arco será interno (Predeterminado)
                    if len(puntos[i+1]) == 3:
                        puntos[i+1].append(False)

                    if type(puntos[i+1][3]) is bool:
                        geoData = self.datosGeometricosRecta(puntos[i], puntos[i+1][:2])

                        #Para poder crear un arco a partir de dos puntos y su radio, es necesario conocer
                        #el centro y la pendiente de la linea recta entre los dos puntos (centro y m)
                        centro = geoData[4]
                        radioIdeal = geoData[3]/2
                        
                        #COMPLETADO Añadir opcion para decidir si el arco es interior o exterior
                        if puntos[i+1][3] is False:
                            xTan = centro[0] + ( math.cos(geoData[1] + (math.pi/2)) * (radioIdeal*0.25) )
                            yTan = centro[1] + ( math.sin(geoData[1] + (math.pi/2)) * (radioIdeal*0.25) )
                        else:
                            xTan = centro[0] + ( math.cos(geoData[1] + (math.pi/2)) * (radioIdeal) )
                            yTan = centro[1] + ( math.sin(geoData[1] + (math.pi/2)) * (radioIdeal) )

                        self.crearArcoTresPuntos(puntos[i], puntos[i+1][:2], [xTan, yTan])
                        
                        #Se bloquea los puntos inicial y final del arco para crear la restriccion de radio
                        self.bloquearPunto(self.contGeometria()-1, 2, puntos[i])
                        self.bloquearPunto(self.contGeometria()-1, 1, puntos[i+1][:2])                            
                        self.base.addConstraint(Sketcher.Constraint('Radius',self.contGeometria()-1,puntos[i+1][2]))
                            
                        #Se eliminan todas las restricciones
                        contRestricciones = self.contRestricciones()-1
                        for j in range(5):
                            self.base.delConstraint(contRestricciones-j)

                        if i != 0:
                            self.base.addConstraint(Sketcher.Constraint('Coincident', (self.contGeometria()-1), 2, (self.contGeometria() - 2), 2))

                    else:
                        print(f"Los puntos {puntos[i+1]} no pueden ser croquizados por esta herramienta")
                        return self

            elif len(puntos[i]) >= 3:
                if len(puntos[i+1]) == 2:
                    self.crearLinea(puntos[i][:2], puntos[i+1])

                    if i != 0:
                        self.base.addConstraint(Sketcher.Constraint('Coincident', (self.contGeometria()-1), 1, (self.contGeometria() - 2), 1))

                #Esto quiere decir que el arco será interno (Predeterminado)
                elif len(puntos[i+1]) == 3:
                    puntos[i+1].append(False)

                    if type(puntos[i+1][3]) is bool:
                        geoData = self.datosGeometricosRecta(puntos[i][:2], puntos[i+1][:2])

                        #Para poder crear un arco a partir de dos puntos y su radio, es necesario conocer
                        #el centro y la pendiente de la linea recta entre los dos puntos (centro y m)
                        centro = geoData[4]
                        radioIdeal = geoData[3]/2
                        
                        #COMPLETADO Añadir opcion para decidir si el arco es interior o exterior
                        if puntos[i+1][3] is False:
                            xTan = centro[0] + ( math.cos(geoData[1] + (math.pi/2)) * (radioIdeal*0.25) )
                            yTan = centro[1] + ( math.sin(geoData[1] + (math.pi/2)) * (radioIdeal*0.25) )
                        else:
                            xTan = centro[0] + ( math.cos(geoData[1] + (math.pi/2)) * (radioIdeal) )
                            yTan = centro[1] + ( math.sin(geoData[1] + (math.pi/2)) * (radioIdeal) )

                        self.crearArcoTresPuntos(puntos[i][:2], puntos[i+1][:2], [xTan, yTan])
                        
                        #Se bloquea los puntos inicial y final del arco para crear la restriccion de radio
                        self.bloquearPunto(self.contGeometria()-1, 2, puntos[i][:2])
                        self.bloquearPunto(self.contGeometria()-1, 1, puntos[i+1][:2])                            
                        self.base.addConstraint(Sketcher.Constraint('Radius',self.contGeometria()-1,puntos[i+1][2]))
                            
                        #Se eliminan todas las restricciones
                        contRestricciones = self.contRestricciones()-1
                        for j in range(5):
                            self.base.delConstraint(contRestricciones-j)

                        if i != 0:
                            self.base.addConstraint(Sketcher.Constraint('Coincident', (self.contGeometria()-1), 2, (self.contGeometria() - 2), 1))

                    else:
                        print(f"Los puntos {puntos[i+1]} no pueden ser croquizados por esta herramienta")
                        return self

        return self

    def crearPoligono(self, radio = 1, centro=[0,0], lados = 6):
        #HACK Agregar opción o crear nuevo metodo para elegir entre poligono 
        # inscrito o circunscrito y tamaño de lados, usar restricciones tangenciales entre dos entidades
        
        #TODO Cambiar las ecuaciones a la unidad para que sea mas rapido el procesamiento
        contGeometria = self.contGeometria()

        n = lados - 2
        
        angulosInternos = (180 * n)
        anguloentreLineas = angulosInternos / lados
        anguloTriangulos = anguloentreLineas / 2
        anguloFaltante = 180 - 90 - anguloTriangulos

        anguloHorizontal = 180 - (anguloentreLineas)

        circuloPosY = math.sin(math.radians(anguloTriangulos)) * 0.5 / math.sin(math.radians(anguloFaltante))

        puntosPoligono = [[centro[0] - (radio / 2), centro[1] - (circuloPosY)], [centro[0] + (radio / 2), centro[1] - (circuloPosY)]]

        for i in range(1, lados):
            puntosPoligono.append(
                            [puntosPoligono[i][0] + radio * math.cos(math.radians(anguloHorizontal*i)), 
                             puntosPoligono[i][1] + radio * math.sin(math.radians(anguloHorizontal*i))]
                         )

        self.crearPolilinea(puntosPoligono)
        self.crearCirculo([0.5+centro[0],centro[1]+circuloPosY], radio, True)

        conList = []
        
        conList.append(Sketcher.Constraint('Radius', contGeometria+lados, radio))
        conList.append(Sketcher.Constraint('Coincident', (contGeometria), 1, (contGeometria+lados-1), 2))
        
        for i in range(1, lados):
            if i > 0:
                conList.append(Sketcher.Constraint('Equal', (contGeometria), (contGeometria + i)))
        
        
        for i in range(lados):
            conList.append(Sketcher.Constraint('PointOnObject', (contGeometria + i), 1,(contGeometria+lados)))
        
        self.doc.base.getObject(self.nombre).addConstraint(conList)
        self.bloquearPunto(contGeometria+lados,3,centro,True)

        return self

    #COMPLETADO Herramienta de ranura vertical u horizantal agregada
    #COMPLETADO Permitir hacer ranuras con inclinación
    #TODO Corregir forma en que se crean los angulos (Sacar la tangente inversa)
    def crearRanura(self, puntoInicial, puntoFinal, radio, constructiva = False):
        contGeometria = self.contGeometria()

        m = (puntoFinal[1] - puntoInicial[1]) / (puntoFinal[0] - puntoInicial[0])
        angulos = [m+(math.pi/2), m+(math.pi/2)+math.pi]

        self.crearArco(puntoInicial, radio, [angulos[0], angulos[1]], 'rad', constructiva)
        self.crearArco(puntoFinal, radio, [angulos[1], angulos[0]], 'rad', constructiva)
        self.crearLinea(self.base.Geometry[contGeometria].StartPoint, self.base.Geometry[contGeometria+1].EndPoint, constructiva)
        self.crearLinea(self.base.Geometry[contGeometria].EndPoint, self.base.Geometry[contGeometria+1].StartPoint, constructiva)
                
        conList = []

        conList.append(Sketcher.Constraint('Equal',contGeometria,contGeometria+1))
        conList.append(Sketcher.Constraint('Radius',contGeometria, radio))
        conList.append(Sketcher.Constraint('Tangent',contGeometria,1,contGeometria+2,1))
        conList.append(Sketcher.Constraint('Tangent',contGeometria,2,contGeometria+3,1))
        conList.append(Sketcher.Constraint('Tangent',contGeometria+1,1,contGeometria+3,2))
        conList.append(Sketcher.Constraint('Tangent',contGeometria+1,2,contGeometria+2,2))

        self.base.addConstraint(conList)

        self.bloquearPunto(contGeometria,3, puntoInicial)
        self.bloquearPunto(contGeometria+1,3, puntoFinal)

        contRestricciones = self.base.ConstraintCount-1

        for i in range(4):
            self.base.delConstraint(contRestricciones-i)

        return self
        
    #COMPLETADO Herramienta de filete completada
    #COMPLETADO Corregir problemas con geometrias que tengan restricciones de posicion
    def chaflan(self, geoIndex = [], longitud = 1):
        """
        Esta herramienta crea un chaflan entre dos lineas unidas por un punto
        """
        contGeometria = self.contGeometria()

        #La siguiente parte es para comprobar la continuidad de las lineas que nos indican los indices
        #Puede darse el caso en que el primer indice no sea el que tenga la continuidad y en ese caso 
        #se invierte cual es la linea Uno y Dos, con el fin de que al establecer las restricciones siempre 
        #se tengan tres puntos diferentes
        lineaUno = self.base.Geometry[geoIndex[0]]
        lineaDos = self.base.Geometry[geoIndex[1]]
        indexUno = geoIndex[0]
        indexDos = geoIndex[1]

        try:
            lineaUno.continuityWith(lineaDos)
        except Part.OCCError:
            lineaUno = self.base.Geometry[geoIndex[1]]
            lineaDos = self.base.Geometry[geoIndex[0]]
            indexUno = geoIndex[1]
            indexDos = geoIndex[0]

            try:
                lineaUno.continuityWith(lineaDos)
            except Part.OCCError:
                print("Las lineas de los indices ingresados no son continuas, la herramientas de recorte no funciona con lineas discontinuas")
                return self
            except TypeError:
                print("Tipo de dato incorrecto")
                return self

        except TypeError:
            print("Tipo de dato incorrecto")
            return self

        self.conmutarRestricciones()

        self.bloquearPunto(indexUno, 1, [lineaUno.StartPoint[0], lineaUno.StartPoint[1]])
        self.bloquearPunto(indexUno, 2, [lineaUno.EndPoint[0], lineaUno.EndPoint[1]])
        self.bloquearPunto(indexDos, 2, [lineaDos.EndPoint[0], lineaDos.EndPoint[1]])

        #Se crea una linea que será la que nos servirá para crear el filete
        lineaPuntoUno = [((lineaUno.StartPoint[0] + lineaUno.EndPoint[0])/2), ((lineaUno.StartPoint[1] + lineaUno.EndPoint[1])/2)]
        lineaPuntoDos = [((lineaUno.EndPoint[0] + lineaDos.EndPoint[0])/2), ((lineaUno.EndPoint[1] + lineaDos.EndPoint[1])/2)]
        
        self.crearLinea(lineaPuntoUno, lineaPuntoDos)

        self.base.addConstraint(Sketcher.Constraint('PointOnObject',contGeometria,1,indexUno)) 
        self.base.addConstraint(Sketcher.Constraint('PointOnObject',contGeometria,2,indexDos)) 
        self.base.addConstraint(Sketcher.Constraint('Distance',contGeometria,1,indexUno,2,longitud)) 
        self.base.addConstraint(Sketcher.Constraint('Distance',contGeometria,2,indexUno,2,longitud)) 

        #Se calcula la posicion de corte, debido a que si se hace en los puntos finales o inciales marca error
        ultimaLinea = self.base.Geometry[contGeometria]

        posTrimUno = [((ultimaLinea.StartPoint[0] + lineaUno.EndPoint[0])/2), ((ultimaLinea.StartPoint[1] + lineaUno.EndPoint[1])/2)]
        posTrimDos = [((ultimaLinea.EndPoint[0] + lineaUno.EndPoint[0])/2), ((ultimaLinea.EndPoint[1] + lineaUno.EndPoint[1])/2)]
        
        self.recortarAristas(indexUno,App.Vector(posTrimUno[0],posTrimUno[1],0))
        self.recortarAristas(indexDos,App.Vector(posTrimDos[0],posTrimDos[1],0))

        #El -3 en la siguiente linea es debido a que queremos conservar las restricciones de coincidencia
        #entre la linea nueva del filete y las lineas de la geometria existente, y dado que al hacer el
        #corte se eliminan las demas restricciones que pusimos (Longitud) las restricciones de coincidencia
        #son las ultimas dos y debemos recordar que para seleccionar una restriccion debemos restar 1
        contRestricciones = self.contRestricciones()-3

        for i in range(4):
            self.base.delConstraint(contRestricciones-i)

        self.conmutarRestricciones()
        self.base.toggleActive(self.contRestricciones() - 1)
        self.base.toggleActive(self.contRestricciones() - 2)

        return self

    def redondeo(self, geoIndex, punto, radio, intersección = False):
        self.base.fillet(geoIndex,punto,radio,True,intersección)
        
        return self

    #COMPLETADO Las coordenadas en lugar de ser directas ahora reemplazan los valores de un vector
    def recortarAristas(self, geoIndex, coordenadas = [0,0]):
        self.base.trim(geoIndex,App.Vector(coordenadas[0],coordenadas[1],0))
        
        return self

    def simetria(self, geoIndex = [], pivote = 0):
        self.base.addSymmetric(geoIndex, pivote, 0)

        return self

    #COMPLETADO Terminar metodo de matriz lineal
    #HACK Preguntar si la distancia debe ser horizontal o normal a los puntos
    #HACK Crear un metodo para creación de matrices polares
    def matrizLineal(self, elementos, colxfil, distancia, direccion = 0, clonar = False, acotar = False):
        """
        Crea una matriz de tamaño [filas x columnas] de la geometria seleccionada, desplazada una  cierta 
        distancia en un cierto angulo dado tomando como referencia el ultimo punto de la lista de elementos

        Parametros:
        elementos: Puede ser un unico entero o una lista de enteros que indican el indice de la geometria
        colxfil: Si solo se proporciona un entero se tomará como el numero de filas, de lo contrario proporcionar una lista [filas, columnas]
        direccion: Angulo con respecto al eje horizontal sobre el cual se creará la matriz, por defecto en grados, si se quiere especificar otra unidad debe ingresar una cadena de texto, ejemplo: '45 rad'
        distancia: Separacion horizontal entre elementos de la matriz
        clonar: Si este parametro es True los elementos de la matriz cambiaran si la geometria original cambia, de lo contrario cada elemento será independiente
        acotar: Si es True, se incluirá una restricción de longitud entre los pivotes de cada elemento
        """
        #Se pregunta el tipo de el parametro 'elementos', si es un solo elemento entonces será Int
        #y se tendrá que convertir a lista para que pueda ser aceptado por la funcion, si el tipo del
        #parametro ya es una lista simplemente se utiliza sin convertir
        if type(elementos) is int:
            elementos = [int(elementos)]

        #Se hace lo mismo con el parametro 'colxfil' y ademas se pregunta por su tamaño, ya que siempre
        #deben haber dos elementos en este parametro si solamente se introdujo uno (columnas)
        #se agrega un uno como filas
        if type(colxfil) is int:
            colxfil = [int(colxfil), 1]

        elif len(colxfil) == 1:
            colxfil.append(1)

        #En la siguiente condicion se pregunta si distancia es un entero o una lista, si es un entero
        #se convierte a una lista y se agrega un uno solo para rellenar, si el parametro es una lista
        #entonces mediante regla de tres se convierte la distancia a un multiplo de la distancia horizontal
        #dado que de esa manera recibo el argumento la funcion de FreeCAD
        if type(distancia) is not list:
            distancia = [distancia, 1]
        else:
            distancia[1] = distancia[1]/distancia[0]

        #Para el parametro 'direccion' si se proporciona un tipo de dato que no es str es 
        #por que implicitamente se estan usando grados, asi que se hace la conversion a radianes para
        #las funciones trigonometricas, de lo contrario simplemente se usa el string proporcionado
        if direccion is not str:
            vectorX = self.convertirUnidades(f"cos({direccion}*pi/180)*{distancia[0]}")
            vectorY = self.convertirUnidades(f"sin({direccion}*pi/180)*{distancia[0]}")

        else: 
            vectorX = self.convertirUnidades(f"cos({direccion})*{distancia[0]}")
            vectorY = self.convertirUnidades(f"sin({direccion})*{distancia[0]}")

        #Funcion de FreeCAD para la creaciones de matrices lineales
        self.base.addRectangularArray(elementos, App.Vector(vectorX, vectorY, 0), clonar, colxfil[0], colxfil[1], acotar, distancia[1])

        return self

    def copiar(self):
        print("Todavia no existo :D")

        return self

    def clonar(self):
        print("Todavia no existo :D")

        return self

    def seleccionarGeometria(self):
        #Idea de implementación: Establecer un punto desde el cual la geometria será seleccionada
        print("Tampoco existo :D")

        """
        This constraint tool takes two points as its argument and serves to make the two points
        coincident. (Meaning to make them as-one-point).

        In practical terms this constraint tool is useful when there is a break in a profile for example 
        - where two lines end near each other and need to be joined - a coincident constraint 
        on their end-points will close the gap.
        """

    def extrusionAditiva(self, nombreExtrusion = "Pad", longitud = 10, invertido = 0, planoMedio = 0):
        FabCAD.extrusionAditiva(self.doc, self.padre, self.nombre, nombreExtrusion, longitud, invertido, planoMedio)

        return self

    def extrusionDeVaciado(self, nombreExtrusion = "Pocket", longitud = 10, invertido = 0, planoMedio = 0):
        FabCAD.extrusionDeVaciado(self.doc, self.padre, self.nombre, nombreExtrusion, longitud, invertido, planoMedio)

        return self

    def revolucionAditiva(self, nombreExtrusion = "Revolucion", angulo = 360, invertido = 0, planoMedio = 0):
        FabCAD.revolucionAditiva(doc = self.doc, padreBase = self.padre, base = self.nombre, nombreExtrusion = nombreExtrusion, angulo = angulo, invertido = invertido, planoMedio = planoMedio)

        return self