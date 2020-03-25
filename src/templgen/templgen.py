"""
Root class
"""
# from templgen.generator import Generator
from templgen.settings import Settings
# from templgen.templatizer import Templatizer
from templgen.user_manager import UserManager


class Templgen:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Settings must be initialized first
        self.settings = Settings(templgen=self)
        self.user_manager = UserManager(templgen=self)

    def ensure_integrity(self):
        self.settings.ensure_integrity()
