;   KurobaM
;           260331


.org 0x800D828
.region 0x800D82E-., 0x00
bl evalTextXpos
.endregion

.autoregion
.func evalTextXpos
push {r4, lr}
lsl r0, r0, #16
lsr r0, r0, #16
cmp r0, #0xff
bne @@done
bl 0x8012EC4
ldrb r4, [r0, #2]
add r0, #8
bl GetStrGlyphWidth
cmp r4, #1
beq @@skip      ; big text 2x size
lsr r0, r0, #1
@@skip:
mov r1, #112
sub r0, r1, r0
ble @@nz
add r0, #8
b @@done
@@nz:
mov r0, #8
@@done:
pop {r4}
pop {pc}
.pool
.endfunc
.endautoregion

