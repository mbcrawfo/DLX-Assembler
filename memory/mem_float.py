from mem_base import Memory
import struct


# Represents a float in memory.
class Float(Memory):
    # Input:
    #   address - The address of the word.
    #   value - The float value.
    def __init__(self, address, value):
        assert isinstance(value, float)
        super(Float, self).__init__(address, 4)
        self.value = value

    # Returns a string description of the double.
    # Input:
    #   n/a
    # Returns:
    #   String
    def description(self):
        return "float {0}".format(self.value)

    # Returns the float encoded as a hex string for file output.
    # Input:
    #   n/a
    # Returns:
    #   String
    def output_string(self):
        s = "".join(
            ["{0:02x}".format(ord(x)) for x in struct.pack(">f", self.value)]
        )
        return s
