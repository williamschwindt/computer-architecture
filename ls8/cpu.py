"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0,0,0,0,0,0,244,0]
        self.pc = 0
        self.sp = self.reg[6]
        self.branch_table = {}
        self.branch_table[0b10000010] = self.LDI
        self.branch_table[0b01000111] = self.PRN
        self.branch_table[0b10100010] = self.MUL
        self.branch_table[0b01000101] = self.PUSH
        self.branch_table[0b01000110] = self.POP
        

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def LDI(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.pc += 3

    def PRN(self, operand_a, operand_b):
        print(self.reg[operand_a])
        self.pc += 2

    def MUL(self, operand_a, operand_b):
        self.alu('MULTIPLY', operand_a, operand_b)
        self.pc += 3

    def PUSH(self, operand_a, operand_b):
        self.sp -= 1
        value = self.reg[operand_a]
        self.ram[self.sp] = value
        self.pc += 2

    def POP(self, operand_a, operand_b):
        value = self.ram[self.sp]
        self.reg[operand_a] = value
        self.sp += 1
        self.pc += 2
        
    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print('usage: cpu.py filename')
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    comment_split = line.split('#')
                    code_snip = comment_split[0].strip()

                    if code_snip == '':
                        continue
                    
                    binary = int(code_snip, 2)
                    self.ram[address] = binary
                    address += 1

        except FileNotFoundError:
            print(f'{sys.argv[1]} could not be found')
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MULTIPLY":
            self.reg[reg_a] *= self.reg[reg_b]
        #elif op == "SUB": etc
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

        running = True
        while running:
            instruction_register = self.pc
            operand_a = self.ram[instruction_register + 1]
            operand_b = self.ram[instruction_register + 2]

            #HLT
            if self.ram[instruction_register] == 0b00000001:
                running = False 

            else:
                self.branch_table[self.ram[instruction_register]](operand_a, operand_b)

            # else:
            #     print(f'unknown command {self.ram[self.pc]}')
            #     running = False







