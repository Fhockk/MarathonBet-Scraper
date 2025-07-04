import os
import string


def abs_path(path):
    """
    use it to get absolute path from relative path
    like
    with open(abs_path("app/scraper/data/get_prices.json"), "r") as f:
    :param path:
    :return:
    """
    # do 2 steps up, because we are in app/common/helpers.py
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', path))


def tokenize(text: str) -> list[str]:
    """
    Tokenizes a string into a list of lowercase words, excluding punctuation
    and one-letter words.

    Steps:
    - Converts text to lowercase.
    - Removes all punctuation.
    - Splits text by whitespace.
    - Filters out tokens with length <= 1.

    Args:
        text (str): Input string to tokenize.

    Returns:
        list[str]: List of cleaned, lowercase tokens.
    """
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return [w for w in text.split() if len(w) > 1]
