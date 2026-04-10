;   KurobaM
;           260312


.autoregion
.func DrawDebugInfo
push {r4, r5, lr}
;disp cnt check
ldr r2, =0x4000000
ldrh r0, [r2]
ldr r1, =0x1F40
cmp r0, r1
bne @@end
; bg mode check suitable
ldrh r0, [r2, #8]
mov r1, #5
lsl r1, r1, #8
cmp r0, r1
bne @@end
; color check in range 0x0a - 0x0f / 0x1f
lsr r3, r2, #2
add r2, r2, r3
ldrh r0, [r2, #2]
cmp r0, #0x0a
blo @@end
cmp r0, #0x10
bhs @@end
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


.autoregion
.func VsyncAndDebug
push {lr}
bl DrawDebugInfo
bl 0x080001D0
bl 0x080B8BE8
pop {pc}
.endfunc
.endautoregion
