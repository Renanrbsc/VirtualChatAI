import argostranslate.translate as at_translate
import argostranslate.package


class PhraseTranslator:
    """
    A class to translate phrases from a source language to a target language using
    Argos Translate offline translation models.

    The class checks for the existence of a downloaded translation model and loads it.
    Once the model is loaded, it can perform translation on a given phrase.

    Attributes:
        user_lang (str): The user's language code (e.g., "pt" for Brazilian Portuguese).
        bot_lang (str): The bot's language code (always "en").
        translator_to_en (argostranslate.translate.Translation): The loaded translator instance for user to English.
        translator_from_en (argostranslate.translate.Translation): The loaded translator instance for English to user.
    """

    def __init__(self, user_lang: str = "pt", bot_lang: str = "en"):
        """
        Initialize the PhraseTranslator with language codes.

        Args:
            user_lang (str, optional): The user's language code. Defaults to "pt".
            bot_lang (str, optional): The bot's language code. Defaults to "en".
        """
        self.user_lang = user_lang
        self.bot_lang = bot_lang

        if self.user_lang == self.bot_lang:
            self.translator_to_en = None
            self.translator_from_en = None
        else:
            self.load_models()

    def load_models(self) -> None:
        """
        Loads the translation models for user to English and English to user.
        """
        # Update package index and install the translation package if not available
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()

        # Load user to English translator
        package_to_install = next(
            filter(
                lambda x: x.from_code == self.user_lang and x.to_code == self.bot_lang,
                available_packages
            ),
            None
        )

        if package_to_install:
            argostranslate.package.install_from_path(package_to_install.download())

        # Load installed languages
        installed_languages = at_translate.load_installed_languages()

        from_lang = None
        to_lang = None
        for lang in installed_languages:
            if lang.code == self.user_lang:
                from_lang = lang
            if lang.code == self.bot_lang:
                to_lang = lang

        if from_lang is None or to_lang is None:
            print("Error: The specified language pair is not installed.")
            return

        try:
            self.translator_to_en = from_lang.get_translation(to_lang)
            self.translator_from_en = to_lang.get_translation(from_lang)
        except Exception as error:
            print("Error initializing translators:", error)
            self.translator_to_en = None
            self.translator_from_en = None

    def translate_user_to_en(self, phrase: str) -> str:
        """
        Translate the user's phrase to English.

        Args:
            phrase (str): The text to be translated.

        Returns:
            str: The translated text in English if successful; otherwise, the original phrase.
        """
        if not self.translator_to_en:
            return None

        try:
            return self.translator_to_en.translate(phrase)
        except Exception as error:
            print("Error during translation:", error)
            return phrase

    def translate_en_to_user(self, phrase: str) -> str:
        """
        Translate the bot's English response to the user's language.

        Args:
            phrase (str): The text to be translated.

        Returns:
            str: The translated text in the user's language if successful; otherwise, the original phrase.
        """
        if not self.translator_from_en:
            return None

        try:
            return self.translator_from_en.translate(phrase)
        except Exception as error:
            print("Error during translation:", error)
            return phrase
