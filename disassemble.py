
trap_condition_table = {
	1: "lgt",
	2: "llt",
	4: "eq",
	5: "lge",
	6: "lle",
	8: "gt",
	12: "ge",
	16: "lt",
	20: "le",
	24: "ne",
	31: "u"
}

spr_table_suffix = {
	1: "xer",
	8: "lr",
	9: "ctr"
}

spr_table = {}

def decodeI(value):
	return (value >> 2) & 0xFFFFFF, (value >> 1) & 1, value & 1

def decodeB(value):
	return (value >> 21) & 0x1F, (value >> 16) & 0x1F, (value >> 2) & 0x3FFF, (value >> 1) & 1, value & 1

def decodeD(value):
	return (value >> 21) & 0x1F, (value >> 16) & 0x1F, value & 0xFFFF

def decodeX(value):
	return (value >> 21) & 0x1F, (value >> 16) & 0x1F, (value >> 11) & 0x1F, value & 1
	
def decodeABC(value):
	return (value >> 21) & 0x1F, (value >> 16) & 0x1F, (value >> 11) & 0x1F, (value >> 6) & 0x1F, value & 1
	
def decodeR(value):
	return (value >> 21) & 0x1F, (value >> 16) & 0x1F, (value >> 11) & 0x1F, (value >> 6) & 0x1F, (value >> 1) & 0x1F, value & 1

def extend_sign(value, bits=16):
	if value & 1 << (bits - 1):
		value -= 1 << bits
	return value

def ihex(value):
	sign = "-" if value < 0 else ""
	return "%s0x%X" %(sign, abs(value))
	
	
condition_table_true = ["lt", "gt", "eq"]
condition_table_false = ["ge", "le", "ne"]

def decode_cond_true(BI):
	if BI % 4 < 3:
		return condition_table_true[BI % 4]
		
def decode_cond_false(BI):
	if BI % 4 < 3:
		return condition_table_false[BI % 4]

def decode_cond(BO, BI):
	ctr = ""
	if not BO & 4:
		if BO & 2:
			ctr = "dz"
		else:
			ctr = "dnz"
			
	cond = ""
	if not BO & 16:
		if BO & 8:
			cond = decode_cond_true(BI)
		else:
			cond = decode_cond_false(BI)
			
	if cond is not None:
		return ctr + cond
	
	
NO_SWAP = False
SWAP = True

UNSIGNED = False
SIGNED = True

def decode_simple(instr):
	def decode(value, addr):
		D, A, B, Rc = decodeX(value)
		if D or A or B or Rc:
			return "???"
		return instr
	return decode

def decode_triple_reg(instr, swap):
	def decode(value, addr):
		D, A, B, Rc = decodeX(value)
		if swap:
			D, A = A, D
		return "%s%s" %(instr, "." * Rc), "r%i, r%i, r%i" %(D, A, B)
	return decode
	
def decode_double_reg(instr, swap):
	def decode(value, addr):
		D, A, B, Rc = decodeX(value)
		if B != 0:
			return "???"
		if swap:
			D, A = A, D
		return "%s%s" %(instr, "." * Rc), "r%i, r%i" %(D, A)
	return decode
	
def decode_single_reg(instr):
	def decode(value, addr):
		D, A, B, Rc = decodeX(value)
		if A or B or Rc:
			return "???"
		return instr, "r%i" %D
	return decode
	
def decode_double_reg_imm(instr, sign, swap):
	def decode(value, addr):
		D, A, IMM = decodeD(value)
		if sign:
			IMM = extend_sign(IMM)
		if swap:
			D, A = A, D
		return instr, "r%i, r%i, %s" %(D, A, ihex(IMM))
	return decode
	
def decode_triple_cr(instr, simple1, simple2):
	def decode(value, addr):
		D, A, B, pad = decodeX(value)
		if pad:
			return "???"
		if D == A == B and simple1:
			return simple1, "cr%i" %D
		if A == B and simple2:
			return simple2, "cr%i, cr%i" %(D, A)
		return instr, "cr%i, cr%i, cr%i" %(D, A, B)
	return decode
	
def decode_single_cr(instr, rc_ok):
	def decode(value, addr):
		D, A, B, Rc = decodeX(value)
		if A or B or (Rc and not rc_ok):
			return "???"
		return instr + "." * Rc, "cr%i" %D
	return decode
	
def decode_compare_reg(instr):
	def decode(value, addr):
		cr, A, B, pad = decodeX(value)
		if cr & 3 or pad:
			return "???"

		if cr == 0:
			return instr, "r%i, r%i" %(A, B)
		return instr, "cr%i, r%i, r%i" %(cr >> 2, A, B)
	return decode

def decode_compare_imm(instr, sign):
	def decode(value, addr):
		cr, A, IMM = decodeD(value)
		if cr & 3:
			return "???"

		if sign:
			IMM = extend_sign(IMM)
		
		if cr == 0:
			return instr, "r%i, %s" %(A, ihex(IMM))
		return instr, "cr%i, r%i, %s" %(cr >> 2, A, ihex(IMM))
	return decode
		
def decode_branch_to_reg(reg):
	def decode(value, addr):
		BO, BI, pad, LK = decodeX(value)
		if pad:
			return "???"

		cond = decode_cond(BO, BI)
		suffix = "l" * LK
		
		if cond is None:
			return "bc%s%s" %(reg, suffix), "%i, %i" %(BO, BI)
			
		instr = "b%s%s%s" %(cond, reg, suffix)
		if BI >= 4:
			return instr, "cr%i" %(BI // 4)
		return instr
	return decode
	
def decode_double_float(instr):
	def decode(value, addr):
		D, A, B, Rc = decodeX(value)
		if A != 0:
			return "???"
		return "%s%s" %(instr, "." * Rc), "f%i, f%i" %(D, B)
	return decode

def decode_triple_float(instr):
	def decode(value, addr):
		D, A, B, Rc = decodeX(value)
		return "%s%s" %(instr, "." * Rc), "f%i, f%i, f%i" %(D, A, B)
	return decode
	
def decode_triple_float_alt(instr):
	def decode(value, addr):
		D, A, B, C, Rc = decodeABC(value)
		if B != 0:
			return "???"
		return "%s%s" %(instr, "." * Rc), "f%i, f%i, f%i" %(D, A, C)
	return decode
	
def decode_quad_float(instr):
	def decode(value, addr):
		D, A, B, C, Rc = decodeABC(value)
		return "%s%s" %(instr, "." * Rc), "f%i, f%i, f%i, f%i" %(D, A, C, B)
	return decode
	
def decode_compare_float(instr):
	def decode(value, addr):
		cr, A, B, pad = decodeX(value)
		if cr & 3 or pad:
			return "???"
		return instr, "cr%i, f%i, f%i" %(cr >> 2, A, B)
	return decode
	
def decode_memory(instr):
	def decode(value, addr):
		D, A, d = decodeD(value)
		d = extend_sign(d)
		return instr, "r%i, %s(r%i)" %(D, ihex(d), A)
	return decode
	
def decode_memory_indexed(instr):
	def decode(value, addr):
		D, A, B, Rc = decodeX(value)
		if Rc:
			return "???"
		if A == 0:
			return instr, "r%i, 0, r%i" %(D, B)
		return instr, "r%i, r%i, r%i" %(D, A, B)
	return decode
	
def decode_memory_float(instr):
	def decode(value, addr):
		D, A, d = decodeD(value)
		A = extend_sign(A)
		return instr, "f%i, %s(r%i)" %(D, ihex(d), A)
	return decode
	
def decode_memory_float_indexed(instr):
	def decode(value, addr):
		D, A, B, Rc = decodeX(value)
		if Rc:
			return "???"
		if A == 0:
			return instr, "f%i, 0, r%i" %(D, B)
		return instr, "f%i, r%i, r%i" %(D, A, B)
	return decode
	
def decode_cache(instr):
	def decode(value, addr):
		D, A, B, Rc = decodeX(value)
		if D != 0 or Rc != 0:
			return "???"
		return instr, "r%i, r%i" %(A, B)
	return decode


add = decode_triple_reg("add", NO_SWAP)
addc = decode_triple_reg("addc", NO_SWAP)
adde = decode_triple_reg("adde", NO_SWAP)

def addi(value, addr):
	D, A, SIMM = decodeD(value)
	SIMM = extend_sign(SIMM)
	if A == 0:
		return "li", "r%i, %s" %(D, ihex(SIMM))
	return "addi", "r%i, r%i, %s" %(D, A, ihex(SIMM))

addic = decode_double_reg_imm("addic", SIGNED, NO_SWAP)
addic_ = decode_double_reg_imm("addic.", SIGNED, NO_SWAP)

def addis(value, addr):
	D, A, SIMM = decodeD(value)
	SIMM = extend_sign(SIMM)
	if A == 0:
		return "lis", "r%i, %s" %(D, ihex(SIMM))
	return "addis", "r%i, r%i, %s" %(D, A, ihex(SIMM))
	
addme = decode_double_reg("addme", NO_SWAP)
addze = decode_double_reg("addze", NO_SWAP)

and_ = decode_triple_reg("and", SWAP)
andc = decode_triple_reg("andc", SWAP)
andi = decode_double_reg_imm("andi.", UNSIGNED, SWAP)
andis = decode_double_reg_imm("andis.", UNSIGNED, SWAP)

def b(value, addr):
	LI, AA, LK = decodeI(value)
	LI = extend_sign(LI, 24) * 4
	if AA: dst = LI
	else:
		dst = addr + LI
	return "b%s%s" %("l" * LK, "a" * AA), ihex(dst)

def bc(value, addr):
	BO, BI, BD, AA, LK = decodeB(value)
	BD = extend_sign(BD, 14) * 4
	
	suffix = "%s%s" %("l" * LK, "a" * AA)
	
	if AA: dst = BD
	else:
		dst = addr + BD
		
	cond = decode_cond(BO, BI)
	if cond is None:
		return "bc" + suffix, "%i, %i, %s" %(BO, BI, ihex(dst))
	if BI >= 4:
		return "b" + cond + suffix, "cr%i, %s" %(BI // 4, ihex(dst))
	return "b" + cond + suffix, ihex(dst)

bcctr = decode_branch_to_reg("ctr")
bclr = decode_branch_to_reg("lr")

cmp = decode_compare_reg("cmpw")
cmpi = decode_compare_imm("cmpwi", SIGNED)
cmpl = decode_compare_reg("cmplw")
cmpli = decode_compare_imm("cmplwi", UNSIGNED)

cntlzw = decode_double_reg("cntlzw", SWAP)

crand = decode_triple_cr("crand", None, None)
crandc = decode_triple_cr("crandc", None, None)
creqv = decode_triple_cr("creqv", "crset", None)
crnand = decode_triple_cr("crnand", None, None)
crnor = decode_triple_cr("crnor", None, "crnot")
cror = decode_triple_cr("cror", None, "crmove")
crorc = decode_triple_cr("crorc", None, None)
crxor = decode_triple_cr("crxor", "crclr", None)

dcba = decode_cache("dcba")
dcbf = decode_cache("dcbf")
dcbi = decode_cache("dcbi")
dcbst = decode_cache("dcbst")
dcbt = decode_cache("dcbt")
dcbtst = decode_cache("dcbtst")
dcbz = decode_cache("dcbz")

divw = decode_triple_reg("divw", NO_SWAP)
divwu = decode_triple_reg("divwu", NO_SWAP)

eieio = decode_simple("eieio")

eqv = decode_triple_reg("eqv", SWAP)

extsb = decode_double_reg("extsb", SWAP)
extsh = decode_double_reg("extsh", SWAP)

fabs = decode_double_float("fabs")
fadd = decode_triple_float("fadd")
fadds = decode_triple_float("fadds")
fcmpo = decode_compare_float("fcmpo")
fcmpu = decode_compare_float("fcmpu")
fctiw = decode_double_float("fctiw")
fctiwz = decode_double_float("fctiwz")
fdiv = decode_triple_float("fdiv")
fdivs = decode_triple_float("fdivs")
fmadd = decode_quad_float("fmadd")
fmadds = decode_quad_float("fmadds")
fmr = decode_double_float("fmr")
fmsub = decode_quad_float("fmsub")
fmsubs = decode_quad_float("fmsubs")
fmul = decode_triple_float_alt("fmul")
fmuls = decode_triple_float_alt("fmuls")
fnabs = decode_double_float("fnabs")
fneg = decode_double_float("fneg")
fnmadd = decode_quad_float("fnmadd")
fnmadds = decode_quad_float("fnmadds")
fnmsub = decode_quad_float("fnmsub")
fnmsubs = decode_quad_float("fnmsubs")
fres = decode_double_float("fres")
frsp = decode_double_float("frsp")
fsel = decode_quad_float("fsel")
fsqrte = decode_double_float("fsqrte")
fsqrt = decode_double_float("fsqrt")
fsqrts = decode_double_float("fsqrts")
fsub = decode_triple_float("fsub")
fsubs = decode_triple_float("fsubs")

icbi = decode_cache("icbi")
isync = decode_simple("isync")

lbz = decode_memory("lbz")
lbzu = decode_memory("lbzu")
lbzux = decode_memory_indexed("lbzux")
lbzx = decode_memory_indexed("lbzx")
lfd = decode_memory_float("lfd")
lfdu = decode_memory_float("lfdu")
lfdux = decode_memory_float_indexed("lfdux")
lfdx = decode_memory_float_indexed("lfdx")
lfs = decode_memory_float("lfs")
lfsu = decode_memory_float("lfsu")
lfsux = decode_memory_float_indexed("lfsux")
lfsx = decode_memory_float_indexed("lfsx")
lha = decode_memory("lha")
lhau = decode_memory("lhau")
lhaux = decode_memory_indexed("lhaux")
lhax = decode_memory_indexed("lhax")
lhbrx = decode_memory_indexed("lhbrx")
lhz = decode_memory("lhz")
lhzu = decode_memory("lhzu")
lhzux = decode_memory_indexed("lhzux")
lhzx = decode_memory_indexed("lhzx")
lmw = decode_memory("lmw")

def lswi(value, addr):
	D, A, NB, Rc = decodeX(value)
	if Rc:
		return "???"
	return "lswi", "r%i, r%i, %i" %(D, A, NB)
	
lswx = decode_memory_indexed("lswx")
lwarx = decode_memory_indexed("lwarx")
lwbrx = decode_memory_indexed("lwbrx")
lwz = decode_memory("lwz")
lwzu = decode_memory("lwzu")
lwzux = decode_memory_indexed("lwzux")
lwzx = decode_memory_indexed("lwzx")

def mcrf(value, addr):
	crD, crS, pad1, pad2 = decodeX(value)
	if crD & 3 or crS & 3 or pad1 or pad2:
		return "???"
	return "mcrf", "cr%i, cr%i" %(crD, crS)
	
def mcrfs(value, addr):
	crD, crS, pad1, pad2 = decodeX(value)
	if crD & 3 or crS & 3 or pad1 or pad2:
		return "???"
	return "mcrfs", "cr%i, cr%i" %(crD, crS)
	
mcrxr = decode_single_cr("mcrxr", False)

mfcr = decode_single_reg("mfcr")

def mffs(value, addr):
	D, A, B, Rc = decodeX(value)
	if A or B:
		return "???"
	return "mffs%s" %("." * Rc), "f%i" %D
	
mfmsr = decode_single_reg("mfmsr")

def mfspr(value, addr):
	D, lo, hi, pad = decodeX(value)
	spr = (hi << 5) | lo
	
	if pad:
		return "???"
		
	if spr in spr_table_suffix:
		return "mf%s" %spr_table_suffix[spr], "r%i" %D
	if spr in spr_table:
		return "mfspr", "r%i, %s" %(D, spr_table[spr])
	return "mfspr", "r%i, %i" %(D, spr)
	
def mfsr(value, addr):
	D, SR, pad1, pad2 = decodeX(value)
	if pad1 or pad2 or SR > 15:
		return "???"
	return "mfsr", "r%i, %i" %(D, SR)
	
def mfsrin(value, addr):
	D, A, B, Rc = decodeX(value)
	if A or Rc:
		return "???"
	return "mfsrin", "r%i, r%i" %(D, B)
	
def mftb(value, addr):
	D, lo, hi, pad = decodeX(value)
	tbr = (hi << 5) | lo

	if pad:
		return "???"
		
	if tbr == 268: return "mftb", "r%i" %D
	if tbr == 269: return "mftbu", "r%i" %D
	return "???"
	
def mtcrf(value, addr):
	S, hi, lo, pad = decodeX(value)
	if lo & 1 or hi & 16 or pad:
		return "???"
	mask = (hi << 4) | (lo >> 1)
	if mask == 0xFF:
		return "mtcr", "r%i" %S
	return "mtcrf", "%s, r%i" %(ihex(mask), S)
	
mtfsb0 = decode_single_cr("mtfsb0", True)
mtfsb1 = decode_single_cr("mtfsb1", True)

def mtfsf(value, addr):
	hi, lo, B, Rc = decodeX(value)
	if lo & 1 or hi & 16:
		return "???"
	mask = (hi << 4) | (lo >> 1)
	return "mtfsf" + "." * Rc, "%s, f%i" %(ihex(mask), B)
	
def mtfsfi(value, addr):
	cr, pad, IMM, Rc = decodeX(value)
	if cr & 3 or pad or IMM & 1:
		return "???"
	return "mtfsfi" + "." * Rc, "cr%i, %i" %(cr >> 2, IMM >> 1)
	
mtmsr = decode_single_reg("mtmsr")

def mtspr(value, addr):
	S, lo, hi, pad = decodeX(value)
	spr = (hi << 5) | lo
	
	if pad:
		return "???"
		
	if spr in spr_table_suffix:
		return "mt%s" %spr_table_suffix[spr], "r%i" %S
	if spr in spr_table:
		return "mtspr", "%s, r%i" %(spr_table[spr], S)
	return "mtspr", "%i, r%i" %(spr, S)

def mtsr(value, addr):
	S, SR, pad1, pad2 = decodeX(value)
	if pad1 or pad2 or SR > 15:
		return "???"
	return "mtsr", "%i, %ri" %(SR, S)
	
def mtsrin(value, addr):
	S, A, B, Rc = decodeX(value)
	if A or Rc:
		return "???"
	return "mtsrin", "r%i, r%i" %(S, B)
	
mulhw = decode_triple_reg("mulhw", NO_SWAP)
mulhwu = decode_triple_reg("mulhwu", NO_SWAP)
mulli = decode_double_reg_imm("mulli", SIGNED, NO_SWAP)
mullwu = decode_triple_reg("mullwu", NO_SWAP)
nand = decode_triple_reg("nand", SWAP)
neg = decode_double_reg("neg", NO_SWAP)

def nor(value, addr):
	S, A, B, Rc = decodeX(value)
	if S == B:
		return "not" + "." * Rc, "r%i, r%i" %(A, S)
	return "nor" + "." * Rc, "r%i, r%i, r%i" %(A, S, B)	
	
def or_(value, addr):
	S, A, B, Rc = decodeX(value)
	if S == B:
		return "mr" + "." * Rc, "r%i, r%i" %(A, S)
	return "or" + "." * Rc, "r%i, r%i, r%i" %(A, S, B)

orc = decode_triple_reg("orc", SWAP)

def ori(value, addr):
	S, A, UIMM = decodeD(value)
	if UIMM == 0:
		return "nop"
	return "ori", "r%i, r%i, %s" %(A, S, ihex(UIMM))

oris = decode_double_reg_imm("oris", UNSIGNED, SWAP)

rfi = decode_simple("rfi")

def rlwimi(value, addr):
	S, A, SH, MB, ME, Rc = decodeR(value)
	suffix = "." * Rc
	if SH == 32 - MB and ME >= MB:
		return "inslwi" + suffix, "r%i, r%i, %i, %i" %(A, S, ME - MB + 1, MB)
	if MB < 31 and SH + ME == 32:
		return "insrwi" + suffix, "r%i, r%i, %i, %i" %(A, S, 32 - MB - SH, MB)
	return "rlwimi" + suffix, "r%i, r%i, %i, %i, %i" %(A, S, SH, MB, ME)
	
def rlwinm(value, addr):
	S, A, SH, MB, ME, Rc = decodeR(value)
	suffix = "." * Rc
	if MB == 0 and ME == 31 - SH:
		return "slwi" + suffix, "r%i, r%i, %i" %(A, S, SH)
	if ME == 31 and SH == 32 - MB:
		return "srwi" + suffix, "r%i, r%i, %i" %(A, S, MB)
	if MB == 0 and ME < 31:
		return "extlwi" + suffix, "r%i, r%i, %i, %i" %(A, S, ME + 1, SH)
	if ME == 31 and SH >= 32 - MB:
		return "extrwi" + suffix, "r%i, r%i, %i, %i" %(A, S, 32 - MB, SH + MB - 32)
	if MB == 0 and ME == 31:
		if SH >= 16:
			return "rotlwi" + suffix, "r%i, r%i, %i" %(A, S, SH)
		return "rotrwi" + suffix, "r%i, r%i, %i" %(A, S, 32 - SH)
	if SH == 0 and ME == 31:
		return "clrlwi" + suffix, "r%i, r%i, %i" %(A, S, MB)
	if SH == 0 and MB == 0:
		return "clrrwi" + suffix, "r%i, r%i, %i" %(A, S, 31 - ME)
	if ME == 31 - SH and MB + SH < 32:
		return "clrlslwi" + suffix, "r%i, r%i, %i, %i" (MB + SH, SH)
	return "rlwinm" + suffix, "r%i, r%i, %i, %i, %i" %(A, S, SH, MB, ME)
	
def rlwnm(value, addr):
	S, A, B, MB, ME, Rc = decodeR(value)
	suffix = "." * Rc
	if MB == 0 and ME == 31:
		return "rotlw" + suffix, "r%i, r%i, r%i" %(A, S, B)
	return "rlwnm" + suffix, "r%i, r%i, r%i, %i, %i" %(A, S, B, MB, ME)
	
sc = decode_simple("sc")

slw = decode_triple_reg("slw", SWAP)
sraw = decode_triple_reg("sraw", SWAP)

def srawi(value, addr):
	S, A, SH, Rc = decodeX(value)
	return "srawi" + "." * Rc, "r%i, r%i, %i" %(A, S, SH)
	
srw = decode_triple_reg("srw", SWAP)

stb = decode_memory("stb")
stbu = decode_memory("stbu")
stbux = decode_memory_indexed("stbux")
stbx = decode_memory_indexed("stbx")
stfd = decode_memory_float("stfd")
stfdu = decode_memory_float("stfdu")
stfdux = decode_memory_float_indexed("stfdux")
stfdx = decode_memory_float_indexed("stfdx")
stfiwx = decode_memory_float_indexed("stfiwx")
stfs = decode_memory_float("stfs")
stfsu = decode_memory_float("stfsu")
stfsux = decode_memory_float_indexed("stfsux")
stfsx = decode_memory_float_indexed("stfsx")
sth = decode_memory("sth")
sthbrx = decode_memory_indexed("sthbrx")
sthu = decode_memory("sthu")
sthux = decode_memory_indexed("sthux")
sthx = decode_memory_indexed("sthx")
stmw = decode_memory("stmw")

def stswi(value, addr):
	S, A, NB, Rc = decodeX(value)
	if Rc:
		return "???"
	return "stswi", "r%i, r%i, %i" %(S, A, NB)
	
stswx = decode_memory_indexed("stswx")
stw = decode_memory("stw")
stwbrx = decode_memory_indexed("stwbrx")

def stwcx(value, addr):
	S, A, B, Rc = decodeX(value)
	if not Rc:
		return "???"
	return "stwcx.", "r%i, r%i, r%i" %(S, A, B)

stwu = decode_memory("stwu")
stwux = decode_memory_indexed("stwux")
stwx = decode_memory_indexed("stwx")

subf = decode_triple_reg("subf", NO_SWAP)
subfc = decode_triple_reg("subfc", NO_SWAP)
subfe = decode_triple_reg("subfe", NO_SWAP)
subfic = decode_double_reg_imm("subfic", SIGNED, NO_SWAP)
subfme = decode_double_reg("subfme", NO_SWAP)
subfze = decode_double_reg("subfze", NO_SWAP)

sync = decode_simple("sync")
tlbia = decode_simple("tlbia")

def tlbie(value, addr):
	D, A, B, Rc = decodeX(value)
	if D or A or Rc:
		return "???"
	return "tlbie", "r%i" %B
	
tlbsync = decode_simple("tlbsync")

def tw(value, addr):
	TO, A, B, Rc = decodeX(value)
	if Rc:
		return "???"
		
	if TO == 31 and A == 0 and B == 0:
		return "trap"
	
	if TO in trap_condition_table:
		return "tw%s" %trap_condition_table[TO], "r%i, r%i" %(A, B)
	return "tw", "%i, r%i, r%i" %(TO, A, B)
	
def twi(value, addr):
	TO, A, SIMM = decodeD(value)
	SIMM = extend_sign(SIMM)
	
	if TO in trap_condition_table:
		return "tw%si" %trap_condition_table[TO], "r%i, %s" %(A, ihex(SIMM))
	return "twi", "%i, r%i, %s" %(TO, A, ihex(SIMM))
	
xor = decode_triple_reg("xor", SWAP)
xori = decode_double_reg_imm("xori", UNSIGNED, SWAP)
xoris = decode_double_reg_imm("xoris", UNSIGNED, SWAP)


opcode_table_19 = {
	0: mcrf,
	16: bclr,
	33: crnor,
	50: rfi,
	129: crandc,
	150: isync,
	193: crxor,
	225: crnand,
	257: crand,
	289: creqv,
	417: crorc,
	449: cror,
	528: bcctr
}

opcode_table_31 = {
	0: cmp,
	4: tw,
	8: subfc,
	10: addc,
	11: mulhwu,
	19: mfcr,
	20: lwarx,
	23: lwzx,
	24: slw,
	26: cntlzw,
	28: and_,
	32: cmpl,
	40: subf,
	54: dcbst,
	55: lwzux,
	60: andc,
	75: mulhw,
	83: mfmsr,
	86: dcbf,
	87: lbzx,
	119: lbzux,
	124: nor,
	138: adde,
	146: mtmsr,
	150: stwcx,
	151: stwx,
	183: stwux,
	202: addze,
	210: mtsr,
	215: stbx,
	234: addme,
	242: mtsrin,
	246: dcbtst,
	247: stbux,
	266: add,
	278: dcbt,
	279: lhzx,
	284: eqv,
	306: tlbie,
	311: lhzux,
	316: xor,
	339: mfspr,
	343: lhax,
	370: tlbia,
	375: lhaux,
	407: sthx,
	412: orc,
	439: sthux,
	444: or_,
	467: mtspr,
	470: dcbi,
	476: nand,
	512: mcrxr,
	533: lswx,
	534: lwbrx,
	535: lfsx,
	536: srw,
	566: tlbsync,
	567: lfsux,
	595: mfsr,
	597: lswi,
	598: sync,
	599: lfdx,
	631: lfdux,
	659: mfsrin,
	661: stswx,
	662: stwbrx,
	663: stfsx,
	695: stfsux,
	725: stswi,
	727: stfdx,
	758: dcba,
	759: stfdux,
	790: lhbrx,
	792: sraw,
	824: srawi,
	854: eieio,
	918: sthbrx,
	922: extsh,
	954: extsb,
	982: icbi,
	983: stfiwx,
	1014: dcbz
}

opcode_table_59 = {
	18: fdivs,
	20: fsubs,
	21: fadds,
	22: fsqrts,
	24: fres,
	25: fmuls,
	28: fmsubs,
	29: fmadds,
	30: fnmsubs,
	31: fnmadds
}

opcode_table_63 = {
	0: fcmpu,
	12: frsp,
	14: fctiw,
	15: fctiwz,
	18: fdiv,
	20: fsub,
	21: fadd,
	22: fsqrt,
	23: fsel,
	25: fmul,
	26: fsqrte,
	28: fmsub,
	29: fmadd,
	30: fnmsub,
	31: fnmadd,
	32: fcmpo,
	38: mtfsb1,
	40: fneg,
	64: mcrfs,
	70: mtfsb0,
	72: fmr,
	134: mtfsfi,
	136: fnabs,
	264: fabs,
	583: mffs,
	711: mtfsf
}

def opcode19(value, addr):
	XO = (value >> 1) & 0x3FF
	if XO not in opcode_table_19:
		return "???"
	return opcode_table_19[XO](value, addr)

def opcode31(value, addr):
	XO = (value >> 1) & 0x3FF
	if XO not in opcode_table_31:
		return "???"
	return opcode_table_31[XO](value, addr)

def opcode59(value, addr):
	XO = (value >> 1) & 0x1F
	if XO not in opcode_table_59:
		return "???"
	return opcode_table_59[XO](value, addr)

def opcode63(value, addr):
	XO = (value >> 1) & 0x3FF
	if XO not in opcode_table_63:
		return "???"
	return opcode_table_63[XO](value, addr)


opcode_table = {
	3: twi,
	7: mulli,
	8: subfic,
	10: cmpli,
	11: cmpi,
	12: addic,
	13: addic_,
	14: addi,
	15: addis,
	16: bc,
	17: sc,
	18: b,
	19: opcode19,
	20: rlwimi,
	21: rlwinm,
	23: rlwnm,
	24: ori,
	25: oris,
	26: xori,
	27: xoris,
	28: andi,
	29: andis,
	31: opcode31,
	32: lwz,
	33: lwzu,
	34: lbz,
	35: lbzu,
	36: stw,
	37: stwu,
	38: stb,
	39: stbu,
	40: lhz,
	41: lhzu,
	42: lha,
	43: lhau,
	44: sth,
	45: sthu,
	46: lmw,
	47: stmw,
	48: lfs,
	49: lfsu,
	50: lfd,
	51: lfdu,
	52: stfs,
	53: stfsu,
	54: stfd,
	55: stfdu,
	59: opcode59,
	63: opcode63
}

def disassemble(value, address):
	opcode = value >> 26
	if opcode not in opcode_table:
		return "???"
	instr = opcode_table[opcode](value, address)
	if type(instr) == str:
		return instr
	return "%-10s%s" %(instr[0], instr[1])
