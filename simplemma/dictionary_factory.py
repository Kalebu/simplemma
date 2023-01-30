"""Parts related to dictonaries."""
import lzma
import logging
import pickle

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from functools import lru_cache

from .constants import LANGLIST

LOGGER = logging.getLogger(__name__)


def _control_lang(lang: Any) -> Tuple[str]:
    "Make sure the lang variable is a valid tuple."
    # convert string
    if isinstance(lang, str):
        lang = (lang,)
    if not isinstance(lang, tuple):
        raise TypeError("lang argument must be a two-letter language code")
    return lang  # type: ignore[return-value]


def _load_dictionary_from_disk(langcode: str) -> Dict[str, str]:
    filename = f"data/{langcode}.plzma"
    filepath = str(Path(__file__).parent / filename)
    with lzma.open(filepath, "rb") as filehandle:
        pickled_dict = pickle.load(filehandle)
        assert isinstance(pickled_dict, dict)
        return pickled_dict


class DictionaryFactory:
    def __init__(self, cache_max_size: Optional[int] = 8):
        self._data: Dict[str, Dict[str, str]] = {}
        self._load_dictionary_from_disk = lru_cache(maxsize=cache_max_size)(
            _load_dictionary_from_disk
        )

    def get_dictionaries(
        self, langs: Optional[Union[str, Tuple[str]]]
    ) -> Dict[str, Dict[str, str]]:
        langs = _control_lang(langs)

        if self._data and tuple(sorted(self._data.keys())) == sorted(langs):
            return self._data

        self._data = {}
        for lang in [lang for lang in self._data if lang not in langs]:
            self._data.pop(lang)

        for lang in [lang for lang in langs if lang not in self._data]:
            if lang not in LANGLIST:
                LOGGER.error("language not supported: %s", lang)
                continue
            LOGGER.debug("loading %s", lang)
            self._data[lang] = self._load_dictionary_from_disk(lang)
        return self._data
