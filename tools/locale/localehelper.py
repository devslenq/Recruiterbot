from babel import Locale
from babel.support import Translations

from utils.Singleton import Singleton

class LocaleHelper(metaclass=Singleton):

    def __init__(self, locale="russian"):
        self.__translations__ = Translations.load('translations', locale)

    def translate(self, message_id):
        return self.__translations__.gettext(message_id)

    @classmethod
    def change_language(cls, new_locale):
        cls.reset_instance()
        return Locale(new_locale)
