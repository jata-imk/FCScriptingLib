import FreeCAD, PartDesign #lgtm [py/unused-import]

import FabCAD.base
from FabCAD.utilidades import *

#COMPLETADO Agregar metodo para seleccionar objetos
class Extrusion:
    #HACK Preguntar si es mejor tener solo un metodo de extrusion y que este acepte 
    # un parametro llamado "Tipo", con el cual se determinará si es de adicion o de vaciado
    # o inclusive tener ambos
    def extrusionAditiva(self, doc, croquis = None, nombreExtrusion = "Pad", longitud = 10, invertido = 0, planoMedio = 0):
        """Extruye la geometria cerrada de un croquis en una o dos direcciones para crear una operacion solida"""
        
        self.nombre = nombreExtrusion
        self.doc = doc
        self.tipo = "extrusionAditiva"

        #Se extrae el string de la base y de su padre mediante metodos que aceptan varios tipos de clases
        stringCroquis = extraerString(croquis)

        if type(croquis) is str:
            croquis = self.doc.seleccionarObjeto(croquis)

        stringPadreCroquis = extraerStringPadre(croquis)


        self.doc.base.getObject(stringPadreCroquis).newObject('PartDesign::Pad',nombreExtrusion)
        self.base = self.doc.base.getObject(nombreExtrusion)

        self.base.Profile = self.doc.base.getObject(stringCroquis)
        self.base.Length = longitud
        self.base.Length2 = 100.000000
        self.base.UseCustomVector = 0
        self.base.Direction = (1, 1, 1)
        self.base.Type = 0
        self.base.UpToFace = None
        self.base.Reversed = invertido
        self.base.Midplane = planoMedio
        self.base.Offset = 0

        self.doc.extrusiones[nombreExtrusion] = self
        self.doc.addExtern("Extrusion", nombreExtrusion)

        return self

    def extrusionDeVaciado(self, doc, croquis = None, nombreExtrusion = "Pocket", longitud = 10, invertido = 0, planoMedio = 0):
        """Corta un solido a traves de la extrusion de la geometria cerrada de un croquis en una o dos direcciones"""
        
        self.nombre = nombreExtrusion
        self.doc = doc
        self.tipo = "extrusionDeVaciado"

        #Se extrae el string de la base y de su padre mediante metodos que aceptan varios tipos de clases
        stringCroquis = extraerString(croquis)

        if type(croquis) is str:
            croquis = self.doc.seleccionarObjeto(croquis)

        stringPadreCroquis = extraerStringPadre(croquis)

        self.doc.base.getObject(stringPadreCroquis).newObject('PartDesign::Pocket',nombreExtrusion)
        self.base = self.doc.base.getObject(nombreExtrusion)

        self.base.Profile = self.doc.base.getObject(stringCroquis)
        self.base.Length = longitud
        self.base.Length2 = 100.000000
        self.base.Type = 0
        self.base.UpToFace = None
        self.base.Reversed = invertido
        self.base.Midplane = planoMedio
        self.base.Offset = 0

        self.doc.extrusiones[nombreExtrusion] = self
        self.doc.addExtern("Extrusion", nombreExtrusion)

        return self

    def revolucionAditiva(self, doc, croquis = None, nombreExtrusion = "Revolucion", angulo = 360, invertido = 0, planoMedio = 0 ):
        """Crea una revolucion de un croquis con respecto a un eje (Primer linea del croquis) para crear una operacion solida"""
        
        self.nombre = nombreExtrusion
        self.doc = doc
        self.tipo = "revolucionAditiva"

        #Se extrae el string de la base y de su padre mediante metodos que aceptan varios tipos de clases
        stringCroquis = extraerString(croquis)

        if type(croquis) is str:
            croquis = self.doc.seleccionarObjeto(croquis)

        stringPadreCroquis = extraerStringPadre(croquis)

        self.doc.contLineasReferencia += 1
        stringEjeRevolucion = f"EjeRevolucion{str(self.doc.contLineasReferencia).zfill(2)}"

        #EJE DE REVOLUCION
        self.doc.base.getObject(stringPadreCroquis).newObject('PartDesign::Line',stringEjeRevolucion)

        self.doc.base.getObject(stringEjeRevolucion).AttachmentOffset = FreeCAD.Placement(
            FreeCAD.Vector(0.0000000000, 0.0000000000, 0.0000000000),
            FreeCAD.Rotation(0.0000000000, 0.0000000000, 0.0000000000)
        )

        self.doc.base.getObject(stringEjeRevolucion).MapReversed = False
        self.doc.base.getObject(stringEjeRevolucion).Support = [(self.doc.base.getObject(stringCroquis),'Edge1')]
        self.doc.base.getObject(stringEjeRevolucion).MapPathParameter = 0.000000
        self.doc.base.getObject(stringEjeRevolucion).MapMode = 'TwoPointLine'

        #REVOLUCION
        self.doc.base.getObject(stringPadreCroquis).newObject('PartDesign::Revolution',nombreExtrusion)
        self.base = self.doc.base.getObject(nombreExtrusion)

        self.base.Profile = self.doc.base.getObject(stringCroquis)
        self.base.ReferenceAxis = (self.doc.base.getObject(stringEjeRevolucion), [''])
        self.base.Angle = angulo
        self.base.Reversed = invertido
        self.base.Midplane = planoMedio

        self.doc.extrusiones[nombreExtrusion] = self
        self.doc.addExtern("Extrusion", nombreExtrusion)

        return self

    def revolucionDeVaciado(self, doc, croquis = None, nombreExtrusion = "RevolucionDeVaciado", angulo = 360, invertido = 0, planoMedio = 0 ):
        """Corta un solido a traves de la revolucion de un croquis con respecto a un eje (Primer linea del croquis)"""
        
        self.nombre = nombreExtrusion
        self.doc = doc
        self.tipo = "revolucionDeVaciado"

        #Se extrae el string de la base y de su padre mediante metodos que aceptan varios tipos de clases
        stringCroquis = extraerString(croquis)

        if type(croquis) is str:
            croquis = self.doc.seleccionarObjeto(croquis)

        stringPadreCroquis = extraerStringPadre(croquis)

        self.doc.contLineasReferencia += 1
        stringEjeRevolucion = f"EjeRevolucion{str(self.doc.contLineasReferencia).zfill(2)}"

        #EJE DE REVOLUCION
        self.doc.base.getObject(stringPadreCroquis).newObject('PartDesign::Line',stringEjeRevolucion)

        self.doc.base.getObject(stringEjeRevolucion).AttachmentOffset = FreeCAD.Placement(
            FreeCAD.Vector(0.0000000000, 0.0000000000, 0.0000000000),
            FreeCAD.Rotation(0.0000000000, 0.0000000000, 0.0000000000)
        )

        self.doc.base.getObject(stringEjeRevolucion).MapReversed = False
        self.doc.base.getObject(stringEjeRevolucion).Support = [(self.doc.base.getObject(stringCroquis),'Edge1')]
        self.doc.base.getObject(stringEjeRevolucion).MapPathParameter = 0.000000
        self.doc.base.getObject(stringEjeRevolucion).MapMode = 'TwoPointLine'

        #REVOLUCION
        self.doc.base.getObject(stringPadreCroquis).newObject('PartDesign::Groove',nombreExtrusion)
        self.base = self.doc.base.getObject(nombreExtrusion)

        self.base.Profile = self.doc.base.getObject(stringCroquis)
        self.base.ReferenceAxis = (self.doc.base.getObject(stringEjeRevolucion), [''])
        self.base.Angle = angulo
        self.base.Reversed = invertido
        self.base.Midplane = planoMedio

        self.doc.extrusiones[nombreExtrusion] = self
        self.doc.addExtern("Extrusion", nombreExtrusion)

        return self

    #COMPLETADO: Preguntarle a Valeria cual es la traduccion de esta cosa xD ---> AdditiveLoft <---
    # y ademas ver como hacer que el metodo pueda recibir varios croquis
    def recubrir(self, doc, croquisInicial, croquisParaRecubrir, nombreExtrusion = "extrusionRecubierta"):
        """Agrega material entre dos o mas croquis (también denominados secciones transversales) para crear una operacion solida"""
        self.nombre = nombreExtrusion
        self.doc = doc
        self.tipo = "extrusionRecubierta"

        self.doc.extrusiones[nombreExtrusion] = self
        self.doc.addExtern("Extrusion", nombreExtrusion)

        #Se extrae el string de la base y de su padre mediante metodos que aceptan varios tipos de clases
        stringCroquisInicial = extraerString(croquisInicial)

        if type(croquisInicial) is str:
            croquisInicial = self.doc.seleccionarObjeto(croquisInicial)

        stringPadreCroquisInicial = extraerStringPadre(croquisInicial)

        #Ya que se pueden recibir uno o mas croquis hay que validar que tipo se recibe y asi asegurar 
        #que siempre se tenga una lista
        if type(croquisParaRecubrir) is not list:
            croquisParaRecubrir = [croquisParaRecubrir]

        stringsCroquis = []

        for croquis in croquisParaRecubrir:
            stringsCroquis.append(extraerString(croquis))

        self.doc.base.getObject(stringPadreCroquisInicial).newObject('PartDesign::AdditiveLoft',nombreExtrusion)
        self.base = self.doc.base.getObject(nombreExtrusion)

        self.base.Profile = self.doc.base.getObject(stringCroquisInicial)

        croquisObjects = []

        #Se agregan las secciones de cada croquis para recubrir
        for croquis in stringsCroquis:
            croquisObjects.append(self.doc.base.getObject(croquis))

        self.base.Sections = croquisObjects

        return self

    def recubrirCorte(self, doc, croquisInicial, croquisParaRecubrir, nombreExtrusion = "corteRecubierto"):
        """Remueve material de un solido al hacer la resta del solido creado mediante la union de dos o mas croquis"""

        self.nombre = nombreExtrusion
        self.doc = doc
        self.tipo = "corteRecubierto"

        self.doc.extrusiones[nombreExtrusion] = self
        self.doc.addExtern("Extrusion", nombreExtrusion)

        #Se extrae el string de la base y de su padre mediante metodos que aceptan varios tipos de clases
        stringCroquisInicial = extraerString(croquisInicial)

        if type(croquisInicial) is str:
            croquisInicial = self.doc.seleccionarObjeto(croquisInicial)

        stringPadreCroquisInicial = extraerStringPadre(croquisInicial)

        #Ya que se pueden recibir uno o mas croquis hay que validar que tipo se recibe y asi asegurar 
        #que siempre se tenga una lista
        if type(croquisParaRecubrir) is not list:
            croquisParaRecubrir = [croquisParaRecubrir]

        stringsCroquis = []

        for croquis in croquisParaRecubrir:
            stringsCroquis.append(extraerString(croquis))
        
        self.doc.base.getObject(stringPadreCroquisInicial).newObject('PartDesign::SubtractiveLoft',nombreExtrusion)
        self.base = self.doc.base.getObject(nombreExtrusion)

        self.base.Profile = self.doc.base.getObject(stringCroquisInicial)

        croquisObjects = []

        #Se agregan las secciones de cada croquis para recubrir
        for croquis in stringsCroquis:
            croquisObjects.append(self.doc.base.getObject(croquis))

        self.base.Sections = croquisObjects

        return self

    def salienteConducida(self, doc, croquisPerfil, croquisGuia, nombreExtrusion="salienteConducida"):
        """Barre un perfil cerrado a lo largo de una trayectoria abierta o cerrada para crear una operacion solida"""
        self.nombre = nombreExtrusion
        self.doc = doc
        self.tipo = "salienteConducida"

        self.doc.extrusiones[nombreExtrusion] = self
        self.doc.addExtern("Extrusion", nombreExtrusion)

        #Se extrae el string de la base y de su padre mediante metodos que aceptan varios tipos de clases
        stringCroquisPerfil = extraerString(croquisPerfil)

        if type(croquisPerfil) is str:
            croquisPerfil = self.doc.seleccionarObjeto(croquisPerfil)

        stringPadreCroquisPerfil = extraerStringPadre(croquisPerfil)

        #Se extrae ahora el string del croquis guia
        stringCroquisGuia = extraerString(croquisGuia)

        self.doc.contPlanosReferencia += 1
        stringPlanoReferenciaCorteConducido = f"planoPerfilBarrido{str(self.doc.contPlanosReferencia).zfill(2)}"

        #CREACION DE PLANO DE REFERENCIA Y REUBICACION DE SOPORTE DEL CROQUIS DE PERFIL
        self.doc.base.getObject(stringPadreCroquisPerfil).newObject('PartDesign::Plane',stringPlanoReferenciaCorteConducido)

        self.doc.base.getObject(stringPlanoReferenciaCorteConducido).AttachmentOffset = FreeCAD.Placement(
            FreeCAD.Vector(0.0000000000, 0.0000000000, 0.0000000000),
            FreeCAD.Rotation(0.0000000000, 0.0000000000, 0.0000000000)
        )

        self.doc.base.getObject(stringPlanoReferenciaCorteConducido).MapReversed = False
        self.doc.base.getObject(stringPlanoReferenciaCorteConducido).Support = [(self.doc.base.getObject(stringCroquisGuia),'Edge1')]
        self.doc.base.getObject(stringPlanoReferenciaCorteConducido).MapPathParameter = 0.000000
        self.doc.base.getObject(stringPlanoReferenciaCorteConducido).MapMode = 'NormalToEdge'
        self.doc.base.getObject(stringCroquisPerfil).Support = self.doc.base.getObject(stringPlanoReferenciaCorteConducido)

        #CREACION DE BARRIDO DE CORTE
        self.doc.base.getObject(stringPadreCroquisPerfil).newObject('PartDesign::AdditivePipe',nombreExtrusion)
        self.doc.base.getObject(nombreExtrusion).Profile = self.doc.base.getObject(stringCroquisPerfil)
        self.doc.base.getObject(nombreExtrusion).Spine = self.doc.base.getObject(stringCroquisGuia)
        self.doc.base.getObject(nombreExtrusion).Transition = 'Round corner'

        return self

    def corteConducido(self, doc, croquisPerfil, croquisGuia, nombreExtrusion="corteConducido"):
        """Corta un perfil cerrado a lo largo de una trayectoria abierta o cerrada"""
        self.nombre = nombreExtrusion
        self.doc = doc
        self.tipo = "corteConducido"

        self.doc.extrusiones[nombreExtrusion] = self
        self.doc.addExtern("Extrusion", nombreExtrusion)

        #Se extrae el string de la base y de su padre mediante metodos que aceptan varios tipos de clases
        stringCroquisPerfil = extraerString(croquisPerfil)

        if type(croquisPerfil) is str:
            croquisPerfil = self.doc.seleccionarObjeto(croquisPerfil)

        stringPadreCroquisPerfil = extraerStringPadre(croquisPerfil)

        #Se extrae ahora el string del croquis guia
        stringCroquisGuia = extraerString(croquisGuia)

        self.doc.contPlanosReferencia += 1
        stringPlanoReferenciaCorteConducido = f"planoPerfilBarrido{str(self.doc.contPlanosReferencia).zfill(2)}"

        #CREACION DE PLANO DE REFERENCIA Y REUBICACION DE SOPORTE DEL CROQUIS DE PERFIL
        self.doc.base.getObject(stringPadreCroquisPerfil).newObject('PartDesign::Plane',stringPlanoReferenciaCorteConducido)

        self.doc.base.getObject(stringPlanoReferenciaCorteConducido).AttachmentOffset = FreeCAD.Placement(
            FreeCAD.Vector(0.0000000000, 0.0000000000, 0.0000000000),
            FreeCAD.Rotation(0.0000000000, 0.0000000000, 0.0000000000)
        )

        self.doc.base.getObject(stringPlanoReferenciaCorteConducido).MapReversed = False
        self.doc.base.getObject(stringPlanoReferenciaCorteConducido).Support = [(self.doc.base.getObject(stringCroquisGuia),'Edge1')]
        self.doc.base.getObject(stringPlanoReferenciaCorteConducido).MapPathParameter = 0.000000
        self.doc.base.getObject(stringPlanoReferenciaCorteConducido).MapMode = 'NormalToEdge'
        self.doc.base.getObject(stringCroquisPerfil).Support = self.doc.base.getObject(stringPlanoReferenciaCorteConducido)

        #CREACION DE BARRIDO DE CORTE
        self.doc.base.getObject(stringPadreCroquisPerfil).newObject('PartDesign::SubtractivePipe',nombreExtrusion)
        self.doc.base.getObject(nombreExtrusion).Profile = self.doc.base.getObject(stringCroquisPerfil)
        self.doc.base.getObject(nombreExtrusion).Spine = self.doc.base.getObject(stringCroquisGuia)
        self.doc.base.getObject(nombreExtrusion).Transition = 'Round corner'

        return self
            
class Cuerpo(Extrusion):
    def nuevoCuerpo(self, doc, nombreCuerpo):
        """Constructor de la clase Parte 3D"""
        self.doc = doc
        self.nombre = nombreCuerpo
        self.padre = self.doc.objetoActivo

        self.doc.base.addObject('PartDesign::Body',self.nombre)
        self.doc.cuerpos[self.nombre] = self
        self.doc.addExtern("Cuerpo", self.nombre)
        self.base = self.doc.base.getObject(nombreCuerpo)

        vincular(self.nombre, doc)

        self.doc.objetoActivo = nombreCuerpo

        return self

    def crearPlano(self, nombrePlano, soporte = "XY_Plane", cuerpo = False, modoDeAdjuncion = "FlatFace", offsets = [0, 0, 0], rotaciones = [0, 0, 0], invertido = False):
        """
        ‎Crea un ‎‎plano de referencia‎‎ que se puede utilizar como referencia para croquis u otra 
        geometría de referencia. Los croquis se pueden adjuntar a planos de referencia.‎
        """
        
        #Lo que se necesita para seleccionar el cuerpo es un string, sin embargo este metodo admite que se 
        #pase como parametro un objeto tipo 'Body', para lo cual se extrae el string de su nombre
        if cuerpo is False:
            stringCuerpo = self.doc.objetoActivo
        else:
            stringCuerpo = extraerString(cuerpo)

        #Se crea y agrega el plano como una propiedad del objeto
        #HACK Probar de en lugar de agregar directamente al cuerpo activo primero crear y luego vincular
        self.doc.base.getObject(stringCuerpo).newObject('PartDesign::Plane', nombrePlano)
        self.doc.planos[nombrePlano] = self
        self.doc.addExtern("Plano", nombrePlano)
        self.base = self.doc.base.getObject(nombrePlano)
        
        #Cuerpo del metodo
        self.base.AttachmentOffset = FreeCAD.Placement(
            FreeCAD.Vector(offsets[0], offsets[1], offsets[2]),
            FreeCAD.Rotation(rotaciones[2], rotaciones[1], rotaciones[0])
        )

        self.base.MapReversed = invertido
        self.base.Support = [(self.doc.base.getObject(soporte),'')]
        self.base.MapPathParameter = 0.000000
        self.base.MapMode = modoDeAdjuncion

        return self

class Pieza(Cuerpo):
    def nuevaPieza(self, doc, nombrePieza):
        """Constructor de la clase Parte 3D"""
        self.doc = doc
        self.nombre = nombrePieza

        self.doc.base.addObject('App::Part',self.nombre)
        self.doc.piezas[self.nombre] = self
        self.doc.addExtern("Pieza", self.nombre)
        self.base = self.doc.base.getObject(nombrePieza)

        self.doc.objetoActivo = nombrePieza

        return self

class Parte3D(Pieza):
    def __init__(self, doc):
        """Constructor de la clase Parte 3D"""
        self.doc = doc
        self.nombre = ""

    #Handler
    def nuevaPieza(self, nombrePieza):
        Pieza().nuevaPieza(self.doc, nombrePieza)

        return self
    
    #Handler
    def nuevoCuerpo(self, nombreCuerpo):
        Cuerpo().nuevoCuerpo(self.doc, nombreCuerpo)

        return self

    #Handler
    def nuevoSketch(self, nombreDibujo, cuerpo = False, soporte = "XY_Plane", modoDeAdjuncion = "FlatFace"):
        FabCAD.nuevoSketch(doc = self.doc, nombreDibujo = nombreDibujo, cuerpo = cuerpo, soporte = soporte, modoDeAdjuncion = modoDeAdjuncion)
        
        return self

    #Handler
    def extrusionAditiva(self, croquis = None, nombreExtrusion = 'Pad', longitud = 10, invertido = 0, planoMedio = 0):
        Extrusion().extrusionAditiva(self.doc, croquis=croquis, nombreExtrusion=nombreExtrusion, longitud=longitud, invertido=invertido, planoMedio=planoMedio)
        
        return self 

    #Handler
    def extrusionDeVaciado(self, croquis = None, nombreExtrusion = 'Pocket', longitud = 10, invertido = 0, planoMedio = 0):
        Extrusion().extrusionDeVaciado(self.doc, croquis=croquis, nombreExtrusion=nombreExtrusion, longitud=longitud, invertido=invertido, planoMedio=planoMedio)
        
        return self 
    
    #Handler
    def revolucionAditiva(self, croquis = None, nombreExtrusion = "Revolucion", angulo = 360, invertido = 0, planoMedio = 0 ):
        Extrusion().revolucionAditiva(self.doc, croquis=croquis, nombreExtrusion=nombreExtrusion, angulo=angulo, invertido=invertido, planoMedio=planoMedio)
        
        return self 

    #Handler
    def revolucionDeVaciado(self, croquis = None, nombreExtrusion = "RevDeVaciado", angulo = 360, invertido = 0, planoMedio = 0 ):
        Extrusion().revolucionDeVaciado(self.doc, croquis=croquis, nombreExtrusion=nombreExtrusion, angulo=angulo, invertido=invertido, planoMedio=planoMedio)

        return self

    #Handler
    def recubrir(self, croquisInicial, croquisParaRecubrir, nombreExtrusion = "extrusionRecubierta"):
        Extrusion().recubrir(self.doc, croquisInicial=croquisInicial, croquisParaRecubrir=croquisParaRecubrir, nombreExtrusion=nombreExtrusion)

        return self

    #Handler
    def recubrirCorte(self, croquisInicial, croquisParaRecubrir, nombreExtrusion = "corteRecubierto"):
        Extrusion().recubrirCorte(self.doc, croquisInicial=croquisInicial, croquisParaRecubrir=croquisParaRecubrir, nombreExtrusion=nombreExtrusion)

        return self

    #Handler
    def salienteConducida(self, croquisPerfil, croquisGuia, nombreExtrusion='salienteConducida'):
        Extrusion().salienteConducida(self.doc, croquisPerfil=croquisPerfil, croquisGuia=croquisGuia, nombreExtrusion=nombreExtrusion)

        return self

    #Handler
    def corteConducido(self, croquisPerfil, croquisGuia, nombreExtrusion='corteConducido'):
        Extrusion().corteConducido(self.doc, croquisPerfil=croquisPerfil, croquisGuia=croquisGuia, nombreExtrusion=nombreExtrusion)

        return self
