import ply.yacc as yacc
from exception import ParseException
# necessary even though not explicitly used
from lexer import tokens

# The parser returns a dictionary describing the contents of the line.
# line_no: int
# label: string for a label on the line
# directive: dictionary {
#       align: int
#       address: int
#       double: [double...]
#       float: [float...]
#       space: int
#       string: [string...]
#       word: [int...]
# }
# instruction: dictionary {
#       opcode: string
#       rd: int
#       rs1: int
#       rs2: int
#       immediate: int
#       label: string
# }

# string values for the above
line_no = "line_no"
label = "label"
directive = "directive"
d_align = "align"
d_address = "address"
d_double = "double"
d_float = "float"
d_space = "space"
d_string = "string"
d_word = "word"
instruction = "instruction"
i_opcode = "opcode"
i_rd = "rd"
i_rs1 = "rs1"
i_rs2 = "rs2"
i_immediate = "immediate"
i_label = label


# default addresses
default_text_addr = 0
default_data_addr = 0x200

# Each function below describes a rule (or rules) in the grammar of the dlx
# syntax. Grammar rules are defined in the docstring of the function.
# Lower case labels are non-terminals.
# Upper case labels are tokens from the lexer (terminals).
# Many functions define invalid rule combinations in order to catch errors,
# because it seems that the parser doesn't always signal errors when it can't
# match all the tokens in its stack.


def p_line(p):
    """line : label statement comment"""
    p[0] = {line_no: p.lineno(0)}
    if p[1]:
        p[0][label] = p[1]
    if p[2]:
        p[0] = dict(p[0].items() + p[2].items())


def p_label(p):
    """label : NAME ':'
             |
    """
    if len(p) is 3:
        p[0] = p[1]
    else:
        p[0] = None


def p_statement_directive(p):
    """statement : directive"""
    p[0] = {directive: p[1]}


def p_statement_instruction(p):
    """statement : instruction"""
    p[0] = {instruction: p[1]}


def p_statement_empty(p):
    """statement :"""
    p[0] = None


def p_comment(p):
    """comment : COMMENT
               |
    """
    p[0] = None


def p_directive_align(p):
    """directive : d_ALIGN unsigned
                 | d_ALIGN
    """
    if len(p) is 3:
        p[0] = {d_align: p[2]}
    else:
        raise ParseException(
            "ERROR line {0}: .align requires 1 integer parameter.".format(
                p.lineno(1)
            )
        )


def p_directive_asciiz(p):
    """directive : d_ASCIIZ stringlist
                 | d_ASCIIZ
    """
    if len(p) is 3:
        p[0] = {d_string: p[2]}
    else:
        raise ParseException(
            "ERROR line {0}: .asciiz requires a list of strings.".format(
                p.lineno(1)
            )
        )


def p_directive_data(p):
    """directive : d_DATA int
                 | d_DATA
    """
    if len(p) is 3:
        p[0] = {d_address: p[2]}
    else:
        p[0] = {d_address: default_data_addr}


def p_directive_double(p):
    """directive : d_DOUBLE numlist
                 | d_DOUBLE
    """
    if len(p) is 3:
        p[2] = [float(x) for x in p[2]]
        p[0] = {d_double: p[2]}
    else:
        raise ParseException(
            "ERROR line {0}: .double requires double parameters".format(
                p.lineno(1)
            )
        )


def p_directive_float(p):
    """directive : d_FLOAT numlist
                 | d_FLOAT
    """
    if len(p) is 3:
        p[2] = [float(x) for x in p[2]]
        p[0] = {d_float: p[2]}
    else:
        raise ParseException(
            "ERROR line {0}: .float requires float parameters".format(
                p.lineno(1)
            )
        )


def p_directive_text(p):
    """directive : d_TEXT unsigned
                 | d_TEXT
    """
    if len(p) is 3:
        p[0] = {d_address: p[2]}
    else:
        p[0] = {d_address: default_text_addr}


def p_directive_space(p):
    """directive : d_SPACE unsigned
                 | d_SPACE
    """
    if len(p) is 3:
        p[0] = {d_space: p[2]}
    else:
        raise ParseException(
            "ERROR line {0}: .space requires 1 integer parameters".format(
                p.lineno(1)
            )
        )


def p_directive_word(p):
    """directive : d_WORD numlist
                 | d_WORD
    """
    if len(p) is 3:
        lst = []
        for word in p[2]:
            if not isinstance(word, int):
                raise ParseException(
                    "ERROR line {0}: .word requires integer parameters".format(
                        p.lineno(1)
                    )
                )
            else:
                lst.append(word)
        p[0] = {d_word: lst}
    else:
        raise ParseException(
            "ERROR line {0}: .word requires integer parameters".format(
                p.lineno(1)
            )
        )


def p_directive_unknown(p):
    """directive : DIRECTIVE numlist
                 | DIRECTIVE stringlist
                 | DIRECTIVE
    """
    raise ParseException(
        "ERROR line {0}: unknown directive {1}".format(
            p.lineno(1),
            p[1]
        )
    )


def p_instruction_none(p):
    """instruction : i_NONE"""
    p[0] = {i_opcode: p[1]}


def p_instruction_name(p):
    """instruction : i_NAME unsigned
                   | i_NAME NAME
                   | i_NAME
                   | i_GPR GPR
                   | i_GPR
                   | i_NUM unsigned
                   | i_NUM
    """
    if len(p) is 3:
        p[0] = {i_opcode: p[1]}
        # label
        if p.slice[2].type == "NAME":
                p[0][i_label] = p[2]
        # gpr
        elif p.slice[2].type == "GPR":
                p[0][i_rs1] = p[2]
        # number
        else:
            p[0][i_immediate] = p[2]
    else:
        raise ParseException(
            "ERROR line {0}: missing parameter for {1}".format(
                p.lineno(0),
                p[1]
            )
        )


def p_instruction_gpr_arg(p):
    """instruction : i_GPR_NAME GPR ',' NAME
                   | i_GPR_NAME GPR ','
                   | i_GPR_NAME GPR
                   | i_GPR_NAME
                   | i_GPR_UINT GPR ',' NAME
                   | i_GPR_UINT GPR ',' unsigned
                   | i_GPR_UINT GPR ','
                   | i_GPR_UINT GPR
                   | i_GPR_UINT
    """
    if len(p) is 5:
        p[0] = {i_opcode: p[1]}
        # these branch instructions use rs1
        if p.slice[1].type == "i_GPR_NAME":
            p[0][i_rs1] = p[2]
        # but lhi uses rd...
        else:
            p[0][i_rd] = p[2]
        # label
        if p.slice[4].type == "NAME":
            p[0][i_label] = p[4]
        # number
        else:
            p[0][i_immediate] = p[4]
    else:
        raise ParseException(
            "ERROR line {0}: missing parameter for {1}".format(
                p.lineno(0),
                p[1]
            )
        )


def p_instruction_2reg(p):
    """instruction : i_GPR_FPR GPR ',' FPR
                   | i_GPR_FPR GPR ','
                   | i_GPR_FPR GPR
                   | i_GPR_FPR
                   | i_2DPR dpr ',' dpr
                   | i_2DPR dpr ','
                   | i_2DPR dpr
                   | i_2DPR
                   | i_2FPR FPR ',' FPR
                   | i_2FPR FPR ','
                   | i_2FPR FPR
                   | i_2FPR
                   | i_FPR_GPR FPR ',' GPR
                   | i_FPR_GPR FPR ','
                   | i_FPR_GPR FPR
                   | i_FPR_GPR
                   | i_FPR_DPR FPR ',' dpr
                   | i_FPR_DPR FPR ','
                   | i_FPR_DPR FPR
                   | i_FPR_DPR
                   | i_DPR_FPR dpr ',' FPR
                   | i_DPR_FPR dpr ','
                   | i_DPR_FPR dpr
                   | i_DPR_FPR
    """
    if len(p) is 5:
        p[0] = {
            i_opcode: p[1],
            i_rd: p[2],
            i_rs1: p[4]
        }
    else:
        raise ParseException(
            "ERROR line {0}: missing parameter for {1}".format(
                p.lineno(0),
                p[1]
            )
        )


def p_instruction_2gpr_num(p):
    """instruction : i_2GPR_INT GPR ',' GPR ',' NAME
                   | i_2GPR_INT GPR ',' GPR ',' int
                   | i_2GPR_INT GPR ',' GPR ','
                   | i_2GPR_INT GPR ',' GPR
                   | i_2GPR_INT GPR ','
                   | i_2GPR_INT GPR
                   | i_2GPR_INT
                   | i_2GPR_UINT GPR ',' GPR ',' NAME
                   | i_2GPR_UINT GPR ',' GPR ',' unsigned
                   | i_2GPR_UINT GPR ',' GPR ','
                   | i_2GPR_UINT GPR ',' GPR
                   | i_2GPR_UINT GPR ','
                   | i_2GPR_UINT GPR
                   | i_2GPR_UINT
    """
    if len(p) is 7:
        p[0] = {
            i_opcode: p[1],
            i_rd: p[2],
            i_rs1: p[4]
        }
        # label
        if p.slice[6].type == "NAME":
            p[0][i_label] = p[6]
        # num
        else:
            p[0][i_immediate] = p[6]
    else:
        raise ParseException(
            "ERROR line {0}: missing parameter for {1}".format(
                p.lineno(0),
                p[1]
            )
        )


def p_instruction_3reg(p):
    """instruction : i_3GPR GPR ',' GPR ',' GPR
                   | i_3GPR GPR ',' GPR ','
                   | i_3GPR GPR ',' GPR
                   | i_3GPR GPR ','
                   | i_3GPR GPR
                   | i_3GPR
                   | i_3DPR dpr ',' dpr ',' dpr
                   | i_3DPR dpr ',' dpr ','
                   | i_3DPR dpr ',' dpr
                   | i_3DPR dpr ','
                   | i_3DPR dpr
                   | i_3DPR
                   | i_3FPR FPR ',' FPR ',' FPR
                   | i_3FPR FPR ',' FPR ','
                   | i_3FPR FPR ',' FPR
                   | i_3FPR FPR ','
                   | i_3FPR FPR
                   | i_3FPR
    """
    if len(p) is 7:
        p[0] = {
            i_opcode: p[1],
            i_rd: p[2],
            i_rs1: p[4],
            i_rs2: p[6]
        }
    else:
        raise ParseException(
            "ERROR line {0}: missing parameter for {1}".format(
                p.lineno(0),
                p[1]
            )
        )


def p_instruction_reg_offset(p):
    """instruction : i_GPR_OFFSET GPR ',' offset
                   | i_GPR_OFFSET GPR ','
                   | i_GPR_OFFSET GPR
                   | i_GPR_OFFSET
                   | i_DPR_OFFSET dpr ',' offset
                   | i_DPR_OFFSET dpr ','
                   | i_DPR_OFFSET dpr
                   | i_DPR_OFFSET
                   | i_FPR_OFFSET FPR ',' offset
                   | i_FPR_OFFSET FPR ','
                   | i_FPR_OFFSET FPR
                   | i_FPR_OFFSET
    """
    if len(p) is 5:
        p[0] = p[4]
        p[0][i_opcode] = p[1]
        p[0][i_rd] = p[2]
    else:
        raise ParseException(
            "ERROR line {0}: missing parameter for {1}".format(
                p.lineno(0),
                p[1]
            )
        )


def p_instruction_offset_reg(p):
    """instruction : i_OFFSET_GPR offset ',' GPR
                   | i_OFFSET_GPR offset ','
                   | i_OFFSET_GPR offset
                   | i_OFFSET_GPR
                   | i_OFFSET_DPR offset ',' dpr
                   | i_OFFSET_DPR offset ','
                   | i_OFFSET_DPR offset
                   | i_OFFSET_DPR
                   | i_OFFSET_FPR offset ',' FPR
                   | i_OFFSET_FPR offset ','
                   | i_OFFSET_FPR offset
                   | i_OFFSET_FPR
    """
    if len(p) is 5:
        p[0] = p[2]
        p[0][i_opcode] = p[1]
        p[0][i_rd] = p[4]
    else:
        raise ParseException(
            "ERROR line {0}: missing parameter for {1}".format(
                p.lineno(0),
                p[1]
            )
        )


def p_dpr(p):
    """dpr : FPR"""
    if int(p[1][1:]) not in range(0, 31, 2):
        raise ParseException(
            "ERROR line {0}: register {1} invalid, even number register "
            "required".format(
                p.lineno(1),
                p[1]
            )
        )
    else:
        p[0] = p[1]


def p_offset(p):
    """offset : int '(' GPR ')'
              | NAME
    """
    if len(p) is 5:
        p[0] = {
            i_immediate: p[1],
            i_rs1: p[3]
        }
    else:
        p[0] = {i_label: p[1]}


def p_unsigned(p):
    """unsigned : NUMBER"""
    if not isinstance(p[1], int):
        raise ParseException(
            "ERROR line {0}: expected int, found float".format(
                p.lineno(1)
            )
        )
    if p[1] < 0:
        raise ParseException(
            "ERROR line {0}: unsigned int required".format(
                p.lineno(1)
            )
        )
    # validate that it will fit in 16 bits
    if (p[1] & ~0xffff) is not 0:
        print "WARNING line {0}: unsigned immediate larger than 16 bits".format(
            p.lineno(1)
        )
    p[0] = p[1]


def p_int(p):
    """int : NUMBER"""
    if not isinstance(p[1], int):
        raise ParseException(
            "ERROR line {0}: expected int, found float".format(
                p.lineno(1)
            )
        )
    imm_max = int(2**16) - 1
    imm_min = -int(2**16)
    if p[1] > imm_max or p[1] < imm_min:
        print "WARNING line {0}: signed immediate larger than 16 bits".format(
            p.lineno(1)
        )
    p[0] = p[1]


def p_numlist(p):
    """numlist : numlist ',' NUMBER
               | numlist ','
               | NUMBER
    """
    if len(p) is 4:
        p[1].append(p[3])
        p[0] = p[1]
    elif len(p) is 3:
        raise ParseException(
            "ERROR line {0}: incomplete list".format(
                p.lineno(1)
            )
        )
    else:
        p[0] = [p[1]]


def p_stringlist(p):
    """stringlist : stringlist ',' STRING
                  | stringlist ','
                  | STRING
    """
    if len(p) is 4:
        p[1].append(p[3])
        p[0] = p[1]
    elif len(p) is 3:
        raise ParseException(
            "ERROR line {0}: incomplete list".format(
                p.lineno(1)
            )
        )
    else:
        p[0] = [p[1]]


# Handle errors signaled from the parser.
def p_error(p):
    if p is not None:
        # line counter isn't auto incremented due to exception
        p.lexer.lineno += 1
        raise ParseException(
            "ERROR line {0}: unknown token type {1} value \"{2}\"".format(
                p.lineno,
                p.type,
                p.value
            )
        )

# build the parser
parser = yacc.yacc()
