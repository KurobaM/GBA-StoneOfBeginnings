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
pop {pc}
.pool
.endregion


.org 0x8001D78
.region 0x8001D88-., 0x00
push {lr}
lsl r1, r1, #16
lsr r1, r1, #13
add r1, #8
bl IsPsi3
pop {pc}
.pool
.endregion


.autoregion
.func IsPsi3
push {r4, lr}
add r1, r0, r1
ldr r1, [r1]
lsl r1, r1, #4
add r0, r0, r1
;dir test
ldrh r1, [r0, #2]
cmp r1, #1
bne @@test_psi3
ldr r1, [r0, #4]
cmp r1, #4
beq @@end
@@test_psi3:
ldr r4, =0x3007900     ; non psi3, size 0x180 (end = 0x3007a80)
ldr r2, =0x33495350
ldr r1, [r0]
cmp r1, r2
beq @@psi3
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
beq @@psi3
ldr r3, [r4]
ldr r2, =0x55555555
cmp r3, r2      ; free ?
bne @@test_full
mov r3, #4
b @@save_other
@@test_full:
cmp r3, #0x5f   ; full ?
bhs @@end 
;test exist
mov r2, #0
@@test_exist_loop:
cmp r2, r3
bhs @@test_end
add r1, r2, #1
lsl r1, r1, #2
ldr r1, [r4, r1]
cmp r0, r1
beq @@end
add r2, #1
b @@test_exist_loop
@@test_end:
ldr r3, [r4]
add r3, #1
lsl r3, r3, #2 
@@save_other: 
str r0, [r4, r3]
lsr r3, r3, #2
str r3, [r4]
b @@end
@@psi3:
ldr r2, =0x3007ad0
ldr r1, [r2, #4]
cmp r1, r0      ; changed?
beq @@end
@@changed:
ldr r1, [r4]
ldr r2, =0x55555555 
cmp r1, r2      ; others free ?
beq @@save_psi3
add r1, #1
mov r4, r0
ldr r0, =0x3007900
bl FreeMemory
mov r0, r4
@@save_psi3: 
ldr r2, =0x3007ad0
str r0, [r2, #4]
lsl r1, r0, #5
lsr r1, r1, #5
str r1, [r2]
@@end:
pop {r4}
pop {pc}
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
push {r4, r5, lr}
; bg mode check suitable
ldr r0, =0x4000008
ldrh r0, [r0]
mov r1, #5
lsl r1, r1, #8
cmp r0, r1
bne @@end
; psi3
ldr r1, =0x3007ad0
ldr r0, [r1]
ldr r2, =0x55555555
cmp r0, r2
beq @@other
ldr r0, =0x2012810
bl WriteHexChar
@@other:
;check enable write other assets info flag 0x3007ad8
; flag = 1 -> draw info for other assets on screen
; can be manual set by using emulator memory editor / debugger
ldr r1, =0x3007ad0
ldrb r0, [r1, #8]
cmp r0, #1
bne @@end
ldr r1, =0x3007900
ldr r2, =0x55555555
ldr r0, [r1]
cmp r0, r2
beq @@end
cmp r0, #47
bls @@start
mov r0, #47
@@start:
mov r4, r0          ;count
mov r5, #0          ;index
@@loop:
cmp r5, r4
bhs @@end 
mov r0, r5
; calc row col
cmp r0, #32
bhs @@col3
lsr r1, r0, #1      ;r1: row
mov r2, #1
and r0, r2          ;r0: col
b @@calc_sc
@@col3:
sub r0, #32
add r1, r0, #1
mov r0, #2
@@calc_sc:
lsl r3, r0, #3
add r0, r3, r0
mov r2, #22
sub r0, r2, r0
lsl r0, r0, #1
lsl r1, r1, #6
add r0, r0, r1      ;   8
ldr r1, =0x2012810
add r0, r1, r0
add r5, #1
lsl r1, r5, #2
ldr r2, =0x3007900
add r1, r2, r1
bl WriteHexChar
b @@loop
@@end:
pop {r4, r5}
pop {pc}
.pool
.endfunc
.endautoregion


.autoregion
.func WriteHexChar
; r0 = screen address, r1 = value address
push {r4-r7, lr}
mov r5, r0
mov r6, r1
ldr r7, =HexChar
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
pop {pc}
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