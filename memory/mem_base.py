# Represents a chunk of memory in the program.
class Memory(object):
    # Input:
    #   address - The address of the chunk.
    #   size - The size of the chunk in bytes.
    def __init__(self, address, size):
        self.address = address
        self.size = size

    # Returns a string description of the chunk.
    # Input:
    #   n/a
    # Returns:
    #   String
    def description(self):
        return ""

    # Returns the chunk of memory encoded as a hex string for file output.
    # Input:
    #   n/a
    # Returns:
    #   String
    def output_string(self):
        return ""
