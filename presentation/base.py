from abc import ABC, abstractmethod


class BaseController(ABC):
    """Marker base for all presentation controllers.

    Each concrete controller declares only the dependencies it actually needs
    (ISP — no forced repos on subclasses that don't use them).
    """


class BaseView(ABC):
    @abstractmethod
    def render(self) -> None: ...
