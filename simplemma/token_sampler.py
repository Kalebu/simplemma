"""TokenSampler module. A TokenSampler is a class that select samples from a text or a tokens collection."""

import re
import sys
from abc import ABC, abstractmethod
from typing import Iterable, List
from collections import Counter
from .tokenizer import Tokenizer, RegexTokenizer

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


SPLIT_INPUT = re.compile(r"[^\W\d_]{3,}")
RELAXED_SPLIT_INPUT = re.compile(r"[\w-]{3,}")


class TokenSampler(Protocol):
    @abstractmethod
    def sample_text(self, text: str) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def sample_tokens(self, tokens: Iterable[str]) -> List[str]:
        raise NotImplementedError


class BaseTokenSampler(ABC, TokenSampler):
    __slots__ = ["_tokenizer"]

    def __init__(
        self,
        tokenizer: Tokenizer = RegexTokenizer(SPLIT_INPUT),
    ) -> None:
        self._tokenizer = tokenizer

    def sample_text(self, text: str) -> List[str]:
        return self.sample_tokens(self._tokenizer.split_text(text))

    @abstractmethod
    def sample_tokens(self, tokens: Iterable[str]) -> List[str]:
        raise NotImplementedError


class MostCommonTokenSampler(BaseTokenSampler):
    __slots__ = ["_capitalized_threshold", "_sample_size"]

    def __init__(
        self,
        tokenizer: Tokenizer = RegexTokenizer(SPLIT_INPUT),
        sample_size: int = 100,
        capitalized_threshold: float = 0.8,
    ) -> None:
        super().__init__(tokenizer)
        self._sample_size = sample_size
        self._capitalized_threshold = capitalized_threshold

    def sample_tokens(self, tokens: Iterable[str]) -> List[str]:
        """Extract potential tokens, scramble them, potentially get rid of capitalized
        ones, and return the most frequent."""

        counter = Counter(tokens)

        if self._capitalized_threshold > 0:
            deletions = [token for token in counter if token[0].isupper()]
            if len(deletions) < self._capitalized_threshold * len(counter):
                for token in deletions:
                    del counter[token]

        return [item[0] for item in counter.most_common(self._sample_size)]


class RelaxedMostCommonTokenSampler(MostCommonTokenSampler):
    def __init__(
        self,
        tokenizer: Tokenizer = RegexTokenizer(RELAXED_SPLIT_INPUT),
        sample_size: int = 1000,
        capitalized_threshold: float = 0,
    ) -> None:
        super().__init__(tokenizer, sample_size, capitalized_threshold)
