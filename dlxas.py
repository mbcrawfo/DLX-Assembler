import sys
import getopt
from assembler import Assembler

# Expected input file extension
in_file_ext = ".dlx"
# Expected output file extension
out_file_ext = ".hex"
# Program options
options = {
    "verbose": False,
    "dump": False,
    "console": False,
    "no_output": False,
    "in_file": None,
    "out_file": None
}


# Main function
# Input:
#   argv - Command line args
# Returns:
#   n/a
def main(argv):
    if parse_args(argv):
        asm = Assembler(options)
        asm.run()


# Prints help information to console
# Input:
#   n/a
# Returns:
#   n/a
def print_help():
    print "dlxas.py [options] [file]"
    print "Options:"
    print "-h\n" \
          "--help\n" \
          "\tPrint this help text."
    print "-v\n" \
          "--verbose\n" \
          "\tEnable verbose output while running."
    print "-d\n" \
          "--dump\n" \
          "\tDump the symbol table before symbol resolution."
    print "-p\n" \
          "--prompt\n" \
          "\tPrompt for the input file."
    print "-c\n" \
          "--console\n" \
          "\tWrite output to stdout instead of to a file."
    print "-n\n" \
          "--no_output\n" \
          "\tProcess the input file, but do not write output."
    print "-i <file>\n" \
          "--input=<file>\n" \
          "\tExplicitly specify the input file rather than " \
          "supplying it as the last parameter."
    print "-o <file>\n" \
          "--output=<file>\n" \
          "\tOverride the default output file name."


# Parses command line args, inserting them into the program options.
# Input:
#   argv - Command line args
# Returns:
#   True if argument parsing was successful.
def parse_args(argv):
    short_opts = "hvdpcni:o:"
    long_opts = ["help", "verbose", "dump", "prompt", "console", "no_output",
                 "input=", "output="]

    try:
        opts, args = getopt.getopt(argv, short_opts, long_opts)
    except getopt.GetoptError:
        print_help()
        return False

    prompt = False
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            return False
        elif opt in ("-v", "--verbose"):
            options["verbose"] = True
        elif opt in ("-d", "--dump"):
            options["dump"] = True
        elif opt in ("-p", "--prompt"):
            prompt = True
        elif opt in ("-c", "--console"):
            options["console"] = True
        elif opt in ("-n", "--no_output"):
            options["no_output"] = True
        elif opt in ("-i", "--input"):
            options["in_file"] = arg
        elif opt in ("-o", "--output"):
            options["out_file"] = arg

    # Get the input file from the last arg, if not specified
    if options["in_file"] is None and len(args) is 1:
        options["in_file"] = args[0]
    elif options["in_file"] is None and len(args) is 0 and prompt:
        options["in_file"] = raw_input("Enter file name: ")
    else:
        print_help()
        return False
    # Verify input file type
    if not options["in_file"].endswith(in_file_ext):
        print "Unknown input file type:", options["in_file"]
        return False
    # Set output file to default if necessary
    if options["out_file"] is None:
        options["out_file"] = options["in_file"].replace(in_file_ext,
                                                         out_file_ext)
    return True

# Python main function call
if __name__ == "__main__":
    main(sys.argv[1:])