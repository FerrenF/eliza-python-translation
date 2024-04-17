import argparse
import sys

from elizascript import ElizaScriptReader
from eliza import Eliza
from DOCTOR_1966_01_CACM import CACM_1966_01_DOCTOR_script

def parse_cmdline():
    parser = argparse.ArgumentParser(description="ELIZA -- A Computer Program for the Study of Natural Language Communication Between Man and Machine")
    parser.add_argument('--nobanner', action='store_true', help="Don't display startup banner")
    parser.add_argument('--showscript', action='store_true', help="Print Weizenbaum's 1966 DOCTOR script and exit")
    parser.add_argument('--quick', action='store_true', help="Print responses without delay (IBM 2741 speed)")
    #parser.add_argument('--help', action='store_true', help="Show usage information")
    parser.add_argument('--port', action='store_true', help="Use serial port for communication")
    parser.add_argument('--portname', metavar='PORT_NAME', help="Specify the serial port name (e.g., COM2)")
    parser.add_argument('script_filename', nargs='?', help="Specify the script file name")
    return parser.parse_args()

def print_banner():
    print("-----------------------------------------------------------------")
    print("      ELIZA -- A Computer Program for the Study of Natural")
    print("         Language Communication Between Man and Machine")
    print("DOCTOR script by Joseph Weizenbaum, 1966  (CC0 1.0) Public Domain")
    print("ELIZA implementation (v0.95) by Anthony Hay, 2022  (CC0 1.0) P.D.")
    print("-----------------------------------------------------------------")
    print("Use command line 'python eliza.py --help' for usage information.\n")

def print_command_help():
    print(        "  <blank line>    quit\n")
    print(        "  *               print trace of most recent exchange\n")
    print(        "  **              print the transformation rules used in the most recent reply\n")
    print(        "  *cacm           replay conversation from Weizenbaum's Jan 1966 CACM paper\n")
    print(        "  *key            show all keywords in the current script\n")
    print(        "  *key KEYWORD    show the transformation rule for the given KEYWORD\n")
    print(        "  *traceoff       turn off tracing\n")
    print(        "  *traceon        turn on tracing; enter '*' after any exchange to see trace\n")
    print(        "  *traceauto      turn on tracing; trace shown after every exchange\n")
    print(        "  *tracepre       show input sentence prior to applying transformation\n")
    print(        "                  (for watching the operation of Turing machines)\n")


#   The ELIZA script contains the opening_remarks followed by rules.
#   (The formal syntax is given in the elizascript namespace below.)
#   There are two types of rule: keyword_rule and memory_rule. They
#   are represented by the following classes. */
#
#  interface and data shared by both rules


def load_script_from_file(script_file):
    pass


def main():

    try:
        args = parse_cmdline()
        if not args.nobanner:
            print_banner()

        eliza_script = None
        if not args.script_filename:
            # Use default 'internal' 1966 CACM published script
            if not args.nobanner:
                print("No script filename given; using built-in 1966 DOCTOR script.")
            eliza_script = CACM_1966_01_DOCTOR_script  # Assuming you have a function to load the default script
        else:
            # Use the named script file
            try:
                with open(args.script_filename) as script_file:
                    if not args.nobanner:
                        print(f"Using script file '{args.script_filename}'\n")


                    eliza_script = load_script_from_file(script_file)
            except FileNotFoundError:
                print(f"{sys.argv[0]}: failed to open script file '{args.script_filename}'")
                sys.exit(-1)


        try:
            status, script = ElizaScriptReader.read_script(eliza_script)
        except RuntimeError as e:
            print(f"Error loading script: {e.__str__()}")
            exit(2)

        eliza = Eliza(script)

        print(eliza.get_greeting())
        if not args.nobanner:
            print("Enter a blank line to quit.\n")
        print("Enter a blank line to quit.\n")

        while True:
            user_input = input()

            if not user_input:
                break

            if user_input.startswith('*'):
                command = user_input.split()[0]
                # Handle special commands
                if command == "*":
                    print(eliza.trace)
                elif command == "**":
                    pass

                else:
                    print("Unknown command. Commands are:\n")
                    print_command_help()
                continue

            response = eliza.response(user_input)
            print(response)

    except Exception as e:
        print("Exception:", e)



if __name__ == "__main__":
    main()