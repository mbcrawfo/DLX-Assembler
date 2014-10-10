from instruction import Instruction
from dlx_parser.grammar import i_opcode, i_rd, i_rs1, i_rs2, i_immediate, \
    i_label
import instruction_table


# Represents a dlx r-type instruction in memory.
class RType(Instruction):
    # Input:
    #   address - The instruction's address.
    #   source - The instruction's source as defined in the grammar.
    def __init__(self, address, source):
        super(RType, self).__init__(address, source)
        self.funcode = instruction_table.get_funcode(self.source[i_opcode])
        self.rd = 0
        if i_rd in self.source:
            self.rd = int(self.source[i_rd][1:])
        self.rs1 = 0
        if i_rs1 in self.source:
            self.rs1 = int(self.source[i_rs1][1:])
        self.rs2 = 0
        if i_rs2 in self.source:
            self.rs2 = int(self.source[i_rs2][1:])

    # Returns the instruction in binary format for encoding.
    # Input:
    #   n/a
    # Returns:
    #   The binary encoding.
    def _binary(self):
        op = self._binary_opcode()
        brs1 = self.rs1 << (32 - 6 - 5)
        brs2 = self.rs2 << (32 - 6 - 5 - 5)
        brd = self.rd << (32 - 6 - 5 - 5 - 5)
        res = op | brs1 | brs2 | brd | self.funcode
        return res & self.mask