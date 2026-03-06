;   KurobaM
;           251213
; Golden weapon crafted message box 
; Fix text spill over

;dialog
.org 0x80894C6
;mov r0, #0x11
mov r0, #0x14   ; increase size by 3 

.org 0x80894CE
;move r0, #7
mov r0, #5   ; move left by 2

; text
.org 0x8089528
mov r3, #9   ; unchanged
