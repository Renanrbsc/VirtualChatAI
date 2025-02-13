
import os
import argostranslate.translate as at_translate
import argostranslate.package


class PhraseTranslator:
    """
    A class to translate phrases from a source language to a target language using
    Argos Translate offline translation models.

    The class checks for the existence of a downloaded translation model and loads it.
    Once the model is loaded, it can perform translation on a given phrase.

    Attributes:
        source_lang (str): The source language code (e.g., "en").
        target_lang (str): The target language code (e.g., "pt" for Brazilian Portuguese).
        translator (argostranslate.translate.Translation): The loaded translator instance.
    """

    def __init__(self, source_lang: str = "en", target_lang: str = "pt"):
        """
        Initialize the PhraseTranslator with a model path and language codes.

        Args:
            source_lang (str, optional): The source language code.
                Defaults to "en".
            target_lang (str, optional): The target language code. Defaults to "pt".
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.translator = None
        self.load_model()

    def load_model(self) -> None:
        """
        Loads the translation model.

        This method verifies that the translation model directory exists. Then
        it loads installed languages via Argos Translate and selects the translation
        pair that matches the source and target languages. If the model is not found
        or the languages are not installed, an error message is printed.
        """

        # Update package index and install the translation package if not available
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        package_to_install = next(
            filter(
                lambda x: x.from_code == self.source_lang and x.to_code == self.target_lang,
                available_packages
            ),
            None
        )

        if package_to_install:
            argostranslate.package.install_from_path(package_to_install.download())

        # Load installed languages (the downloaded packages must be installed beforehand)
        installed_languages = at_translate.load_installed_languages()

        from_lang = None
        to_lang = None
        for lang in installed_languages:
            if lang.code == self.source_lang:
                from_lang = lang
            if lang.code == self.target_lang:
                to_lang = lang

        if from_lang is None or to_lang is None:
            print("Error: The specified language pair is not installed.")
            return

        try:
            self.translator = from_lang.get_translation(to_lang)
        except Exception as error:
            print("Error initializing translator:", error)
            self.translator = None

    def translate(self, phrase: str) -> str:
        """
        Translate the given phrase using the loaded translator.

        Args:
            phrase (str): The text to be translated.

        Returns:
            str: The translated text if translation is successful;
                 otherwise, the original phrase is returned.
        """
        if self.source_lang == self.target_lang:
            return None
        
        if self.translator is None:
            print("Translation model is not available. Returning the original phrase.")
            return phrase

        try:
            return self.translator.translate(phrase)
        except Exception as error:
            print("Error during translation:", error)
            return phrase
