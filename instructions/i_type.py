from instruction import Instruction
from dlx_parser.grammar import i_opcode, i_rd, i_rs1, i_rs2, i_immediate, \
    i_label


# Represents a dlx i-type instruction in memory.
class IType(Instruction):
    # Instructions that need an immediate offset.
    offset_instructions = ("beqz", "bnez")
    # Mask of the immediate field.
    immediate_mask = 0x0000ffff

    # Input:
    #   address - The instruction's address.
    #   source - The instruction's source as defined in the grammar.
    def __init__(self, address, source):
        super(IType, self).__init__(address, source)
        self.rd = 0
        if i_rd in self.source:
            self.rd = int(self.source[i_rd][1:])
        self.rs1 = 0
        if i_rs1 in self.source:
            self.rs1 = int(self.source[i_rs1][1:])
        self.immediate = 0
        if i_immediate in self.source:
            self._set_immediate(self.source[i_immediate])

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
            self._set_immediate(sym_tab[label])

    # Returns the instruction in binary format for encoding.
    # Input:
    #   n/a
    # Returns:
    #   The binary encoding.
    def _binary(self):
        op = self._binary_opcode()
        brs1 = self.rs1 << (32 - 6 - 5)
        brd = self.rd << (32 - 6 - 5 - 5)
        res = op | brs1 | brd | self.immediate
        return res & self.mask

    # Sets the immediate value of the instruction. Will set a PC offset or
    # absolute value depending on the opcode.
    # Input:
    #   value - The supplied value/address for the immediate.
    # Returns:
    #   n/a
    def _set_immediate(self, value):
        if self.source[i_opcode] in self.offset_instructions:
            self.immediate = value - (self.address + 4)
        else:
            self.immediate = value
        self.immediate &= self.immediate_mask