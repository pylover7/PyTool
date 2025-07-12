from app.core.crud import CRUDBase
from  app.models import Api, ApiCreate, ApiUpdate


class ApiController(CRUDBase[Api, ApiCreate, ApiUpdate]):
    def __init__(self):
        super().__init__(Api)

apiController = ApiController()
