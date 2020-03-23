"""
Root class
"""
from templgen.generator import Generator
from templgen.settings import Settings
from templgen.templatizer import Templatizer
from templgen.user_manager import UserManager


class Templgen:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._settings = Settings(templgen=self)

    def ensure_integrity(self):
        self._settings.ensure_integrity()
