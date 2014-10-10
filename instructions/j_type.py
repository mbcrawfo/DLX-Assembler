from instruction import Instruction
from dlx_parser.grammar import i_opcode, i_rd, i_rs1, i_rs2, i_immediate, \
    i_label


# Represents a dlx j-type instruction in memory.
class JType(Instruction):
    # Input:
    #   address - The instruction's address.
    #   source - The instruction's source as defined in the grammar.
    def __init__(self, address, source):
        super(JType, self).__init__(address, source)
        self.offset = 0
        if i_immediate in self.source:
            self.offset = self.source[i_immediate] - (self.address + 4)

    # Resolves the label (if any) used in the instruction.
    # Input:
    #   sym_tab - The symbol table (mapping strings to addresses).
    # Returns:
    #   n/a
    # Throws:
    #   LookupError - The label was not found.
    def resolve_label(self, sym_tab):
        if i_label in self.source:
            label = self.source[i_label]
            if not label in sym_tab:
                raise LookupError(label)
            target = sym_tab[label]
            self.offset = target - (self.address + 4)

    # Returns the instruction in binary format for encoding.
    # Input:
    #   n/a
    # Returns:
    #   The binary encoding.
    def _binary(self):
        op = self._binary_opcode()
        of = self.offset & ~self.opcode_mask
        # have to force the value back to 32 bits
        return (op | of) & self.mask