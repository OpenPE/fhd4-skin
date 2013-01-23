from Components.Converter.Converter import Converter
from Components.Element import cached
from ServiceReference import ServiceReference
from enigma import eEPGCache
from time import localtime, time

class bmNext(Converter, object):
    nextNAME = 1
    nextTIME = 2
    nextSTART = 4
    nextEventFull = 3
    NONE = 0

    def __init__(self, type):
        Converter.__init__(self, type)
        self.epgcache = None
        if type == 'NextEvent':
            self.type = self.nextNAME
        elif type == 'NextStart':
            self.type = self.nextSTART
        elif type == 'NextTime':
            self.type = self.nextTIME
        elif type == 'NextEventFull':
            self.type = self.nextEventFull
        else:
            self.type = 0

    @cached
    def getText(self):
        servicio = self.source.service
        if servicio is None:
            return ''
        self.epgcache = eEPGCache.getInstance()
        nextstartdisplay, nextepg, nexttimedisplay = self.getEPGNowNext(servicio, 1)
        if self.type == self.nextNAME:
            cret = nextepg
            if len(cret) > 55:
                cret = cret[0:53] + '...'
            if len(nexttimedisplay) > 2:
                cret = cret + ' (' + nexttimedisplay + ')'
            return cret
        if self.type == self.nextSTART:
            if len(nextepg) > 1:
                return '>> ' + nextstartdisplay
        else:
            if self.type == self.nextTIME:
                return nexttimedisplay
            if self.type == self.nextEventFull:
                cret = nextepg
                if len(cret) > 1:
                    cret = '>> ' + nextstartdisplay + ' ' + cret
                else:
                    return ' '
                if len(cret) > 55:
                    cret = cret[0:53] + '...'
                if len(nexttimedisplay) > 2:
                    cret = cret + ' (' + nexttimedisplay + ')'
                return cret
            return ' '

    text = property(getText)

    def getEPGNowNext(self, ref, modus = 1):
        if self.epgcache is not None:
            event = self.epgcache.lookupEvent(['IBDCTSERNX', (ref.toString(), modus, -1)])
            if event:
                if event[0][4]:
                    t = localtime(event[0][1])
                    duration = event[0][2]
                    if modus == 0:
                        timedisplay = '+%d min' % ((event[0][1] + duration - time()) / 60)
                    elif modus == 1:
                        timedisplay = '%d min.' % (duration / 60)
                    return ('%02d:%02d' % (t[3], t[4]), event[0][4], timedisplay)
                else:
                    return ('', '', '')
        return ('', '', '')
