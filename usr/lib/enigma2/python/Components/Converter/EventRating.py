from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.Language import language

class EventRating(Converter, object):

    def __init__(self, type):
        Converter.__init__(self, type)
        lang = language.getLanguage()
        self.idioma = str(lang[:2])
        self.ini = ''
        self.fin = ''
        if self.idioma == 'ca' or self.idioma == 'eu' or self.idioma == 'ga' or self.idioma == 'va':
            self.idioma = 'es'
        if type == 'SmallRating':
            pass
        elif type == 'Rating':
            self.ini = '('
            self.fin = ')'

    @cached
    def getText(self):
        event = self.source.event
        if event is None:
            return ''
        else:
            try:
                rating = event.getParentalData()
            except:
                return ''

            if rating is None:
                return ''
            age = rating.getRating()
            if age == 0 or age == 29 or age >= 16 and age <= 17:
                if self.idioma == 'es':
                    return self.ini + 'TP' + self.fin
                else:
                    return self.ini + 'G' + self.fin
            else:
                if age == 30:
                    return self.ini + '+1' + self.fin
                if age == 31:
                    return self.ini + 'X' + self.fin
                if age > 15:
                    return ''
                age += 3
                cret = '+%d' % age
                return self.ini + cret + self.fin
            return ''

    text = property(getText)
