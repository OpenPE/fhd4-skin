from Converter import Converter
from Components.Element import cached
from Poll import Poll
from enigma import eDVBVolumecontrol

class spzVolume(Poll, Converter, object):
    VOLUMEN = 0

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        if type == 'volume':
            self.type = self.VOLUMEN
            self.poll_interval = 100
            self.poll_enabled = True

    @cached
    def getText(self):
        text = ''
        if self.type == self.VOLUMEN:
            try:
                self.volctrl = eDVBVolumecontrol.getInstance()
                valor = self.volctrl.getVolume()
                text = str(valor) + '%'
            except:
                pass

        return text

    text = property(getText)

    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC or what[1] == self.type:
            Converter.changed(self, what)
