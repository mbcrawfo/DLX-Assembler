import ply.lex as lex

# directive tokens
directives = {
    ".align": "d_ALIGN",
    ".asciiz": "d_ASCIIZ",
    ".data": "d_DATA",
    ".double": "d_DOUBLE",
    ".float": "d_FLOAT",
    ".space": "d_SPACE",
    ".text": "d_TEXT",
    ".word": "d_WORD"
}

# instruction type tokens
instructions = {
    # (none)
    "i_NONE": ("nop",),
    # num
    "i_NUM": ("trap",),
    # name
    "i_NAME": ("j", "jal"),
    # gpr
    "i_GPR": ("jr", "jalr"),
    # gpr, name
    "i_GPR_NAME": ("beqz", "bnez"),
    # gpr, fpr
    "i_GPR_FPR": ("movfp2i",),
    # dpr, dpr
    "i_2DPR": ("movd",),
    # fpr, fpr
    "i_2FPR": ("cvtf2i", "cvti2f", "movf"),
    # gpr, num
    "i_GPR_UINT": ("lhi",),
    # fpr, gpr
    "i_FPR_GPR": ("movi2fp",),
    # fpr, dpr
    "i_FPR_DPR": ("cvtd2f", "cvtd2i"),
    # dpr, fpr
    "i_DPR_FPR": ("cvtf2d", "cvti2d"),
    # gpr, gpr, int
    "i_2GPR_INT": ("addi" , "seqi", "sgei", "sgti", "slei", "slti", "snei",
                   "subi"),
    # gpr, gpr, uint
    "i_2GPR_UINT": ("addui", "andi", "ori", "slli", "srai", "srli", "subui",
                    "xori"),
    # gpr, gpr, gpr
    "i_3GPR": ("add", "addu", "and", "or", "seq", "sge", "sgt", "sle", "sll",
               "slt", "sne", "sra", "srl", "sub", "subu", "xor"),
    # dpr, dpr, dpr
    "i_3DPR": ("addd", "divd", "multd", "subd"),
    # fpr, fpr, fpr
    "i_3FPR": ("addf", "div", "divf", "divu", "mult", "multf", "multu", "subf"),
    # gpr, num(gpr)
    "i_GPR_OFFSET": ("lb", "lbu", "lh", "lhu", "lw"),
    # dpr, num(gpr)
    "i_DPR_OFFSET": ("ld",),
    # fpr, num(gpr)
    "i_FPR_OFFSET": ("lf",),
    # num(gpr), gpr
    "i_OFFSET_GPR": ("sb", "sh", "sw"),
    # num(gpr), dpr
    "i_OFFSET_DPR": ("sd",),
    # num(gpr), fpr
    "i_OFFSET_FPR": ("sf",)
}

# register type tokens
registers = {
    "GPR": ["r" + repr(x) for x in range(0, 32)],
    "FPR": ["f" + repr(x) for x in range(0, 32)]
}

# assemble all tokens for the lexer
tokens = [
    "NUMBER",
    "DIRECTIVE",
    "NAME",
    "STRING",
    "COMMENT"
] + list(directives.values()) + list(instructions.keys()) + \
         list(registers.keys())


# Numbers - either int in decimal or hex, or float.
def t_NUMBER(t):
    r"""[-+]?((0[xX][\dA-Fa-f]+)|((\d*\.)?\d+))"""
    if "." in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value, 0)
    return t


# Directive name - period followed by letters.
def t_DIRECTIVE(t):
    r"""\.[a-zA-Z]+"""
    t.value = t.value.lower()
    t.type = directives.get(t.value, "DIRECTIVE")
    return t


# Name - a letter followed by letters, numbers, or underscore.
# Names are ambiguous for labels, registers, and instructions, so found names
# are searched to see if they match a known instruction or register.
def t_NAME(t):
    r"""[a-zA-Z]\w*"""
    t.value = t.value.lower()
    # search for instructions
    for name in instructions.keys():
        if t.value in instructions[name]:
            t.type = name
            return t
    # search for registers
    for name in registers.keys():
        if t.value in registers[name]:
            t.type = name
            return t
    # not found, remains a name
    return t


# String - text in quotes with escaped sequences
def t_STRING(t):
    r"""\"([^\"\\]|\\.)*\""""
    t.value = t.value[1:-1]
    t.value = t.value.replace(r"\t", "\t")
    t.value = t.value.replace(r"\"", "\"")
    t.value = t.value.replace(r"\n", "\n")
    return t

# comments - semicolon followed by anything
t_COMMENT = r";.*"

# characters that are returned directly as tokens
literals = [',', '(', ')', ':']

# ignored characters
t_ignore = " \t"


# line counter
def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


# Handle unknown characters found by the lexer.
def t_error(t):
    print "WARNING line {0}: unknown character \"{1}\"".format(
        t.lexer.lineno, t.value[0]
    )
    t.lexer.skip(1)

# build the lexer
lexer = lex.lex()

