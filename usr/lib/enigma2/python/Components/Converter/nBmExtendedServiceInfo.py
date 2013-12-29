from Components.config import config, ConfigYesNo
from Components.Converter.Converter import Converter
from Components.Element import cached
from enigma import eServiceCenter, eServiceReference, iServiceInformation
from xml.etree.cElementTree import parse
from Poll import Poll
from os import system
from Components.Network import iNetwork
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import threading
import re

lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('nBmExtendedServiceInfo', '%s%s' % ('/usr/lib/enigma2/python/Components/', 'Converter/locale/'))

def _(txt):
    t = gettext.dgettext('nBmExtendedServiceInfo', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t

config.misc.spazeinfobartp = ConfigYesNo(default=True)
config.misc.spazeinfobarecm = ConfigYesNo(default=True)
config.misc.spazeinfobarnum = ConfigYesNo(default=True)
config.misc.spazeinfobarinet = ConfigYesNo(default=True)
config.misc.spazeinfobarrec = ConfigYesNo(default=True)

class segundoplano(threading.Thread):

    def __init__(self, parametro, six):
        threading.Thread.__init__(self)
        self.parametro = parametro
        self.six = six

    def run(self):
        self.parametro.subcargasat(self.six)

def haytp():
    ret = True
    try:
        ret = config.misc.spazeinfobartp.value
    except:
        pass

    return ret

def hayecm():
    ret = True
    try:
        ret = config.misc.spazeinfobarecm.value
    except:
        pass

    return ret

def haynum():
    ret = True
    try:
        ret = config.misc.spazeinfobarnum.value
    except:
        pass

    return ret

def hayinet():
    ret = True
    try:
        ret = config.misc.spazeinfobarinet.value
    except:
        pass

    return ret

def devStr(cadena, inicio = ':', fin = None):
    try:
        if cadena == None:
            return ''
        if not inicio == None:
            if inicio not in cadena:
                return cadena
            str = cadena.split(inicio)[1]
        else:
            str = cadena
        if not fin == None:
            if fin in cadena:
                str = str.split(fin)[0]
        return str.strip()
    except:
        return ''

    return

def _commafy(s):
    r = []
    for i, c in enumerate(reversed(s)):
        if i and not i % 3:
            r.insert(0, '#')
        r.insert(0, c)

    return ''.join(r)

def FormatWithCommas(value, sepmil = '.', sepdec = ',', ndecimales = 0, cmoneda = ''):
    re_digits_nondigits = re.compile('\\d+|\\D+')
    format = '%.' + str(ndecimales) + 'f' + cmoneda
    if value == None:
        return ''
    elif str(value) == '':
        return ''
    else:
        cvalue = str(value)
        try:
            fvalue = float(value)
        except:
            return value

        try:
            parts = re_digits_nondigits.findall(format % (fvalue,))
            for i in xrange(len(parts)):
                s = parts[i]
                if s.isdigit():
                    parts[i] = _commafy(s)
                    break

            return ''.join(parts).replace('.', sepdec).replace('#', sepmil)
        except:
            return value

        return

def getFEData(frontendDataOrg):
    from Tools.Transponder import ConvertToHumanReadable
    try:
        if frontendDataOrg and len(frontendDataOrg):
            frontendData = ConvertToHumanReadable(frontendDataOrg)
            if frontendDataOrg['tuner_type'] == 'DVB-S':
                return str(FormatWithCommas(int(frontendData['frequency']) / 1000)) + ' MHz ' + str(FormatWithCommas(int(frontendData['symbol_rate']) / 1000)) + ' ' + str(frontendData['polarization'][0:1]) + ' ' + str(frontendData['fec_inner'])
            if frontendDataOrg['tuner_type'] == 'DVB-C':
                return str(frontendData['frequency']) + ' ' + str(frontendData['symbol_rate'])
            if frontendDataOrg['tuner_type'] == 'DVB-T':
                return str(FormatWithCommas(ajustafr(int(frontendData['frequency'])))) + ' Khz (UHF ' + str(devchfr(frontendData['frequency'])) + ') ' + str(frontendData['bandwidth'])
        return ' '
    except:
        return ' '

def ajustafr(frecu):
    return int(round(float(frecu) / 1000000, 0)) * 1000

def devchfr(frecu):
    ret = 'NA'
    arrfecs = [(21, 474),
     (22, 482),
     (23, 490),
     (24, 498),
     (25, 506),
     (26, 514),
     (27, 522),
     (28, 530),
     (29, 538),
     (30, 546),
     (31, 554),
     (32, 562),
     (33, 570),
     (34, 578),
     (35, 586),
     (36, 594),
     (37, 602),
     (38, 610),
     (39, 618),
     (40, 626),
     (41, 634),
     (42, 642),
     (43, 650),
     (44, 658),
     (45, 666),
     (46, 674),
     (47, 682),
     (48, 690),
     (49, 698),
     (50, 706),
     (51, 714),
     (52, 722),
     (53, 730),
     (54, 738),
     (55, 746),
     (56, 754),
     (57, 762),
     (58, 770),
     (59, 778),
     (60, 786),
     (61, 794),
     (62, 802),
     (63, 810),
     (64, 818),
     (65, 826),
     (66, 834),
     (67, 842),
     (68, 850),
     (69, 858)]
    nfrecu = ajustafr(frecu) / 1000
    for ele in arrfecs:
        if ele[1] == nfrecu:
            ret = ele[0]
            return ret

    return ret

class nBmExtendedServiceInfo(Poll, Converter, object):
    SERVICENAME = 0
    SERVICENUMBER = 1
    ORBITALPOSITION = 2
    SATNAME = 3
    PROVIDER = 4
    FROMCONFIG = 5
    ALL = 6
    ECMINFO = 7
    CAMNAME = 8
    INETCONECTION = 9
    NETCONECTION = 10

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.poll_interval = 10000
        self.poll_enabled = True
        self.tv_list = []
        self.seg_plano = None
        self.radio_list = []
        self.satNames = {}
        self.systemCaids = {'06': 'irdeto',
         '01': 'seca',
         '18': 'nagra',
         '05': 'via',
         '0B': 'conax',
         '17': 'betacrypt',
         '0D': 'crypto',
         '4A': 'dreamcrypt',
         '09': 'nds'}
        if type == 'ServiceName':
            self.type = self.SERVICENAME
        elif type == 'Number':
            self.type = self.SERVICENUMBER
        elif type == 'TunerInfo':
            self.type = self.ORBITALPOSITION
        elif type == 'SatName':
            self.type = self.SATNAME
        elif type == 'Provider':
            self.type = self.PROVIDER
        elif type == 'Config':
            self.type = self.FROMCONFIG
        elif type == 'InetConection':
            self.poll_interval = 5000
            self.type = self.INETCONECTION
        elif type == 'NetConection':
            self.poll_interval = 5000
            self.type = self.NETCONECTION
        elif type == 'EcmInfo':
            self.poll_interval = 3000
            self.type = 7
        elif type == 'CamName':
            self.type = 8
        else:
            self.type = self.ALL
        return

    @cached
    def getBoolean(self):
        ret = False
        service = self.source.service
        info = service and service.info()
        if not info:
            return False
        if self.type == self.INETCONECTION:
            if not hayinet():
                ret = False
            else:
                try:
                    f = open('/tmp/testinet.txt', 'r')
                    texto = f.read().replace('\n', '')
                    f.close()
                    if '1 packets transmitted, 1 packets received' in texto:
                        ret = True
                except:
                    pass

                try:
                    system('ping -q -c 1 -s 6 -w 2 www.google.com >/tmp/testinet.txt &')
                except:
                    pass

        elif self.type == self.NETCONECTION:
            try:
                adapters = [ (iNetwork.getFriendlyAdapterName(x), x) for x in iNetwork.getAdapterList() ]
            except:
                adapters = False

            if not adapters:
                ret = False
            else:
                puerta = '0.0.0.0'
                for x in adapters:
                    if iNetwork.getAdapterAttribute(x[1], 'up') is True:
                        puerta = str(iNetwork.getAdapterAttribute(x[1], 'gateway')).replace(',', '.').replace('[', '').replace(' ', '').replace(']', '')
                        break

                if puerta == '0.0.0.0':
                    ret = False
                else:
                    try:
                        f = open('/tmp/testnet.txt', 'r')
                        texto = f.read().replace('\n', '')
                        f.close()
                        if '1 packets transmitted, 1 packets received' in texto:
                            ret = True
                    except:
                        pass

                    try:
                        system('ping -q -c 1 -s 6 -w 2 ' + puerta + ' >/tmp/testnet.txt &')
                    except:
                        pass

        return ret

    boolean = property(getBoolean)

    @cached
    def getText(self):
        if len(self.tv_list) == 0:
            if haytp():
                self.cargasat(self.type)
            elif haynum():
                self.cargasat(self.type, False)
        service = self.source.service
        info = service and service.info()
        if not info:
            return ''
        else:
            text = ''
            orbital = ''
            number = ''
            satName = ''
            name = info.getName().replace('\xc2\x86', '').replace('\xc2\x87', '')
            if self.type == self.SERVICENAME:
                text = name
            elif self.type == self.CAMNAME:
                text = ''
                if hayecm():
                    try:
                        f = open('/tmp/.cam.info', 'r')
                        text = text + f.read().replace('\n', '')
                        f.close()
                    except:
                        pass

                    try:
                        f = open('/etc/.ActiveCamd', 'r')
                        text = text + f.read().replace('\n', '')
                        f.close()
                        if text == 'no':
                            text = _('No CAM')
                    except:
                        pass

                    if text == '':
                        text == _('No CAM')
            elif self.type == self.SERVICENUMBER:
                if haynum():
                    number = self.getServiceNumber(name, info.getInfoString(iServiceInformation.sServiceref))
                    text = number
            elif self.type == self.ORBITALPOSITION:
                if haytp():
                    orbital = self.getOrbitalPosition(info)
                    text = orbital
            elif self.type == self.SATNAME:
                if haytp():
                    orbital = self.getOrbitalPosition(info)
                    satName = self.satNames.get(orbital, orbital)
                    text = satName
            elif self.type == self.PROVIDER:
                text = info.getInfoString(iServiceInformation.sProvider)
            elif self.type == self.FROMCONFIG:
                if haytp():
                    orbital = self.getOrbitalPosition(info)
                    satName = self.satNames.get(orbital, orbital)
                    number = self.getServiceNumber(name, info.getInfoString(iServiceInformation.sServiceref))
                    if config.plugins.ExtendedServiceInfo.showServiceNumber.value == True and number != '':
                        text = '%s. %s' % (number, name)
                    else:
                        text = name
                    if config.plugins.ExtendedServiceInfo.showOrbitalPosition.value == True and orbital != '':
                        if config.plugins.ExtendedServiceInfo.orbitalPositionType.value == 'name':
                            text = '%s (%s)' % (text, satName)
                        else:
                            text = '%s (%s)' % (text, orbital)
            elif self.type == 7:
                text = ''
                if hayecm():
                    ecmInfoString = ' '
                    using = ''
                    address = ''
                    hops = ''
                    ecmTime = ''
                    sistema = ''
                    try:
                        f = open('/tmp/ecm.info', 'r')
                        content = f.read()
                        f.close()
                    except:
                        content = ''

                    contentInfo = content.split('\n')
                    for line in contentInfo:
                        if line.startswith('system:'):
                            esisd = devStr(line)
                            if esisd.replace('\n', '').strip() == 'FTA':
                                ecmInfoString = _('FTA channel')
                                break
                        elif line.startswith('caid:'):
                            caid = devStr(line)
                            if caid.__contains__('x'):
                                idx = caid.index('x')
                                caid = caid[idx + 1:]
                                if len(caid) == 3:
                                    caid = '0%s' % caid
                                caid = caid[:2]
                                caid = caid.upper()
                                sistema = caid
                                if self.systemCaids.has_key(caid):
                                    sistema = self.systemCaids.get(caid)
                        elif line.startswith('address:'):
                            address2 = line.replace('address:', '')
                            address = devStr(address2, None, ':')
                            porto = devStr(address2)
                            if porto == address or porto == '':
                                porto = ''
                            else:
                                porto = ':' + porto
                            if len(address) > 23:
                                address = address[:20] + '...'
                            address = address + porto
                        elif line.startswith('hops:'):
                            hops = ' (' + devStr(line) + ' ' + _('hops') + ')'
                        elif line.startswith('ecm time:'):
                            ecmTime = devStr(line)
                            if len(ecmTime) > 4:
                                ecmTime = ecmTime[0:4]
                            ecmTime = ecmTime + ' ' + _('secs.')

                    if sistema != '':
                        ecmInfoString = '%s' % sistema
                    if using != '':
                        ecmInfoString = '%s :: %s' % (ecmInfoString, using)
                    if address != '':
                        ecmInfoString = '%s :: %s' % (ecmInfoString, address)
                    if ecmTime != '':
                        ecmInfoString = '%s :: %s' % (ecmInfoString, ecmTime + hops)
                    text = ecmInfoString
            elif haytp():
                number = self.getServiceNumber(name, info.getInfoString(iServiceInformation.sServiceref))
                orbital = self.getOrbitalPosition(info)
                if number == '':
                    text = name
                else:
                    text = '%s. %s' % (number, name)
                if orbital != '':
                    text = '%s (%s)' % (text, orbital)
            return str(text)

    text = property(getText)

    def getListFromRef(self, ref):
        list = []
        try:
            serviceHandler = eServiceCenter.getInstance()
            services = serviceHandler.list(ref)
            bouquets = services and services.getContent('SN', True)
            for bouquet in bouquets:
                services = serviceHandler.list(eServiceReference(bouquet[0]))
                channels = services and services.getContent('SN', True)
                for channel in channels:
                    if not channel[0].startswith('1:64:'):
                        list.append(channel[1].replace('\xc2\x86', '').replace('\xc2\x87', ''))

        except:
            pass

        return list

    def getServiceNumber(self, name, ref):
        try:
            list = []
            if ref.startswith('1:0:2'):
                list = self.radio_list
            elif ref.startswith('1:0:1'):
                list = self.tv_list
            number = ''
            if name in list:
                for idx in range(1, len(list)):
                    if name == list[idx - 1]:
                        number = str(idx)
                        break

            return number
        except:
            return ''

    def getOrbitalPosition(self, info):
        cret = ''
        try:
            transponderData = info.getInfoObject(iServiceInformation.sTransponderData)
            orbital = 0
            if transponderData is not None:
                if isinstance(transponderData, float):
                    return ''
                if transponderData.has_key('tuner_type'):
                    if transponderData['tuner_type'] == 'DVB-S' or transponderData['tuner_type'] == 'DVB-S2':
                        orbital = transponderData['orbital_position']
                        orbital = int(orbital)
                        if orbital > 1800:
                            orbital = str(float(3600 - orbital) / 10.0) + 'W'
                        else:
                            orbital = str(float(orbital) / 10.0) + 'E'
                    else:
                        orbital = '0'
            if not str(orbital) == '0':
                satName = self.satNames.get(orbital, orbital)
                if not satName == None and not satName == '':
                    satName = devStr(satName, None, '(')
                    cret = cret + devStr(satName, None, '/')
                    if str(orbital) not in satName:
                        cret = cret + ' (' + str(orbital) + ')'
            cret = cret + ' ' + getFEData(transponderData)
            return cret
        except:
            return '---x---'

        return

    def cargasat(self, tipo, sixml = True):
        if tipo < 1 or tipo > 6:
            return
        else:
            if tipo == 1:
                sixml = False
            if not self.seg_plano == None:
                return
            try:
                self.seg_plano._Thread__stop()
            except:
                pass

            self.seg_plano = None
            self.seg_plano = segundoplano(self, sixml)
            self.seg_plano.start()
            return

    def subcargasat(self, sixml = True):
        if sixml:
            try:
                satXml = parse('/etc/tuxbox/satellites.xml').getroot()
                if satXml is not None:
                    for sat in satXml.findall('sat'):
                        name = sat.get('name') or None
                        position = sat.get('position') or None
                        if name is not None and position is not None:
                            position = '%s.%s' % (position[:-1], position[-1:])
                            if position.startswith('-'):
                                position = '%sW' % position[1:]
                            else:
                                position = '%sE' % position
                            if position.startswith('.'):
                                position = '0%s' % position
                            self.satNames[position] = name

            except:
                pass

        try:
            self.tv_list = self.getListFromRef(eServiceReference('1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 25) FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
            self.radio_list = self.getListFromRef(eServiceReference('1:7:2:0:0:0:0:0:0:0:(type == 2) FROM BOUQUET "bouquets.radio" ORDER BY bouquet'))
        except:
            pass

        self.seg_plano = None
        return

    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC or what[1] == self.type:
            Converter.changed(self, what)
