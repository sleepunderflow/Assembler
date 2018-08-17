# examples taken from nasm
# reference https://www.nasm.us/doc/nasmdoc3.html#section-3.2.1
 . . .  . . . .
db    55                # just the byte 55 
db    0x55,56, 0x57      # three bytes in succession 
db    'a',0x55, 'A'            # character constants are OK 
db    'hello',13,10,'$'   # so are string constants 
dw    0x1234              # 0x34 0x12 
dw    'a'                 # 0x61 0x00 (it's just a number) 
dw    'ab'                # 0x61 0x62 (character constant) 
dw    'abc'               # 0x61 0x62 0x63 0x00 (string) 
dd    0x12345678          # 0x78 0x56 0x34 0x12 
dq    0x123456789abcdef0  # eight byte constant 
