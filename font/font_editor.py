# Copyright (C) 2026, KurobaM
# SPDX-License-Identifier: GPL-3.0-or-later
# SN CSM3 Font Editor v1.7.2


from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from enum import Enum
import os
import random
import string
import unicodedata

import numpy as np
from PyQt5.QtCore import pyqtSignal, Qt,  QTimer
from PyQt5.QtGui import QKeyEvent, QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView,   QHBoxLayout, QLineEdit, QPushButton, QSpinBox, QVBoxLayout, QWidget)

from font_editor_ui import Ui_FontEditor


folder = os.path.join(os.path.dirname(__file__), 'data')


with open(os.path.join(folder, 'font.bit'), 'rb') as f:
    font_data = f.read()

with open(os.path.join(folder, 'lookup_tbl_8b6d624.bin'), 'rb') as f:
    data_81 = f.read()

with open(os.path.join(folder, 'lookup_tbl_8b704a4.bin'), 'rb') as f:
    data_e0 = f.read()

with open(os.path.join(folder, 'ascii_lut.bin'), 'rb') as f:
    data_a_lut = f.read()

with open(os.path.join(folder, 'ascii_width.bin'), 'rb') as f:
    data_a_w = f.read()


# glyphs -------------------------------------------
glyphs = {
    i: np.unpackbits(np.frombuffer(
        font_data[0x1c + i * 24: 0x1c + (i+1) * 24],
        np.uint8)).reshape((12, 16))
    for i in range(0, (len(font_data) - 0x1c)//24)}

invalid_glyph = np.unpackbits(
    np.frombuffer((b'\xff\xe0\x00\x00\xff\xe0\x00\x00'
                   b'\xff\xe0\x00\x00\xff\xe0\x00\x00'
                   b'\xff\xe0\x00\x00\xff\xe0\x00\x00'),
                  np.uint8)
).reshape((12, 16))
# -------------------------------------------------------


# lookup table -----------------------------------------
lut_81 = np.frombuffer(data_81, np.uint16)  # 81 40 -> 9F FF,  192x31 values

lut_e0 = np.frombuffer(data_e0, np.uint16)  # E0 40 -> EA A1,  192x10+98 values

# uint16
ascii_lut = np.frombuffer(data_a_lut, np.uint16).tolist()

ascii_width = np.frombuffer(data_a_w, np.uint8).tolist()
# --------------------------------------------------


# color -------------------------------------------
mint_green = 0xff96ebad
white = 0xffffffff
black = 0xff000000
red = 0xff00007d
green = 0xff004000
blue = 0xffe80000
color_map = np.array([white, black], np.uint32)  # white, black
text_color = np.array([0xffcef7ff, 0xff00006b], np.uint32)  # same as ROM.
editor_color = np.array([white, black, red, blue, green], np.uint32)
# --------------------------------------------------

test = string.printable.split('\n')[0]
watanare = (
    'Watashi ga Koibito ni Nareru Wakenaijan, '
    'Muri Muri! (*Muri Janakatta!?)')


def zoom(data_2d, factor):
    scaling_matrix = np.ones((factor, factor))
    dtype = data_2d.dtype
    scaled_arr = np.kron(data_2d, scaling_matrix)
    return scaled_arr.astype(dtype)


def cacl_sjis_2b_index(code_point: bytes):
    if len(code_point) != 2:
        raise ValueError('Must be two bytes code point')
    first = code_point[0]
    second = code_point[1]
    col = second - 0x40
    row = first - 0xE0 if first > 0x9f else first - 0x81
    lookup_tbl = lut_e0 if first > 0x9f else lut_81
    return int(lookup_tbl[row * (0xff - 0x40 + 1) + col])


def sjis_2b_to_glyph(code_point: bytes, width: int = 16):
    try:
        index = cacl_sjis_2b_index(code_point) - 1
        if index == -1:
            return (invalid_glyph, width)
        else:
            return (glyphs[index], width if width <= 16 else 16)
    except IndexError:
        raise ValueError('Invalid code point')


def sjis_1b_to_glyph(code_point: bytes):
    if len(code_point) != 1:
        raise ValueError('Must be two bytes code point')
    lu_index = code_point[0]
    try:
        index = ascii_lut[lu_index] - 1
        width = ascii_width[lu_index]
        if index == -1:
            return (invalid_glyph, 12)
        else:
            return (glyphs[index], width)
    except IndexError:
        raise ValueError('Invalid code point')


def sjis_to_glyph(code_point: bytes):
    if len(code_point) == 1:
        g, w = sjis_1b_to_glyph(code_point)
    elif len(code_point) == 2:
        g, w = sjis_2b_to_glyph(code_point, 12)
    else:
        raise ValueError()
    return (g, w)


def sjis_width(code_point: bytes):
    if len(code_point) == 1:
        lu_index = code_point[0]
        try:
            return ascii_width[lu_index]
        except IndexError:
            raise ValueError('Invalid code point')
    elif len(code_point) == 2:
        return 12


def font_index_to_sjis(index: int):
    if index < 0 or index >= len(glyphs):
        raise IndexError()
    idx = index + 1
    if idx in lut_81:
        lut_idx = np.where(lut_81 == idx)[0][0]
        fp = (lut_idx // (0xff - 0x40 + 1)) + 0x81
    elif idx in lut_e0:
        lut_idx = np.where(lut_e0 == idx)[0][0]
        fp = (lut_idx // (0xff - 0x40 + 1)) + 0xe0
    else:
        raise ValueError('Glyph with no sjis code point')
    sp = (lut_idx % (0xff - 0x40 + 1)) + 0x40
    return int.to_bytes(int(fp + (sp << 8)), 2, 'little')


def unicode_to_sjis(text: str, silent=False):
    char = [x for x in text]
    out: list[bytes] = []
    err: list[str] = []
    for x in char:
        try:
            out.append(x.encode('sjis'))
        except UnicodeEncodeError:
            err.append(x)
    if err and not silent:
        raise ValueError('Invalid character(s): '
                         ', '.join([f"'{x}'" for x in err]))
    return out, err


def unicode_text_to_pixmap(text: str, zoom_level: int):
    err: list[str] = []
    out = []
    code_points, e = unicode_to_sjis(text)
    err.extend(e)
    for code in code_points:
        try:
            g, w = sjis_to_glyph(code)
            out.append(g[:, :w])
        except ValueError:
            err.append(code.decode('sjis'))
    text_img = text_color[zoom(np.hstack(out), zoom_level)]
    th, tw = text_img.shape
    w = tw // zoom_level
    err_msg = 'Invalid character(s): ' + (
        ', '.join([f"'{x}'" for x in err]) if err else 'none')
    return (QPixmap.fromImage(QImage(text_img.tobytes(),
                                     tw, th, QImage.Format.Format_RGBA8888)),
            err_msg, w)


def to_pixmap(glyph, zf):
    zoomed = zoom(glyph, zf)
    h, w = zoomed.shape
    return QPixmap.fromImage(
        QImage(color_map[zoomed].tobytes(), w, h,
               QImage.Format.Format_RGBA8888))


def to_editor_pixmap(glyph, width, vert_guide, horz_guide):
    arr = np.zeros((12*9+1, 16*9+1), np.uint8)
    arr[:12*9, :16*9] = zoom(glyph, 9)
    arr[:, [i for i in range(0, 16*9+1, 9)]] = 2  # red cell divide vert
    arr[[i for i in range(0, 12*9+1, 9)], :] = 2  # red cell divide horz
    arr[:, [i*9 for i in vert_guide]] = 4  # green guide vert
    arr[[i*9 for i in horz_guide], :] = 4  # green guide horz
    arr[:, [0, width*9]] = 3  # blue boundary vert
    return QPixmap.fromImage(
        QImage(editor_color[zoom(arr, 2)].tobytes(), (16*9+1)*2, (12*9+1)*2,
               QImage.Format.Format_RGBA8888))


def get_glyph_preview_pixmap(glyph):
    x4 = zoom(glyph, 4)
    x2 = zoom(glyph, 2)
    arr = np.zeros((12*4, 16*6), np.uint8)
    arr[:, : 16*4] = x4
    arr[: 12*2, 16*4:] = x2
    arr[12*2: 12*3, 16*4: 16*5] = glyph
    img = color_map[arr]
    return QPixmap.fromImage(
        QImage(img.tobytes(), 16*6, 12*4, QImage.Format.Format_RGBA8888))


@dataclass
class Glyph:
    index_ascii: int
    index_font: int
    data: np.ndarray
    width: int


class EditorScene(QGraphicsScene):
    KM = Qt.KeyboardModifier
    glyph_changed = pyqtSignal()
    request_width_change = pyqtSignal(bool)
    request_glyph_change = pyqtSignal(bool)
    request_apply_change = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.item = QGraphicsPixmapItem()
        self.addItem(self.item)
        self.request_map = {
            int(Qt.Key.Key_Up): (self.request_glyph_change, True),
            int(Qt.Key.Key_Down): (self.request_glyph_change, False),
            int(Qt.Key.Key_Left): (self.request_width_change, False),
            int(Qt.Key.Key_Right): (self.request_width_change, True),
            int(Qt.Key.Key_S): (self.request_apply_change, True),
            int(Qt.Key.Key_P): (self.request_apply_change, False),
        }
        self.call_map = {
            int(Qt.Key.Key_Up): (self.shift, (0, -1)),
            int(Qt.Key.Key_Down): (self.shift, (0, 1)),
            int(Qt.Key.Key_Left): (self.shift, (-1, 0)),
            int(Qt.Key.Key_Right): (self.shift, (1, 0)),
            int(Qt.Key.Key_Z): (self.undo, None),
            int(Qt.Key.Key_Y): (self.redo, None),
            int(Qt.Key.Key_N): (self.new, None),
        }
        self.glyph_changed.connect(self.update_pixmap)

        self.glyph: Glyph | None = None
        self.draw = False
        self.line_draw = set()
        self.undo_list = deque(maxlen=32)
        self.redo_list = deque(maxlen=32)
        self.v_guide = set()
        self.h_guide = set()

    def reset(self):
        self.glyph: Glyph | None = None
        self.draw = False
        self.line_draw = set()
        self.undo_list = deque(maxlen=32)
        self.redo_list = deque(maxlen=32)
        self.item.setPixmap(QPixmap())

    def set_glyph(self, glyph: Glyph):
        self.glyph = glyph
        self.glyph_changed.emit()

    def set_guide(self, guide: tuple[set, set]):
        self.v_guide = guide[0]
        self.h_guide = guide[1]
        self.glyph_changed.emit()

    def set_width(self, width: int):
        if self.glyph is None:
            return
        self.glyph.width = width
        self.glyph_changed.emit()

    def update_pixmap(self):
        if self.glyph is None:
            self.item.setPixmap(QPixmap())
        else:
            self.item.setPixmap(
                to_editor_pixmap(self.glyph.data, self.glyph.width,
                                 self.v_guide, self.h_guide))
    def shift(self, dx, dy):
        max_y, max_x = self.glyph.data.shape
        arr  = np.zeros((max_y, max_x), np.uint8)
        indices = [dx, max_x + dx, dy, max_y + dy,
                   0 - dx, max_x - dx, 0 - dy, max_y - dy]
        for i, v in enumerate(indices):
            if v < 0:
                indices[i] = 0
            if i in [2, 3, 6, 7] and v > max_y:
                indices[i] = max_y
            if i in [0, 1, 4, 5] and v > max_x:
                indices[i] = max_x
        data = self.glyph.data[indices[6]: indices[7],
                               indices[4]: indices[5]]
        arr[indices[2]: indices[3], indices[0]: indices[1]] = data
        line = {tuple(reversed(pair))
                for pair in np.stack(self.glyph.data.nonzero(),
                                     axis=-1).tolist()}
        self.undo_list.append(line)
        self.redo_list.clear()
        self.glyph.data = arr
        self.glyph_changed.emit()

    def undo(self):
        if self.glyph is None:
            return
        if not self.undo_list:
            return
        line = self.undo_list.pop()
        self.redo_list.append(line)
        for x, y in line:
            self.glyph.data[y, x] = self.glyph.data[y, x] ^ 1
        self.glyph_changed.emit()

    def redo(self):
        if self.glyph is None:
            return
        if not self.redo_list:
            return
        line = self.redo_list.pop()
        self.undo_list.append(line)
        for x, y in line:
            self.glyph.data[y, x] = self.glyph.data[y, x] ^ 1
        self.glyph_changed.emit()

    def new(self):
        if self.glyph is None:
            return
        line = {tuple(reversed(pair))
                for pair in np.stack(self.glyph.data.nonzero(),
                                     axis=-1).tolist()}
        self.undo_list.append(line)
        self.redo_list.clear()
        self.glyph.data.fill(0)
        self.glyph_changed.emit()

    def mousePressEvent(self, event):
        if event is not None and self.glyph is not None:
            point = self.item.mapFromScene(event.scenePos())
            x = int(point.x()) // (9*2)
            y = int(point.y()) // (9*2)
            if 0 <= x <= 15 and 0 <= y <= 11:
                self.draw = True
                self.line_draw.add((x, y))
                self.glyph.data[y, x] = self.glyph.data[y, x] ^ 1
                self.glyph_changed.emit()
        event.accept()

    def mouseMoveEvent(self, event):
        if event is not None and self.glyph is not None and self.draw:
            point = self.item.mapFromScene(event.scenePos())
            x = int(point.x()) // (9*2)
            y = int(point.y()) // (9*2)
            if 0 <= x <= 15 and 0 <= y <= 11:
                if (x, y) not in self.line_draw:
                    self.line_draw.add((x, y))
                    self.glyph.data[y, x] = self.glyph.data[y, x] ^ 1
                    self.glyph_changed.emit()
        event.accept()

    def mouseReleaseEvent(self, event):
        self.draw = False
        if event is not None and self.glyph is not None:
            point = self.item.mapFromScene(event.scenePos())
            x = int(point.x()) // (9*2)
            y = int(point.y()) // (9*2)
            if 0 <= x <= 15 and 0 <= y <= 11:
                if (x, y) not in self.line_draw:
                    self.line_draw.add((x, y))
                    self.glyph.data[y, x] = self.glyph.data[y, x] ^ 1
                    self.glyph_changed.emit()
        self.undo_list.append(self.line_draw)
        self.redo_list.clear()
        self.line_draw = set()
        event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if (event.modifiers() & EditorScene.KM.ControlModifier):  # type: ignore
            if key in [Qt.Key.Key_Z, Qt.Key.Key_Y, Qt.Key.Key_N]:
                call, value = self.call_map[key]
                if value is None:
                    call()
                else:
                    call(*value)
                return event.accept()
            if key in [Qt.Key.Key_S, Qt.Key.Key_P,
                       Qt.Key.Key_Up, Qt.Key.Key_Down,
                       Qt.Key.Key_Left, Qt.Key.Key_Right]:
                signal, value = self.request_map[key]
                signal.emit(value)
        elif key in [Qt.Key.Key_Up, Qt.Key.Key_Down,
                     Qt.Key.Key_Left, Qt.Key.Key_Right]:
            call, value = self.call_map[key]
            if value is None:
                call()
            else:
                call(*value)
        return super().keyPressEvent(event)


class FontEditor(QWidget):
    class Mode(Enum):
        ALL = 0
        ASCII_ONLY = 1

    class SearchBy(Enum):
        CHAR = 0
        INDEX = 1

    glyph_update = pyqtSignal()
    reset_selected_glyph = pyqtSignal()
    guide_update = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_FontEditor()
        self.ui.setupUi(self)
        self.ui.line_preview.setText(test)
        #
        self.mode = FontEditor.Mode.ASCII_ONLY
        self.search = FontEditor.SearchBy.INDEX
        self.ui.spin_index.setMaximum(0x7e)
        self.ui.spin_index.setMinimum(0x20)
        self.ui.spin_index.setValue(0x20)
        #
        self.sc_glyph_preview = QGraphicsScene()
        self.pi_glyph_preview = QGraphicsPixmapItem()
        self.sc_glyph_preview.addItem(self.pi_glyph_preview)
        self.sc_text_preview = QGraphicsScene()
        self.pi_text_preview = QGraphicsPixmapItem()
        self.sc_text_preview.addItem(self.pi_text_preview)
        self.ui.gv_glyph_preview.setScene(self.sc_glyph_preview)
        self.ui.gv_text_preview.setScene(self.sc_text_preview)
        self.sc_editor = EditorScene()
        self.ui.gv_editor.setScene(self.sc_editor)
        self.ui.gv_editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        #
        self.s_glyph: Glyph | None = None  # selected glyph
        self.e_glyph: Glyph | None = None  # editing glyph
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)
        self.timer.setInterval(5000)
        #
        self.ui.checkBox.toggled.connect(self.mode_change)
        self.ui.btn_edit.clicked.connect(self.edit)
        self.ui.btn_save_glyph.clicked.connect(self.replace_glyph)
        self.ui.btn_save_font.clicked.connect(self.save_font)
        self.ui.btn_preview.clicked.connect(self.update_preview_glyph)
        self.ui.line_preview.returnPressed.connect(self.update_preview_text)
        self.ui.line_char_search.returnPressed.connect(self.show_glyph_c)
        self.ui.line_guide.returnPressed.connect(self.set_guide)
        self.ui.line_guide.setText('h2, h6, h10, 0xff20be20')
        self.ui.spin_index.valueChanged.connect(self.show_glyph_i)
        self.ui.spin_width.valueChanged.connect(self.sc_editor.set_width)
        self.ui.spin_width.setButtonSymbols(
            QSpinBox.ButtonSymbols.PlusMinus)  # not work
        self.ui.spin_zoom.valueChanged.connect(self.update_preview_text)
        self.sc_editor.glyph_changed.connect(self.update_label_glyph)
        self.sc_editor.request_glyph_change.connect(self.handle_request_glyph)
        self.sc_editor.request_width_change.connect(self.handle_request_width)
        self.sc_editor.request_apply_change.connect(self.handle_request_apply_change)
        self.glyph_update.connect(self.update_preview_text)
        self.glyph_update.connect(self.update_preview_glyph)
        self.reset_selected_glyph.connect(self.sc_editor.reset)
        self.reset_selected_glyph.connect(self.reset_glyph_preview)
        self.reset_selected_glyph.connect(self.update_label_glyph)
        self.guide_update.connect(self.sc_editor.set_guide)

    def handle_request_apply_change(self, save: bool):
        if save:
            self.replace_glyph()
        else:
            self.update_preview_glyph()

    def handle_request_glyph(self, increase: bool):
        i = (self.ui.spin_index.value() + 1
             if increase else self.ui.spin_index.value() - 1)
        if self.ui.spin_index.minimum() <= i <= self.ui.spin_index.maximum():
            self.ui.spin_index.setValue(i)
        self.edit()

    def handle_request_width(self, increase: bool):
        i = (self.ui.spin_width.value() + 1
             if increase else self.ui.spin_width.value() - 1)
        if self.ui.spin_width.minimum() <= i <= self.ui.spin_width.maximum():
            self.ui.spin_width.setValue(i)

    def set_guide(self):
        v_guide = set()
        h_guide = set()
        color = None
        for value in self.ui.line_guide.text().split(','):
            try:
                if 'v' in value:
                    col = int(value.split('v')[1])
                    if 0 <= col <= 16:
                        v_guide.add(col)
                elif 'h' in value:
                    row = int(value.split('h')[1])
                    if 0 <= row <= 12:
                        h_guide.add(row)
                elif '0x' in value:
                    color = int(value, base=16)
            except (ValueError, IndexError):
                pass

        if color is not None:
            global editor_color
            editor_color = np.array(
                [white, black, red, blue, color], np.uint32)
        self.guide_update.emit((v_guide, h_guide))

    def mode_change(self, checked: bool):
        if checked:
            self.ui.spin_index.setMaximum(0x7f)
            self.ui.spin_index.setMinimum(0x20)
            orig = self.ui.spin_index.blockSignals(True)
            self.ui.spin_index.setValue(0x20)
            self.ui.spin_index.blockSignals(orig)
            self.mode = FontEditor.Mode.ASCII_ONLY
        else:
            self.ui.spin_index.setMaximum(len(glyphs)-1)
            self.ui.spin_index.setMinimum(0)
            orig = self.ui.spin_index.blockSignals(True)
            self.ui.spin_index.setValue(0)
            self.ui.spin_index.blockSignals(orig)
            self.mode = FontEditor.Mode.ALL
        self.reset_selected_glyph.emit()

    def edit(self):
        if self.s_glyph is None:
            self.ui.label_preview_msg.setText(
                '<b>Must select glyph first!</b>')
            return
        self.e_glyph = Glyph(self.s_glyph.index_ascii,
                             self.s_glyph.index_font,
                             np.copy(self.s_glyph.data),
                             self.s_glyph.width)
        self.sc_editor.set_glyph(self.e_glyph)
        self.ui.gv_editor.setFocus()
        orig = self.ui.spin_width.blockSignals(True)
        self.ui.spin_width.setValue(self.e_glyph.width)
        self.ui.spin_width.blockSignals(orig)
        self.update_label_glyph()

    def update_label_glyph(self):
        if self.e_glyph is not None:
            self.ui.label_glyph.setPixmap(
                to_pixmap(
                    self.e_glyph.data[:, :self.e_glyph.width], 3))
            self.ui.label_glyph.setAlignment(
                Qt.AlignmentFlag.AlignHCenter
                | Qt.AlignmentFlag.AlignVCenter)  # type: ignore
            self.ui.label_glyph_w.setText(str(self.e_glyph.width))
        else:
            self.ui.label_glyph.setPixmap(QPixmap())
            self.ui.label_glyph_w.setText('')

    def replace_glyph(self):
        if self.e_glyph is None:
            return
        if self.e_glyph.index_ascii >= 0:
            w = ascii_width[self.e_glyph.index_ascii]
            if w != self.e_glyph.width:
                ascii_width[self.e_glyph.index_ascii] = self.e_glyph.width
        g = glyphs[self.e_glyph.index_font]
        if not np.array_equal(g, self.e_glyph.data):
            new_g = np.copy(self.e_glyph.data)
            glyphs[self.e_glyph.index_font] = new_g
        self.ui.label_save.setText(
            f'Font glyph with index {self.e_glyph.index_font} saved.')
        self.timer.start()
        self.glyph_update.emit()

    def save_font(self):
        data = [font_data[:0x1c], ]
        for i in range(0, len(glyphs)):
            data.append(np.packbits(glyphs[i].flatten()).tobytes())
        data.append(font_data[0x1c + (len(font_data) - 0x1c)//24 * 24:])

        with open(os.path.join(folder, 'font.bit'), 'wb') as f:
            f.write(b''.join(data))

        with open(os.path.join(folder, 'ascii_width.bin'), 'wb') as f:
            f.write(np.array(ascii_width, np.uint8).tobytes())

        self.ui.label_save.setText('Change have been saved to: '
                                   '"font.bit", "ascii_width.bin"')
        self.timer.start()

    def timeout(self):
        self.ui.label_save.setText('')
        self.timer.stop()

    def random_text_preview(self):
        if random.randint(0,1):
            txt = watanare
        else:
            txt = ''.join(random.sample(test, len(test)))
        self.ui.line_preview.setText(txt)
        self.update_preview_text()

    def update_preview_text(self):
        txt = self.ui.line_preview.text()
        if not txt:
            return
        pixmap, err, w = unicode_text_to_pixmap(txt, self.ui.spin_zoom.value())
        self.pi_text_preview.setPixmap(pixmap)
        self.sc_text_preview.setSceneRect(
            self.sc_text_preview.itemsBoundingRect())
        self.ui.label_msg.setText(f'Width: {w}; {err}')

    def reset_glyph_preview(self):
        self.ui.label_preview_msg.setText('')
        self.pi_glyph_preview.setPixmap(QPixmap())

    def show_glyph_c(self):
        self.search = FontEditor.SearchBy.CHAR
        self.s_glyph = None
        self.e_glyph = None
        self.reset_selected_glyph.emit()
        txt = self.ui.line_char_search.text()
        if not txt:
            return
        self.ui.label_preview_msg.setText(unicodedata.name(txt[0], ''))
        try:
            code_point = txt[0].encode('sjis')
        except UnicodeEncodeError:
            self.ui.label_preview_msg.setText(f"Invalid character: '{txt[0]}'")
            return
        if self.mode is FontEditor.Mode.ALL:
            self.show_glyph_c_view_all(code_point)
        else:
            self.show_glyph_c_ascii(code_point)

    def show_glyph_c_ascii(self, code_point):
        try:
            idx_a = code_point[0]
            orig = self.ui.spin_index.blockSignals(True)
            self.ui.spin_index.setValue(idx_a)
            self.ui.spin_index.blockSignals(orig)
            idx_f = ascii_lut[idx_a] - 1
            g = glyphs[idx_f]
            w = ascii_width[idx_a]
            self.s_glyph = Glyph(idx_a, idx_f, g, w)
            p = get_glyph_preview_pixmap(g)
            self.pi_glyph_preview.setPixmap(p)
        except (ValueError, IndexError):
            self.ui.label_preview_msg.setText('Invalid code point')

    def show_glyph_c_view_all(self, code_point):
        try:
            if len(code_point) == 1:
                idx_a = code_point[0]
                idx_f = ascii_lut[idx_a] - 1
                if idx_f == 0:
                    return self.ui.label_preview_msg.setText(
                        f"Code point with no glyph")
            else:
                idx_a = -1
                idx_f = cacl_sjis_2b_index(code_point) - 1
            orig = self.ui.spin_index.blockSignals(True)
            self.ui.spin_index.setValue(idx_f)
            self.ui.spin_index.blockSignals(orig)
            g, w = sjis_to_glyph(code_point)
            self.s_glyph = Glyph(idx_a, idx_f, g, w)
            p = get_glyph_preview_pixmap(g)
            self.pi_glyph_preview.setPixmap(p)
        except (ValueError, IndexError):
            self.ui.label_preview_msg.setText(f"Invalid code point")

    def show_glyph_i(self, value: int):
        self.search = FontEditor.SearchBy.INDEX
        self.s_glyph = None
        self.e_glyph = None
        self.reset_selected_glyph.emit()
        if self.mode is FontEditor.Mode.ALL:
            self.show_glyph_i_view_all(value)
        else:
            self.show_glyph_i_ascii(value)

    def show_glyph_i_view_all(self, value: int):
        p = get_glyph_preview_pixmap(glyphs[value])
        self.pi_glyph_preview.setPixmap(p)
        self.s_glyph = Glyph(-1, value, glyphs[value], 12)
        try:
            cp = font_index_to_sjis(value)
            u_char = cp.decode('sjis')
            self.ui.label_preview_msg.setText(unicodedata.name(u_char, ''))
        except UnicodeDecodeError:
            self.ui.label_preview_msg.setText(
                'Glyph with no unicode code point')

    def show_glyph_i_ascii(self, value: int):
        idx = ascii_lut[value]
        if idx == 0:
            return
        g = glyphs[idx - 1]
        w = ascii_width[value]
        self.s_glyph = Glyph(value, idx - 1, g, w)
        p = get_glyph_preview_pixmap(g)
        self.pi_glyph_preview.setPixmap(p)

        try:
            cp = int.to_bytes(value, 1, 'little')
            u_char = cp.decode('ascii')
            self.ui.label_preview_msg.setText(unicodedata.name(u_char, ''))
        except UnicodeDecodeError:
            self.ui.label_preview_msg.setText(
                'Glyph with no unicode code point')
            return

    def update_preview_glyph(self):
        if self.e_glyph is None:
            return
        else:
            p = get_glyph_preview_pixmap(self.e_glyph.data)
            self.pi_glyph_preview.setPixmap(p)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # type: ignore
        if (event.modifiers()
                & Qt.KeyboardModifier.ControlModifier):  # type: ignore
            if event.key() in [
                    Qt.Key.Key_E, Qt.Key.Key_Enter,  Qt.Key.Key_Return]:
                self.edit()
                return event.accept()
            elif event.key() == Qt.Key.Key_W:
                self.save_font()
                return event.accept()
            elif event.key() == Qt.Key.Key_R:
                self.random_text_preview()
                return event.accept()
        return super().keyPressEvent(event)


class FontDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.counter = 0
        self.pi = QGraphicsPixmapItem()
        self.sc = QGraphicsScene()
        self.sc.addItem(self.pi)
        self.gv = QGraphicsView()
        self.gv.setScene(self.sc)
        self.btn = QPushButton('Start')
        self.btn.clicked.connect(self.start)
        self.btn_view = QPushButton('View')
        self.btn_view.clicked.connect(self.view)
        self.line_view = QLineEdit()
        layout_view = QHBoxLayout()
        layout_view.addWidget(self.line_view)
        layout_view.addWidget(self.btn_view)
        layout = QVBoxLayout()
        layout.addWidget(self.btn)
        layout.addWidget(self.gv)
        layout.addLayout(layout_view)
        self.setLayout(layout)
        self.resize(240, 240)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)
        self.timer.setInterval(500)
        invalid_pixmap = to_pixmap(invalid_glyph, 8)
        self.pi.setPixmap(invalid_pixmap)

    def view(self):
        try:
            one_idx = int(self.line_view.text())
            if one_idx > len(glyphs):
                one_idx = len(glyphs)
            if one_idx < 1:
                one_idx = 1
        except ValueError:
            one_idx = 1
        self.pi.setPixmap(to_pixmap(glyphs[one_idx - 1], 8))

    def start(self):
        self.counter = 0
        self.timer.start()

    def timeout(self):
        self.counter += 1
        if self.counter >= len(glyphs):
            self.timer.stop()
            return
        self.pi.setPixmap(to_pixmap(glyphs[self.counter], 8))


if __name__ == '__main__':
    app = QApplication([])
    view = FontEditor()
    view.show()
    app.exec()
