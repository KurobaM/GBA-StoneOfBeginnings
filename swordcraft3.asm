.ifdef DEBUG
.notice "Debug build"
.else
.notice "Release build"
.endif

.gba
.open "swordcraft3.gba","build/swordcraft3-test.gba",0x08000000

; Patches to enable ASCII and the VWF.
.include "asm/vwf_font.asm"
.include "asm/vwf_main.asm"
.include "asm/vwf_dialog.asm"
.include "asm/vwf_extend_sprite_tables.asm"
.include "asm/vwf_sprite_renderer.asm"
.include "asm/vwf_sprites.asm"
.include "asm/name_portrait_check.asm"
.include "asm/names_obj.asm"

; Reduces the size of scripts so we don't have to worry about space much.
.include "asm/script_expr.asm"

; Patches to allow text to be wider and other tweaks.
.include "asm/craft.asm"
.include "asm/menu.asm"
.include "asm/shop.asm"
.include "asm/saving.asm"

; Fixes and tweaks for the naming screen.
.include "asm/naming.asm"
.include "asm/name_input.asm"
.include "asm/sjis2ascii.asm"

.include "asm/name_input_cursor.asm"
.include "asm/name_input_disable_kana.asm"

; subroutine for free custom alloc memory
.include "asm/free_mem.asm"

; Allow using the debug menu features.
.ifdef DEBUG
.include "asm/vsync_debug.asm"
.include "asm/debug_menu.asm"
.endif

;Solves location space limitations
.include "asm/saving_location.asm"

;Fixes obtained! issue with money and items
.include "asm/item_obtained.asm"
.include "asm/money_obtained.asm"

;text dialog fixes
.include "asm/golden_weapon_dialog.asm"
.include "asm/battle_item_get_dialog.asm"
.include "asm/weapon_crafted.asm"

;location text fixes
.include "asm/location_text.asm"

;psi3 debug
.ifdef DEBUG
.include "asm/psi3_debug.asm"
.endif

;graphics
; title
.org 0x095AE3AC
.import "graphic/title.cg8"
.org 0x095B34DC
.import "graphic/title.sc8"

;title options
.include "asm/gfx_title_2player.asm"
.include "asm/gfx_title_omake.asm"
;title options EN
.include "asm/title_obj.asm"

; craft sword text
.org 0x09593A8C
.import "graphic/craft_sword.cg4"
.org 0x0959479C
.import "graphic/craft_sword.sc4"

.org 0x0958632C
.import "graphic/lyndbaum_text_1.cg4"
.org 0x09586C1C
.import "graphic/lyndbaum_text_1.sc4"
.org 0x095870EC
.import "graphic/lyndbaum_text_2.cg4"
.org 0x0958791C
.import "graphic/lyndbaum_text_2.sc4"

.org 0x954458C
.import "asm/credits_craftsword_tile.lzss"
.org 0x9544BFC
.import "asm/credits_craftsword_map.lzss"
.org 0x966090C
.import "asm/select_hero.lz"

.include "asm/select partner.asm"

;partner_info_gfx
.include "asm/partner_info_gfx/balance_TL.asm"
.include "asm/partner_info_gfx/flight_TL.asm"
.include "asm/partner_info_gfx/power_TL.asm"
.include "asm/partner_info_gfx/speed_TL.asm"

;fishing_minigame
.org 0x09646E2C
.import "graphic/fishing.cg4.lz77"
.org 0x0964684C
.import "graphic/fishing.sc4.lz77"

;link
.org 0x0952891C
.import "graphic/s_tsuushin_k1.cg4.lz77"
.org 0x0953682C
.import "graphic/s_tsuushin_k1.sc4.lz77"
;s_omake
.org 0x0952A5EC
.import "graphic/s_omake_k1.cg4.lz77"
.org 0x09536DEC
.import "graphic/s_omake_k1.sc4.lz77"
;bestiary
.org 0x094FF70C
.import "graphic/bestiary_k1.cg4.lz77"
.org 0x0952F9EC
.import "graphic/bestiary_k1.sc4.lz77"


;lottery minigame gfx
.org 0x964DD6C
.import "asm/lottery/start_ready.bin"

;firewood minigame gfx
.org 0x094CF11C
.import "graphic/firewood_k1_tile.bin"
.org 0x094D3C4C
.import "graphic/firewood_k1_map.bin"

;minigame results
.org 0x964F58C
.import "asm/lottery/1_place.lzss"
.org 0x964FE2C
.import "asm/lottery/2_place.lzss"
.org 0x965048C
.import "asm/lottery/3_place.lzss"
.org 0x96509FC
.import "asm/lottery/4_place.lzss"
.org 0x9650F1C
.import "asm/lottery/5_place.lzss"
.org 0x0965513C
.import "graphic/lottery_rules_k1.cg4.lz77"
.org 0x0965827C
.import "graphic/lottery_rules_k1.sc4.lz77"
.org 0x964A99C
.import "graphic/lottery_scr_k1.cg4.lz77"
.org 0x0964B9AC
.import "graphic/lottery_scr_k1.sc4.lz77"
.include "asm/lottery_ticket.asm"

;battle messages (guard, poison, sleep)
.include "asm/guard.asm"

;customize screen
.org 0x0951237C
.import "graphic/s_custom_1_k1_tile.lzss"
.org 0x09532E0C
.import "graphic/s_custom_1_k1_map.lzss"

;other messages
.include "asm/non_psi3_script_text.asm"

.close
