import time, sys, socket


class System:
    
    @staticmethod
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    
    @staticmethod
    def load():
        # load / CPU / mem / disk space. 
        # TODO
        pass

    @staticmethod
    def shutdown():
        # TODO
        pass