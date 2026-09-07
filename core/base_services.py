class BaseDataService:
    """ejemplo de claudio este no se queda"""

    def fetch(self, lat: float, lng: float) -> dict:
        raise NotImplementedError

    def normalize(self, raw_data) -> dict:
        raise NotImplementedError

    def get_data(self, lat: float, lng: float) -> dict:
        try:
            raw = self.fetch(lat, lng)
            return self.normalize(raw)
        except Exception as e:
            return {"error": str(e), "source": self.__class__.__name__}  
        
class BaseDataServiceINE:
    """Clase base general sin firmas forzadas"""

    def fetch(self, **kwargs):
        raise NotImplementedError

    def normalize(self, raw_data):
        raise NotImplementedError

    def get_data(self, **kwargs) -> dict:
        try:
            raw = self.fetch(**kwargs)
            return self.normalize(raw)
        except Exception as e:
            return {"error": str(e), "source": self.__class__.__name__}