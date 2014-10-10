from mem_base import Memory
import struct


# Represents a double in memory.
class Double(Memory):
    # Input:
    #   address - The address of the word.
    #   value - The double value.
    def __init__(self, address, value):
        assert isinstance(value, float)
        super(Double, self).__init__(address, 8)
        self.value = value

    # Returns a string description of the double.
    # Input:
    #   n/a
    # Returns:
    #   String
    def description(self):
        return "double {0}".format(self.value)

    # Returns the double encoded as a hex string for file output.
    # Input:
    #   n/a
    # Returns:
    #   String
    def output_string(self):
        s = "".join(
            ["{0:02x}".format(ord(x)) for x in struct.pack(">d", self.value)]
        )
        return s
