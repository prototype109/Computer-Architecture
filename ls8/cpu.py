"""CPU functionality."""

import sys
import fileio

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.dispatchtable = {}
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.ir = HLT
        self.fl = 0
        self.dispatchtable[LDI] = self.ldi
        self.dispatchtable[PRN] = self.prn
        self.dispatchtable[PUSH] = self.push
        self.dispatchtable[POP] = self.pop
        self.dispatchtable[CALL] = self.call
        self.dispatchtable[RET] = self.ret
        self.dispatchtable[JMP] = self.jmp
        self.dispatchtable[JEQ] = self.jeq
        self.dispatchtable[JNE] = self.jne

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = fileio.command_list

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def ram_read(self, pc):
        return self.ram[pc]

    def ram_write(self, value, pc):
        self.ram[pc] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == CMP:
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            else:
                self.fl = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ldi(self):
        register = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[register] = value

    def prn(self):
        register = self.ram_read(self.pc + 1)
        value = self.reg[register]
        print(value)

    def push(self):
        self.reg[7] -= 1
        current_sp = self.reg[7]
        register = self.ram_read(self.pc + 1)
        value = self.reg[register]
        self.ram_write(value, current_sp)

    def pop(self):
        current_sp = self.reg[7]
        value = self.ram_read(current_sp)
        register = self.ram_read(self.pc + 1)
        self.reg[register] = value
        self.reg[7] += 1

    def call(self):
        # Push next command onto stack
        self.reg[7] -= 1
        current_sp = self.reg[7]
        self.ram_write(self.pc + 2, current_sp)

        #Point PC to subroutine
        self.jmp()

    def ret(self):
        current_sp = self.reg[7]
        value = self.ram_read(current_sp)
        self.pc = value
        self.reg[7] += 1

    def jmp(self):
        register = self.ram_read(self.pc + 1)
        value = self.reg[register]
        self.pc = value

    def jeq(self):
        if self.fl & 0b00000001:
            self.jmp()
        else:
            self.pc += 2

    def jne(self):
        if not self.fl & 0b00000001:
            self.jmp()
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""
        self.reg[7] = 0xF4 
        self.ir = self.ram[self.pc]

        command = self.ir

        while command != HLT:

            self.ir = self.ram[self.pc]

            command = self.ir
            num_operands = self.ir >> 6
            is_alu = self.ir >> 5 & 0b00000001
            set_pc = self.ir >> 4 & 0b00000001

            if is_alu:
                self.alu(command, self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
            elif command != HLT:
                self.dispatchtable[command]()

            if not set_pc:
                self.pc += num_operands + 1
