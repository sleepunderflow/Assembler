# Assembler

Simple AMD64 assembler

Usage:
./assembler.py [OPTIONS..]

OPTIONS:
-i: fileName specify the input file
-o: fileName specify the output file
-e: little/big specify endianess of the output
-h, --help: show this help message and exit
-v, --verbose: increase the number of debugging info
-f: generated file type

SUPPORTED OUTPUT FILE TYPES:
bin - just a plain unmodified file
elf - create headers to make it executable (currently just minimum headers with fixed addresses so that it just runs)

SUPPORTED INSTRUCTIONS/LABELS:
.start - label pointing to where execution should start if it's an ELF file
DB, DW, DD, DQ - just put the parameter as a byte, word, double word or quad word (with endianess if necessary)

testAsmFiles:
There is a couple of files added in the testAsmFiles directory for testing purposes:

- binary.asm - just some random stuff, not meant to be executable, just for testing instructions and errors
- reverseShell.asm - if used with '-f elf' should generate a working but simple reverse shell (connects to localhost:4444) using only .start, DB,DW,DD,DQ
