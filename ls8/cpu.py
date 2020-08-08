"""CPU functionality."""

import sys
import fileio

HLT = 0b0001
LDI = 0b0010
PRN = 0b0111
ADD = 0b0000
MUL = 0b0010

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.ir = HLT

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
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.ir = self.ram[self.pc]

        command = self.ir & 0b00001111

        while command != HLT:

            self.ir = self.ram[self.pc]

            num_operands = self.ir >> 6
            is_alu = self.ir >> 5 & 0b00000001
            command = self.ir & 0b00001111

            if is_alu:
                self.alu(command, self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
            else:
                if command == LDI:
                    register = self.ram_read(self.pc + 1)
                    value = self.ram_read(self.pc + 2)
                    self.reg[register] = value

                if command == PRN:
                    register = self.ram_read(self.pc + 1)
                    value = self.reg[register]
                    print(value)
                
            self.pc += num_operands + 1
