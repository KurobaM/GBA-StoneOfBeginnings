.ifdef DEBUG
.notice "Debug build"
.else
.notice "Release build"
.endif

.gba
.open "swordcraft3.gba","build/swordcraft3-test.gba",0x08000000

.include "asm/psi3_free.asm"

; Patches to enable ASCII and the VWF.
.include "asm/vwf_font.asm"
.include "asm/vwf_main.asm"
.include "asm/vwf_dialog.asm"
.include "asm/vwf_extend_sprite_tables.asm"
.include "asm/vwf_sprite_renderer.asm"
.include "asm/vwf_sprites.asm"
.include "asm/name_portrait_check.asm"


; Reduces the size of scripts so we don't have to worry about space much.
.include "asm/script_expr.asm"

; Patches to allow text to be wider and other tweaks.
.include "asm/craft.asm"
.include "asm/menu.asm"
.include "asm/shop.asm"
.include "asm/saving.asm"

; Fixes and tweaks for the naming screen.
;.include "asm/naming.asm"
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

; sfx text center align
.include "asm/sfx_text.asm"

;graphics

; name tag
.org 0x9dbed8c
.import "graphic/name_tag/100.9dbed8c.cg4"
.org 0x9dbefec
.import "graphic/name_tag/101.9dbefec.cg4"
.org 0x9dbf24c
.import "graphic/name_tag/102.9dbf24c.cg4"
.org 0x9dbf4ac
.import "graphic/name_tag/103.9dbf4ac.cg4"
.org 0x9dbf70c
.import "graphic/name_tag/104.9dbf70c.cg4"
.org 0x9dbf96c
.import "graphic/name_tag/105.9dbf96c.cg4"
.org 0x9dbfbcc
.import "graphic/name_tag/106.9dbfbcc.cg4"
.org 0x9dbfe2c
.import "graphic/name_tag/107.9dbfe2c.cg4"
.org 0x9dc008c
.import "graphic/name_tag/108.9dc008c.cg4"
.org 0x9dc02ec
.import "graphic/name_tag/109.9dc02ec.cg4"
.org 0x9dc054c
.import "graphic/name_tag/110.9dc054c.cg4"
.org 0x9dc07ac
.import "graphic/name_tag/111.9dc07ac.cg4"
.org 0x9dc0a0c
.import "graphic/name_tag/112.9dc0a0c.cg4"
.org 0x9dc0c6c
.import "graphic/name_tag/113.9dc0c6c.cg4"
.org 0x9dc0ecc
.import "graphic/name_tag/114.9dc0ecc.cg4"
.org 0x9dc112c
.import "graphic/name_tag/115.9dc112c.cg4"
.org 0x9dc138c
.import "graphic/name_tag/116.9dc138c.cg4"
.org 0x9dc15ec
.import "graphic/name_tag/117.9dc15ec.cg4"
.org 0x9dc184c
.import "graphic/name_tag/118.9dc184c.cg4"
.org 0x9dc1aac
.import "graphic/name_tag/119.9dc1aac.cg4"
.org 0x9dc1d0c
.import "graphic/name_tag/120.9dc1d0c.cg4"
.org 0x9dc1f6c
.import "graphic/name_tag/121.9dc1f6c.cg4"
.org 0x9dc21cc
.import "graphic/name_tag/122.9dc21cc.cg4"
.org 0x9dc242c
.import "graphic/name_tag/123.9dc242c.cg4"
.org 0x9dc268c
.import "graphic/name_tag/124.9dc268c.cg4"
.org 0x9dc28ec
.import "graphic/name_tag/125.9dc28ec.cg4"
.org 0x9dc2b4c
.import "graphic/name_tag/126.9dc2b4c.cg4"
.org 0x9dc2dac
.import "graphic/name_tag/127.9dc2dac.cg4"
.org 0x9dc300c
.import "graphic/name_tag/128.9dc300c.cg4"
.org 0x9dc326c
.import "graphic/name_tag/129.9dc326c.cg4"
.org 0x9dc34cc
.import "graphic/name_tag/130.9dc34cc.cg4"
.org 0x9dc372c
.import "graphic/name_tag/131.9dc372c.cg4"
.org 0x9dc398c
.import "graphic/name_tag/132.9dc398c.cg4"
.org 0x9dc3bec
.import "graphic/name_tag/133.9dc3bec.cg4"
.org 0x9dc3e4c
.import "graphic/name_tag/134.9dc3e4c.cg4"
.org 0x9dc40ac
.import "graphic/name_tag/135.9dc40ac.cg4"
.org 0x9dc430c
.import "graphic/name_tag/136.9dc430c.cg4"
.org 0x9dc456c
.import "graphic/name_tag/137.9dc456c.cg4"
.org 0x9dc47cc
.import "graphic/name_tag/138.9dc47cc.cg4"
.org 0x9dc4a2c
.import "graphic/name_tag/139.9dc4a2c.cg4"
.org 0x9dc4c8c
.import "graphic/name_tag/140.9dc4c8c.cg4"
.org 0x9dc4eec
.import "graphic/name_tag/141.9dc4eec.cg4"
.org 0x9dc514c
.import "graphic/name_tag/142.9dc514c.cg4"
.org 0x9dc53ac
.import "graphic/name_tag/143.9dc53ac.cg4"
.org 0x9dc560c
.import "graphic/name_tag/144.9dc560c.cg4"
.org 0x9dc586c
.import "graphic/name_tag/145.9dc586c.cg4"
.org 0x9dc5acc
.import "graphic/name_tag/146.9dc5acc.cg4"
.org 0x9dc5d2c
.import "graphic/name_tag/147.9dc5d2c.cg4"
.org 0x9dc5f8c
.import "graphic/name_tag/148.9dc5f8c.cg4"
.org 0x9dc61ec
.import "graphic/name_tag/149.9dc61ec.cg4"
.org 0x9dc644c
.import "graphic/name_tag/150.9dc644c.cg4"
.org 0x9dc66ac
.import "graphic/name_tag/151.9dc66ac.cg4"
.org 0x9dc690c
.import "graphic/name_tag/152.9dc690c.cg4"
.org 0x9dc6b6c
.import "graphic/name_tag/153.9dc6b6c.cg4"
.org 0x9dc6dcc
.import "graphic/name_tag/154.9dc6dcc.cg4"
.org 0x9dc702c
.import "graphic/name_tag/155.9dc702c.cg4"


;partner_info
.org 0x967abcc
.import "graphic/rundor_info.0967abcc.cg4"
.org 0x967c63c
.import "graphic/rundor_info.0967c63c.sc4"
.org 0x9687f3c
.import "graphic/enzi_info.9687f3c.cg4"
.org 0x96945cc
.import "graphic/enzi_info.96945cc.cg4"
.org 0x968968c
.import "graphic/killfith_info.968968c.sc4"
.org 0x969605c
.import "graphic/killfith_info.969605c.sc4"
.org 0x96a2d5c
.import "graphic/rufeel_info.96a2d5c.cg4"
.org 0x96a47ec
.import "graphic/rufeel_info.96a47ec.sc4"

; title
.org 0x095AE3AC
.import "graphic/title.95ae3ac.cg8"
.org 0x095B34DC
.import "graphic/title.95b34dc.sc8"

;title options
.include "asm/gfx_title_2player.asm"
.include "asm/gfx_title_omake.asm"
;title options EN
.include "asm/title_obj.asm"

; craft sword text
.org 0x09593A8C
.import "graphic/craft_sword.9593a8c.cg4"
.org 0x0959479C
.import "graphic/craft_sword.959479c.sc4"

.org 0x0958632C
.import "graphic/lyndbaum_text_1.958632c.cg4"
.org 0x09586C1C
.import "graphic/lyndbaum_text_1.9586c1c.sc4"
.org 0x095870EC
.import "graphic/lyndbaum_text_2.95870ec.cg4"
.org 0x0958791C
.import "graphic/lyndbaum_text_2.958791c.sc4"

.org 0x954458C
.import "asm/credits_craftsword_tile.lzss"
.org 0x9544BFC
.import "asm/credits_craftsword_map.lzss"
.org 0x966090C
.import "asm/select_hero.lz"

.include "asm/select partner.asm"

;fishing_minigame
.org 0x09646E2C
.import "graphic/fishing.9646e2c.cg4.lz77"
.org 0x0964684C
.import "graphic/fishing.964684c.sc4.lz77"

;link
.org 0x0952891C
.import "graphic/s_tsuushin_k1.952891c.cg4.lz77"
.org 0x0953682C
.import "graphic/s_tsuushin_k1.953682c.sc4.lz77"
;s_omake
.org 0x0952A5EC
.import "graphic/s_omake_k1.952a5ec.cg4.lz77"
.org 0x09536DEC
.import "graphic/s_omake_k1.9536dec.sc4.lz77"
;bestiary
.org 0x094FF70C
.import "graphic/bestiary_k1.94ff70c.cg4.lz77"
.org 0x0952F9EC
.import "graphic/bestiary_k1.952f9ec.sc4.lz77"


;lottery minigame gfx
.org 0x964DD6C
.import "asm/lottery/start_ready.bin"

;firewood minigame gfx
.org 0x094CF11C
.import "graphic/firewood_k1.94cf11c.cg4"
.org 0x094D3C4C
.import "graphic/firewood_k1.94d3c4c.sc4"

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
.import "graphic/lottery_rules_k1.965513c.cg4.lz77"
.org 0x0965827C
.import "graphic/lottery_rules_k1.965827c.sc4.lz77"
.org 0x964A99C
.import "graphic/lottery_scr_k1.964a99c.cg4.lz77"
.org 0x0964B9AC
.import "graphic/lottery_scr_k1.964b9ac.sc4.lz77"
.include "asm/lottery_ticket.asm"

;battle messages (guard, poison, sleep)
.include "asm/guard.asm"

;customize screen
.org 0x0951237C
.import "graphic/s_custom_1_k1.951237c.cg4.lz77"
.org 0x09532E0C
.import "graphic/s_custom_1_k1.9532e0c.sc4.lz77"

;other messages
.include "asm/non_psi3_script_text_struc.asm"
.include "asm/non_psi3_script_text.asm"

.close

