import math
import Sketcher, Part
import FreeCAD as App

from FabCAD.utilidades import extraerString

class Dibujo: 
    contGeometria = 0 #FIXME Comprobar si en realidad esta propiedad se actualiza hasta ejecutar cada metodo
    contRestricciones = 0
    listaGeometria = []

#nuevoSketch = doc.nuevoSketch("sketch", doc.cuerpos[nameBody], doc.planos["Planta"])
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

        #Se vincula la lista de geometria proporcionada por FreeCAD al cuerpo de la instancia
        self.listaGeometria = self.doc.base.getObject(nombreDibujo).Geometry

    def bloquearPunto(self, index, punto, coordenadas = [0,0], temporal = False):
        self.base.addConstraint(Sketcher.Constraint('DistanceX',index,punto,coordenadas[0]))
        self.base.addConstraint(Sketcher.Constraint('DistanceY',index,punto,coordenadas[1]))
        
    def geometriaPunto(self, coordenadas = [0,0]):
        return Part.Point(App.Vector(coordenadas[0],coordenadas[1],0))

    def crearPunto(self, coordenadas = [0,0]):
        """
        The Point tool creates a point in the current sketch, which can be used for 
        constructing geometry elements. The point is always an construction element
        """
        geometriaPunto = self.geometriaPunto(coordenadas)
        self.doc.base.getObject(self.nombre).addGeometry(geometriaPunto)

        return geometriaPunto

    def geometriaLinea(self, puntoInicial = ['x','y'], puntoFinal = ['x','y']):
        return Part.LineSegment(App.Vector(puntoInicial[0],puntoInicial[1],0),App.Vector(puntoFinal[0],puntoFinal[1]))
    
    def crearLinea(self, puntoInicial = ['x','y'], puntoFinal = ['x','y'], constructiva=False):
        """Dibuja una linea dados dos puntos"""

        geometriaLinea = self.geometriaLinea(puntoInicial, puntoFinal)

        self.doc.base.getObject(self.nombre).addGeometry(geometriaLinea, constructiva)
        self.contGeometria = self.doc.base.getObject(self.nombre).GeometryCount

        return geometriaLinea

    def crearLineaCentro(self, centro = [0,0], esquina = [0,0], constructiva = False):
        """
        A midpoint-to-midpoint placement of two straight lines can be achieved by creating a new Sketcher
        CreatePoint.svg Point and using two Sketcher ConstrainSymmetric.svg Symmetric constraints so 
        that it lies on the midpoint of both lines.
        """
        contGeometria = self.contGeometria

        esquinaOpuestaX = centro[0] - (esquina[0] - centro[0])
        esquinaOpuestaY = centro[1] - (esquina[1] - centro[1])

        geometriaLinea = self.geometriaLinea([esquinaOpuestaX, esquinaOpuestaY], esquina)
        geometriaPunto = self.geometriaPunto(centro)

        self.doc.base.getObject(self.nombre).addGeometry(geometriaLinea, constructiva)
        self.doc.base.getObject(self.nombre).addGeometry(geometriaPunto, constructiva)

        self.doc.base.addConstraint(Sketcher.Constraint('Symmetric',contGeometria,1,contGeometria,2,contGeometria + 1,1))

        self.contGeometria = self.doc.base.getObject(self.nombre).GeometryCount
        
    #TODO Eliminar el parametro 'constructiva' de los metodos de las geometrias
    def geometriaCirculo(self, centro = [0 , 0], radio = 0, constructiva = False):
        return (Part.Circle(App.Vector(centro[0], centro[1], 0),App.Vector(0,0,1), radio),constructiva)

    def geometriaArco(self, centro = [0, 0], radio = 1, angulos = [0,0], constructiva = False):
        return (Part.ArcOfCircle(Part.Circle(App.Vector(centro[0],centro[1],0),App.Vector(0,0,1),radio),angulos[0],angulos[1]),constructiva)

    def crearArco(self, centro = [0, 0], radio = 1, angulos = [0,90], constructiva = False):
        """
        Esta herramienta dibuja un arco seleccionando tres datos: el centro, el radio y los
        ángulo de inicio y fin del arco. 
        """
        geometriaArco = self.geometriaArco(centro, radio,angulos,constructiva)
        self.doc.base.getObject(self.nombre).addGeometry(geometriaArco)

        self.contGeometria = self.doc.base.getObject(self.nombre).GeometryCount

        return [self.contGeometria, geometriaArco]
        
    #TODO Terminar de implementar la teoria del arco para obtener todos sus datos
    #Actualización: Muy dificil con trigonometria xD mejor hacerlo con relaciones de posicion
    def crearArcoTresPuntos(self, puntoInicial = [0, 0], puntoFinal = [0,0], puntoArco = [0,0], constructiva = False):
        """
        Esta herramienta dibuja un arco seleccionando tres puntos: el punto inicial, el punto final y
        un punto entre los dos anteriores
        """
        arcoBase = self.crearArco()
        self.bloquearPunto(arcoBase[0]-1, 1, puntoInicial)
        self.bloquearPunto(arcoBase[0]-1, 2, puntoFinal)

        self.crearPunto(puntoArco)
        self.bloquearPunto(arcoBase[0],1,puntoArco)

        self.doc.base.getObject(self.nombre).addConstraint(Sketcher.Constraint('PointOnObject',arcoBase[0],1,arcoBase[0]-1)) 
        
        contRestricciones = self.base.ConstraintCount

        for i in range(1,7):
            self.doc.base.getObject(self.nombre).delConstraint(contRestricciones - i)

        self.contGeometria = self.doc.base.getObject(self.nombre).GeometryCount

        return [self.contGeometria, arcoBase[1]]
        
    def crearCirculo(self, centro = [0 , 0], radio = 0, constructiva = False):
        """Dibuja una circulo con los datos de centro y longitud de radio"""
        self.doc.base.getObject(self.nombre).addGeometry(Part.Circle(App.Vector(centro[0], centro[1], 0),App.Vector(0,0,1), radio),constructiva)
        self.contGeometria = self.doc.base.getObject(self.nombre).GeometryCount

    def crearElipse(self):
        print("No existo :D")

    def crearRectangulo(self, puntoInicial = [0,0], puntoFinal = [0, 0]):
        """Dibuja un rectangulo dados dos puntos"""
        contGeometria = self.contGeometria

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

        self.contGeometria = self.doc.base.getObject(self.nombre).GeometryCount

    def crearPolilinea (self, puntos):
        """Esta herramiento crea segmentos continuos de lineas conectadas por sus vertices """
        #TODO: Revisar documentación: https://wiki.freecadweb.org/Sketcher_CreatePolyline
        #BUG El numero de geometria que se agrega es n-1 para todos los casos
        contGeometria = self.contGeometria
        geoList = []
        conList = []
        
        for i in range(len(puntos)-1):
            geoList.append(self.geometriaLinea(puntos[i], puntos[i+1]))

        self.doc.base.getObject(self.nombre).addGeometry(geoList, False)

        for i in range (1,(len(puntos)-1)):
            conList.append(Sketcher.Constraint('Coincident', (contGeometria - 1 + i), 2, (contGeometria + i), 1))
            
        self.doc.base.getObject(self.nombre).addConstraint(conList)
        self.contGeometria = self.doc.base.getObject(self.nombre).GeometryCount

    def crearPoligono(self, radio = 1, centro=[0,0], lados = 6):
        #HACK Agregar opción o crear nuevo metodo para elegir entre poligono inscrito o circunscrito y tamaño de lados
        contGeometria = self.contGeometria

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
        
        conList.append(Sketcher.Constraint('Radius', contGeometria+lados, App.Units.Quantity(f"{radio} mm")))
        conList.append(Sketcher.Constraint('Coincident', (contGeometria), 1, (contGeometria+lados-1), 2))
        
        for i in range(1, lados):
            if i > 0:
                conList.append(Sketcher.Constraint('Equal', (contGeometria), (contGeometria + i)))
        
        
        for i in range(lados):
            conList.append(Sketcher.Constraint('PointOnObject', (contGeometria + i), 1,(contGeometria+lados)))
        
        conList.append(Sketcher.Constraint('DistanceX',contGeometria+lados,3,App.Units.Quantity(f"{centro[0]} mm")))
        conList.append(Sketcher.Constraint('DistanceY',contGeometria+lados,3,App.Units.Quantity(f"{centro[1]} mm")))
        
        #FIXME Programa da error de indice fuera de rango al querer mover el circulo
        #self.doc.base.getObject(self.nombre).movePoint(contGeometria+lados,3,App.Vector(centro[0],centro[1],0),0)
        self.doc.base.getObject(self.nombre).addConstraint(conList)

    def crearRanura(self):
        print("Tampoco existo :D")
        
    def filete(self):
        print("Tampoco existo :D")

    def redondeo(self):
        print("Tampoco existo :D")

    def recortarAristas(self):
        print("Tampoco existo :D")

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