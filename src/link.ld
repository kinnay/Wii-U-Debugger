
OUTPUT(diibugger.elf)

ENTRY(entryPoint)

SECTIONS {
	. = 0x00802000;
	.text : {
		*(.text*);
	}
	.rodata : {
		*(.rodata*);
	}
	.data : {
		*(.data*);
		*(.sdata*);
	}
	.bss : {
		*(.bss*);
		*(.sbss*);
	}
	
	/DISCARD/ : {
		*(*);
	}
}
