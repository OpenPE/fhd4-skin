from Converter import Converter
from Components.Element import cached
from Poll import Poll
import NavigationInstance
from enigma import eTimer
from time import time as time_now

class info_timerno(Poll, Converter, object):
    HayTimer = 0

    def __init__(self, argstr):
        Converter.__init__(self, argstr)
        Poll.__init__(self)
        args = argstr.split(',')
        self.noblink = 'noBlink' in args
        if self.noblink:
            self.poll_interval = 30000
        else:
            self.poll_interval = 6000
        self.poll_enabled = True
        self.blink = False
        self.blinktime = 500
        self.timer = eTimer()
        self.timer.callback.append(self.blinkFunc)
        self.recordings = False
        self.type = 0

    def blinkFunc(self):
        if self.blinking == True:
            for x in self.downstream_elements:
                x.visible = not x.visible

    def startBlinking(self):
        self.blinking = True
        self.timer.start(self.blinktime)

    def stopBlinking(self):
        self.blinking = False
        for x in self.downstream_elements:
            if x.visible:
                x.hide()

        self.timer.stop()

    def calcVisibility(self):
        b = self.simostrar()
        if b == 2:
            self.blink = True
        else:
            self.blink = False
        return b

    def changed(self, what):
        vis = self.calcVisibility()
        if self.blink:
            if vis == 2:
                self.startBlinking()
                return
        self.stopBlinking()
        for x in self.downstream_elements:
            x.visible = vis == 1

    def connectDownstream(self, downstream):
        Converter.connectDownstream(self, downstream)
        vis = self.calcVisibility()
        if self.blink:
            if vis == 2:
                self.startBlinking()
            else:
                self.stopBlinking()
                downstream.visible = self.calcVisibility() == 1
        else:
            downstream.visible = self.calcVisibility() == 1

    def destroy(self):
        if self.timer:
            self.timer.callback.remove(self.blinkFunc)

    def simostrar(self):
        self.recordings = self.source.boolean
        ret = 0
        if self.recordings:
            ret = 0
            if self.poll_interval != 30000:
                self.poll_interval = 30000
        elif self.type == self.HayTimer:
            try:
                for timer in NavigationInstance.instance.RecordTimer.timer_list:
                    if not self.noblink and (timer.state == timer.StatePrepared or timer.begin - time_now() < 50 and timer.begin - time_now() >= 0) and not timer.disabled:
                        ret = 2
                        break
                    if timer.state == timer.StateWaiting and not timer.disabled:
                        ret = 1
                        if self.noblink:
                            break

            except:
                pass

            if self.noblink:
                if self.poll_interval != 30000:
                    self.poll_interval = 30000
            elif self.poll_interval != 5000:
                self.poll_interval = 5000
        return ret
