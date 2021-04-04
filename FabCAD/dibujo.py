import math

import FreeCAD as App
import Sketcher, Part

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
        
    #TODO Terminar de implementar la teoria del arco para obtener todos sus datos
    #Actualización: Muy dificil con trigonometria xD mejor hacerlo con relaciones de posicion
    def crearArcoTresPuntos(self, puntoInicial = [0, 0], puntoFinal = [0,0], puntoArco = [0,0], constructiva = False):
        """
        Esta herramienta dibuja un arco seleccionando tres puntos: el punto inicial, el punto final y
        un punto entre los dos anteriores
        """
        arcoBase = self.geometriaArco()
        self.doc.base.getObject(self.nombre).addGeometry(arcoBase,constructiva)

        contGeometria = self.contGeometria()

        self.bloquearPunto(contGeometria-1, 1, puntoInicial)
        self.bloquearPunto(contGeometria-1, 2, puntoFinal)

        self.crearPunto(puntoArco)
        self.bloquearPunto(contGeometria,1,puntoArco)

        self.doc.base.getObject(self.nombre).addConstraint(Sketcher.Constraint('PointOnObject',contGeometria,1,contGeometria-1)) 
        
        contRestricciones = self.base.ConstraintCount

        for i in range(1,7):
            self.doc.base.getObject(self.nombre).delConstraint(contRestricciones - i)

        return self
        
    def crearCirculo(self, centro = [0 , 0], radio = 0, constructiva = False):
        """Dibuja una circulo con los datos de centro y longitud de radio"""
        geometriaCirculo = self.geometriaCirculo(centro, radio)

        self.doc.base.getObject(self.nombre).addGeometry(geometriaCirculo,constructiva)

        return self

    #HACK Metodo de elipse terminado
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
        #TODO: Revisar documentación: https://wiki.freecadweb.org/Sketcher_CreatePolyline
        contGeometria = self.contGeometria()
        
        geoList = [self.geometriaLinea(puntos[i], puntos[i+1]) for i in range(len(puntos)-1)]
        self.doc.base.getObject(self.nombre).addGeometry(geoList, constructiva)

        conList = [(Sketcher.Constraint('Coincident', (contGeometria - 1 + i), 2, (contGeometria + i), 1)) for i in range(1,(len(puntos)-1))]   
        self.doc.base.getObject(self.nombre).addConstraint(conList)

        return self

    def crearPoligono(self, radio = 1, centro=[0,0], lados = 6):
        #HACK Agregar opción o crear nuevo metodo para elegir entre poligono 
        # inscrito o circunscrito y tamaño de lados, usar restricciones tangenciales entre dos entidades
        
        #TODO Corregir las ecuaciones a la unidad para que sea mas rapido el procesamiento
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
        """This tool creates a fillet between two lines joined at one point."""
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
        except:
            lineaUno = self.base.Geometry[geoIndex[1]]
            lineaDos = self.base.Geometry[geoIndex[0]]
            indexUno = geoIndex[1]
            indexDos = geoIndex[0]

            try:
                lineaUno.continuityWith(lineaDos)
            except:
                print("Las lineas de los indices ingresados no son continuas, la herramientas de recorte no funciona con lineas discontinuas")
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
    def matrizLineal(self, elementos, colxfil, distancia, direccion = 0, pivote = None, clonar = False, acotar = False):
        """
        Agrega una matriz de tamaño [filas x columnas] donde cada elemento es una copia de la geometria 
        seleccionada, desplazada en X y Y una determinada distancia en un cierto angulo dado

        Parametros:
        elementos: Puede ser un unico entero o una lista de enteros que indican el indice de la geometria
        colxfil: Si solo se proporciona un entero se tomará como el numero de filas, de lo contrario proporcionar una lista [filas, columnas]
        direccion: Angulo con respecto al eje horizontal sobre el cual se creará la matriz, por defecto en grados, si se quiere especificar otra unidad debe ingresar una cadena de texto, ejemplo: '45 rad'
        distancia: Separacion horizontañ entre elementos de la matriz con respecto al punto pivote proporcionado
        pivote: Punto base sobre el cual se iniciara la separación de cada elemento de la matriz
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

        #Ahora se comprueba si se especifica un punto pivote, de lo contrario se usa el primer punto del primer elemento
        if pivote is None:
            pivote = [elementos[0], 1]

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