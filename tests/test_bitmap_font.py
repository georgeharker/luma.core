#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:module:`luma.core.bitmap_font` module.
"""

import os
from pathlib import Path

import cbor2
import pytest
from PIL import Image, ImageDraw
from luma.core import bitmap_font
from luma.core.bitmap_font import embedded_fonts

from helpers import get_reference_pillow_font, get_reference_file


FONTDATA = {
    'metrics': [
        # A00 ENGLISH_JAPANESE 5x8 METRICS
        {
            'name': 'A00',
            'index': range(16, 256),
            'xwidth': 5,
            'cell_size': (5, 10),
            'glyph_size': (5, 8),
            'table_size': (800, 20)
        },
        # A02 ENGLISH_EUROPEAN 5x8 METRICS
        {
            'name': 'A02',
            'index': range(16, 256),
            'xwidth': 5,
            'cell_size': (5, 10),
            'glyph_size': (5, 8),
            'table_size': (800, 20)
        }
    ],
    'mappings': [
        {
            0x00a5:   0x5c,  # ¥ YEN SIGN
            0x2192:   0x7e,  # → RIGHTWARDS ARROW
            0x2190:   0x7f,  # ← LEFTWARDS ARROW
            0x300c:   0xa2,  # 「 LEFT CORNER BRACKET
            0x300d:   0xa3,  # 」 RIGHT CORNER BRACKET
            0x30a1:   0xa7,  # ァ KATAKANA LETTER SMALL A
            0x30a3:   0xa8,  # ィ KATAKANA LETTER SMALL I
            0x30a5:   0xa9,  # ゥ KATAKANA LETTER SMALL U
            0x30a7:   0xaa,  # ェ KATAKANA LETTER SMALL E
            0x30a9:   0xab,  # ォ KATAKANA LETTER SMALL O
            0x30e3:   0xac,  # ャ KATAKANA LETTER SMALL YA
            0x30e5:   0xad,  # ュ KATAKANA LETTER SMALL YU
            0x30e7:   0xae,  # ョ KATAKANA LETTER SMALL YO
            0x30c3:   0xaf,  # ッ KATAKANA LETTER SMALL TU
            0x00f7:   0xfd,  # ÷ DIVISION SIGN
            0x25ae:   0xff,  # ▮ BLACK VERTICAL RECTANGLE
        },
        {   # A02 ENGLISH_EUROPEAN CHARACTER FONT
            # Contains no 5x10 fonts
            0x25b6:   0x10,  # ▶ BLACK RIGHT-POINTING TRIANGLE
            0x25c0:   0x11,  # ◀ BLACK LEFT-POINTING TRIANGLE
            0x201c:   0x12,  # “ LEFT DOUBLE QUOTATION MARK
            0x201d:   0x13,  # ” RIGHT DOUBLE QUOTATION MARK
            0x23eb:   0x14,  # ⏫ BLACK UP-POINTING DOUBLE TRIANGLE
            0x23ec:   0x15,  # ⏬ BLACK DOWN-POINTING DOUBLE TRIANGLE
            0x25cf:   0x16,  # ● BLACK CIRCLE
            0x00bc:   0xbc,  # ¼ VULGAR FRACTION ONE QUARTER
            0x00bd:   0xbd,  # ½ VULGAR FRACTION ONE HALF
            0x00be:   0xbe,  # ¾ VULGAR FRACTION THREE QUARTERS
            0x00bf:   0xbf,  # ¿ INVERTED QUESTION MARK
            0x00c0:   0xc0,  # À LATIN CAPITAL LETTER A WITH GRAVE
            0x00c1:   0xc1,  # Á LATIN CAPITAL LETTER A WITH ACUTE
            0x00c2:   0xc2,  # Â LATIN CAPITAL LETTER A WITH CIRCUMFLEX
            0x00c3:   0xc3,  # Ã LATIN CAPITAL LETTER A WITH TILDE
            0x00c4:   0xc4,  # Ä LATIN CAPITAL LETTER A WITH DIAERESIS
            0x00c5:   0xc5,  # Å LATIN CAPITAL LETTER A WITH RING ABOVE
            0x00c6:   0xc6,  # Æ LATIN CAPITAL LETTER AE
            0x0393:   0x92,  # Γ GREEK CAPITAL LETTER GAMMA
            0x0413:   0x92,  # Г CYRILLIC CAPITAL LETTER GHE
        }
    ],
    'fonts': [
        # A00 ENGLISH_JAPANESE CHARACTER FONT
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x14\xa2a\x8c\x12\x00\x00\x00\x00q\x1d\xf1|\xdfs\x80\x01\x01\x0es\xbc\xee\x7f\xee\x8b\x8f\x18F.\xf3\xbc\xff\xc61\x8c\x7f\xc8\xb8\x80@ \x00\x80\xc0\x81\x05\x06\x00\x00\x00\x00\x04\x00\x00\x00\x00" \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x14\xa7\xe6D!\x08@\x00\x01\x8b"#A\x11\x8cX\xc2\x00\x91\x8cc\x19B\x11\x89\x05(n1\x8cc\x02F1\x8cC\x05\t@  \x00\x81/\x80\x01\x02\x00\x00\x00\x00\x04\x00\x00\x00\x00B\x10\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x03\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x15\xfa\n\x88@\xaa@\x00\x02\x99\x02Ez\x01\x8cX\xc4|A\x0cc\x08\xc2\x10\x89\x05HW1\x8cc\x02F1TE\x0f\x8a \x13\xac\xe6\xb9\x11\xb3\r"j\xce\xf3l\xeeF1\x8c~B\x10H\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00?\x11>$\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\xa7\x11\x00@\x9d\xf0|\x04\xa9\x04)\x07\xc2s\xc0\x08\x00"l}\x08\xfb\xd7\xf9\x05\x88V\xb1\xf4|\xe2F5"\x89\x02\x08\x00\x00s\t\xc7\x91\xc9\x05BW1\x8c\xf3\x04F5TD\x82\x0b\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08@3\xe1\'\xc9\xff\xb8U\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xf2\xa2\xa0@\xaaF\x00\x08\xc9\x08\x1f\x86$\x88X\xc4|D\xaf\xe3\x08\xc2\x11\x89\x05HFq\x85h\x12F5Q\x11\x0f\x88\x00\x03\xe3\x08\xfd\x0f\x89\x05\x82V1\xf3\xe0\xe4F5#\xc8B\x10H\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00H0&dHd\x8b\xd5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xafN@!\x08B\x01\x90\x89\x11\x11F$\x88\x98B\x00\x80\xacc\x19B\x11\x89%(F1\x84\xa4\x12EU\x89!\x02\x08\x00\x04c\x18\xc1\x01\x89%BF1\x80`\x14\xcdUPPB\x10\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00D\x00D\xa0H\xa5\x08A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\xa2\r\xa0\x12\x00\x04\x01\x80s\xbe\xe19\xc4s\x00\x81\x01\x04t|\xee~\x0f\x8b\x99\x1f\xc6.\x83c\xe28\x8a\x89?\xc28\x1f\x03\xfc\xe7\xb9\x0e\x8b\x99\'F.\x80a\xe34\x8a\x8b\xbe" \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x01\xc2\x00\x88!\xbf$\x7f\xc6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xc2@\t\x04\x02\x00\xa0\x01\x00\x00\x80\xe4\x10\x00 \x81\x00\x00\x80\x00\x00\x04\x00\x0e\x90\x00\x00\x00\x9c\x02\x80\x00\x00\x00\x00\x04\x00!\xca\x00\x00\x00+\xe0\xf8\x00\x00\x00\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00E\xff\xff\xff{\xff\xfc\x7f\xf1\x7f*\x04\x11\xdf\xf8\x89\x0f\xa3\xffq\x03\xf4;\xe0\x91!\xff\xe2T\x00\x00\x00\x00\x00\x00\x81B \x00\x00\x1c\x00\x02\x00\x00\x02\x00\x10\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01I\x12\t$L\x82\xa0\x851I+\xf4|\x01\x10\x85\xf0\xd0\x81\x02\x02\x8f\x88?\x95!\x18\x81\x1cK\x9c\xe8\xbc\xcf>\x8c\x87r\xce\xb3b\x07E\x1f\x8c}\xff\x80\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf9\x99\x12\x19?\x88\x82\xac\x89I\xaf\xeaF\x10\n \xa3\x00\x88\x81t\x15\xf4\x8b\xe1\x95#\x18\x84\x00\xa8c\x08\xd11 \x85J#1\xcc\xfe\xb8\xc4\x8aTH\x8a\xfc\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01(\x12)$\x08\x82 \x91\x01\x19\x02E\x10\x04p\xa3\x00\x86\xaa\x04H\x85\x08!\x15e\x10\x84\x00\x93\xfc\xc8\xca1 \x04\n\xf21\x8ccX\xc5\n$~\xff\x80\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x08"I$\x10\x82A)\x02\x11\x04D \n\xa9#\x01\x06\xa4w\xd4\x84\x08"%i\x11\x08\x00\x94c\x19\xc61\xa0\x04\x07"1\x8cc\xa5F\nTH\x98\x90\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x08O\x8aDa>\x8eD\xecb\x08\x84C\xf0""\xf6\x00\x82\x08`t\x7f\xe4E\xb1\xf2p\x00k\xfc\xee\xbb\xcf@\x04\x02>.\xf3\xdc\r\xcf\xf3\x8b\xc9\x18\x80\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x08\x02\x01\x00\x04\x00\x00\x00\x80@\x004\x00\x00@\x00\x00\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x08\x02\x01\x00$\x00\x00\x00\x80@\x00\x00\x00\x00@\x00\x00\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x08\x02\x0e\x00\x18\x00\x00\x00\x80@\x00\x00\x00\x03\x80\x00\x00\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',

        # A02 WESTERN EUROPEAN CHARACTER FONT
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xc0\x00(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x93\xb2|\x01!\x00\x01 \x00\x01\x14\xa2a\x8c\x12\x00\x00\x00\x00q\x1d\xf1|\xdfs\x80\x01\x01\x0eq<\xee\x7f\xee\x8b\x8f\x18F.\xf3\xbc\xef\xc61\x8c~\xe08\x80@ \x00\x80\xc0\x81\x05\x06\x00\x00\x00\x00\x04\x00\x00\x00\x00" \x04\xf9k\xe8\x91\xff\x8cb\n\xe2.\x01>\x0f\x80\xa0#\x80`\x00\x0e\xd9\x08`D\x86\x17\xdc\t?\xe4a\xa4\x979\xc1q\x08B\x10\x9f\x01\x14\xa7\xe6D!\x08@\x00\x01\x8b"#A\x11\x8cX\xc2\x00\x91\x8a\xa3\x19B\x11\x89\x05(n1\x8cc\x12F1\x8cB\x88\t@  \x00\x81 \x80\x01\x02\x00\x00\x00\x00\x04\x00\x00\x00\x00B\x10\n\x89j\x18\xc4\xb1\x8ccZ\xa21\x01\xa2\x08\x00\xe1t\\\x90(\x11\xd8\x1c\x88\xa8\x89,BZ\xc6(s\xb7/\x93\xe5\xa9\x04\x84\x08\x8e\x01\x15\xfa\n\x88@\xaa@\x00\x02\x99\x02Ez\x01\x8cX\xc4|A\x0cc\x08\xc2\x10\x89\x05HW1\x8cc\x02F1TD\x84\n \x13\xac\xe6\xb9\x0f\xb1\r"j\xce\xf3l\xeeF1\x8c~B\x10\x11\x82j\x19\xc4\xb1\x8ccZ\xa2%Ia\xf4<\xaetbE\xfd\xd1\xd8(\x87|\x84%^\xaa\xc6\xac\x7f\x80\x00\x03\xe9!?\xf2\x11\xce\x01\x00\xa7\x11\x00@\x9d\xf0|\x04\xa9\x04)\x07\xc2s\xc0\x08\x00"l}\x08\xfb\xd7\xf9\x05\x88V\xb1\xf4|\xe2F5"\x88\x82\x08\x00\x00s\t\xc7\x91\xcb\x05BW1\x8c\xf3\x04F1TD\x82\t\xb1\xf4\\j\xcc\xb1T_Z\xbb+\xa9`\xa2H\xb4w\xe2\xaa\xfe\x11\xd9)\xc5\x10\n\xfd\xe3N\xbe s\x80\x02\x7f\xff%D\x81!\xc4\x00\x01\xf2\xa2\xa0@\xaaF\x00\x08\xc9\x08\x1f\x86$\x88X\xc4|D\xaf\xe3\x08\xc2\x11\x89\x05HFq\x85h\x12F5Q\x10\x81\x08\x00\x03\xe3\x08\xfd\x0f\x89\x05\x82V1\xf3\xe0\xe4F5#\xc8B\x12Q\x8f\xea\x1c\xd4\xb1$CZ\xa6\xa1\x91 \xa4K\xa4\xfcc\x1d}\x91\xd9*\x87|\x84%^\xaa\x96`a\x80\x079\xc8#\x88@\x03\xe4\x00\x00\xafN@!\x08B\x01\x90\x89\x11\x11F$\x88\x98B\x00\x80\xacc\x19B\x11\x89%(F1\x84\xa5\x12EU\x89 \x80\x88\x00\x04c\x18\xc1\x01\x89%BV1\x80`\x14\xcdUPPB\x10\x1f\x8cj\x18\xe6\xb1G\xc3_\xa6\xb1\x97 \xa8Kd$U\x10:1\xd9\x1c\x98\x90\x92\xa4@Z\xa6\xa0@\x80\x0f\x90\x04!\x00\x0f\xfc\x00\x01\x00\xa2\r\xa0\x12\x00\x04\x01\x80s\xbe\xe19\xc4s\x00\x81\x01\x04t|\xee~\x0f\x8b\x99\x1f\xc6.\x83b\xe28\x8a\x89>\xe08\x1f\x03\xfc\xe7\xb9\x0e\x8b\x99\'V.\x80a\xe34\x8a\x8b\xbe" \x00\xf4k\xe8\xc51\x80C\xf0\xbb.o!?\xb0b\x03\xb6\xe0\x11\xd1\xd9\t`\x10\x8cG\xfe\tG\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`\x19\xce\x00\x00\x02\x00\x08\xc7\x00@\x88\xd5\x10\x0e@\x88\x04\x08\x80\x03P"5@\x02\x04E\x0b\x00@\x88\xd0\x10\x00@\x88\x04\x08\x80\x03P \x00\x00\x02\x04@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x91$)E\xe0\x06\x1c\tI\x04!\x15 (\xf1!\x14\xa2\x11Jt\x88EH\x00q\x08\xa0\x11\x06!\x15%(\x00!\x14\xa2\x11J\xa4\x88B5@\x11\x08\xa5\t\x8a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x91\x08\xceF`\x02#JS\x00!\x00\x02\x11\x90\x00\x00\x00\x00\x00H\x1c\xe0\x01\xd1$b\x08\xc5\xc9\x00\x00\x00\x13N\x00\x00\x00\x00\x00@\x00\x05H\x04 \x00\x00\x10\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x97\xd0(F`R"\xa5)$R\x9c\xe5:\x90\xff\xff\xf79\xceLc\x17:*tc\x18\xa9)s\x9c\xe78\xb0s\x9c\xe2\x10\x84\xa5\x9c\xe0\x01\xc0tc\x18\xc4\xd1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00a=\xc9M\xec\x8f"[Wh\x8cc\x18\xc6\xf1\x84!\x02\x10\x84\xeec\x18\xc6$\xacc\x18\x91.\x08B\x10\x85\xf1\x8cc\x161\x8c\x16c\x17:?\xacc\x18\xc4\xb1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x0b\xf4l\xa8\x1c\xa5\x04\xb0\xff\xff\xff\xff\x8e\xf7\xbd\xe2\x10\x84Mc\x18\xc6*tc\x18\x91\xc9{\xde\xf7\xbe\x8e\xff\xff\xf2\x10\x84|c\x18\xc6 tc\x18\xbc\xcf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t@`\xa8\x01G\x88\xf1\x8cc\x18\xc6\x82\x84!\x02\x10\x84L\xe3\x18\xc61$c\x18\x91\t\x8cc\x18\xc6\xa4\x84!\x02\x10\x84\x8cc\x18\xc6$$\xe79\x84\x81\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xc0\x01\xc0`P>\x01\x1c.\x8cc\x18\xc6\xe6\xff\xff\xf79\xcet\\\xe79\xc0s\x9c\xe7\x13\x96{\xde\xf7\xbdLs\x9c\xe79\xcet\\\xe79\xc0CZ\xd6\xb9\xce\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    ]
}


def make_sprite_table(fnt):
    """
    Generate a page filled with glyphs from character value 16-255 using the
    provided font

    :param fnt: The font to use to draw the page
    :type fnt: `PIL.ImageFont`
    :return: Image containing the drawn glyphs
    :rtype: `PIL.Image`
    """
    img = Image.new('1', (80, 120), 0)
    drw = ImageDraw.Draw(img)
    for i in range(240):
        drw.text(((i % 16) * 5, (i // 16) * 8), chr(i + 16), font=fnt, fill='white', spacing=0)
    return img


@pytest.fixture()
def bm_font(request):
    """
    Fixture which loads a ``bitmap_font`` persists it to disk
    The fixture removes the file when it is finished.
    """
    filename = get_reference_file(Path('font').joinpath('hd44780a02.pbm'))
    bmf = bitmap_font.load_sprite_table(filename, range(16, 256), 5, (5, 8),
        (5, 8), FONTDATA['mappings'][1])
    bmf.save('test.bmf')

    def tear_down():
        os.remove('test.bmf')
    request.addfinalizer(tear_down)

    return bmf


@pytest.fixture()
def load_all_embedded(request):
    """
    Fixture which loads the two fonts contained within the test FONTDATA information
    """
    fnt_cnt = len(FONTDATA['metrics'])
    bmfs = [None] * fnt_cnt

    for i in range(fnt_cnt):
        m = FONTDATA['metrics'][i]
        sp_data = FONTDATA['fonts'][i]
        mappings = FONTDATA['mappings'][i]
        sprite_table = Image.frombytes('1', m['table_size'], sp_data)
        bmfs[i] = bitmap_font.load_sprite_table(sprite_table, m['index'], m['xwidth'],
            m['glyph_size'], m['cell_size'], mappings)
        sprite_table.close()
    return bmfs


def test_load_from_pillow_font():
    """
    Test the loading of a pillow font from disk by loading the font from bitmap_font
    and PIL.ImageFont, rendering a page of glyphs which each and testing to make
    sure the results are the same.
    """
    fnt = get_reference_pillow_font('hd44780a02.pil')
    filename = get_reference_file(Path('font').joinpath('hd44780a02.pil'))
    bmf = bitmap_font.load_pillow_font(filename)

    img1 = make_sprite_table(fnt)
    img2 = make_sprite_table(bmf)

    assert img1 == img2


def test_load_from_pillow_exceptions():
    """
    Test that exceptions are thrown as appropriate if bitmap_font is asked to
    load a pillow font that is not a PIL.ImageFont file, is damaged or does not
    include the required font metrics data.
    """

    with pytest.raises(SyntaxError) as ex:
        filename = get_reference_file(Path('font').joinpath('hd44780a02.pbm'))
        bitmap_font.load_pillow_font(filename, FONTDATA['mappings'][1])
    assert str(ex.value) == "Not a PIL.ImageFont file"

    with pytest.raises(SyntaxError) as ex:
        filename = get_reference_file(Path('font').joinpath('hd44780a02_nodata.pil'))
        bitmap_font.load_pillow_font(filename, FONTDATA['mappings'][1])
    assert str(ex.value) == "PIL.ImageFont file missing metric data"

    with pytest.raises(SyntaxError) as ex:
        filename = get_reference_file(Path('font').joinpath('hd44780a02_incomplete.pil'))
        bitmap_font.load_pillow_font(filename, FONTDATA['mappings'][1])
    assert str(ex.value) == "PIL.ImageFont file metric data incomplete"

    filename = get_reference_file(Path('font').joinpath('wrong_mode.pil'))
    with pytest.raises(OSError) as ex:
        bitmap_font.load_pillow_font(filename)
    assert str(ex.value) == 'cannot find glyph data file'


def test_mapping():
    """
    Test to make sure that values that have unicode mappings work correctly
    """
    fnt = get_reference_pillow_font('hd44780a02.pil')
    filename = get_reference_file(Path('font').joinpath('hd44780a02.pil'))
    bmf = bitmap_font.load_pillow_font(filename, FONTDATA['mappings'][1])

    size = bmf.getsize('\u0010')
    img1 = Image.new('1', size, 0)
    img2 = Image.new('1', (5, 8), 0)

    drw = ImageDraw.Draw(img1)
    drw.text((0, 0), '\u0010', font=fnt, fill='white')
    drw = ImageDraw.Draw(img2)
    drw.text((0, 0), '\u25b6', font=bmf, fill='white')

    assert img1 == img2


def test_load_sprite_table():
    """
    Test loading a font from a sprite_table
    """
    fnt = get_reference_pillow_font('hd44780a02.pil')
    filename = get_reference_file(Path('font').joinpath('hd44780a02.pbm'))
    bmf = bitmap_font.load_sprite_table(filename, range(16, 256), 5, (5, 8), (5, 8), FONTDATA['mappings'][1])

    img1 = make_sprite_table(fnt)
    img2 = make_sprite_table(bmf)

    assert img1 == img2


def test_load_sprite_table_exceptions_1():
    """
    Test that exceptions are thrown as appropriate if bitmap_font is asked to
    load from a sprite table from a filename that does not exist, is not a
    PIL.Image file, or is damaged.
    """
    with pytest.raises(FileNotFoundError) as ex:
        filename = 'badfile'
        bitmap_font.load_sprite_table(filename, range(16, 256), 5, (5, 8), (5, 8), FONTDATA['mappings'][1])
    assert str(ex.value) == '[Errno 2] No such file or directory: \'{0}\''.format(filename)


def test_load_sprite_table_exceptions_2():
    """
    Test that exceptions are thrown as appropriate if bitmap_font is asked to
    load from a sprite table from a filename that does not exist, is not a
    PIL.Image file, or is damaged.
    """
    with pytest.raises(ValueError) as ex:
        filename = get_reference_file(Path('font').joinpath('hd44780a02.pil'))
        bitmap_font.load_sprite_table(filename, range(16, 256), 5, (5, 8), (5, 8), FONTDATA['mappings'][1])
    assert str(ex.value) == 'File {0} not a valid sprite table'.format(filename)

    with pytest.raises(ValueError) as ex:
        bitmap_font.load_sprite_table(1, range(16, 256), 5, (5, 8), (5, 8), FONTDATA['mappings'][1])
    assert str(ex.value) == 'Provided image is not an instance of PIL.Image'


def test_dumps_loads_saves_load(bm_font):
    """
    Test which verifies the loading and restoring of bitmap_fonts
    """
    bmf = bm_font

    data = bmf.dumps()
    bmf2 = bitmap_font.loads(data)
    bmf3 = bitmap_font.load('test.bmf')

    img1 = make_sprite_table(bmf)
    img2 = make_sprite_table(bmf2)
    img3 = make_sprite_table(bmf3)

    assert img1 == img2
    assert img1 == img3

    with pytest.raises(SyntaxError) as ex:
        filename = get_reference_file(Path('font').joinpath('hd44780a02.pil'))
        bitmap_font.load(filename)
    assert str(ex.value) == 'Not a luma.core.bitmap_font file'


def test_loads_exception():
    """
    Exception is thrown when attempting to load font data that is incomplete.
    """
    data = cbor2.dumps({'xwidth': 5, 'glyph_size': (5, 8)})
    with pytest.raises(Exception) as ex:
        bitmap_font.loads(data)
    assert str(ex.value) == 'Cannot parse fontdata. It is invalid.'


def test_combine(load_all_embedded):
    """
    Fonts can be combined successfully.
    """
    bmfs = load_all_embedded

    # Demonstrate that \u25b6 and \u25c0 are not in bmfs[0]
    img = Image.new('1', (10, 8), 0)
    drw = ImageDraw.Draw(img)
    drw.text(((0, 0)), '\u00a5\u25b6', font=bmfs[0], fill='white', spacing=0)
    assert sum(img.crop((5, 0, 9, 7)).tobytes()) == 0
    drw.text(((0, 0)), '\u00a5\u25c0', font=bmfs[0], fill='white', spacing=0)
    assert sum(img.crop((5, 0, 9, 7)).tobytes()) == 0

    # Combine a couple of characters (one new, one conflicting)
    bmfs[0].combine(bmfs[1], '\u25b6\U000f8041')
    img1 = Image.new('1', (10, 8), 0)
    drw = ImageDraw.Draw(img1)
    drw.text(((0, 0)), '\u00a5\u25b6', font=bmfs[0], fill='white', spacing=0)

    img2 = Image.new('1', (10, 8), 0)
    drw = ImageDraw.Draw(img2)
    drw.text(((0, 0)), '\u00a5', font=bmfs[0], fill='white', spacing=0)
    drw.text(((5, 0)), '\u25b6', font=bmfs[1], fill='white', spacing=0)

    assert img1 == img2

    img2 = Image.new('1', (10, 8), 0)
    drw = ImageDraw.Draw(img2)
    drw.text(((0, 0)), '\u00a5', font=bmfs[1], fill='white', spacing=0)
    drw.text(((5, 0)), '\u25b6', font=bmfs[0], fill='white', spacing=0)

    assert img1 != img2

    # Combine entire font
    bmfs[0].combine(bmfs[1])
    img1 = Image.new('1', (10, 8), 0)
    drw = ImageDraw.Draw(img1)
    drw.text(((0, 0)), '\u00a5\u25c0', font=bmfs[0], fill='white', spacing=0)

    img2 = Image.new('1', (10, 8), 0)
    drw = ImageDraw.Draw(img2)
    drw.text(((0, 0)), '\u00a5', font=bmfs[0], fill='white', spacing=0)
    drw.text(((5, 0)), '\u25c0', font=bmfs[1], fill='white', spacing=0)

    assert img1 == img2

    with pytest.raises(ValueError) as ex:
        c = '\u0000'
        bmfs[0].combine(bmfs[1], c)
    assert str(ex.value) == '{0} is not a valid character within the source font'.format(c)


def test_embedded_font(load_all_embedded):
    """
    Tests the embedded_fonts class.  Loads FONTDATA.  Changes current font
    by name and number.  Combines two fonts and verifies that combined
    characters get rendered correctly.
    """
    bmfs = load_all_embedded
    ebf = embedded_fonts(FONTDATA)

    assert ebf.current == ebf.font_by_number[0]
    ebf.current = 'A02'
    assert ebf.current == ebf.font_by_number[1]
    a02fnt = ebf.current
    ebf.current = 0
    assert ebf.current == ebf.font_by_number[0]

    ebf.combine(a02fnt)

    img1 = Image.new('1', (10, 8), 0)
    drw = ImageDraw.Draw(img1)
    drw.text(((0, 0)), '\u00a5\u25c0', font=ebf, fill='white', spacing=0)

    img2 = Image.new('1', (10, 8), 0)
    drw = ImageDraw.Draw(img2)
    drw.text(((0, 0)), '\u00a5', font=bmfs[0], fill='white', spacing=0)
    drw.text(((5, 0)), '\u25c0', font=bmfs[1], fill='white', spacing=0)

    assert img1 == img2


def test_embedded_font_exceptions():
    """
    Tests exceptions when attempting to select a font that does not exist
    within the ``embedded_fonts`` object
    """
    ebf = embedded_fonts(FONTDATA)

    with pytest.raises(ValueError) as ex:
        ebf.current = 2
    assert str(ex.value) == 'No font with index {0}'.format(2)

    with pytest.raises(ValueError) as ex:
        ebf.current = 'BAD'
    assert str(ex.value) == 'No font with name {0}'.format('BAD')

    with pytest.raises(TypeError) as ex:
        ebf.current = []
    assert str(ex.value) == 'Expected int or str.  Received {0}'.format(type([]))


def test_metrics(load_all_embedded):
    """
    ``bitmap_font`` correctly handles fonts that have characters within
    the font that have offsets.
    """
    bmfs = load_all_embedded

    img1 = Image.new('1', (10, 8), 0)
    drw = ImageDraw.Draw(img1)
    drw.text(((0, 0)), 'ij', font=bmfs[0], fill='white', spacing=0)
    size = bmfs[0].getsize('ij')
    assert size == (10, 8)

    img1d = Image.new('1', (10, 10), 0)
    drw = ImageDraw.Draw(img1d)
    drw.text(((0, 0)), 'i', font=bmfs[0], fill='white', spacing=0)
    drw.text(((5, 2)), 'j', font=bmfs[0], fill='white', spacing=0)

    # Make j descend 2 pixels below the baseline
    j = bmfs[0]._lookup(ord('j'))
    dst = bmfs[0].metrics[j]['dst']
    dst[1] = dst[1] + 2
    dst[3] = dst[3] + 2
    bmfs[0]._calculate_font_size()

    size = bmfs[0].getsize('ij')
    assert size == (10, 10)

    img2 = Image.new('1', size, 0)
    drw = ImageDraw.Draw(img2)
    drw.text(((0, 0)), 'ij', font=bmfs[0], fill='white', spacing=0)

    assert img1 != img2
    assert img1d == img2

    data = bmfs[0].dumps()
    restore = bitmap_font.loads(data)

    img2 = Image.new('1', size, 0)
    drw = ImageDraw.Draw(img2)
    drw.text(((0, 0)), 'ij', font=restore, fill='white', spacing=0)
    assert img1d == img2


def test_glyph_index(load_all_embedded):
    """
    ``glyph_table`` contains expected values
    """
    bmfs = load_all_embedded

    # Test space 'A' and 'a' characters
    for i in [0x20, 0x41, 0x61]:
        img = Image.new('1', (5, 8), 0)
        drw = ImageDraw.Draw(img)
        drw.text((0, 0), chr(i), font=bmfs[0], fill='white')
        assert bmfs[0].glyph_index[img.tobytes()] == i, '{0} does not match its glyph_index value'.format(i)
