import secrets
import string
from enum import IntEnum
from typing import Optional


class PasswordGenerator:
    class CharacterSet(IntEnum):
        LETTERS = 1
        DIGITS = 1 << 1
        SPECIALS = 1 << 2

    @staticmethod
    def generatePassword(
        length: int = 12,
        charSet: Optional[CharacterSet] = (
            CharacterSet.LETTERS | CharacterSet.DIGITS | CharacterSet.SPECIALS
        ),
    ) -> str:
        def isSet(value, charSet: PasswordGenerator.CharacterSet):
            return value & charSet != 0

        letters = string.ascii_letters
        digits = string.digits
        specials = string.punctuation

        allCharacters = []

        # Ensure at least on character from each set is included
        password = []
        if isSet(charSet, PasswordGenerator.CharacterSet.LETTERS):
            allCharacters += letters
            password.append(secrets.choice(letters))
        if isSet(charSet, PasswordGenerator.CharacterSet.DIGITS):
            allCharacters += digits
            password.append(secrets.choice(digits))
        if isSet(charSet, PasswordGenerator.CharacterSet.SPECIALS):
            allCharacters += specials
            secrets.choice(specials)

        # Fill the rest of the password with random characters.
        password.extend(secrets.choice(allCharacters) for _ in range(length - 3))

        # Shuffle the password to randomize the order
        secrets.SystemRandom().shuffle(password)

        return "".join(password)
