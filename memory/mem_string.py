from mem_base import Memory


# Represents a null terminated string in memory.
class String(Memory):
    # Input:
    #   address - The address of the string.
    #   value - The string.
    def __init__(self, address, value):
        super(String, self).__init__(address, len(value) + 1)
        self.value = value

    # Returns a string description of the string.
    # Input:
    #   n/a
    # Returns:
    #   String
    def description(self):
        return "string \"{0}\"".format(self.value)

    # Returns the string encoded as a hex string for file output.
    # Input:
    #   n/a
    # Returns:
    #   String
    def output_string(self):
        s = "".join(
            ["{0:02x}".format(ord(x)) for x in self.value]
        )
        s += "00"
        return s