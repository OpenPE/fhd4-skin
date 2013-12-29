from Components.config import config
from Converter import Converter
from Components.Element import cached
import os
import time
from Poll import Poll
import urllib
import string
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, fileExists

lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
lenguaje = str(lang[:2])
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('spzWeather', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spzWeather/locale/'))
modificando = False

def pondebug(loque, etipo = 0):
    pass

def _(txt):
    t = gettext.dgettext('spzWeather', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t

def equivnoche(imagen):
    listaequi = {'21': '43',
     '14': '39',
     '17': '41',
     '13': '40',
     '5': '37',
     '3': '35',
     '4': '36',
     '6': '38',
     '1': '33',
     '2': '34',
     '16': '42',
     '20': '44',
     '23': '44'}
    if imagen not in listaequi:
        return imagen
    return listaequi[imagen]

def devgificono(imagen, actual = False):
    listaimagenes = {'chance_of_rain.gif': '14',
     'chance_of_snow.gif': '21',
     'chance_of_storm.gif': '17',
     'cloudy.gif': '7',
     'dusty.gif': '11',
     'flurries.gif': '13',
     'fog.gif': '5',
     'foggy.gif': '5',
     'hazy.gif': '5',
     'icy.gif': '31',
     'mist.gif': '18',
     'mostly_cloudy.gif': '6',
     'mostly_sunny.gif': '4',
     'partly_cloudy.gif': '3',
     'rain.gif': '12',
     'rain_snow.gif': '26',
     'showers.gif': '14',
     'sleet.gif': '29',
     'smoke.gif': '8',
     'snow.gif': '22',
     'storm.gif': '15',
     'sunny.gif': '1',
     'thunderstorm.gif': '99'}
    if imagen not in listaimagenes:
        return '14_int-fs8.png'
    valor = listaimagenes[imagen]
    if actual:
        t2 = time.localtime()
        chora = int(time.strftime('%H', t2))
        valornoche = equivnoche(valor)
        if valornoche and (chora >= 22 or chora < 7):
            valor = valornoche
    return valor + '_int-fs8.png'

def devtipo():
    try:
        return config.plugins.spzWeatherPlugin.default.value
    except:
        return 0

def devarchivo():
    if devtipo() == 0:
        return 'wf_spz.xml'
    else:
        return 'wf_forespz.xml'

def devfecha(lafecha = None, sepa = '-'):
    if not lafecha == None:
        t2 = lafecha
    else:
        t2 = time.localtime()
    cdia = str(time.strftime('%d', t2))
    cmes = str(time.strftime('%m', t2))
    chora = '' + str(time.strftime('%H:%M', t2))
    return cdia + sepa + cmes + sepa + chora

def sinovalido(xtipo = 0):
    archivo = '/tmp/' + devarchivo()
    if not fileExists(archivo):
        return
    try:
        dir_stats = os.stat(archivo)
    except:
        return True

    t1 = dir_stats.st_mtime
    t2 = time.localtime()
    tiempsec = time.mktime(t2)
    diferencia = int(tiempsec - t1) / 60 / 60
    if diferencia >= 1 or diferencia < 0:
        pondebug('' + ' archivo caducado :: dif:' + str(diferencia) + ' :: fecha:' + devfecha(time.localtime(dir_stats.st_mtime)) + ' :: ahora:' + devfecha(None), xtipo)
        if diferencia >= 2 or diferencia < 0:
            pondebug('forzado borrado', xtipo)
            os.system('rm -f /tmp/' + devarchivo())
        return True
    else:
        return False

def cargaDatos(tipo = 1, extendido = False):
    ret = False
    if not haywheather():
        return ('',
         '',
         '',
         '',
         '',
         '',
         '',
         False)
    crear = False
    if hayinfowheather():
        crear = sinovalido(tipo)
        chequeanuevo(tipo)
        lugar, estado, temperatura, tmin, tmax, iconohoy, estado2, tmin2, tmax2, iconomanana, ahora = devinfowheather(extendido)
        if extendido:
            textohoy = '' + estado + '\n' + _('Max:') + tmax + ' / ' + _('Min:') + tmin + ''
            textomanana = estado2 + '\n' + _('Max:') + tmax2 + ' / ' + _('Min:') + tmin2 + ''
        else:
            textohoy = tmax + ' / ' + '' + tmin + ''
            textomanana = estado2 + '\n' + tmax2 + ' / ' + '' + tmin2 + ''
        if crear and tipo == 5:
            devxml(tipo)
            ret = True
        if ',' in lugar:
            lugar = lugar.split(',')[0]
        return (lugar,
         temperatura,
         textohoy,
         textomanana,
         iconohoy,
         iconomanana,
         ahora,
         ret)
    chequeanuevo(tipo)
    crear = True
    if crear and tipo == 5:
        devxml(tipo)
    return ('',
     '',
     '',
     '',
     '',
     '',
     '',
     False)

def devxml(etipo = 0):
    if haywheather():
        if hayinet():
            nomw, lanw, pais, comunidad = devwheather()
            pondebug('devxml ' + str(nomw) + str(lanw), etipo)
            if nomw:
                if fileExists('/tmp/tempwf.xml'):
                    return
                if devtipo() == 0:
                    url = 'http://www.google.com/ig/api?weather=%s&hl=%s' % (urllib.quote(nomw), lanw)
                else:
                    url = 'http://www.foreca.%s/%s/%s' % (lanw, pais, nomw)
                pondebug('devxml url:' + str(url), etipo)
                os.system('killall wget')
                os.system('rm -f /tmp/tempwf.xml')
                os.system('wget -qO "/tmp/tempwf.xml" "' + str(url) + '" &')
                pondebug('wget -qO "/tmp/testwf.xml" "' + str(url) + '"', etipo)

def devStrTm(cadena, inicio, fin):
    try:
        if inicio not in cadena:
            return ''
        str = cadena.split(inicio)[1]
        if not fin == '':
            str = str.split(fin)[0]
        return str
    except:
        return ''

def devXml(cadena, tag):
    return devStrTm(cadena, '<' + tag + '>', '</' + tag + '>')

def chequeanuevo(etipo):
    if fileExists('/tmp/tempwf.xml'):
        try:
            f = open('/tmp/tempwf.xml', 'r')
            ret = f.read()
            f.close()
            if '</weather>' in ret and '<forecast_information>' in ret or '<div class="datecopy">' in ret:
                os.system('rm -f /tmp/' + devarchivo())
                if devtipo() == 1:
                    try:
                        os.system('rm /tmp/tempwf.xml')
                        f = open('/tmp/wf_forespz.xml', 'w')
                        ertexto = devStrTm(ret, '<h1 class="entry-title"', '<div class="datecopy">').replace('<strong>', '').replace('</strong>', '').replace('\t', '').replace('   ', '').replace('  ', '').replace('<br /><br />', '<br />').replace('<br /> <br />', '<br />').replace('\n', '').replace('&deg;', '\xc2\xbaC') + ' (from renderer)'
                        f.write(ertexto)
                        f.close()
                    except:
                        pondebug('Error escribiendo en /tmp/wf_forespz.xml', etipo)

                else:
                    os.system('mv -f /tmp/tempwf.xml /tmp/' + devarchivo())
                pondebug('chequea nuevo creado', etipo)
            else:
                pondebug('chequeanuevo incompleto', etipo)
                archivo = '/tmp/tempwf.xml'
                if not fileExists(archivo):
                    return
                try:
                    dir_stats = os.stat(archivo)
                except:
                    return

                t1 = dir_stats.st_mtime
                t2 = time.localtime()
                tiempsec = time.mktime(t2)
                diferencia = int(tiempsec - t1) / 60
                if diferencia >= 1 or diferencia < 0:
                    os.system('killall wget')
                    os.system('rm -f /tmp/tempwf.xml')
                    pondebug('caducado tempwf.xml y borrado', etipo)
        except:
            pondebug('error renombrando', etipo)

def devHtml(cadena, etiqueta, cortar = False):
    tempcad = devStrTm(cadena, etiqueta, '')
    devcad = devStrTm(tempcad, '>', '<')
    if cortar:
        devcad2 = devStrTm(devcad, ':', '').replace(' ', '')
    else:
        devcad2 = devcad
    return devcad2.replace('&deg;', '\xc2\xba')

def devImagen(cadena, etiqueta):
    tempcad = devStrTm(cadena, etiqueta, '')
    devcad = devStrTm(tempcad, 'src="', '"')
    parts = string.split(devcad, '/')
    filename = parts[-1]
    return filename

def devinfoacuOLD(xmlstring, extendido):
    t2 = devHtml(xmlstring, 'ctl00_LocationHeader_lnkLocation')
    t12 = devHtml(xmlstring, 'ctl00_cphContent_lblCurrentText')
    t4 = devHtml(xmlstring, 'ctl00_cphContent_lblCurrentTemp')
    t3 = ''
    if extendido:
        t3 = t3 + '' + _('Humidity') + ' ' + devHtml(xmlstring, 'ctl00_cphContent_lblHumidityValue')
        t3 = t3 + ', ' + _('Wind') + ' ' + devHtml(xmlstring, 'ctl00_cphContent_lblWindsValue')
        t3 = t3 + '\n' + _('Pressure') + ' ' + devHtml(xmlstring, 'ctl00_cphContent_lblPressureValue') + '(' + devHtml(xmlstring, 'ctl00_cphContent_lblPressureTenValue') + ')'
    t5 = devHtml(xmlstring, 'ctl00_cphContent_lblLow1', True)
    t6 = devHtml(xmlstring, 'ctl00_cphContent_lblHigh1', True)
    t7 = devImagen(xmlstring, 'ctl00_cphContent_imgCurConCondition')
    t8 = ''
    t8 = t8 + '' + devHtml(xmlstring, 'ctl00_cphContent_lblDayName2')
    if extendido:
        t8 = t8 + '\n' + devHtml(xmlstring, 'ctl00_cphContent_lblTxtForecast2')
    t9 = devHtml(xmlstring, 'ctl00_cphContent_lblLow2', True)
    t10 = devHtml(xmlstring, 'ctl00_cphContent_lblHigh2', True)
    t11 = devImagen(xmlstring, 'ctl00_cphContent_imgDay2Icon')
    return (t2,
     t3,
     t4,
     t5,
     t6,
     t7,
     t8,
     t9,
     t10,
     t11,
     t12)

def devinfoacu(xmlstring, extendido):
    try:
        t2 = devStrTm(xmlstring, '>', '<').strip()
        lacondicion = devStrTm(xmlstring, '<div class="right txt-tight">', '</div>').replace('<br />', '\n').replace('\n ', '\n')
        arrcon = lacondicion.split('\n')
        if len(arrcon) > 1:
            t12 = arrcon[0]
        t4 = devHtml(xmlstring, 'warm txt-xxlarge').strip().replace('+', '').strip()
        t3 = ''
        if extendido:
            tempviento = devStrTm(xmlstring, '/img/symb-wind', '<br />')
            dirviento = devStrTm(tempviento, 'alt="', '"')
            dirviento = dirviento.replace('N', _('North')).replace('S', _('South')).replace('E', _('East')).replace('W', _('West')).replace('NorteOeste', 'NorOeste').replace('NorteEste', 'NorEste')
            iviento = devStrTm(tempviento, '/>', '').replace('<br />', '')
            viento = _('Wind') + ':' + dirviento + ' ' + iviento
            if len(arrcon) > 6:
                t3 = t3 + arrcon[4].strip()
                t3 = t3 + ', ' + viento.strip()
                t3 = t3 + '\n' + arrcon[2].strip()
            else:
                conta = 1
                for iij in range(0, len(arrcon) - 1):
                    if arrcon[iij].strip != '':
                        if conta == 3:
                            t3 = t3 + '\n'
                            t3 = t3 + arrcon[iij]
                        elif conta > 1:
                            pass
                        else:
                            t3 = t3 + arrcon[iij]
                        conta = conta + 1
                        if conta > 3:
                            break

        tempdias = devStrTm(xmlstring, '<div class="c2">', '').replace('<br />', '')
        arrdias = tempdias.split('<div class="c2_a">')
        t5 = ''
        t6 = ''
        if len(arrdias) > 1:
            eltexto = arrdias[1]
            t6 = devStrTm(eltexto, '<span>', '</span>')
            t6 = devStrTm(t6, ':', '').strip().replace('+', '')
            temp2 = devStrTm(eltexto, '</span>', '</span>')
            t5 = devStrTm(temp2, '<span>', '</span>')
            t5 = devStrTm(t5, ':', '').strip().replace('+', '')
        simirar = False
        itemp = None
        if 'cc_symb">' not in xmlstring:
            simirar = True
        if simirar:
            try:
                tempact = t4.split(' ')[0]
                itemp = int(tempact)
            except:
                pass

        t7 = gesImagen(xmlstring, simirar, itemp)
        t8 = ''
        t9 = ''
        t10 = ''
        cana = ''
        eltexto = ''
        if len(arrdias) > 2:
            eltexto = arrdias[2]
            t8 = devHtml(eltexto, 'a href="')
            cana = devStrTm(eltexto, 'title="', '"')
            t10 = devStrTm(eltexto, '<span>', '</span>')
            t10 = devStrTm(t10, ':', '').strip().replace('+', '')
            temp2 = devStrTm(eltexto, '</span>', '</span>')
            t9 = devStrTm(temp2, '<span>', '</span>')
            t9 = devStrTm(t9, ':', '').strip().replace('+', '')
        if extendido:
            t8 = t8 + '\n' + cana
        t11 = gesImagen(eltexto)
        return (t2,
         t3,
         t4,
         t5,
         t6,
         t7,
         t8,
         t9,
         t10,
         t11,
         t12)
    except:
        return ('', '', '', '', '', '', '', '', '', '', '')

    return

def getImagen(codigo, mirarnoche = False):
    listaimagenes = {'111': '5',
     '000': '1',
     '100': '2',
     '200': '3',
     '210': '14',
     '211': '21',
     '212': '21',
     '220': '13',
     '221': '20',
     '222': '20',
     '240': '17',
     '300': '6',
     '310': '13',
     '311': '23',
     '312': '23',
     '320': '13',
     '321': '20',
     '322': '20',
     '340': '16',
     '400': '7',
     '410': '8',
     '411': '24',
     '412': '24',
     '420': '18',
     '421': '26',
     '422': '19',
     '430': '12',
     '431': '29',
     '432': '22',
     '440': '15'}
    imagen = codigo[1:]
    if imagen not in listaimagenes:
        valor = '5'
    else:
        valor = listaimagenes[imagen]
    if codigo[0] == 'n' or mirarnoche:
        valor = equivnoche(valor)
    return valor + '_int-fs8.png'

def gesImagen(xmlstring, mirarnoche = False, temperatura = None):
    if temperatura == None:
        tempxml = devStrTm(xmlstring, '<div class="symbol_', '</div>')
        tempxml = devStrTm(tempxml, 'symbol_', '_')
        if mirarnoche:
            t2 = time.localtime()
            chora = int(time.strftime('%H', t2))
            if chora >= 21 or chora < 7:
                mirarnoche = True
            else:
                mirarnoche = False
        if len(tempxml) <= 2:
            laimagen = getImagen('d111', mirarnoche)
        else:
            laimagen = getImagen(tempxml, mirarnoche)
    elif temperatura <= 3:
        laimagen = 't0-fs8.png'
    elif temperatura <= 10:
        laimagen = 't1-fs8.png'
    elif temperatura <= 19:
        laimagen = 't2-fs8.png'
    elif temperatura <= 28:
        laimagen = 't3-fs8.png'
    elif temperatura <= 36:
        laimagen = 't4-fs8.png'
    else:
        laimagen = 't5-fs8.png'
    filename = laimagen
    filenamepng = filename.replace('.jpg', '-fs8.png')
    return filenamepng

def devinfowheather(extendido):
    try:
        f = open('/tmp/' + devarchivo(), 'r')
        rettemp = f.read()
        f.close()
    except:
        pondebug('devinfowheater ERROR')
        return ('', '', '', '', '', '', '', '', '', '', '')

    if devtipo() == 1:
        return devinfoacu(rettemp, extendido)
    sourceEncoding = 'iso-8859-1'
    targetEncoding = 'utf-8'
    ret = unicode(rettemp, sourceEncoding).encode(targetEncoding)
    infoactual = devXml(ret, 'current_conditions')
    infolugar = devXml(ret, 'forecast_information')
    infohoy = devXml(ret, 'forecast_conditions')
    ret2 = ret.replace(infohoy, '')
    infoman = devStrTm(ret, 'forecast_conditions><forecast_conditions>', '</forecast_conditions>')
    unidades = '\xc2\xbaF'
    if 'unit_system data="SI"' in infolugar:
        unidades = '\xc2\xbaC'
        t4 = devStrTm(infoactual, 'temp_c data="', '"') + unidades
    else:
        t4 = devStrTm(infoactual, 'temp_f data="', '"') + unidades
    t2 = devStrTm(infolugar, 'city data="', '"')
    t12 = devStrTm(infoactual, 'condition data="', '"')
    t3 = ''
    if extendido:
        t3 = t3 + '' + devStrTm(infoactual, 'humidity data="', '"').replace(':', '')
        t3 = t3 + ', ' + devStrTm(infoactual, 'wind_condition data="', '"').replace(':', '')
    t5 = devStrTm(infohoy, 'low data="', '"') + unidades
    t6 = devStrTm(infohoy, 'high data="', '"') + unidades
    t7 = devStrTm(infoactual, 'icon data="', '"').replace('/ig/images/weather/', '')
    t8 = ''
    t8 = t8 + '' + devsem(devStrTm(infoman, 'day_of_week data="', '"'))
    if extendido:
        t8 = t8 + '\n' + devStrTm(infoman, 'condition data="', '"')
    t9 = devStrTm(infoman, 'low data="', '"') + unidades
    t10 = devStrTm(infoman, 'high data="', '"') + unidades
    t11 = devStrTm(infoman, 'icon data="', '"').replace('/ig/images/weather/', '')
    return (t2,
     t3,
     t4,
     t5,
     t6,
     t7,
     t8,
     t9,
     t10,
     t11,
     t12)

from string import upper

def devsem(dia):
    ret = dia
    if config.plugins.spzWeatherPlugin.Entries[0].language.value == 'es':
        if dia == 'lun':
            ret = 'Lunes'
        elif dia == 'mar':
            ret = 'Martes'
        elif dia == 'mi\xc3\xa9':
            ret = 'Mi\xc3\xa9rcoles'
        elif dia == 'jue':
            ret = 'Jueves'
        elif dia == 'vie':
            ret = 'Viernes'
        elif dia == 's\xc3\xa1b':
            ret = 'S\xc3\xa1bado'
        elif dia == 'dom':
            ret = 'Domingo'
        else:
            ret = upper(ret)
    else:
        ret = upper(ret)
    return ret

def hayinfowheather():
    if fileExists('/tmp/' + devarchivo()):
        return True
    else:
        return False

def haywheather():
    rethay = False
    try:
        if config.misc.spazeinfobarmeteo.value:
            rethay = True
        else:
            rethay = False
            return rethay
    except:
        rethay = True

    try:
        if devtipo() == 0:
            numero = config.plugins.spzWeatherPlugin.entriescount.value
        else:
            numero = config.plugins.spzWeatherPlugin.foreentriescount.value
        if numero >= 1:
            rethay = True
        else:
            rethay = False
    except:
        rethay = False

    return rethay

def hayinet():
    ret = False
    try:
        f = open('/tmp/testinet.txt', 'r')
        texto = f.read().replace('\n', '')
        f.close()
        if 'packets transmitted, 1 packets received' in texto:
            ret = True
    except:
        pass

    if not ret:
        try:
            os.system('ping -q -c 1 -s 6 -w 2 www.google.es >/tmp/testinet.txt &')
        except:
            pass

    return ret

def devwheather():
    rethay = None
    rethay2 = None
    rethay3 = None
    rethay4 = None
    try:
        if devtipo() == 0:
            numero = config.plugins.spzWeatherPlugin.entriescount.value
            if numero >= 1:
                rethay = config.plugins.spzWeatherPlugin.Entries[0].city.value
                rethay2 = config.plugins.spzWeatherPlugin.Entries[0].language.value
        else:
            numero = config.plugins.spzWeatherPlugin.foreentriescount.value
            if numero >= 1:
                rethay = config.plugins.spzWeatherPlugin.foreEntries[0].city.value
                rethay4 = None
                rethay3 = config.plugins.spzWeatherPlugin.foreEntries[0].pais.value
                rethay2 = config.plugins.spzWeatherPlugin.foreEntries[0].dominio.value
    except:
        pass

    return (rethay,
     rethay2,
     rethay3,
     rethay4)

class wheaterSpz(Poll, Converter, object):
    WFEXIST = 0
    TIEMPOHOY = 1
    ICONOHOY = 2
    TIEMPOMAN = 3
    ICONOMAN = 4
    WFLUGAR = 5
    WFTEMP = 6
    WFNOEXIST = 7
    AHORA = 8
    LUGARGRADOS = 10

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.poll_enabled = True
        self.textohoy = ''
        self.textomanana = ''
        self.iconohoy = ''
        self.iconomanana = ''
        self.lugar = ''
        self.temperatura = ''
        self.ahora = ''
        self.png = None
        self.rutaimagen = '/usr/lib/enigma2/python/Plugins/Extensions/spzWeather/wheathericons/'
        self.rutapng = '/usr/lib/enigma2/python/Plugins/Extensions/spzWeather/spzwheatherIcons/'
        self.rutapngacu = '/usr/lib/enigma2/python/Plugins/Extensions/spzWeather/acuwheathericons/'
        self.extended = False
        if type == 'Existe':
            self.type = self.WFEXIST
        elif type == 'noExiste':
            self.type = self.WFNOEXIST
        elif type == 'TextoHoy':
            self.type = self.TIEMPOHOY
        elif type == 'TextoHoyExt':
            self.type = self.TIEMPOHOY
            self.extended = True
        elif type == 'TextoManExt':
            self.type = self.TIEMPOMAN
            self.extended = True
        elif type == 'TextoMan':
            self.type = self.TIEMPOMAN
        elif type == 'IconoHoy':
            self.type = self.ICONOHOY
        elif type == 'IconoMan':
            self.type = self.ICONOMAN
        elif type == 'Lugar':
            self.type = self.WFLUGAR
        elif type == 'Temperatura':
            self.type = self.WFTEMP
        elif type == 'Ahora':
            self.type = self.AHORA
        elif type == 'LugarGrados':
            self.type = self.LUGARGRADOS
        self.intervalo = 3720000
        self.poll_interval = 30000
        pondebug('init - tipo [' + str(type) + ']', self.type)
        return

    @cached
    def getBoolean(self):
        ret = False
        service = self.source.service
        self.png = None
        info = service and service.info()
        if not info:
            ret = False
            if self.type == self.WFNOEXIST:
                ret = not ret
            return ret
        else:
            pondebug('getBoolean - tipo [' + str(self.type) + ']', self.type)
            self.poll_interval = self.intervalo
            if haywheather() and hayinfowheather():
                ret = True
            else:
                if haywheather():
                    self.poll_interval = 6000
                ret = False
            if self.type == self.WFNOEXIST:
                ret = not ret
            return ret

    boolean = property(getBoolean)

    @cached
    def getText(self):
        global modificando
        info = None
        pondebug('getext - tipo [' + str(self.type) + ']' + str(modificando), self.type)
        try:
            service = self.source.service
            info = service and service.info()
            pondebug('service - tipo [' + str(self.type) + ']', self.type)
        except:
            pass

        if not info:
            return ''
        else:
            text = ''
            if haywheather():
                self.poll_interval = self.intervalo
                if modificando:
                    if self.type == 5:
                        modificando = False
                    else:
                        pondebug('getext' + ' MODIFICANDO - tipo [' + str(self.type) + ']', self.type)
                        self.poll_interval = 7000
                self.lugar, self.temperatura, self.textohoy, self.textomanana, self.iconohoy, self.iconomanana, self.ahora, actualizando = cargaDatos(self.type, self.extended)
                if actualizando:
                    if self.type == 5:
                        modificando = True
                    self.poll_interval = 7000
                if self.type == self.TIEMPOHOY:
                    text = self.textohoy
                elif self.type == self.AHORA:
                    text = self.ahora
                elif self.type == self.TIEMPOMAN:
                    text = self.textomanana
                elif self.type == self.WFLUGAR:
                    text = self.lugar
                elif self.type == self.WFTEMP:
                    text = self.temperatura
                elif self.type == self.LUGARGRADOS:
                    if len(self.lugar) > 17:
                        self.lugar = self.lugar[:16] + '...'
                    text = self.lugar + ' ' + self.textohoy.replace('C', '').replace('F', '').replace(' ', '')
                elif self.type == self.ICONOHOY:
                    if self.iconohoy == '':
                        pngname = ''
                    else:
                        iconogif = self.iconohoy
                        if devtipo() == 0:
                            iconopng = devgificono(iconogif, actual=True)
                            rpng = self.rutapngacu
                        else:
                            iconopng = iconogif.replace('.jpg', '-fs8.png')
                            rpng = self.rutapngacu
                        pondebug('imagen [' + rpng + iconopng + ']', self.type)
                        if fileExists(rpng + iconopng):
                            pngname = rpng + iconopng
                        elif fileExists(self.rutaimagen + iconogif):
                            pngname = self.rutaimagen + iconogif
                        else:
                            pngname = self.rutapng + '0-fs8.png'
                    text = pngname
                elif self.type == self.ICONOMAN:
                    if self.iconomanana == '':
                        pngname = ''
                    else:
                        iconogif = self.iconomanana
                        if devtipo() == 0:
                            iconopng = devgificono(iconogif)
                            rpng = self.rutapngacu
                        else:
                            iconopng = iconogif.replace('.jpg', '-fs8.png')
                            rpng = self.rutapngacu
                        if fileExists(rpng + iconopng):
                            pngname = rpng + iconopng
                        elif fileExists(self.rutaimagen + iconogif):
                            pngname = self.rutaimagen + iconogif
                        else:
                            pngname = self.rutapng + '0-fs8.png'
                    text = pngname
            if text == '':
                self.poll_interval = 6000
            pondebug('return  - tipo [' + str(self.type) + ']' + '-[' + str(text) + ']', self.type)
            return text

    text = property(getText)

    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC or what[1] == self.type:
            pondebug('changed - tipo [' + str(self.type) + ']' + '-' + str(what), self.type)
            Converter.changed(self, what)
