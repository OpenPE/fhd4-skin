from Components.config import config
from Converter import Converter
from Components.Element import cached
from Poll import Poll
from enigma import eServiceCenter, eServiceReference, iServiceInformation
from xml.etree.cElementTree import parse
from time import time
from ServiceReference import ServiceReference
from Tools.FuzzyDate import FuzzyTime
import NavigationInstance
import os

class infoRecBm(Poll, Converter, object):
    DURACION = 0
    INICIO = 1
    FIN = 2
    NOMBRE = 3
    RESTAN = 4
    PROGRESO = 5
    CANAL = 6
    NOMBREYCANAL = 7
    INFO = 8

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        if type == 'Programa':
            self.type = self.NOMBRE
        elif type == 'Inicio':
            self.type = self.INICIO
            self.poll_interval = 30000
            self.poll_enabled = True
        elif type == 'Fin':
            self.type = self.FIN
            self.poll_interval = 30000
            self.poll_enabled = True
        elif type == 'Duracion':
            self.type = self.DURACION
            self.poll_interval = 30000
            self.poll_enabled = True
        elif type == 'Restan':
            self.type = self.RESTAN
            self.poll_interval = 10000
            self.poll_enabled = True
        elif type == 'Progress':
            self.type = self.PROGRESO
            self.poll_interval = 300
            self.poll_enabled = True
        elif type == 'Canal':
            self.type = self.CANAL
            self.poll_interval = 10000
            self.poll_enabled = True
        elif type == 'NombreyCanal':
            self.type = self.NOMBREYCANAL
            self.poll_interval = 30000
            self.poll_enabled = True
        elif type == 'Info':
            self.type = self.INFO
            self.poll_interval = 30000
            self.poll_enabled = True

    @cached
    def getText(self):
        self.recordings = self.source.getBoolean()
        text = None
        mostrardebug = False
        if self.recordings:
            ref = 'err'
            try:
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    ref = str(ServiceReference(InfoBar.instance.session.nav.getCurrentlyPlayingServiceReference()))
            except:
                pass

            if mostrardebug:
                os.system("echo 'inicio[" + str(self.type) + "]'>/tmp/testrec.txt")
            conta = 0
            infovarios = False
            for timer in NavigationInstance.instance.RecordTimer.timer_list:
                if timer.state == timer.StateRunning:
                    conta = conta + 1
                    infovarios = False
                    nombre = timer.name
                    if mostrardebug:
                        os.system("echo 'nombre: [" + str(nombre) + "]'>>/tmp/testrec.txt")
                        os.system("echo 'ref: [" + str(ref) + "]'>>/tmp/testrec.txt")
                    if len(nombre) < 2:
                        try:
                            nombre = os.path.split(timer.Filename)[1]
                        except:
                            nombre = '(' + _('Record') + ')'

                    try:
                        archivo = str(timer.Filename).replace('\n', '')
                    except:
                        archivo = 'NA'

                    if mostrardebug:
                        os.system("echo 'archivo: [" + archivo + "]'>>/tmp/testrec.txt")
                    inicio = str(FuzzyTime(timer.begin)[1])
                    fin = str(FuzzyTime(timer.end)[1])
                    duracion = str((timer.end - timer.begin) / 60) + ' ' + _('mins')
                    nfaltan = (timer.end - time()) / 60
                    if nfaltan >= 1:
                        faltan = str(int(nfaltan)) + ' ' + _('mins')
                    else:
                        faltan = str(int(nfaltan * 60)) + ' ' + _('secs')
                        self.poll_interval = 300
                    nomcan = timer.service_ref.getServiceName()
                    if self.type == self.DURACION:
                        text = duracion
                    elif self.type == self.INICIO:
                        text = inicio
                    elif self.type == self.FIN:
                        text = fin
                    elif self.type == self.NOMBRE:
                        text = nombre
                    elif self.type == self.RESTAN:
                        text = faltan
                    elif self.type == self.CANAL:
                        text = nomcan
                    elif self.type == self.NOMBREYCANAL:
                        text = nomcan
                        if len(text) > 20:
                            text = text[:17] + '...'
                        text = text + ' (+' + faltan + ') '
                    elif self.type == self.INFO:
                        infovarios = True
                        text = inicio + ' - ' + fin + ' (+' + faltan + ') '
                        text = text + ' ' + nomcan
                        if len(text) > 40:
                            text = text[:37] + '...'
                        text = text + ' :: ' + nombre
                        if len(text) > 69:
                            text = text[:66] + '...'
                    elif self.type == self.PROGRESO:
                        now = int(time())
                        start_time = timer.begin
                        duration = timer.end - timer.begin
                        valor = int((int(time()) - timer.begin) * 100 / duration)
                        text = str(valor) + ' %'
                    if archivo in ref or ref == str(timer.service_ref):
                        if mostrardebug:
                            os.system("echo 'break'>>/tmp/testrec.txt")
                        break
                    if mostrardebug:
                        os.system("echo '-----------------------------------------------------'>>/tmp/testrec.txt")

            if conta > 1 and infovarios:
                text = text + '(' + str(conta) + ' RECs)'
        return text

    text = property(getText)

    @cached
    def getValue(self):
        self.recordings = self.source.getBoolean()
        valor = None
        if self.recordings:
            ref = 'err'
            try:
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    ref = str(ServiceReference(InfoBar.instance.session.nav.getCurrentlyPlayingServiceReference()))
            except:
                pass

            for timer in NavigationInstance.instance.RecordTimer.timer_list:
                if timer.state == timer.StateRunning:
                    if self.type == self.PROGRESO:
                        now = int(time())
                        start_time = timer.begin
                        duration = timer.end - timer.begin
                        try:
                            archivo = str(timer.Filename).replace('\n', '')
                        except:
                            archivo = 'NA'

                        valor = int((int(time()) - timer.begin) * 100 / duration)
                        pos = valor
                        len = 100
                        valor = pos * 10000 / len
                        if archivo in ref or ref == str(timer.service_ref):
                            break

        return valor

    range = 10000
    value = property(getValue)

    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC or what[1] == self.type:
            Converter.changed(self, what)
