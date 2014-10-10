from mem_base import Memory
import struct


# Represents a signed integer word in memory.
class Word(Memory):
    # Input:
    #   address - The address of the word.
    #   value - The integer value.
    def __init__(self, address, value):
        assert isinstance(value, int)
        super(Word, self).__init__(address, 4)
        self.value = value

    # Returns a string description of the word.
    # Input:
    #   n/a
    # Returns:
    #   String
    def description(self):
        return "word {0}".format(self.value)

    # Returns the word encoded as a hex string for file output.
    # Input:
    #   n/a
    # Returns:
    #   String
    def output_string(self):
        s = "".join(
            ["{0:02x}".format(ord(x)) for x in struct.pack(">i", self.value)]
        )
        return s