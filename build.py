
import os
import subprocess

PPC_GCC = r"C:\devkitPro\devkitPPC\bin\powerpc-eabi-g++"

files = []
for dirname, subdirs, subfiles in os.walk("src"):
	for filename in subfiles:
		if filename.endswith(".cpp") or filename.endswith(".c") or \
		   filename.endswith(".S") or filename.endswith(".s"):
			filepath = os.path.join(dirname, filename)
			files.append(filepath)

args = "-O2 -Isrc -fno-exceptions -nostartfiles -T src/link.ld -Wl,-n -Wl,--gc-sections"
subprocess.call("%s %s %s" %(PPC_GCC, args, " ".join(files)))
