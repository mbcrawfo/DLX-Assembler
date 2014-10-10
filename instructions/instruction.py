from memory.mem_base import Memory
import instruction_table
from dlx_parser.grammar import i_opcode, i_rd, i_rs1, i_rs2, i_immediate, \
    i_label
import struct


# Represents a dlx instruction in memory.
class Instruction(Memory):
    # Mask for the full instruction.
    mask = 0xffffffff
    # Mask for the opcode bits in the instruction.
    opcode_mask = 0xfc000000

    # Input:
    #   address - The instruction's address.
    #   source - The instruction's source as defined in the grammar.
    def __init__(self, address, source):
        super(Instruction, self).__init__(address, 4)
        self.source = source
        self.opcode = instruction_table.get_opcode(self.source[i_opcode])

    # Returns a description of the instruction
    # Input:
    #   n/a
    # Returns:
    #   Description string.
    def description(self):
        desc = self.source[i_opcode]
        if i_rd in self.source:
            desc += " rd=" + self.source[i_rd]
        if i_rs1 in self.source:
            desc += " rs1=" + self.source[i_rs1]
        if i_rs2 in self.source:
            desc += " rs2=" + self.source[i_rs2]
        if i_label in self.source:
            desc += " label=" + self.source[i_label]
        if i_immediate in self.source:
            desc += " imm=" + repr(self.source[i_immediate])
        return desc

    # Returns the instruction encoded as a hex string for file output.
    # Input:
    #   n/a
    # Returns:
    #   Hex string.
    def output_string(self):
        b = self._binary()
        s = "".join(
            ["{0:02x}".format(ord(x)) for x in struct.pack(">I", b)]
        )
        return s

    # Resolves the label (if any) used in the instruction.
    # Input:
    #   sym_tab - The symbol table (mapping strings to addresses).
    # Returns:
    #   n/a
    # Throws:
    #   LookupError - The label was not found.
    def resolve_label(self, sym_tab):
        pass

    # Returns the opcode encoded in binary.
    # Input:
    #   n/a
    # Returns:
    #   The binary opcode.
    def _binary_opcode(self):
        # shift 6 opcode bits to the MSB
        return (self.opcode << (32 - 6)) & self.mask

    # Returns the instruction in binary format for encoding.
    # Input:
    #   n/a
    # Returns:
    #   The binary encoding.
    def _binary(self):
        # delegate to sub classes
        return 0