# Specifies exceptions related to parsing.
class ParseException(Exception):
    # Input:
    #   msg - The exception message.
    def __init__(self, msg):
        self.message = msg

    # The representation of the exception is its message.
    def __repr__(self):
        return self.message
