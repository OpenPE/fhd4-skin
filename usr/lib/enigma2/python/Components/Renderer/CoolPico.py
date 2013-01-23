from enigma import ePixmap, ePicLoad, eServiceReference, eServiceCenter
from Renderer import Renderer
from Tools.Directories import fileExists

class CoolPico(Renderer):
    searchCoolPiconPaths = ('/usr/share/enigma2/picon/', '/media/cf/picon/', '/media/usb/picon/', '/media/hdd/picon/', '/picon/')

    def __init__(self):
        Renderer.__init__(self)
        self.size = []

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        attribs = []
        for attrib, value in self.skinAttributes:
            if attrib == 'size':
                self.size = value.split(',')
            attribs.append((attrib, value))

        self.skinAttributes = attribs
        ret = Renderer.applySkin(self, desktop, parent)
        return ret

    def changed(self, what):
        if self.instance:
            try:
                service = self.source.service
            except:
                service = None

            coolpico = ''
            if what[0] != self.CHANGED_CLEAR:
                if service is not None:
                    service = serviceName = service.toString()
                else:
                    serviceName = self.source.text
                coolpico = self.findCoolPicon(service, serviceName)
            if coolpico == '':
                coolpico = '/usr/lib/enigma2/python/Plugins/Extensions/CoolTVGuide/Cool3D/dummy.png'
            if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/CoolTVGuide/Cool3D/dummy.png'):
                if coolpico != '':
                    CoolPicLoad = ePicLoad()
                    CoolPicLoad.setPara((int(self.size[0]),
                     int(self.size[1]),
                     1,
                     1,
                     0,
                     1,
                     '#00000000'))
                    CoolPicLoad.startDecode(coolpico, 0, 0, False)
                    coolpico = CoolPicLoad.getData()
                    self.instance.setPixmap(coolpico)

    def findCoolPicon(self, service = None, serviceName = None):
        if service is not None:
            myref = eServiceReference(str(service))
            if myref.flags & eServiceReference.isGroup:
                serviceHandler = eServiceCenter.getInstance()
                mylist = serviceHandler.list(myref)
                if mylist is not None:
                    mask = eServiceReference.isMarker | eServiceReference.isDirectory
                    while 1:
                        s = mylist.getNext()
                        if not s.valid():
                            break
                        playable = not s.flags & mask
                        if playable:
                            service = s.toCompareString()
                            break

        if service is not None:
            pos = service.rfind(':')
            if pos != -1:
                service = service[:pos].rstrip(':').replace(':', '_')
                for path in self.searchCoolPiconPaths:
                    coolpico = path + service + '.png'
                    if fileExists(coolpico):
                        return coolpico

        elif serviceName is not None:
            pos = serviceName.rfind(':')
            if pos != -1:
                serviceName = serviceName[:pos].rstrip(':').replace(':', '_')
                for path in self.searchCoolPiconPaths:
                    coolpico = path + serviceName + '.png'
                    if fileExists(coolpico):
                        return coolpico

        return ''
