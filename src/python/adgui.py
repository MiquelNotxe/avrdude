#!/usr/bin/env python

# This is a simple GUI demonstrator for the SWIG_Avrdude Python
# bindings to libavrdude.

# Its main purpose is to demonstrate that these Python bindings
# provide all the functionality that is needed for a full-featured AVR
# programming tool with similar features as the CLI version. It is not
# meant to be complete though, or to be a full replacement for the CLI
# tool.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import pathlib
import re
import time

builddir = None
if os.name == 'posix':
    # Linux, *BSD, MacOS
    sysname = os.uname()[0].lower()
    builddir = f'build_{sysname}/src'
elif os.name == 'nt':
    # Windows
    for candidate in ['build_msvc/src', 'build_mingw64/src']:
        if os.path.exists(candidate):
            builddir = candidate
            os.add_dll_directory(os.path.realpath(candidate))
            break

if builddir == None:
    print("Cannot determine build directory, module loading might fail.", file=sys.stderr)
else:
    sys.path.append(builddir)
    sys.path.append(builddir + '/python')

global avrlogo
# source: https://github.com/avrdudes/avrdude/discussions/841
avrlogo = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00`'+ \
    b'\x00\x00\x00`\x08\x06\x00\x00\x00\xe2\x98w8\x00\x00\x00\tpHY'+ \
    b's\x00\x00\x0b\x12\x00\x00\x0b\x12\x01\xd2\xdd~\xfc\x00\x00\x05iID'+ \
    b'ATx\x9c\xed\x9d\xffU\x1c7\x10\xc7\x87\xbc\xfc\x8fS\x81\x9d\n'+ \
    b'N\xa9\x00w`:\x00wp\xae \xa2\x82\\\x076\x15\x84\x0e\xe0'+ \
    b'*\xc8\\\x05\x86\n\x12* O\xce,\xec-\xd2\xccH\xab\xbd\x81'+ \
    b'0\x9f\xf7\xee\xbdc\x7fh%}5#i\xa4c\x8f\x1e\x1e\x1e\xc0'+ \
    b"\xb1\xe3'\xaf{[\\\x00c\\\x00c\\\x00c~\xd6>>\xc6"+ \
    b'x\x0e\x00_G\x87>\xc7\x18\xbf\xf5\xca~\x8c\xf1\x1d\x00\xdc\x00\xc0'+ \
    b'\x8a\x0e\xed\x00\xe0c\x8c\xf1\x9f\x97\x98\xee$\xef\xcduSc\x01_'+ \
    b'\x85\xbf\xe7\xb2\x1eU\x12\xd0\xf7\xf5\x0bN\xb7K\xdd\xb8\x0b2F='+ \
    b'\x0f\x881j.\xacvK\x19\xf3\xfd?\xa4\x9b\xae;\xd2\xa4\xd7\xdb'+ \
    b'\x02Z\xdc\x92\xe6\x9e\xd7\x96\xae\x1awA\xc6\xb8\x00\xc6\xb8\x00\xc6\xb8'+ \
    b'\x00\xc6\xb8\x00\xc6\x1c\xadV\xab\x08\x00\xbf\xbf\xe9Z\xb0\xe3"\t\xe0'+ \
    b'\x0b\x02\x86\xb8\x0b2\xc6\x050\xc6\x050\xc6\x050\xc6\x050\xc6\x05'+ \
    b'0\xc6\x050\xc6\x050\xc6\x050\xc6\x050\xc6\x050\xc6\x050\xc6'+ \
    b'\x050\xc6\x050F\xbd3\xae\x92/\x00p\x0b\x00\x7f*n\xdb"'+ \
    b'\xe2\xc7\xe9\xc1\x10B\xda\xd1v\x05\x00\'\x8dy\xd8\x02\xc0)">'+ \
    b'\xdb\x01\x17B\xb8\xc9\xa4{\x89\x88\xe75\x0f\x08!\x0c\xf9\x0e\xe9Y'+ \
    b'-y]b=\xe0\xb1BC\x08i\xcf\xcd\x99p\xfd\x17D\xdc\xe4'+ \
    b'N\x84\x10R\xc1\xfej\xcc\xc7o\x88\x88\x85t\xd3\xce\xb8?\xc6\xc7'+ \
    b'\x10Q\xb5\x8f\x87\x83\xf2\xbb\xa9\x11b\t\x17\x14G\xdf5\x9b\x9e\x8a'+ \
    b'\xdb\x04\xa9\x02\xb7\ry\xd8\x96*_z\xe6\x1c\xf0?R\xe3\xbb\xd4'+ \
    b'&\xd3[\x80\x1d"\xde\x0c\x7f\xd0w\xa9\x02\xdf\x87\x108\xd3\x8f\xcc'+ \
    b'\xb9\xea{\xe8Y\xef\x1b\xd2TC\xaeL%Bo\x01r\xaeDS'+ \
    b'\x81\xc5kH\xc4]E\x1e\xf6\x1aAc~fC"\x88\xf9\xee)'+ \
    b'\xc0\x1d">s9\x9d\xac \xdbG\xd4^{\x88\xd6?Atu'+ \
    b'=GA\\\xcb\xd2tL\xebR\x9f\x91\x84\r!DE\xe5e\x1b'+ \
    b'\x812\x8fYh\xc4T"\x8d\xb0\xbe!\xe2U!\xdf7!\x84\xdd'+ \
    b'd{\xfc\x1e\xbd,\x80-8e\xf0NHc5\x1a\xd6\xe5\x98\xe5'+ \
    b'\xca(\xed\x96\xd6\x7f\xc2|>\xa5\xa1\xb6`\xbdYq\x06z\t\xa0'+ \
    b'q\x11\xb3*\x90\nr\xcf\x9c\xbf\x17\n\xbb\xa4\xef\xe7\xca\xcf\x8d\xc6'+ \
    b'\xba\x08p\xaf\x19n\x92\x85HVpR\xb2\x02\x9aPq\x05\xdd\xe4'+ \
    b"&]\xf0\xd4\xfa['t\x1a\x8ei\x0e\x90\x83\xfd)T\x0f\x01\x8a"+ \
    b'\x05\xcf0\xd7\n6\x05+\xb8\x17\xc49\xc4\xc8\xe7\xb6\xe5\xa6\xb9\x02'+ \
    b'H\x05\x9f"\xb9\x11 +\xf8\x90;AB\xe7\xdc\xcc\x95a\xeb\x07'+ \
    b'\x9a\xf8\x95\x1a!\xd7\xaf\xcd\x16\xa0\xa6\xf5k\xdc\xc8\x00\xd7bs\xe7'+ \
    b'\xb8\xeb\xab\xe2;\r\xec(\x0eT\x82;7;\x16\xf4K\x8d\x00\xf0'+ \
    b'\x14dK\xe6z,\\\xfa+"f\xcdz\x12c*\x06\xd1\xc8\x92'+ \
    b'\xbek\xf2U\x8a\x05\t#3\xe0&}t\xef5w\xff\x9cy\xc0'+ \
    b'%c\xf6\x01\x9eb9{\xa4{B\x08\x1b\xc5\x8e\xec\xc8\xb4\xde\xcd'+ \
    b'H\x80E}\xbf0\xab\x96\x10\xad}\x8e\x0b\x92:Kv\xc4\xa2H'+ \
    b'\xff\x8c\xac\xe5\x19\xa3 ]1\xe8F\xad_\x8a\xc4.\x06Yiq'+ \
    b'\x026\xd0*\xc0%\xe3\x1e\xc20q)\r\xcd\xc8r4\xc1*n'+ \
    b'*\xbf\x16\xce\x1f$\xe63%5\x1ae\x18\xfe\x07\xad\x02p\x85['+ \
    b'\x17\xbe\xd7\xa4\xf1\x98\x16g\x05L\xeb\x7fg\xd1\xfa\xc9\xe7c\xcd\xb3'+ \
    b'[\x04\xe0Z\xff\xd4\xec\xcf\x98!eJC\xb2\x82\xe3\xc6\xd8}\xb7'+ \
    b"x\x7f\xaa\xd4\xd1'\xdb\x18\xe0\xc9\xe5\\\xd7\x86;Z\x04\xa8\rv"+ \
    b'\xd5\x0e)\xa7\x14\xad \x07]\xdbs\xc1\xe5z\xf4\xe1\xfa.6\xe6'+ \
    b'S\xa2V\x80miT@\x05\xcf\x8dyO\x197r\xab\x08U\x1f'+ \
    b'Kc\xe9\tk\xc5\x10\xb7\x15\xce\xa2\xafZV\xefj\x05\x90|\x7f'+ \
    b'\xae\xe0\x92\x1b\x99\x1b\x9exd\x81\xd6_\x9b\x97\xea\x8e\xbfF\x00\xa9'+ \
    b'\xf5\xb3#\x16\xc6\nz,\xd8\x0c\x9c/\xd8\xfa\x078+\xd0\x94e'+ \
    b'\x8f\x1a\x018uO\x85\x82Kn\xa4\x97\x15,\xdd\xfa\x07\xba\x85>'+ \
    b'\xb4\x02\xdcuXg\x9d\xbb\xee\x9b\xac\xa0(\xe2\x81\x97\x1b\xe7\x8e\xee'+ \
    b'\x1e\xd1\n\xd0c\x97A\x8fu\xdf\x974\xf1\x92\xfa\x02)\xea\xfb\x03'+ \
    b'\x8d\x00\xd2:k\x8d\xd9s{\x80\x9a\x17l\x0c\x16\xdbAa\x05\xaa'+ \
    b'0\xbdF\x00i\x9dU\x8cw\x8cXj\xdd\xf7P\xbe\x7fJ\xcb\xe2'+ \
    b'\xd1\x1e\x92\x00\xddw\x19\x08}A\xb5\x1544\x82\x9epV\xa0Z'+ \
    b'\xfb\x90\x04(V\xfe(\xe8VK1HGhLw\xdc\x97\x98\x04'+ \
    b'\xdd4\xcfGD\xb1/\x90\x04\xc8\xba\x0b\x1a\xd3\xd7,EN\xd90'+ \
    b'\xe1\x05\xcd\xac7\xb5\xbcS\xdad\xdbe\xb9\x91b9\xd3c\x9a!'+ \
    b'\xe5YitF\xd6\xc9\xceK\xfc\xbf\xa5\x18\xe3?\xd00\xc6\x050'+ \
    b'\xc6\x050\xc6\x050\xc6\x050\xc6\x050\xc6\x050\xc6\x050\xc6\x05'+ \
    b'0\xc6\x050\xc6\x050\xc6\x050\xc6\x050\xc6\x050\xc6\x050\xc6'+ \
    b'\x050\xc6\x050&\tp\xf1\xa6k\xc0\x96\x0b\xd5\x8b\xdc\xe8}\x8c'+ \
    b'\x7fk\xb2\xaa}\x81\xd9\xe8z\xd5\x92\xe8kK7\xfd\x80Q\xf3\xbe'+ \
    b'J\x95\x0b\xea\xf9\xe2\xcb\xb7\x82\xb6\xce\xbc\x0f0\xc6\x050\xc6\x050'+ \
    b'\xc6\x050\xa6\xb7\x00\x9f\x17\xba\xe7\xb5\xa5\xabf\xd6\xfb\x84k\x87p'+ \
    b'B\xfa\xb9\x17\xca]\xd0\xf1\x17\x97\xee$\xef\xcdu\xe3.\xc8\x98\x1a'+ \
    b'\x01\xa6\xa6\xd7\xd5\x14i\xb3\xef\xf8gJ\xbb\x99\x1b\x80\x97NwL'+ \
    b's\xdd\xa8]\x90\xb3\x0c\xee\x82\x8cq\x01\x8cq\x01\x8cq\x01,\x01'+ \
    b'\x80\x7f\x01\xd4\xa0\x1d\x07\x10\x94\xee\x92\x00\x00\x00\x00IEND\xae'+ \
    b'B`\x82'

import swig_avrdude as ad

def avrdude_init():
    ad.init_config()

    found = False
    for d in [builddir, "/etc", "/usr/local/etc"]:
        p = pathlib.Path(d + "/avrdude.conf")
        if p.is_file():
            ad.read_config(d + "/avrdude.conf")
            return (True, f"Found avrdude.conf in {d}")

    return (False, "Sorry, no avrdude.conf could be found.")

def classify_devices():
    result = {
        'at90': [],
        'attiny': [],
        'atmega': [],
        'atxmega': [],
        'avr_de': [],
        'other': []
    }
    avr_de_re = re.compile('AVR\d+[DE][A-Z]\d+')
    part = ad.lfirst(ad.cvar.part_list)
    while part:
        p = ad.ldata_avrpart(part)
        part = ad.lnext(part)
        if not p.id.startswith('.'):
            if p.desc.startswith('AT90'):
                result['at90'].append(p.desc)
            elif p.desc.startswith('ATtiny'):
                result['attiny'].append(p.desc)
            elif p.desc.startswith('ATmega'):
                result['atmega'].append(p.desc)
            elif p.desc.startswith('ATxmega'):
                result['atxmega'].append(p.desc)
            elif avr_de_re.match(p.desc):
                result['avr_de'].append(p.desc)
            else:
                result['other'].append(p.desc)
    return result

def classify_programmers():
    result = {
        'isp': [],
        'tpi': [],
        'pdi': [],
        'updi': [],
        'jtag': [],
        'hv': [],
        'other': []
    }
    pgm = ad.lfirst(ad.cvar.programmers)
    while pgm:
        p = ad.ldata_programmer(pgm)
        pgm = ad.lnext(pgm)
        names = []
        l = ad.lfirst(p.id)
        while l:
            names.append(ad.ldata_string(l))
            l = ad.lnext(l)
        pm = p.prog_modes
        matched = False
        if (pm & ad.PM_ISP) != 0:
            for name in names:
                result['isp'].append(name)
            matched = True
        if (pm & ad.PM_TPI) != 0:
            for name in names:
                result['tpi'].append(name)
            matched = True
        if (pm & ad.PM_PDI) != 0:
            for name in names:
                result['pdi'].append(name)
            matched = True
        if (pm & ad.PM_UPDI) != 0:
            for name in names:
                result['updi'].append(name)
            matched = True
        if (pm & (ad.PM_JTAG | ad.PM_JTAGmkI | ad.PM_XMEGAJTAG)) != 0:
            for name in names:
                result['jtag'].append(name)
            matched = True
        if (pm & (ad.PM_HVSP | ad.PM_HVPP)) != 0:
            for name in names:
                result['hv'].append(name)
            matched = True
        if not matched:
            for name in names:
                result['other'].append(name)
    return result

def size_to_str(size: int):
    if size >= 1024:
        return f"{size // 1024} KiB"
    return f"{size} B"

def yesno(val: bool):
    if val:
        return "Y"
    return "N"

def avrpart_to_mem(avrpart):

    if str(type(avrpart)).find('AVRPART') < 0:
        raise Exception(f"wrong argument: {type(avrpart)}, expecting swig_avrdude.AVRPART")

    res = []
    m = ad.lfirst(avrpart.mem)
    while m:
        mm = ad.ldata_avrmem((m))
        res.append(mm)
        m = ad.lnext(m)
    return res

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtUiTools import QUiLoader

class adgui(QObject):
    def __init__(self, argv):
        super().__init__()

        # members for logging
        self.logstring = "<font color='#000060'><strong>Welcome to AVRDUDE!</strong></font><br>\n"
        self.at_bol = { 'stdout': True, 'stderr': True }
        self.debuglog = ""
        self.debug_bol = True

        # the main Qt app
        self.app = QApplication(sys.argv)

        self.port = None
        self.dev_selected = None
        self.prog_selected = None
        self.connected = False

        self.flash_size = 0

        ad.set_msg_callback(self.msg_callback)
        ad.set_progress_callback(self.progress_callback)

        p = pathlib.Path(argv[0])
        srcdir = str(p.parent)
        for f in [ "adgui.ui", "about.ui", "device.ui",
                   "devinfo.ui", "loglevel.ui", "programmer.ui",
                   "memories.ui" ]:
            ui = QFile(srcdir + '/' + f)
            if not ui.open(QFile.ReadOnly):
                print(f"Cannot open {f}: {ui.errorString()}", file = sys.stderr)
                sys.exit(1)
            loader = QUiLoader()
            widgetname = f[:-3] # strip .ui suffix
            self.__dict__[widgetname] = loader.load(ui)
            ui.close()
            if not self.__dict__[widgetname]:
                print(loader.errorString(), file = sys.stderr)

        # Create pixmap for AVR logo from above, create a QGraphicsScene
        # out of it, and populate the QGraphicsView items with it.
        global avrlogo
        logo = QPixmap()
        logo.loadFromData(avrlogo)
        gsc = QGraphicsScene()
        gsc.addPixmap(logo)
        self.memories.avr.setScene(gsc)
        self.memories.ee_avr.setScene(gsc)

        self.adgui.show()

        self.adgui.actionAbout.triggered.connect(self.about.show)
        self.adgui.actionDevice.triggered.connect(self.device.show)
        self.app.lastWindowClosed.connect(self.cleanup)
        self.adgui.actionProgrammer.triggered.connect(self.programmer.show)
        self.adgui.loggingArea.setHtml(self.logstring)
        self.adgui.actionSave_log.triggered.connect(self.save_logfile)

        (success, message) = avrdude_init()
        self.initialized = success
        self.log(message)
        self.loglevel.radioButton.toggled.connect(self.loglevel_changed)
        self.loglevel.radioButton_2.toggled.connect(self.loglevel_changed)
        self.loglevel.radioButton_3.toggled.connect(self.loglevel_changed)
        self.loglevel.radioButton_4.toggled.connect(self.loglevel_changed)
        self.loglevel.radioButton_5.toggled.connect(self.loglevel_changed)
        self.loglevel.radioButton_6.toggled.connect(self.loglevel_changed)
        self.loglevel.radioButton_7.toggled.connect(self.loglevel_changed)
        self.loglevel.radioButton_8.toggled.connect(self.loglevel_changed)
        self.loglevel.radioButton_9.toggled.connect(self.loglevel_changed)
        self.adgui.actionLog_level.triggered.connect(self.loglevel.show)
        if not success:
            self.adgui.actionDevice.setEnabled(False)
            self.adgui.actionProgrammer.setEnabled(False)
            # essentially, only Exit and Help work anymore
        else:
            self.devices = classify_devices()
            self.update_device_cb()
            self.device.at90.stateChanged.connect(self.update_device_cb)
            self.device.attiny.stateChanged.connect(self.update_device_cb)
            self.device.atmega.stateChanged.connect(self.update_device_cb)
            self.device.atxmega.stateChanged.connect(self.update_device_cb)
            self.device.avr_de.stateChanged.connect(self.update_device_cb)
            self.device.other.stateChanged.connect(self.update_device_cb)
            self.device.buttonBox.accepted.connect(self.device_selected)
            self.programmers = classify_programmers()
            self.update_programmer_cb()
            self.programmer.isp.stateChanged.connect(self.update_programmer_cb)
            self.programmer.tpi.stateChanged.connect(self.update_programmer_cb)
            self.programmer.pdi.stateChanged.connect(self.update_programmer_cb)
            self.programmer.updi.stateChanged.connect(self.update_programmer_cb)
            self.programmer.hv.stateChanged.connect(self.update_programmer_cb)
            self.programmer.other.stateChanged.connect(self.update_programmer_cb)
            self.programmer.buttonBox.accepted.connect(self.programmer_selected)
            self.programmer.programmers.currentTextChanged.connect(self.programmer_update_port)
            self.adgui.actionDevice_Info.triggered.connect(self.devinfo.show)
            self.adgui.actionProgramming.triggered.connect(self.memories.show)
            self.memories.readSig.pressed.connect(self.read_signature)
            self.memories.choose.pressed.connect(self.ask_flash_file)
            self.memories.read.pressed.connect(self.flash_read)
            self.memories.program.pressed.connect(self.flash_write)
            self.memories.save.pressed.connect(self.flash_save)
            self.memories.load.pressed.connect(self.flash_load)
            self.memories.erase.pressed.connect(self.chip_erase)
            self.memories.clear.pressed.connect(self.clear_buffer)
            self.memories.filename.editingFinished.connect(self.detect_flash_file)
            self.memories.ee_choose.pressed.connect(self.ask_eeprom_file)
            self.memories.ee_read.pressed.connect(self.eeprom_read)
            self.memories.ee_program.pressed.connect(self.eeprom_write)
            self.memories.ee_save.pressed.connect(self.eeprom_save)
            self.memories.ee_load.pressed.connect(self.eeprom_load)
            self.memories.ee_filename.editingFinished.connect(self.detect_eeprom_file)
            self.load_settings()

        self.buffer_empty = 'background-color: rgb(255,240,240);'
        self.buffer_full = 'background-color: rgb(240,255,240);'

    def log(self, s: str, level: int = ad.MSG_INFO, no_nl: bool = False):
        # level to color mapping
        colors = [
            '#804040', # MSG_EXT_ERROR
            '#A03030', # MSG_ERROR
            '#A08000', # MSG_WARNING
            '#000000', # MSG_INFO
            '#006000', # MSG_NOTICE
            '#005030', # MSG_NOTICE2
            '#808080', # MSG_DEBUG
            '#60A060', # MSG_TRACE - not used
            '#6060A0', # MSG_TRACE2 - not used
        ]
        color = colors[level - ad.MSG_EXT_ERROR]
        html = None
        if level <= ad.MSG_WARNING:
            html = f"<font color={color}><strong>{s}</strong></font>"
        elif level < ad.MSG_TRACE:
            html = f"<font color={color}>{s}</font>"
        if html and (not no_nl or s[-1] == '\n'):
            html += "<br>\n"
        if s != "" and s != "\n":
            new_bol = not no_nl or (s[-1] == '\n')
            if not no_nl:
                s += '\n'
            # always save non-empty messages to debug log
            # prepend timestamp when at beginning of line
            if self.debug_bol:
                tstamp = time.strftime('%Y-%m-%dT%H:%M:%S')
                self.debuglog += f"{tstamp} {s}"
            else:
                self.debuglog += s
            self.debug_bol = new_bol
        if html:
            # only update loggingArea if not trace message
            self.logstring += html
            self.adgui.loggingArea.setHtml(self.logstring)
            self.adgui.loggingArea.moveCursor(QTextCursor.End)

    def message_type(self, msglvl: int):
        tnames = ('OS error', 'error', 'warning', 'info', 'notice',
                  'notice2', 'debug', 'trace', 'trace2')
        msglvl -= ad.MSG_EXT_ERROR # rebase to 0
        if msglvl > len(tnames):
            return 'unknown msglvl'
        else:
            return tnames[msglvl]

    # rough equivalent of avrdude_message2()
    # first argument is either "stdout" or "stderr"
    #
    # install callback with ad.set_msg_callback(msg_callback)
    def msg_callback(self, target: str, lno: int, fname: str, func: str,
                     msgmode: int, msglvl: int, msg: str, backslash_v: bool):
        if ad.cvar.verbose >= msglvl:
            s = ""
            if msgmode & ad.MSG2_PROGNAME:
                if not self.at_bol[target]:
                    s += "\n"
                    self.at_bol[target] = True
                s += ad.cvar.progname + ": "
                if ad.cvar.verbose >= ad.MSG_NOTICE and (msgmode & ad.MSG2_FUNCTION) != 0:
                    s += " " + func + "()"
                if ad.cvar.verbose >= ad.MSG_DEBUG and (msgmode & ad.MSG2_FILELINE) != 0:
                    n = os.path.basename(fname)
                    s += f" [{n}:{lno}]"
                if (msgmode & ad.MSG2_TYPE) != 0:
                    s += " " + self.message_type(msglvl)
                    s += ": "
            elif (msgmode & ad.MSG2_INDENT1) != 0:
                s = (len(ad.cvar.progname) + 1) * ' '
            elif (msgmode & ad.MSG2_INDENT2) != 0:
                s = (len(ad.cvar.progname) + 2) * ' '
            if backslash_v and not self.at_bol[target]:
                s += "\n"
            s += msg
            self.at_bol[target] = s[-1] == '\n'
            self.log(s, msglvl, no_nl = True)

    def progress_callback(self, percent: int, etime: float, hdr: str, finish: int):
        if hdr:
            self.adgui.operation.setText(hdr)
            self.adgui.progressBar.setEnabled(True)
        if percent == 100:
            if finish != -1:
                # "normal" end: reset and turn off progress bar
                self.adgui.progressBar.setValue(0)
                self.adgui.time.setText("-:--")
                self.adgui.operation.setText("")
            #else: freeze progress bar at previous value
            # but disable it anyway
            self.adgui.progressBar.setEnabled(False)
        else:
            self.adgui.progressBar.setValue(percent)
            secs = int(etime % 60)
            mins = int(etime / 60)
            self.adgui.time.setText(f"{mins}:{secs:02d}")
        self.app.processEvents()

    def load_settings(self):
        self.settings = QSettings(QSettings.NativeFormat, QSettings.UserScope, 'avrdude', 'adgui')
        s = self.settings
        name = s.fileName()
        k = s.allKeys()
        if (amnt := len(k)) == 0:
            # new file
            self.log(f"Settings file: {name}", ad.MSG_NOTICE)
        else:
            # we loaded something
            self.log(f"Loaded {amnt} settings from {name}", ad.MSG_INFO)
            if 'settings/log_level' in k:
                ll = int(s.value('settings/log_level'))
                ad.cvar.verbose = ll
                found = False
                for obj in self.loglevel.groupBox.children():
                    tt = obj.toolTip()
                    if tt and (int(tt) == ll):
                        obj.setChecked(True)
                        found = True
                        break
                if not found:
                    # appropriate level not found, default to INFO
                    self.loglevel.radioButton_4.setChecked(True)
                    self.cvar.verbose = 0
                    ll = 0
                self.log(f"Log level set to {ll}", ad.MSG_INFO)
            if 'file/device' in k:
                n = s.value('file/device')
                idx = self.device.devices.findText(n)
                if idx != -1:
                    self.device.devices.setCurrentIndex(idx)
                    self.log(f"Device set to {n}", ad.MSG_INFO)
            if 'file/programmer' in k:
                n = s.value('file/programmer')
                idx = self.programmer.programmers.findText(n)
                if idx != -1:
                    self.programmer.programmers.setCurrentIndex(idx)
                    self.log(f"Programmer set to {n}", ad.MSG_INFO)
            if 'file/port' in k:
                n = s.value('file/port')
                self.programmer.port.setText(n)
                self.log(f"Port set to {n}")

    def update_device_cb(self):
        fams = list(self.devices.keys())
        #fams.sort()
        self.device.devices.clear()
        for f in fams:
            obj = eval('self.device.' + f + '.isChecked()')
            if obj:
                for d in self.devices[f]:
                    self.device.devices.addItem(d)

    def update_programmer_cb(self):
        fams = list(self.programmers.keys())
        self.programmer.programmers.clear()
        l = {}
        for f in fams:
            obj = eval('self.programmer.' + f + '.isChecked()')
            if obj:
                for d in self.programmers[f]:
                    l[d] = True
        l = list(l.keys())
        l.sort()
        for k in l:
            self.programmer.programmers.addItem(k)

    def update_device_info(self):
        p = ad.locate_part(ad.cvar.part_list, self.dev_selected)
        if not p:
            log(f"Could not find {self.dev_selected} again, confused\n")
            return
        ad.avr_initmem(p)
        self.devinfo.label_2.setText(p.desc)
        self.devinfo.label_4.setText(p.id)
        self.devinfo.label_6.setText(p.config_file)
        self.devinfo.label_8.setText(str(p.lineno))
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Name', 'Size', 'Paged', 'Page Size', '# Pages'])
        mm = avrpart_to_mem(p)
        row = 0
        for m in mm:
            model.setItem(row, 0, QStandardItem(m.desc))
            sz = QStandardItem(size_to_str(m.size))
            sz.setTextAlignment(Qt.Alignment(int(Qt.AlignRight) | int(Qt.AlignVCenter)))
            model.setItem(row, 1, sz)
            pg = QStandardItem(yesno(m.paged))
            pg.setTextAlignment(Qt.Alignment(int(Qt.AlignHCenter) | int(Qt.AlignVCenter)))
            model.setItem(row, 2, pg)
            if m.paged:
                sz = QStandardItem(size_to_str(m.page_size))
                sz.setTextAlignment(Qt.Alignment(int(Qt.AlignRight) | int(Qt.AlignVCenter)))
                model.setItem(row, 3, sz)
                pg = QStandardItem(str(m.num_pages))
                pg.setTextAlignment(Qt.Alignment(int(Qt.AlignRight) | int(Qt.AlignVCenter)))
                model.setItem(row, 4, pg)
            row += 1
        self.devinfo.tableMemories.setModel(model)
        self.devinfo.tableMemories.resizeColumnsToContents()
        self.devinfo.tableMemories.resizeRowsToContents()
        self.devinfo.listVariants.clear()
        v = ad.lfirst(p.variants)
        while v:
            vv = ad.ldata_string(v)
            self.devinfo.listVariants.addItem(vv)
            v = ad.lnext(v)
        # update signature TAB in memories popup
        sig = p.signature
        sigstr = sig.hex(' ').upper()
        self.memories.configSig.setText(sigstr)

    def device_selected(self):
        self.dev_selected = self.device.devices.currentText()
        self.dev = ad.locate_part(ad.cvar.part_list, self.dev_selected)
        self.log(f"Selected device: {self.dev_selected}")
        self.settings.setValue('file/device', self.dev_selected)
        self.update_device_info()
        self.adgui.actionDevice_Info.setEnabled(True)
        if self.port != "set_this" and self.prog_selected and self.dev_selected:
            self.start_programmer()

    def programmer_selected(self):
        self.prog_selected = self.programmer.programmers.currentText()
        self.pgm = ad.locate_programmer(ad.cvar.programmers, self.prog_selected)
        self.port = self.programmer.port.text()
        self.log(f"Selected programmer: {self.pgm.desc} ({self.prog_selected})")
        self.settings.setValue('file/programmer', self.prog_selected)
        self.log(f"Selected port: {self.port}")
        self.settings.setValue('file/port', self.port)
        if self.port != "set_this" and self.prog_selected and self.dev_selected:
            self.start_programmer()

    def programmer_update_port(self):
        selected = self.programmer.programmers.currentText()
        pgm = ad.locate_programmer(ad.cvar.programmers, selected)
        if not pgm:
            return
        if pgm.conntype == ad.CONNTYPE_USB:
            self.programmer.port.clear()
            self.programmer.port.insert("usb")
        elif pgm.conntype == ad.CONNTYPE_LINUXGPIO:
            self.programmer.port.clear()
            self.programmer.port.insert("dummy")

    def loglevel_changed(self, checked: bool):
        btn = self.sender()
        if checked:
            # we abuse the tooltip for the verbosity value
            val = int(btn.toolTip())
            ad.cvar.verbose = val
            self.settings.setValue('settings/log_level', val)

    def start_programmer(self):
        if self.connected:
            return
        self.pgm.initpgm()
        self.pgm.setup()
        rv = self.pgm.open(self.port)
        if rv == -1:
            self.log('Could not open programmer', ad.MSG_ERROR)
        else:
            self.pgm.enable(self.dev)
            self.pgm.initialize(self.dev)
            self.log('Programmer successfully started')
            self.adgui.actionProgramming.setEnabled(True)
            self.connected = True

    def stop_programmer(self):
        if self.connected:
            self.pgm.disable()
            self.pgm.close()
            self.pgm.teardown()

    def cleanup(self):
        self.settings.sync()
        self.stop_programmer()

    def read_signature(self):
        sig_ok = "background-color: rgb(255, 255, 255);\ncolor: rgb(0, 100, 0);"
        sig_bad = "background-color: rgb(255, 255, 255);\ncolor: rgb(150, 0, 0);"
        if self.connected:
            m = ad.avr_locate_mem(self.dev, 'signature')
            if m:
                ad.avr_read_mem(self.pgm, self.dev, m)
                self.progress_callback(100, 0, "", 0) # clear progress bar
                read_sig = m.get(3)
                if read_sig == self.dev.signature:
                    self.memories.deviceSig.setStyleSheet(sig_ok)
                else:
                    self.memories.deviceSig.setStyleSheet(sig_bad)
                    self.log("Signature read from device does not match config file",
                             ad.MSG_WARNING)
                self.memories.flash.setEnabled(True)
                self.memories.eeprom.setEnabled(True)
                sigstr = read_sig.hex(' ').upper()
                self.memories.deviceSig.setText(sigstr)
                p = ad.locate_part_by_signature(ad.cvar.part_list, read_sig)
                if p:
                    self.memories.candidate.setText(p.desc)
                else:
                    self.memories.candidate.setText("???")
            else:
                ad.log("Could not find signature memory", ad.MSG_ERROR)

    def ask_flash_file(self):
        dlg = QFileDialog(caption = "Select file",
                          filter = "Load files (*.elf *.hex *.eep *.srec *.bin);; All Files (*)")
        if dlg.exec():
            self.memories.filename.setText(dlg.selectedFiles()[0])
            self.detect_flash_file()

    def detect_flash_file(self):
        # If file exists, try finding out real format. If file doesn't
        # exist, try guessing the intended file format based on the
        # suffix.
        fname = self.memories.filename.text()
        if len(fname) > 0:
            self.flashname = fname
            self.memories.load.setEnabled(True)
            self.memories.save.setEnabled(True)
        else:
            # no filename, disable load/save buttons
            self.flashname = None
            self.memories.load.setEnabled(False)
            self.memories.save.setEnabled(False)
            return
        p = pathlib.Path(fname)
        if p.is_file():
            fmt = ad.fileio_fmt_autodetect(fname)
            if fmt == ad.FMT_ELF:
                self.memories.ffELF.setChecked(True)
            elif fmt == ad.FMT_IHEX:
                self.memories.ffIhex.setChecked(True)
            elif fmt == ad.FMT_SREC:
                self.memories.ffSrec.setChecked(True)
        else:
            if fname.endswith('.hex') or fname.endswith('.ihex') \
               or fname.endswith('.eep'): # common name for EEPROM Intel hex files
                self.memories.ffIhex.setChecked(True)
            elif fname.endswith('.srec'):
                self.memories.ffSrec.setChecked(True)
            elif fname.endswith('.bin'):
                self.memories.ffRbin.setChecked(True)

    def flash_read(self):
        self.adgui.progressBar.setEnabled(True)
        m = ad.avr_locate_mem(self.dev, 'flash')
        if not m:
            self.log("Could not find 'flash' memory", ad.MSG_ERROR)
            return
        amnt = ad.avr_read_mem(self.pgm, self.dev, m)
        self.flash_size = amnt
        self.log(f"Read {amnt} bytes")
        if amnt > 0:
            self.memories.buffer.setStyleSheet(self.buffer_full)

    def flash_write(self):
        self.adgui.progressBar.setEnabled(True)
        m = ad.avr_locate_mem(self.dev, 'flash')
        if not m:
            self.log("Could not find 'flash' memory", ad.MSG_ERROR)
            return
        if self.flash_size == 0:
            self.log("No data to write into 'flash' memory", ad.MSG_WARNING)
            return
        amnt = ad.avr_write_mem(self.pgm, self.dev, m, self.flash_size)
        self.log(f"Programmed {amnt} bytes")

    def clear_buffer(self):
        m = ad.avr_locate_mem(self.dev, 'flash')
        if not m:
            self.log("Could not find 'flash' memory", ad.MSG_ERROR)
            return
        m.clear(m.size)
        self.log(f"Cleared {m.size} bytes of buffer, and allocation flags")
        self.flash_size = 0
        self.memories.buffer.setStyleSheet(self.buffer_empty)

    def flash_save(self):
        if self.memories.ffAuto.isChecked() or \
           self.memories.ffELF.isChecked():
            self.log("Auto or ELF are not valid for saving files", ad.MSG_ERROR)
            return
        if self.memories.ffIhex.isChecked():
            fmt = ad.FMT_IHEX
        elif self.memories.ffSrec.isChecked():
            fmt = ad.FMT_SREC
        elif self.memories.ffRbin.isChecked():
            fmt = ad.FMT_RBIN
        else:
            self.log("Internal error: cannot determine file format", ad.MSG_ERROR)
            return
        fname = self.flashname
        p = pathlib.Path(fname)
        if p.is_file():
            result = QMessageBox.question(self.memories,
                                          f"Overwrite {fname}?",
                                          f"Do you want to overwrite {fname}?")
            if result != QMessageBox.StandardButton.Yes:
                return
        if self.flash_size != 0:
            amnt = self.flash_size
        else:
            amnt = -1
        amnt = ad.fileio(ad.FIO_WRITE, self.flashname, fmt, self.dev, "flash", amnt)
        self.log(f"Wrote {amnt} bytes to {self.flashname}")

    def flash_load(self):
        if self.memories.ffAuto.isChecked():
            fmt = ad.FMT_AUTO
        elif self.memories.ffELF.isChecked():
            fmt = ad.FMT_ELF
        elif self.memories.ffIhex.isChecked():
            fmt = ad.FMT_IHEX
        elif self.memories.ffSrec.isChecked():
            fmt = ad.FMT_SREC
        elif self.memories.ffRbin.isChecked():
            fmt = ad.FMT_RBIN
        else:
            self.log("Internal error: cannot determine file format", ad.MSG_ERROR)
            return
        amnt = ad.fileio(ad.FIO_READ, self.flashname, fmt, self.dev, "flash", -1)
        self.log(f"Read {amnt} bytes from {self.flashname}")
        self.flash_size = amnt
        if amnt > 0:
            self.memories.buffer.setStyleSheet(self.buffer_full)

    def chip_erase(self):
        result = QMessageBox.question(self.memories,
                                      f"Erase {self.dev.desc}?",
                                      f"Do you want to erase the entire device?")
        if result != QMessageBox.StandardButton.Yes:
            return
        result = self.pgm.chip_erase(self.dev)
        if result == 0:
            self.log("Device erased")
            self.flash_size = 0
            self.memories.buffer.setStyleSheet(self.buffer_empty)
        else:
            self.log("Failed to erase device", ad.MSG_WARNING)

    def save_logfile(self):
        fname = QFileDialog.getSaveFileName(caption = "Save logfile to",
                                            filter = "Text files (*.txt *.log);; All Files (*)")
        if fname:
            fname = fname[0]  # [1] is filter used
            if fname.rfind(".") == -1:
                # no suffix given
                fname += ".log"
            try:
                f = open(fname, "w")
            except Exception as e:
                self.log(f"Cannot create log file: {str(e)}", ad.LOG_EXT_ERROR)
                return
            try:
                f.write(self.debuglog)
                self.debuglog = ""
            except Exception as e:
                self.log(f"Cannot write log file: {str(e)}", ad.LOG_WXT_ERROR)

    def ask_eeprom_file(self):
        dlg = QFileDialog(caption = "Select file",
                          filter = "Load files (*.elf *.hex *.eep *.srec *.bin);; All Files (*)")
        if dlg.exec():
            self.memories.ee_filename.setText(dlg.selectedFiles()[0])
            self.detect_eeprom_file()

    def detect_eeprom_file(self):
        # If file exists, try finding out real format. If file doesn't
        # exist, try guessing the intended file format based on the
        # suffix.
        fname = self.memories.ee_filename.text()
        if len(fname) > 0:
            self.eepromname = fname
            self.memories.ee_load.setEnabled(True)
            self.memories.ee_save.setEnabled(True)
        else:
            # no filename, disable load/save buttons
            self.eepromname = None
            self.memories.ee_load.setEnabled(False)
            self.memories.ee_save.setEnabled(False)
            return
        p = pathlib.Path(fname)
        if p.is_file():
            fmt = ad.fileio_fmt_autodetect(fname)
            if fmt == ad.FMT_ELF:
                self.memories.ee_ffELF.setChecked(True)
            elif fmt == ad.FMT_IHEX:
                self.memories.ee_ffIhex.setChecked(True)
            elif fmt == ad.FMT_SREC:
                self.memories.ee_ffSrec.setChecked(True)
        else:
            if fname.endswith('.hex') or fname.endswith('.ihex') \
               or fname.endswith('.eep'): # common name for EEPROM Intel hex files
                self.memories.ee_ffIhex.setChecked(True)
            elif fname.endswith('.srec'):
                self.memories.ee_ffSrec.setChecked(True)
            elif fname.endswith('.bin'):
                self.memories.ee_ffRbin.setChecked(True)

    def eeprom_read(self):
        self.adgui.progressBar.setEnabled(True)
        m = ad.avr_locate_mem(self.dev, 'eeprom')
        if not m:
            self.log("Could not find 'eeprom' memory", ad.MSG_ERROR)
            return
        amnt = ad.avr_read_mem(self.pgm, self.dev, m)
        self.eeprom_size = amnt
        self.log(f"Read {amnt} bytes")
        if amnt > 0:
            self.memories.ee_buffer.setStyleSheet(self.buffer_full)

    def eeprom_write(self):
        self.adgui.progressBar.setEnabled(True)
        m = ad.avr_locate_mem(self.dev, 'eeprom')
        if not m:
            self.log("Could not find 'eeprom' memory", ad.MSG_ERROR)
            return
        if self.eeprom_size == 0:
            self.log("No data to write into 'eeprom' memory", ad.MSG_WARNING)
            return
        amnt = ad.avr_write_mem(self.pgm, self.dev, m, self.eeprom_size)
        self.log(f"Programmed {amnt} bytes")

    def clear_buffer(self):
        m = ad.avr_locate_mem(self.dev, 'eeprom')
        if not m:
            self.log("Could not find 'eeprom' memory", ad.MSG_ERROR)
            return
        m.clear(m.size)
        self.log(f"Cleared {m.size} bytes of buffer, and allocation flags")
        self.eeprom_size = 0
        self.memories.ee_buffer.setStyleSheet(self.buffer_empty)

    def eeprom_save(self):
        if self.memories.ee_ffAuto.isChecked() or \
           self.memories.ee_ffELF.isChecked():
            self.log("Auto or ELF are not valid for saving files", ad.MSG_ERROR)
            return
        if self.memories.ee_ffIhex.isChecked():
            fmt = ad.FMT_IHEX
        elif self.memories.ee_ffSrec.isChecked():
            fmt = ad.FMT_SREC
        elif self.memories.ee_ffRbin.isChecked():
            fmt = ad.FMT_RBIN
        else:
            self.log("Internal error: cannot determine file format", ad.MSG_ERROR)
            return
        fname = self.eepromname
        p = pathlib.Path(fname)
        if p.is_file():
            result = QMessageBox.question(self.memories,
                                          f"Overwrite {fname}?",
                                          f"Do you want to overwrite {fname}?")
            if result != QMessageBox.StandardButton.Yes:
                return
        if self.eeprom_size != 0:
            amnt = self.eeprom_size
        else:
            amnt = -1
        amnt = ad.fileio(ad.FIO_WRITE, self.eepromname, fmt, self.dev, "eeprom", amnt)
        self.log(f"Wrote {amnt} bytes to {self.eepromname}")

    def eeprom_load(self):
        if self.memories.ee_ffAuto.isChecked():
            fmt = ad.FMT_AUTO
        elif self.memories.ee_ffELF.isChecked():
            fmt = ad.FMT_ELF
        elif self.memories.ee_ffIhex.isChecked():
            fmt = ad.FMT_IHEX
        elif self.memories.ee_ffSrec.isChecked():
            fmt = ad.FMT_SREC
        elif self.memories.ee_ffRbin.isChecked():
            fmt = ad.FMT_RBIN
        else:
            self.log("Internal error: cannot determine file format", ad.MSG_ERROR)
            return
        amnt = ad.fileio(ad.FIO_READ, self.eepromname, fmt, self.dev, "eeprom", -1)
        self.log(f"Read {amnt} bytes from {self.eepromname}")
        self.eeprom_size = amnt
        if amnt > 0:
            self.memories.ee_buffer.setStyleSheet(self.buffer_full)

def main():
    gui = adgui(sys.argv)

    sys.exit(gui.app.exec_())

if __name__ == "__main__":
    main()
