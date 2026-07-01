from abc import ABC, abstractmethod


class PedidosProvider(ABC):
    """
    Aqui definimos o contrato que todas as APIs
    devem fornecer para o serviço de pedidos

    """

    @abstractmethod
    def id_pag(self):
        """
        Chama o service para retornar os ids por pagina
        """
        pass

    @abstractmethod
    def processa_ids(self):
        """
        Chama o metodo id_pag para ter os ids e depois
        chama o service para consulta cada id
        """
        pass
