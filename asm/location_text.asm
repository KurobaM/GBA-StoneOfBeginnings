;   KurobaM
;           260116

.org 0x8018E64
.region 0x8018E74-., 0x00

push {lr}
bl GetLocationTxt
pop {pc}
.pool
.endregion


.autoregion
.func GetLocationTxt
push {lr}
ldr r0, =0x3006994
ldr r0, [r0]
mov r1, #0xb6
lsl r1, r1, 3
add r0, r0, r1
push {r0}
bl GetTextFromId
mov r1, r0
pop {r0}
cmp r0, r1
beq @@end
mov r3, #0
@@loop:
ldrh r2, [r1, r3]
strh r2, [r0, r3]
cmp r2, #0
beq @@end
add r3, r3, 2
b @@loop
@@end:
pop {pc}
.pool
.endfunc
.endautoregion


.autoregion
.func GetTextFromId
; r0: *placeholder_text, return r0: * text
push {lr}
ldr r2, =0x6F72754B
ldr r1, [r0]
cmp r1, r2
bne @@end
ldr r2, =0x2E4D6162
ldr r1, [r0, #4]
cmp r1, r2
bne @@end
ldrb r1, [r0, #8]
mov r2, #0x31
cmp r1, r2
blo @@end 
sub r1, r1, r2
lsl r1, r1, 2
ldr r2, =StringTable
add r1, r1, r2
ldr r0, [r1]
@@end:
pop {pc}
.pool
.endfunc
.endautoregion


.autoregion
.align 4
StringTable:
.word txt_gumag 
txt_gumag:
.db 0x47, 0x75, 0x6D, 0x61, 0x67, 0x20, 0x46, 0x69, 0x72, 0x65, 0x20, 0x52, 0x75, 0x69, 0x6E, 0x73, 0x00, 0x00
.align 2
.endautoregion

