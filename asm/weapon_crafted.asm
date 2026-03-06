;   KurobaM
;           251219

.org 0x806A3CC
.region 0x806A450-., 0x00
;r2 = 0x3000000
mov r1, #203
lsl r1, r1, #2          ; 0x32C
add r0, r2, r1
ldr r0, [r0]
mov r1, #204
lsl r1, r1, #2          ; 0x330
add r1, r2, r1
ldr r1, [r1]
bl WeaponCraftedStrConcat
bl GetStrGlyphWidth
push {r0}      ; r3 text length in pixel
; find full width length
add r0, 11
mov r1, 12
swi 6
ldr r5, =0x3006B04
ldr r2, [r5]
mov r1, #206
lsl r1, r1, #2
add r2, r2, r1
strh r0, [r2]
; find length in bg char
pop {r0}
add r0, 7
lsr r3, r0, #3  ;r0 text length in bg char
add r3, #6
cmp r3, #11
bhi @@save
mov r3, #12
@@save:
add r1, sp, #0x14
strb r3, [r1, #4]   ;width
mov r6, #0
mov r7, #0
mov r0, #4          ; height
strb r0, [r1, #5]
b 0x806A456
.pool
.endregion

.org 0x806A4EC
.region 0x806A58A-., 0x00
ldr r6, =0x3006B04
ldr r4, [r6]        ; r4 = 0x3000000
mov r3, #201
lsl r3, r3, #2
add r0, r4, r3      ; r0 = 0x3000324
ldr r2, =0x3007a80
add r3, #0x16
add r1, r4, r3      ; r1 = 0x300033A
ldrb r3, [r1]
add r3, #3
ldr r1, =0x33B
add r4, r4, r1
ldrb r1, [r4]
add r1, #1
str r1, [sp]
ldr r1, =0x44444444
str r1, [sp, #4]
mov r4, #0
str r4, [sp, #8]
mov r1, #2
str r1, [SP, #12]
str r4, [SP, #16]
mov r1, #1
bl 0x800B1AC
ldr r0, =0x3007a80
mov r1, 8
bl FreeMemory
ldr r6, =0x3006B04
ldr r5, =0x33A
ldr r1, =0x33B
mov r8, r1
b 0x806A58A
.pool
.endregion


.org 0x806A640
.region 0x806A64A-., 0x00
b 0x806A64A
.pool
.endregion

.autoregion
.func WeaponCraftedStrConcat
; args r0: char *str1, r1: char* str2 -> return r0: char* str out
push {lr}
ldr r3, =0x3007a80
mov r2, #0
; alloc 32 bytes; longest weapon name = 17, received text = 10, + 2 null = 29 
str r2, [r3]
str r2, [r3, #4]
str r2, [r3, #8]
str r2, [r3, #0xC]
str r2, [r3, #0x10]
str r2, [r3, #0x14]
str r2, [r3, #0x18]
str r2, [r3, #0x1C]
@@loop1:
ldrh r2, [r0]
cmp r2, #0xff
blo @@end1
strh r2, [r3]
add r0, #2
add r3, #2
b @@loop1
@@end1:
cmp r2, #0
beq @@loop2
strb r2, [r3]
add r3, #1
@@loop2:
ldrb r2, [r1]
cmp r2, #0
beq @@end2
strb r2, [r3]
add r1, #1
add r3, #1
b @@loop2
@@end2:
ldr r0, =0x3007a80
pop {pc}
.pool
.endfunc
.endautoregion
