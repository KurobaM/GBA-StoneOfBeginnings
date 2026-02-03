@echo off

python init.py

call .\build_stage\gen_font_asm.bat > build\build_log.txt 2>&1

call .\build_stage\armips.bat >> build\build_log.txt 2>&1

call .\build_stage\system_message.bat >> build\build_log.txt 2>&1

call .\build_stage\compile_cmd_generate.bat  >> build\build_log.txt 2>&1

call .\build\compile.bat >> build\build_log.txt 2>&1

call .\build_stage\import_psi3.bat >> build\build_log.txt 2>&1

call .\build_stage\import_font.bat >> build\build_log.txt 2>&1

call .\build_stage\create_patch.bat >> build\build_log.txt 2>&1

python version.py
