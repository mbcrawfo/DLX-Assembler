import sys
import instructions.instruction_table as instruction_table
from memory.mem_word import Word
from memory.mem_string import String
from memory.mem_double import Double
from memory.mem_float import Float
import dlx_parser.grammar as grammar
from dlx_parser.exception import ParseException
from instructions.j_type import JType
from instructions.r_type import RType
from instructions.i_type import IType


# The main assembler application.
class Assembler(object):
    # Input:
    #   options - The program options.
    def __init__(self, options):
        # settings
        self.verbose = options["verbose"]
        self.dump = options["dump"]
        self.console = options["console"]
        self.no_output = options["no_output"]
        self.in_file = options["in_file"]
        self.out_file = options["out_file"]
        # internal state
        self.error = False
        self.line_no = 0
        self.address = 0
        self.symbol_table = {}
        self.program = {}
        self.unresolved_instructions = []
        if self.verbose:
            print "Input file:", self.in_file
            print "Output file:", self.out_file

    # Runs the assembler.
    # Input:
    #   n/a
    # Returns:
    #   n/a
    def run(self):
        instruction_table.load()
        self.error = False
        with open(self.in_file, "r") as f:
            for line in f:
                try:
                    data = grammar.parser.parse(line, tracking=True)
                    self.line_no = data[grammar.line_no]
                    if grammar.label in data:
                        self._add_label(data[grammar.label])
                        if not grammar.directive in data and \
                           not grammar.instruction in data:
                            data[grammar.instruction] = {
                                grammar.i_opcode: "nop"
                            }
                    if grammar.directive in data:
                        self._handle_directive(data[grammar.directive])
                    elif grammar.instruction in data:
                        self._handle_instruction(data[grammar.instruction])
                except ParseException as e:
                    print e.message
                    self.error = True

        self._resolve_symbols()
        if not self.error and not self.no_output:
            if self.console:
                print "Assembled Output:"
                self._write_output(sys.stdout)
            else:
                with open(self.out_file, "w") as f:
                    self._write_output(f)

    # Writes the assembled program out to a file.
    # Input:
    #   f - The output file.
    # Returns:
    #   n/a
    def _write_output(self, f):
        for address in sorted(self.program):
            mem = self.program[address]
            f.write("{0:08x}: {1} # {2}\n".format(
                address,
                mem.output_string(),
                mem.description()
            ))

    # Applies a directive to the assembler state.
    # Input:
    #   directive - The directive action to be performed
    #               (see dlx_parser.grammar).
    # Returns:
    #   n/a
    def _handle_directive(self, directive):
        if grammar.d_align in directive:
            self._align_address(directive[grammar.d_align])
        elif grammar.d_address in directive:
            self._set_address(directive[grammar.d_address])
        elif grammar.d_double in directive:
            self._store_double(directive[grammar.d_double])
        elif grammar.d_float in directive:
            self._store_float(directive[grammar.d_float])
        elif grammar.d_space in directive:
            self._set_address(self.address + directive[grammar.d_space])
        elif grammar.d_string in directive:
            self._store_string(directive[grammar.d_string])
        elif grammar.d_word in directive:
            self._store_word(directive[grammar.d_word])
        else:
            print "ERROR line {0}: unknown directive found".format(self.line_no)

    # Adds an instruction to the program.
    # Input:
    #   instr - The instruction info.
    # Returns:
    #   n/a
    def _handle_instruction(self, instr):
        try:
            type_id = instruction_table.get_type(instr[grammar.i_opcode])
        except ValueError:
            self.error = True
            print "ERROR line {0}: instruction {1} not found".format(
                self.line_no,
                instr[grammar.i_opcode]
            )
            return

        i = None
        if type_id == instruction_table.InstructionType.J:
            i = JType(self.address, instr)
        elif type_id == instruction_table.InstructionType.R:
            i = RType(self.address, instr)
        elif type_id == instruction_table.InstructionType.I:
            i = IType(self.address, instr)

        self.program[self.address] = i
        self.address += i.size
        if grammar.i_label in instr:
            self.unresolved_instructions.append(i)

    # Adds a label to the symbol table at the current address.
    # Input:
    #   label - The label name.
    # Returns:
    #   n/a
    def _add_label(self, label):
        if not label in self.symbol_table:
            self.symbol_table[label] = self.address
            if self.verbose:
                print "New label {0}: 0x{1:08x}".format(label, self.address)
        else:
            print "ERROR line {0}: duplicate label {1}".format(
                self.line_no,
                label
            )
            self.error = True

    # Processes all unresolved symbols in the program instructions.
    # Input:
    #   n/a
    # Returns:
    #   n/a
    def _resolve_symbols(self):
        if self.dump:
            print "Symbol Table:"
            for name, address in self.symbol_table.iteritems():
                print "{0:>15} : 0x{1:08x}".format(name, address)
        for i in self.unresolved_instructions:
            try:
                i.resolve_label(self.symbol_table)
            except LookupError as e:
                print "ERROR: Unresolved label \"{0}\"".format(e.args[0])
                self.error = True

    # Aligns the address so that the lower n bits are 0.
    # Input:
    #   n - Number of lower order bits to be zeroed.
    # Returns:
    #   n/a
    def _align_address(self, n):
        # make a mask with n bits set
        mask = int(2**n) - 1
        while self.address & mask != 0:
            self.address += 1
        if self.verbose:
            print "Aligned address to 0x{0:08x} (mod {1})".format(
                self.address,
                mask + 1
            )

    # Sets the current address of the assembler.
    # Input:
    #   address - The new address.
    # Returns:
    #   n/a
    def _set_address(self, address):
        self.address = address
        if self.verbose:
            print "Set address to 0x{0:08x}".format(self.address)

    # Stores a sequence of doubles in the program.
    # Input:
    #   values - The doubles to store.
    # Returns:
    #   n/a
    def _store_double(self, values):
        for value in values:
            dbl = Double(self.address, value)
            self.program[self.address] = dbl
            self.address += dbl.size
            if self.verbose:
                print "Storing double {0} at 0x{1:08x}".format(
                    dbl.value,
                    dbl.address
                )
            if dbl.address % dbl.size is not 0:
                print "WARNING line {0}: unaligned double".format(self.line_no)

    # Stores a sequence of floats in the program.
    # Input:
    #   values - The floats to store.
    # Returns:
    #   n/a
    def _store_float(self, values):
        for value in values:
            flt = Float(self.address, value)
            self.program[self.address] = flt
            self.address += flt.size
            if self.verbose:
                print "Storing float {0} at 0x{1:08x}".format(
                    flt.value,
                    flt.address
                )
            if flt.address % flt.size is not 0:
                print "WARNING line {0}: unaligned float".format(self.line_no)

    # Stores a sequence of strings in the program.
    # Input:
    #   values - The strings to store.
    # Returns:
    #   n/a
    def _store_string(self, values):
        for value in values:
            string = String(self.address, value)
            self.program[self.address] = string
            self.address += string.size
            if self.verbose:
                print "Storing string \"{0}\" at 0x{1:08x}".format(
                    string.value,
                    string.address
                )

    # Stores a sequence of words in the program.
    # Input:
    #   values - The words to store.
    # Returns:
    #   n/a
    def _store_word(self, values):
        for value in values:
            word = Word(self.address, value)
            self.program[self.address] = word
            self.address += word.size
            if self.verbose:
                print "Storing word {0} (0x{1}) at 0x{2:08x}".format(
                    word.value,
                    word.output_string(),
                    word.address
                )
            if word.address % word.size is not 0:
                print "WARNING line {0}: unaligned word".format(self.line_no)
