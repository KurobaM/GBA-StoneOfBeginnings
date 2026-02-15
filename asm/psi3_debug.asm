;   KurobaM
;           260215


.org 0x8001D3C
.region 0x8001D5C-., 0x00
push {lr}
lsl r0, r0, #16
lsl r1, r1, #16
ldr r2, =0x03002970
lsr r0, r0, #14
add r0, r0, r2
lsr r1, r1, #13
add r1, #8
ldr r0, [r0, #0]
bl IsPsi3
pop {lr}
bx lr
.pool
.endregion


.org 0x8001D78
.region 0x8001D88-., 0x00
push {lr}
lsl r1, r1, #16
lsr r1, r1, #13
add r1, #8
bl IsPsi3
pop {lr}
bx lr
.pool
.endregion


.autoregion
.func IsPsi3
push {lr}
add r1, r0, r1
ldr r1, [r1, #0]
lsl r1, r1, #4
add r0, r0, r1
ldr r2, =0x33495350
ldr r1, [r0]
cmp r1, r2
beq @@save
mov r1, #0
ldrb r3, [r0, #5]
add r1, r1, r3
ldrh r3, [r0, #6]
lsl r3, r3, #8
add r1, r1, r3
ldrb r3, [r0, #8]
lsl r3, r3, #24
add r1, r1, r3
cmp r1, r2
bne @@end
@@save:
ldr r2, =0x3007AD0
lsl r1, r0, #5
lsr r1, r1, #5
str r1, [r2]
@@end:
pop {lr}
bx lr
.pool
.endfunc
.endautoregion


.org 0x8002092
.region 0x80020A8-., 0x00
push {lr}
bl DrawDebugInfo
bl 0x080001D0
bl 0x080B8BE8
pop {pc}
.pool
.endregion


.autoregion
.func DrawDebugInfo
push {r4-r7, lr}
ldr r0, =0x4000008
ldrh r0, [r0]
mov r1, #5
lsl r1, r1, #8
cmp r0, r1
bne @@end
ldr r6, =0x3007AD0
ldr r0, [r6]
ldr r1, =0x55555555
cmp r0, r1
beq @@end
ldr r7, =HexChar
ldr r5, =0x2012810
mov r4, #0xF
mov r3, #0
@@loop:
ldrb r1, [r6, r3]
lsr r2, r1, #4      ;hi part
and r1, r4          ;lo part
sub r5, r5, #4
ldrb r0, [r7, r2]
strb r0, [r5]
ldrb r0, [r7, r1]
strb r0, [r5, #2]
add r3, #1
cmp r3, #4
blo @@loop
@@end:
pop {r4-r7}
pop {lr}
bx lr
.pool
.endfunc
.endautoregion


.autoregion
HexChar:
.db 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26
.endautoregion


/*
.autoregion
.func CopyHexFontVRAM
push {lr}
ldr r1, =0x600fd00
ldr r0, =0x94d504c
mov r2, #0x50           ; 10 * 0x20 / 4
bl 0x80B8BC8            ; CpuFastSet
ldr r1, =0x600fe40
ldr r0, =0x94d526c
mov r2, #0x30           ; 6 * 0x20 / 4
bl 0x80B8BC8            ; CpuFastSet
pop {lr}
bx lr
.pool
.endfunc
.endautoregion
*/

/*
.autoregion
HexFont:
;0
.dw 0x94d504c
;1
.dw 0x94d506c
;2
.dw 0x94d508c
;3
.dw 0x94d50ac
;4
.dw 0x94d50cc
;5
.dw 0x94d50ec
;6
.dw 0x94d510c
;7
.dw 0x94d512c
;8
.dw 0x94d514c
;9
.dw 0x94d516c
;A
.dw 0x94d526c
;B
.dw 0x94d528c
;C
.dw 0x94d52ac
;D
.dw 0x94d52cc
;E
.dw 0x94d52ec
;F
.dw 0x94d530c
.endautoregion


.autoregion
HexFont2:
; 0
.db 0b00111000
.db 0b01000100
.db 0b01000100
.db 0b01000100
.db 0b01000100
.db 0b01000100
.db 0b00111000
.db 0b00000000
; 1
.db 0b00010000
.db 0b00110000
.db 0b00010000
.db 0b00010000
.db 0b00010000
.db 0b00010000
.db 0b00111000
.db 0b00000000
; 2
.db 0b00111000
.db 0b01000100
.db 0b00000100
.db 0b00011000
.db 0b00100000
.db 0b01000000
.db 0b01111100
.db 0b00000000
; 3
.db 0b00111000
.db 0b01000100
.db 0b00000100
.db 0b00011000
.db 0b00000100
.db 0b01000100
.db 0b00111000
.db 0b00000000
; 4
.db 0b00001000
.db 0b00011000
.db 0b00101000
.db 0b01001000
.db 0b01111100
.db 0b00001000
.db 0b00001000
.db 0b00000000
; 5
.db 0b01111100
.db 0b01000000
.db 0b01111000
.db 0b00000100
.db 0b00000100
.db 0b01000100
.db 0b00111000
.db 0b00000000
; 6
.db 0b00111000
.db 0b01000100
.db 0b01000000
.db 0b01111000
.db 0b01000100
.db 0b01000100
.db 0b00111000
.db 0b00000000
; 7
.db 0b01111100
.db 0b00000100
.db 0b00001000
.db 0b00010000
.db 0b00010000
.db 0b00010000
.db 0b00010000
.db 0b00000000
; 8
.db 0b00111000
.db 0b01000100
.db 0b01000100
.db 0b00111000
.db 0b01000100
.db 0b01000100
.db 0b00111000
.db 0b00000000
; 9
.db 0b00111000
.db 0b01000100
.db 0b01000100
.db 0b00111100
.db 0b00000100
.db 0b01000100
.db 0b00111000
.db 0b00000000
; A
.db 0b00111000
.db 0b01000100
.db 0b01000100
.db 0b01000100
.db 0b01111100
.db 0b01000100
.db 0b01000100
.db 0b00000000
; B
.db 0b01111000
.db 0b01000100
.db 0b01000100
.db 0b01111000
.db 0b01000100
.db 0b01000100
.db 0b01111000
.db 0b00000000
; C
.db 0b00111000
.db 0b01000100
.db 0b01000000
.db 0b01000000
.db 0b01000000
.db 0b01000100
.db 0b00111000
.db 0b00000000
; D
.db 0b01111000
.db 0b01000100
.db 0b01000100
.db 0b01000100
.db 0b01000100
.db 0b01000100
.db 0b01111000
.db 0b00000000
; E
.db 0b01111100
.db 0b01000000
.db 0b01000000
.db 0b01111000
.db 0b01000000
.db 0b01000000
.db 0b01111100
.db 0b00000000
; F
.db 0b01111100
.db 0b01000000
.db 0b01000000
.db 0b01111000
.db 0b01000000
.db 0b01000000
.db 0b01000000
.db 0b00000000
.endautoregion
*/