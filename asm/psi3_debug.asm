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
