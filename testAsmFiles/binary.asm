# examples taken from nasm
# reference https://www.nasm.us/doc/nasmdoc3.html#section-3.2.1
DB    55                # just the byte 55 
DB    0x55,56, 0x57      # three bytes in succession 
DB    'a',0x55, 'A'            # character constants are OK 
.start
DB    'hello',13,10,'$'   # so are string constants 
DW    0x1234              # 0x34 0x12 
DW    'a'                 # 0x61 0x00 (it's just a number) 
DW    "ab"               # 0x61 0x62 (character constant) 
DW    'abc'               # 0x61 0x62 0x63 0x00 (string) 
DD    0x12345678          # 0x78 0x56 0x34 0x12 
DQ    0x123456789abcde  # eight byte constant
# MOV   eax, ebx
# BD
