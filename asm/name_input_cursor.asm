;   KurobaM
;           260131

.org 0x80A8A9A
.region 0x80A8AC4-., 0x00
; r4 200e074, r5 200e000
mov r1, #8
ldrsh r0, [r5, r1]
lsl r1, r0, #1
add r1, r1, r0
lsl r1, r1, #18
mov r3, #128
lsl r3, r3, #13
add r1, r1, r3
asr r1, r1, #16
ldrb r0, [r5, #14]
bl SetCursorPos
pop {r4, r5}
pop {r0}
bx r0
.pool
.endregion


.autoregion
.func SetCursorPos
; args r0: charset, r1: x, r4: 200e074, r5 200e000 
ldrh r2, [r5, #10]
lsl r2, r2, #20
mov r3, #160
lsl r3, r3, #14
add r2, r2, r3
asr r2, r2, #16
strh r2, [r4, #22]
cmp r0, #2
bne @@save_x
mov r3, #8
ldrsh r0, [r5, r3]
ldrh r3, [r5, #10]
cmp r3, #5
bhi @@save_x
cmp r0, #12
blo @@sub_x
cmp r3, #1
bhi @@save_x
@@sub_x:
sub r1, r1, #3
@@save_x:
strh r1, [r4, #20]
bx lr
.pool
.endfunc
.endautoregion