import time
import microdotphat


class Screen: 

    def __init__(self):
        microdotphat.set_rotate180(True)
        microdotphat.clear()


    def __draw_tiny(self, tiny=[]):
        for index, number in enumerate(tiny):
            if number:
                microdotphat.draw_tiny(index, number)

    def show(self, text='', tiny=[], duration=None):
        microdotphat.clear()
        microdotphat.write_string(text, kerning=False)
        
        if tiny:
            self.__draw_tiny(tiny)
        
        microdotphat.show()    
        if duration is not None: 
            time.sleep(duration)
            microdotphat.clear()
