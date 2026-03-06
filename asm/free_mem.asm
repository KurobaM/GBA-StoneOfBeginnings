;   KurobaM
;           260305

.autoregion
.func FreeMemory
; args r0: *dword arr, r1: arr size 
push {lr}
ldr r3, =0x55555555
mov r2, #0
@@loop:
cmp r2, r1
beq @@end
str r3, [r0]
add r0, #4
add r2, #1
b @@loop 
@@end:
pop {pc}
.pool
.endfunc
.endautoregion