::ASM
@echo off
set build=%1
armips swordcraft3.asm -temp build\swordcraft3_asm.txt -sym build\swordcraft3_sym.txt -stat -definelabel %build% 1
