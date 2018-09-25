
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import socket
import struct
import string
import sys
import os

import disassemble


"""""""""""""""""""""""""""
          Signals
"""""""""""""""""""""""""""

class EventHolder(QObject):
	Connected = pyqtSignal()
	Closed = pyqtSignal()
	BreakPointChanged = pyqtSignal()
	Exception = pyqtSignal(object)
	Continue = pyqtSignal(object)
	Step = pyqtSignal(object)
events = EventHolder()


"""""""""""""""""""""""""""
      Debugger client
"""""""""""""""""""""""""""

class ExceptionState:

	exceptionNames = ["DSI", "ISI", "Program"]

	def __init__(self, message):
		#Convert tuple to list to make it mutable
		data = message.data
		self.gpr = list(struct.unpack_from(">32I", data, 8))
		self.cr, self.lr, self.ctr, self.xer = struct.unpack_from(">4I", data, 0x88)
		self.srr0, self.srr1, self.ex0, self.ex1 = struct.unpack_from(">4I", data, 0x98)
		self.fpr = list(struct.unpack_from(">32d", data, 0xB8))
		self.gqr = list(struct.unpack_from(">8I", data, 0x1BC))
		self.psf = list(struct.unpack_from(">32d", data, 0x1E0))
		
		self.thread = message.arg

		self.exceptionName = self.exceptionNames[message.type]
		
		self.stepping = False

	def isBreakPoint(self):
		return self.exceptionName == "Program" and self.srr1 & 0x20000
		
	def isFatal(self):
		return not self.isBreakPoint()


class Message:
	#Server messages
	DSI = 0
	ISI = 1
	Program = 2

	#Client messages
	Continue = 0
	Step = 1
	StepOver = 2

	def __init__(self, type, data, arg):
		self.type = type
		self.data = data
		self.arg = arg


class Thread:

	cores = {
		1: "Core 0",
		2: "Core 1",
		4: "Core 2"
	}

	def __init__(self, data, offs=0):
		self.handle = struct.unpack_from(">I", data, offs)[0]
		self.core = self.cores[struct.unpack_from(">I", data, offs + 4)[0]]
		self.priority = struct.unpack_from(">I", data, offs + 8)[0]
		self.stackBase = struct.unpack_from(">I", data, offs + 12)[0]
		self.stackEnd = struct.unpack_from(">I", data, offs + 16)[0]
		self.entryPoint = struct.unpack_from(">I", data, offs + 20)[0]
		self.namelen = struct.unpack_from(">I", data, offs + 24)[0]
		self.name = data[offs + 28 : offs + 28 + self.namelen].decode("shift-jis")
		
		
class Module:
	def __init__(self, data, offs=0):
		self.textAddr = struct.unpack_from(">I", data, offs)[0]
		self.textSize = struct.unpack_from(">I", data, offs + 4)[0]
		self.dataAddr = struct.unpack_from(">I", data, offs + 8)[0]
		self.dataSize = struct.unpack_from(">I", data, offs + 12)[0]
		self.entryPoint = struct.unpack_from(">I", data, offs + 16)[0]
		
		self.namelen = struct.unpack_from(">I", data, offs + 20)[0]
		self.name = data[offs + 24 : offs + 24 + self.namelen].decode("ascii")


COMMAND_CLOSE = 0
COMMAND_READ = 1
COMMAND_WRITE = 2
COMMAND_WRITE_CODE = 3
COMMAND_GET_MODULE_NAME = 4
COMMAND_GET_MODULE_LIST = 5
COMMAND_GET_THREAD_LIST = 6
COMMAND_GET_STACK_TRACE = 7
COMMAND_TOGGLE_BREAKPOINT = 8
COMMAND_POKE_REGISTERS = 9
COMMAND_RECEIVE_MESSAGES = 10
COMMAND_SEND_MESSAGE = 11
		
class Debugger:
	def __init__(self):
		super().__init__()

		self.reset()

		self.messageHandlers = {
			Message.DSI: self.handleException,
			Message.ISI: self.handleException,
			Message.Program: self.handleException
		}
		
	def reset(self):
		self.connected = False
		self.breakpoints = []
		self.trapEvents = []
		self.crashEvents = []
		self.threads = []

	def connect(self, host):
		self.s = socket.socket()
		self.s.settimeout(4)
		self.s.connect((host, 1560))
		self.connected = True
		events.Connected.emit()
		
	def handleClose(self):
		self.reset()
		events.Closed.emit()

	def close(self):
		self.sendbyte(COMMAND_CLOSE)
		self.s.close()
		self.handleClose()
		
	def read(self, addr, num):
		self.sendbyte(COMMAND_READ)
		self.sendall(struct.pack(">II", addr, num))
		data = self.recvall(num)
		return data

	def write(self, addr, data):
		self.sendbyte(COMMAND_WRITE)
		self.sendall(struct.pack(">II", addr, len(data)))
		self.sendall(data)
		
	def writeCode(self, addr, data):
		self.sendbyte(COMMAND_WRITE_CODE)
		self.sendall(struct.pack(">II", addr, len(data)))
		self.sendall(data)
		
	def writeInstr(self, addr, value):
		self.writeCode(addr, struct.pack(">I", value))
		
	def getModuleName(self):
		self.sendbyte(COMMAND_GET_MODULE_NAME)
		length = struct.unpack(">I", self.recvall(4))[0]
		return self.recvall(length).decode("ascii") + ".rpx"
		
	def getModuleList(self):
		self.sendbyte(COMMAND_GET_MODULE_LIST)
		length = struct.unpack(">I", self.recvall(4))[0]
		data = self.recvall(length)
		
		offset = 0
		modules = []
		while offset < length:
			module = Module(data, offset)
			modules.append(module)
			offset += 24 + len(module.name)
		return sorted(modules, key=lambda m: m.textAddr)
		
	def getThreadList(self):
		self.sendbyte(COMMAND_GET_THREAD_LIST)
		length = struct.unpack(">I", self.recvall(4))[0]
		data = self.recvall(length)
		
		offset = 0
		self.threads = []
		while offset < length:
			thread = Thread(data, offset)
			self.threads.append(thread)
			offset += 28 + thread.namelen
		return self.threads
		
	def getStackTrace(self, state):
		self.sendbyte(COMMAND_GET_STACK_TRACE)
		self.sendall(struct.pack(">I", state.thread))
		count = struct.unpack(">I", self.recvall(4))[0]
		trace = struct.unpack(">%iI" %count, self.recvall(4 * count))
		return trace
		
	def toggleBreakPoint(self, addr):
		if addr in self.breakpoints:
			self.breakpoints.remove(addr)
		else:
			self.breakpoints.append(addr)

		self.sendbyte(COMMAND_TOGGLE_BREAKPOINT)
		self.sendall(struct.pack(">I", addr))
		events.BreakPointChanged.emit()
		
	def pokeRegisters(self, state):
		self.sendbyte(COMMAND_POKE_REGISTERS)
		self.sendall(struct.pack(">I", state.thread))
		self.sendall(struct.pack(">32I32d", *state.gpr, *state.fpr))

	def updateMessages(self):
		self.sendbyte(COMMAND_RECEIVE_MESSAGES)
		count = struct.unpack(">I", self.recvall(4))[0]
		for i in range(count):
			type, ptr, length, arg = struct.unpack(">IIII", self.recvall(16))
			data = None
			if length:
				data = self.recvall(length)
			self.messageHandlers[type](Message(type, data, arg))
			
	def sendMessage(self, message, data0=0, data1=0, data2=0):
		self.sendbyte(COMMAND_SEND_MESSAGE)
		self.sendall(struct.pack(">IIII", message, data0, data1, data2))
			
	def handleException(self, msg):
		state = ExceptionState(msg)
		events.Exception.emit(state)

	def continueThread(self, state): self.sendCrashMessage(Message.Continue, state)
	def stepInto(self, state): self.sendCrashMessage(Message.Step, state)
	def stepOver(self, state): self.sendCrashMessage(Message.StepOver, state)

	def sendCrashMessage(self, message, state):
		self.sendMessage(message, state.thread)
		if message == Message.Continue:
			state.stepping = False
			events.Continue.emit(state)
		else:
			state.stepping = True
			events.Step.emit(state)
		
	def _findThread(self, handle):
		for thread in self.threads:
			if thread.handle == handle:
				return thread
		
	def findThread(self, handle):
		thread = self._findThread(handle)
		if not thread:
			self.getThreadList()
			thread = self._findThread(handle)
		return thread
		
	def sendbyte(self, byte):
		self.sendall(bytes([byte]))

	def sendall(self, data):
		if self.connected:
			try:
				self.s.sendall(data)
			except socket.error:
				self.handleClose()

	def recvall(self, num):
		if not self.connected:
			return bytes(num)
	
		try:
			data = b""
			while len(data) < num:
				chunk = self.s.recv(num - len(data))
				if not chunk:
					self.handleClose()
					return bytes(num)
				data += chunk
		except socket.error:
			self.handleClose()
			return bytes(num)

		return data
debugger = Debugger()


"""""""""""""""""""""""""""
      Custom widgets
"""""""""""""""""""""""""""

class HexSpinBox(QAbstractSpinBox):
	def __init__(self, stepSize = 1):
		super().__init__()
		self._value = 0
		self.stepSize = stepSize

	def validate(self, text, pos):
		if all([char in "0123456789abcdefABCDEF" for char in text]):
			if not text:
				return QValidator.Intermediate, text.upper(), pos

			value = int(text, 16)
			if value <= 0xFFFFFFFF:
				self._value = value
				if value % self.stepSize:
					self._value -= value % self.stepSize
					return QValidator.Acceptable, text.upper(), pos
				return QValidator.Acceptable, text.upper(), pos

		return QValidator.Invalid, text.upper(), pos

	def stepBy(self, steps):
		self._value = min(max(self._value + steps * self.stepSize, 0), 0x100000000 - self.stepSize)
		self.lineEdit().setText("%X" %self._value)

	def stepEnabled(self):
		return QAbstractSpinBox.StepUpEnabled | QAbstractSpinBox.StepDownEnabled

	def setValue(self, value):
		self._value = value
		self.lineEdit().setText("%X" %self._value)

	def value(self):
		return self._value


"""""""""""""""""""""""""""
      Memory widgets
"""""""""""""""""""""""""""
		
def format_hex(blob, offs):
	return "%02X" %blob[offs]

def format_ascii(blob, offs):
	char = chr(blob[offs])
	if char in string.ascii_letters + string.digits + string.punctuation + " ":
		return char
	return "?"

def format_float(blob, offs):
	value = struct.unpack_from(">f", blob, offs)[0]
	if abs(value) >= 1000000 or 0 < abs(value) < 0.000001:
		return "%e" %value
	return ("%.8f" %value).rstrip("0")


class MemoryViewer(QWidget):

	class Format:
		Hex = 0
		Ascii = 1
		Float = 2

	Width = 1, 1, 4
	Funcs = format_hex, format_ascii, format_float

	def __init__(self):
		super().__init__()

		self.layout = QGridLayout()

		for i in range(16):
			self.layout.addWidget(QLabel("%X" %i, self), 0, i + 1)
		self.addrLabels = []
		for i in range(16):
			label = QLabel("%X" %(i * 0x10), self)
			self.layout.addWidget(label, i + 1, 0)
			self.addrLabels.append(label)
		self.dataCells = []

		self.base = 0
		self.format = self.Format.Hex
		self.updateData()

		self.setLayout(self.layout)

		events.Connected.connect(self.connected)

	def connected(self):
		self.setBase(0x10000000)

	def setFormat(self, format):
		self.format = format
		self.updateData()

	def setBase(self, base):
		window.mainWidget.tabWidget.memoryTab.memoryInfo.baseBox.setValue(base)
		self.base = base
		for i in range(16):
			self.addrLabels[i].setText("%X" %(self.base + i * 0x10))
		self.updateData()

	def updateData(self):
		for cell in self.dataCells:
			self.layout.removeWidget(cell)
			cell.setParent(None)

		if debugger.connected:
			blob = debugger.read(self.base, 0x100)
		else:
			blob = b"\x00" * 0x100

		width = self.Width[self.format]
		func = self.Funcs[self.format]
		for i in range(16 // width):
			for j in range(16):
				label = QLabel(func(blob, j * 0x10 + i * width), self)
				self.layout.addWidget(label, j + 1, i * width + 1, 1, width)
				self.dataCells.append(label)


class MemoryInfo(QWidget):
	def __init__(self):
		super().__init__()
		self.dataTypeLabel = QLabel("Data type:")
		self.dataTypeBox = QComboBox()
		self.dataTypeBox.addItems(["Hex", "Ascii", "Float"])
		self.dataTypeBox.currentIndexChanged.connect(self.updateDataType)

		self.baseLabel = QLabel("Address:")
		self.baseBox = HexSpinBox(0x10)
		self.baseButton = QPushButton("Update", self)
		self.baseButton.clicked.connect(self.updateMemoryBase)

		self.pokeAddr = HexSpinBox(4)
		self.pokeValue = HexSpinBox()
		self.pokeButton = QPushButton("Poke", self)
		self.pokeButton.clicked.connect(self.pokeMemory)

		self.layout = QGridLayout()
		self.layout.addWidget(self.baseLabel, 0, 0)
		self.layout.addWidget(self.baseBox, 0, 1)
		self.layout.addWidget(self.baseButton, 0, 2)
		self.layout.addWidget(self.pokeAddr, 1, 0)
		self.layout.addWidget(self.pokeValue, 1, 1)
		self.layout.addWidget(self.pokeButton, 1, 2)
		self.layout.addWidget(self.dataTypeLabel, 2, 0)
		self.layout.addWidget(self.dataTypeBox, 2, 1, 1, 2)
		self.setLayout(self.layout)

	def updateDataType(self, index):
		window.mainWidget.tabWidget.memoryTab.memoryViewer.setFormat(index)

	def updateMemoryBase(self):
		window.mainWidget.tabWidget.memoryTab.memoryViewer.setBase(self.baseBox.value())

	def pokeMemory(self):
		debugger.write(self.pokeAddr.value(), struct.pack(">I", self.pokeValue.value()))
		window.mainWidget.tabWidget.memoryTab.memoryViewer.updateData()


class MemoryTab(QWidget):
	def __init__(self):
		super().__init__()
		self.memoryInfo = MemoryInfo()
		self.memoryViewer = MemoryViewer()
		self.layout = QHBoxLayout()
		self.layout.addWidget(self.memoryInfo)
		self.layout.addWidget(self.memoryViewer)
		self.setLayout(self.layout)


"""""""""""""""""""""""""""
    Disassembly widgets
"""""""""""""""""""""""""""
		
class DisassemblyWidget(QTextEdit):
	def __init__(self):
		super().__init__()
		self.setTextInteractionFlags(Qt.NoTextInteraction)
		
		self.setMinimumWidth(500)

		self.currentInstruction = None
		self.selectedAddress = 0
		self.setBase(0)

		events.Closed.connect(self.updateHighlight)
		events.BreakPointChanged.connect(self.updateHighlight)

	def setCurrentInstruction(self, instr):
		self.currentInstruction = instr
		if instr is not None:
			self.setBase(instr - 0x20)
		else:
			self.updateHighlight()

	def setBase(self, base):
		self.base = base
		self.updateText()
		self.updateHighlight()

	def updateText(self):
		if debugger.connected:
			blob = debugger.read(self.base, 0x60)
		else:
			blob = b"\x00" * 0x60

		text = ""
		for i in range(24):
			address = self.base + i * 4
			value = struct.unpack_from(">I", blob, i * 4)[0]
			instr = disassemble.disassemble(value, address)
			text += "%08X:  %08X  %s\n" %(address, value, instr)
		self.setPlainText(text)

	def updateHighlight(self):
		selections = []
		for i in range(24):
			address = self.base + i * 4

			color = self.getColor(address)
			if color:
				cursor = self.textCursor()
				cursor.movePosition(QTextCursor.Down, n=i)
				cursor.select(QTextCursor.LineUnderCursor)
				format = QTextCharFormat()
				format.setBackground(QBrush(QColor(color)))
				selection = QTextEdit.ExtraSelection()
				selection.cursor = cursor
				selection.format = format
				selections.append(selection)
		self.setExtraSelections(selections)

	def getColor(self, addr):
		colors = []
		if addr in debugger.breakpoints:
			colors.append((255, 0, 0))
		if addr == self.currentInstruction:
			colors.append((0, 255, 0))
		if addr == self.selectedAddress:
			colors.append((128, 128, 255))

		if not colors:
			return None

		color = [sum(l)//len(colors) for l in zip(*colors)]
		return "#%02X%02X%02X" %tuple(color)

	def mousePressEvent(self, e):
		super().mousePressEvent(e)
		line = self.cursorForPosition(e.pos()).blockNumber()
		self.selectedAddress = self.base + line * 4
		if e.button() == Qt.MidButton:
			debugger.toggleBreakPoint(self.selectedAddress)
		self.updateHighlight()


class DisassemblyInfo(QWidget):
	def __init__(self):
		super().__init__()
		self.baseLabel = QLabel("Address:")
		self.baseBox = HexSpinBox(4)
		self.baseButton = QPushButton("Update", self)
		self.baseButton.clicked.connect(self.updateDisassemblyBase)

		self.pokeBox = HexSpinBox()
		self.pokeButton = QPushButton("Poke", self)
		self.pokeButton.clicked.connect(self.poke)

		self.layout = QGridLayout()
		self.layout.addWidget(self.baseLabel, 0, 0)
		self.layout.addWidget(self.baseBox, 0, 1)
		self.layout.addWidget(self.baseButton, 0, 2)
		self.layout.addWidget(self.pokeBox, 1, 0)
		self.layout.addWidget(self.pokeButton, 1, 1, 1, 2)
		self.setLayout(self.layout)
		self.setMinimumWidth(300)

	def updateDisassemblyBase(self):
		window.mainWidget.tabWidget.disassemblyTab.disassemblyWidget.setBase(self.baseBox.value())

	def poke(self):
		disassembly = window.mainWidget.tabWidget.disassemblyTab.disassemblyWidget
		if disassembly.selectedAddress:
			debugger.writeInstr(disassembly.selectedAddress, self.pokeBox.value())
			disassembly.updateText()


class DisassemblyTab(QWidget):
	def __init__(self):
		super().__init__()
		self.disassemblyInfo = DisassemblyInfo()
		self.disassemblyWidget = DisassemblyWidget()
		self.layout = QHBoxLayout()
		self.layout.addWidget(self.disassemblyInfo)
		self.layout.addWidget(self.disassemblyWidget)
		self.setLayout(self.layout)

		events.Connected.connect(self.connected)

	def connected(self):
		self.disassemblyWidget.setBase(0x10000000)

		
"""""""""""""""""""""""""""
      Thread widgets
"""""""""""""""""""""""""""

class ThreadList(QTableWidget):
	def __init__(self):
		super().__init__(0, 5)
		self.setHorizontalHeaderLabels(["Name", "Priority", "Core", "Stack", "Entry Point"])
		self.setEditTriggers(self.NoEditTriggers)
		self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

		events.Connected.connect(self.updateThreads)

	def updateThreads(self):
		threads = debugger.getThreadList()
		self.setRowCount(len(threads))
		for i in range(len(threads)):
			thread = threads[i]
			self.setItem(i, 0, QTableWidgetItem(thread.name))
			self.setItem(i, 1, QTableWidgetItem(str(thread.priority)))
			self.setItem(i, 2, QTableWidgetItem(thread.core))
			self.setItem(i, 3, QTableWidgetItem("0x%X - 0x%X" %(thread.stackEnd, thread.stackBase)))
			self.setItem(i, 4, QTableWidgetItem("0x%X" %thread.entryPoint))


class ThreadingTab(QWidget):
	def __init__(self):
		super().__init__()
		self.threadList = ThreadList()
		self.updateButton = QPushButton("Update", self)
		self.updateButton.clicked.connect(self.threadList.updateThreads)
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.threadList)
		self.layout.addWidget(self.updateButton)
		self.setLayout(self.layout)

		
"""""""""""""""""""""""""""
      Module widgets
"""""""""""""""""""""""""""

class ModuleList(QTableWidget):
	def __init__(self):
		super().__init__(0, 4)
		self.setHorizontalHeaderLabels(["Name", "Code", "Data", "Entry Point"])
		self.setEditTriggers(self.NoEditTriggers)
		self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		
		events.Connected.connect(self.updateModules)
		
	def updateModules(self):
		modules = debugger.getModuleList()
		self.setRowCount(len(modules))
		for i in range(len(modules)):
			module = modules[i]
			textEnd = module.textAddr + module.textSize
			dataEnd = module.dataAddr + module.dataSize
			self.setItem(i, 0, QTableWidgetItem(module.name))
			self.setItem(i, 1, QTableWidgetItem("%X - %X" %(module.textAddr, textEnd)))
			self.setItem(i, 2, QTableWidgetItem("%X - %X" %(module.dataAddr, dataEnd)))
			self.setItem(i, 3, QTableWidgetItem("%X" %module.entryPoint))
		
		
class ModuleTab(QWidget):
	def __init__(self):
		super().__init__()
		self.moduleList = ModuleList()
		self.updateButton = QPushButton("Update", self)
		self.updateButton.clicked.connect(self.moduleList.updateModules)
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.moduleList)
		self.layout.addWidget(self.updateButton)
		self.setLayout(self.layout)

		
"""""""""""""""""""""""""""
     Breakpoint widgets
"""""""""""""""""""""""""""

class BreakPointList(QListWidget):
	def __init__(self):
		super().__init__()
		self.itemDoubleClicked.connect(self.goToDisassembly)
		events.BreakPointChanged.connect(self.updateList)

	def updateList(self):
		self.clear()
		for bp in debugger.breakpoints:
			self.addItem("0x%08X" %bp)

	def goToDisassembly(self, item):
		address = debugger.breakpoints[self.row(item)]
		window.mainWidget.tabWidget.disassemblyTab.disassemblyWidget.setBase(address)
		window.mainWidget.tabWidget.setCurrentIndex(1)


class BreakPointTab(QWidget):
	def __init__(self):
		super().__init__()
		self.list = BreakPointList()
		self.button = QPushButton("Remove")
		self.button.clicked.connect(self.removeBreakPoint)
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.list)
		self.layout.addWidget(self.button)
		self.setLayout(self.layout)

	def removeBreakPoint(self):
		if self.list.currentRow() != -1:
			debugger.toggleBreakPoint(debugger.breakpoints[self.list.currentRow()])

			
"""""""""""""""""""""""""""
     Exception widgets
"""""""""""""""""""""""""""

class ExceptionThreadList(QTableWidget):

	itemSelected = pyqtSignal(object)

	def __init__(self, title):
		super().__init__(0, 1)
		
		self.setHorizontalHeaderLabels([title])
		
		self.setEditTriggers(self.NoEditTriggers)
		self.setSelectionMode(QAbstractItemView.NoSelection)
		self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.verticalHeader().hide()
		
		self.currentItem = None
		self.itemDoubleClicked.connect(self.selectItem)
		
		self.threads = []
		
		events.Closed.connect(self.handleClose)
		
	def getItem(self, state):
		if state.thread in self.threads:
			return self.item(self.threads.index(state.thread), 0)
		
	def addItem(self, state):
		if state.thread not in self.threads:
			thread = debugger.findThread(state.thread)
			if thread and thread.name:
				name = thread.name
			else:
				name = "<%08X>"
			item = QTableWidgetItem(name)
			item.state = state
			self.setRowCount(self.rowCount() + 1)
			self.setItem(self.rowCount() - 1, 0, item)
			self.threads.append(state.thread)
			return item
		else:
			item = self.getItem(state)
			item.state = state
			return item
			
	def removeItem(self, state):
		if state.thread in self.threads:
			index = self.threads.index(state.thread)
			item = self.item(index, 0)
			if item == self.currentItem:
				self.currentItem = None
				self.itemSelected.emit(None)
			self.removeRow(self.threads.index(state.thread))
			self.threads.remove(state.thread)
			
	def selectItem(self, item):
		if item != self.currentItem:
			self.resetSelection()
			item.setBackground(QBrush(QColor(128, 128, 255)))
			self.currentItem = item
		self.itemSelected.emit(item)
		
	def resetSelection(self):
		if self.currentItem:
			self.currentItem.setBackground(QBrush())
		self.currentItem = None
		
	def handleClose(self):
		self.threads = []
		self.currentItem = None
		self.clearContents()
		self.setRowCount(0)


class ExceptionThreads(QWidget):

	itemSelected = pyqtSignal(object)

	def __init__(self):
		super().__init__()
		
		self.pausedThreads = ExceptionThreadList("Paused threads")
		self.pausedThreads.itemSelected.connect(self.handlePauseSelect)
		self.crashedThreads = ExceptionThreadList("Crashed threads")
		self.crashedThreads.itemSelected.connect(self.handleCrashSelect)
		
		layout = QVBoxLayout(self)
		layout.addWidget(self.pausedThreads)
		layout.addWidget(self.crashedThreads)
		
		events.Exception.connect(self.handleException)
		events.Continue.connect(self.handleContinue)
	
	def handlePauseSelect(self, item):
		if item:
			self.crashedThreads.resetSelection()
		self.itemSelected.emit(item)
		
	def handleCrashSelect(self, item):
		if item:
			self.pausedThreads.resetSelection()
		self.itemSelected.emit(item)
		
	def handleException(self, state):
		if state.isFatal():
			self.pausedThreads.removeItem(state)
			item = self.crashedThreads.addItem(state)
			self.crashedThreads.selectItem(item)
		else:
			self.crashedThreads.removeItem(state)
			item = self.pausedThreads.addItem(state)
			self.pausedThreads.selectItem(item)
			
	def handleContinue(self, state):
		self.pausedThreads.removeItem(state)
		self.crashedThreads.removeItem(state)

		
class ExceptionInfo(QGroupBox):
	def __init__(self):
		super().__init__("Info")
		self.typeLabel = QLabel()

		self.layout = QVBoxLayout(self)
		self.layout.addWidget(self.typeLabel)

	def setState(self, state):
		self.typeLabel.setText("Type: %s" %state.exceptionName)
		
		
class SpecialRegisters(QGroupBox):
	def __init__(self):
		super().__init__("Special registers")
		self.cr = QLabel()
		self.lr = QLabel()
		self.ctr = QLabel()
		self.xer = QLabel()
		self.srr0 = QLabel()
		self.srr1 = QLabel()
		self.ex0 = QLabel()
		self.ex1 = QLabel()

		self.userLayout = QFormLayout()
		self.kernelLayout = QFormLayout()

		self.userLayout.addRow("CR:", self.cr)
		self.userLayout.addRow("LR:", self.lr)
		self.userLayout.addRow("CTR:", self.ctr)
		self.userLayout.addRow("XER:", self.xer)

		self.kernelLayout = QFormLayout()
		self.kernelLayout.addRow("SRR0:", self.srr0)
		self.kernelLayout.addRow("SRR1:", self.srr1)
		self.kernelLayout.addRow("EX0:", self.ex0)
		self.kernelLayout.addRow("EX1:", self.ex1)

		self.layout = QHBoxLayout(self)
		self.layout.addLayout(self.userLayout)
		self.layout.addLayout(self.kernelLayout)

	def setState(self, state):
		self.cr.setText("%08X" %state.cr)
		self.lr.setText("%08X" %state.lr)
		self.ctr.setText("%08X" %state.ctr)
		self.xer.setText("%08X" %state.xer)
		self.srr0.setText("%08X" %state.srr0)
		self.srr1.setText("%08X" %state.srr1)
		self.ex0.setText("%08X" %state.ex0)
		self.ex1.setText("%08X" %state.ex1)
		
	
class ExceptionInfoTab(QWidget):
	def __init__(self):
		super().__init__()
		self.exceptionInfo = ExceptionInfo()
		self.specialRegisters = SpecialRegisters()
		
		self.layout = QHBoxLayout(self)
		self.layout.addWidget(self.exceptionInfo)
		self.layout.addWidget(self.specialRegisters)
		
	def setState(self, state):
		self.exceptionInfo.setState(state)
		self.specialRegisters.setState(state)

	
class RegisterTab(QWidget):
	def __init__(self):
		super().__init__()
		self.gprLabels = []
		self.gprBoxes = []
		self.fprLabels = []
		self.fprBoxes = []
		for i in range(32):
			self.gprLabels.append(QLabel("r%i" %i))
			self.fprLabels.append(QLabel("f%i" % i))
			gprBox = HexSpinBox()
			fprBox = QDoubleSpinBox()
			fprBox.setRange(float("-inf"), float("inf"))
			self.gprBoxes.append(gprBox)
			self.fprBoxes.append(fprBox)

		self.layout = QGridLayout(self)
		for i in range(32):
			self.layout.addWidget(self.gprLabels[i], i % 16, i // 16 * 2)
			self.layout.addWidget(self.gprBoxes[i], i % 16, i // 16 * 2 + 1)
			self.layout.addWidget(self.fprLabels[i], i % 16, i // 16 * 2 + 4)
			self.layout.addWidget(self.fprBoxes[i], i % 16, i // 16 * 2 + 5)

		self.pokeButton = QPushButton("Poke")
		self.resetButton = QPushButton("Reset")
		self.pokeButton.clicked.connect(self.pokeRegisters)
		self.resetButton.clicked.connect(self.updateRegisters)
		self.layout.addWidget(self.pokeButton, 16, 0, 1, 4)
		self.layout.addWidget(self.resetButton, 16, 4, 1, 4)

		self.setEditEnabled(False)

		events.Step.connect(self.handleStep)

	def setState(self, state):
		self.state = state
		self.updateRegisters()
		self.setEditEnabled(state.isBreakPoint() and not state.stepping)
		
	def handleStep(self, state):
		if state == self.state:
			self.setEditEnabled(False)
		
	def setEditEnabled(self, enabled):
		for i in range(32):
			self.gprBoxes[i].setEnabled(enabled)
			self.fprBoxes[i].setEnabled(enabled)
		self.pokeButton.setEnabled(enabled)
		self.resetButton.setEnabled(enabled)
		
	def updateRegisters(self):
		for i in range(32):
			self.gprBoxes[i].setValue(self.state.gpr[i])
			self.fprBoxes[i].setValue(self.state.fpr[i])

	def pokeRegisters(self):
		for i in range(32):
			self.state.gpr[i] = self.gprBoxes[i].value()
			self.state.fpr[i] = self.fprBoxes[i].value()
		debugger.pokeRegisters(self.state)

	
class StackTrace(QListWidget):
	def setState(self, state):
		self.clear()
		stackTrace = debugger.getStackTrace(state)
		for address in (state.srr0, state.lr) + stackTrace:
			self.addItem("%X" %address)
	
class StackTraceTab(QWidget):
	def __init__(self):
		super().__init__()
		self.stackTrace = StackTrace()
		self.disassembly = DisassemblyWidget()
		
		layout = QHBoxLayout(self)
		layout.addWidget(self.stackTrace)
		layout.addWidget(self.disassembly)
		
		self.stackTrace.itemDoubleClicked.connect(self.jumpDisassembly)
		
		events.Step.connect(self.handleStep)
		
	def handleStep(self, state):
		self.disassembly.setCurrentInstruction(None)
		
	def setState(self, state):
		self.stackTrace.setState(state)
		if not state.stepping:
			self.disassembly.setCurrentInstruction(state.srr0)
		else:
			self.disassembly.setCurrentInstruction(None)
	
	def jumpDisassembly(self, item):
		self.disassembly.setCurrentInstruction(int(item.text(), 16))
	

class ExceptionStateTabs(QTabWidget):
	def __init__(self):
		super().__init__()
		self.infoTab = ExceptionInfoTab()
		self.registerTab = RegisterTab()
		self.stackTab = StackTraceTab()
		self.addTab(self.infoTab, "General")
		self.addTab(self.registerTab, "Registers")
		self.addTab(self.stackTab, "Stack trace")
		
	def setState(self, state):
		self.infoTab.setState(state)
		self.registerTab.setState(state)
		self.stackTab.setState(state)
		
		
class BreakpointActions(QWidget):
	def __init__(self):
		super().__init__()
		
		self.continueButton = QPushButton("Continue")
		self.continueButton.clicked.connect(self.continueThread)
		self.stepButton = QPushButton("Step")
		self.stepButton.clicked.connect(self.stepInto)
		self.stepOverButton = QPushButton("Step over")
		self.stepOverButton.clicked.connect(self.stepOver)
		
		layout = QHBoxLayout(self)
		layout.addWidget(self.continueButton)
		layout.addWidget(self.stepButton)
		layout.addWidget(self.stepOverButton)
		
		self.state = None
		
	def setState(self, state):
		self.state = state
		if state.isFatal():
			self.continueButton.hide()
			self.stepButton.hide()
			self.stepOverButton.hide()
		else:
			self.continueButton.show()
			self.stepButton.show()
			self.stepOverButton.show()
			
	def continueThread(self): debugger.continueThread(self.state)
	def stepInto(self): debugger.stepInto(self.state)
	def stepOver(self): debugger.stepOver(self.state)

	
class ExceptionStateWidget(QTabWidget):
	def __init__(self):
		super().__init__()
		
		self.exceptionTabs = ExceptionStateTabs()
		self.breakpointActions = BreakpointActions()
		
		layout = QVBoxLayout(self)
		layout.addWidget(self.exceptionTabs)
		layout.addWidget(self.breakpointActions)
		
		events.Step.connect(self.handleStep)
		
	def setState(self, state):
		self.exceptionTabs.setState(state)
		self.breakpointActions.setState(state)
		self.breakpointActions.setEnabled(not state.stepping)
		
	def handleStep(self, state):
		self.breakpointActions.setEnabled(False)
			
			
class ExceptionTab(QSplitter):
	def __init__(self):
		super().__init__()
		self.threadList = ExceptionThreads()
		self.threadList.itemSelected.connect(self.handleItemSelected)
		self.stateWidget = ExceptionStateWidget()
		self.stateWidget.setEnabled(False)
		self.addWidget(self.threadList)
		self.addWidget(self.stateWidget)
		
		self.setSizes([100, 400])
		
		events.Closed.connect(self.handleClose)
		
	def handleItemSelected(self, item):
		if item:
			self.stateWidget.setState(item.state)
			self.stateWidget.setEnabled(True)
		else:
			self.stateWidget.setEnabled(False)
			
	def handleClose(self):
		self.stateWidget.setEnabled(False)

		
"""""""""""""""""""""""""""
        Main widgets
"""""""""""""""""""""""""""

class DebuggerTabs(QTabWidget):
	def __init__(self):
		super().__init__()
		self.memoryTab = MemoryTab()
		self.disassemblyTab = DisassemblyTab()
		self.threadingTab = ThreadingTab()
		self.moduleTab = ModuleTab()
		self.breakPointTab = BreakPointTab()
		self.exceptionTab = ExceptionTab()
		self.addTab(self.memoryTab, "Memory")
		self.addTab(self.disassemblyTab, "Disassembly")
		self.addTab(self.threadingTab, "Threads")
		self.addTab(self.moduleTab, "Modules")
		self.addTab(self.breakPointTab, "Breakpoints")
		self.addTab(self.exceptionTab, "Exceptions")

		events.Exception.connect(self.exceptionOccurred)
		events.Connected.connect(self.connected)
		events.Closed.connect(self.disconnected)

	def exceptionOccurred(self, state):
		self.setCurrentIndex(5) #Exceptions

	def connected(self):
		self.setEnabled(True)

	def disconnected(self):
		self.setEnabled(False)


class StatusWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.serverLabel = QLabel("Wii U IP:")
		self.serverBox = QLineEdit(self)
		self.serverBox.returnPressed.connect(self.connect)
		self.connectButton = QPushButton("Connect", self)
		self.connectButton.clicked.connect(self.connect)
		self.disconnectButton = QPushButton("Disconnect", self)
		self.disconnectButton.clicked.connect(debugger.close)
		self.disconnectButton.setEnabled(False)

		self.statusInfo = QLabel("Disconnected", self)

		self.layout = QGridLayout()
		self.layout.addWidget(self.serverLabel, 0, 0)
		self.layout.addWidget(self.serverBox, 1, 0)
		self.layout.addWidget(self.connectButton, 0, 1)
		self.layout.addWidget(self.disconnectButton, 1, 1)
		self.layout.addWidget(self.statusInfo, 3, 0, 1, 2)
		self.setLayout(self.layout)

		events.Connected.connect(self.connected)
		events.Closed.connect(self.disconnected)

	def connect(self):
		try:
			address = self.serverBox.text()
			debugger.connect(address)
		except:
			pass

	def connected(self):
		self.statusInfo.setText("Connected")
		self.connectButton.setEnabled(False)
		self.serverBox.setEnabled(False)
		self.disconnectButton.setEnabled(True)

	def disconnected(self):
		self.statusInfo.setText("Disconnected")
		self.connectButton.setEnabled(True)
		self.serverBox.setEnabled(True)
		self.disconnectButton.setEnabled(False)


class MainWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.tabWidget = DebuggerTabs()
		self.statusWidget = StatusWidget()
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.tabWidget)
		self.layout.addWidget(self.statusWidget)
		self.tabWidget.setEnabled(False)
		self.setLayout(self.layout)


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("DiiBugger")
		self.resize(1080, 720)
	
		self.mainWidget = MainWidget()
		self.setCentralWidget(self.mainWidget)
		
		self.timer = QTimer(self)
		self.timer.setInterval(100)
		self.timer.timeout.connect(self.updateMessages)
		self.timer.start()
		
		events.Connected.connect(self.updateTitle)
		events.Closed.connect(self.updateTitle)
		
	def updateTitle(self):
		if debugger.connected:
			name = debugger.getModuleName()
			self.setWindowTitle("DiiBugger - %s" %name)
		else:
			self.setWindowTitle("DiiBugger")
			
	def updateMessages(self):
		if debugger.connected:
			debugger.updateMessages()


if __name__ == "__main__":
	app = QApplication(sys.argv)
	app.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
	window = MainWindow()
	window.show()
	app.exec()
