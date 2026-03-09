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

; Allow using the debug menu features.
.ifdef DEBUG
.include "asm/debug_menu.asm"
.endif

;Solves location space limitations
.include "asm/saving_location.asm"

;Fixes obtained! issue with money and items
.include "asm/item_obtained.asm"
.include "asm/money_obtained.asm"

; subroutine for free custom alloc memory
.include "asm/free_mem.asm"

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
.include "asm/title.asm"
.include "asm/gfx_craftsword_edit.asm"
.include "asm/lyndbaum_text_en_1.asm"
.include "asm/lyndbaum_text_en_2.asm"
.include "asm/gfx_insert_lzss.asm"
.include "asm/select partner.asm"

;partner_info_gfx
.include "asm/partner_info_gfx/balance_TL.asm"
.include "asm/partner_info_gfx/flight_TL.asm"
.include "asm/partner_info_gfx/power_TL.asm"
.include "asm/partner_info_gfx/speed_TL.asm"

;title options
.include "asm/gfx_title_2player.asm"
.include "asm/gfx_title_omake.asm"
;title options EN
.include "asm/title_obj.asm"

;fishing_minigame
.org 0x09646E2C
.import "asm/fishing/fishing_tile.lzss"
.org 0x0964684C
.import "asm/fishing/fishing_map.lzss"

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
