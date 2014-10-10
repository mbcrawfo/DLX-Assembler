import string

# File to load r-type instructions
r_type_file = "Rtypes"
# File to load i-type instructions
i_type_file = "Itypes"
# File to load j-type instructions
j_type_file = "Jtypes"

# instruction table
instruction_table = {}


# Acts as an enum of instruction types.
class InstructionType:
    R, I, J = range(3)
    all = [R, I, J]

    # just to suppress warnings
    def __init__(self):
        pass


# Gets the file name to load a particular instruction type.
# Input:
#   type_id - The instruction type.
# Return:
#   The file name to load that instruction type from.
# Throws:
#   ValueError - Invalid instruction type.
def file_name(type_id):
    if type_id is InstructionType.R:
        return r_type_file
    elif type_id is InstructionType.I:
        return i_type_file
    elif type_id is InstructionType.J:
        return j_type_file
    else:
        raise ValueError("Unknown instruction type")


# Loads the instruction set from files.
# Input:
#   n/a
# Returns:
#   n/a
# Throws:
#   IOError - The file format isn't recognized.
def load():
    for type_id in InstructionType.all:
        name = file_name(type_id)
        with open(name, "r") as f:
            for line in f:
                words = string.split(string.lower(line))
                if len(words) in (2, 3):
                    i = {
                        "type": type_id,
                        "opcode": int(words[1]),
                        "fun_code": 0
                    }
                    if len(words) is 3:
                        i["fun_code"] = int(words[2])
                    instruction_table[words[0]] = i
                else:
                    raise IOError("file {} has unknown format".format(name))


# Returns an instruction's information.
# Input:
#   name - The instruction name.
# Return:
#   type, opcode, fun_code
# Throws:
#   ValueError - Unknown instruction name.
def get_info(name):
    assert isinstance(name, str)
    if not name in instruction_table:
        raise ValueError("Unknown instruction " + name)
    i = instruction_table[name]
    return i["type"], i["opcode"], i["fun_code"]


# Returns an instruction's type.
# Input:
#   name - The instruction name.
# Return:
#   type
# Throws:
#   ValueError - Unknown instruction name.
def get_type(name):
    type_id, _, _ = get_info(name)
    return type_id


# Returns an instruction's opcode.
# Input:
#   name - The instruction name.
# Return:
#   opcode
# Throws:
#   ValueError - Unknown instruction name.
def get_opcode(name):
    _, opcode, _ = get_info(name)
    return opcode


# Returns an instruction's function code.
# Input:
#   name - The instruction name.
# Return:
#   funcode
# Throws:
#   ValueError - Unknown instruction name.
def get_funcode(name):
    _, _, funcode = get_info(name)
    return funcode