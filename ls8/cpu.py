"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0,0,0,0,0,0,0,0]
        self.running = False
        self.pc = 0
        self.sp = 7
        self.reg[self.sp] = 0xf4
        self.fl = 0b00000000
        self.branch_table = {}
        self.branch_table[0b10000010] = self.LDI
        self.branch_table[0b01000111] = self.PRN
        self.branch_table[0b00000001] = self.HLT
        self.branch_table[0b10100000] = self.ADD
        self.branch_table[0b10100010] = self.MUL
        self.branch_table[0b01000101] = self.PUSH
        self.branch_table[0b01000110] = self.POP
        self.branch_table[0b01010000] = self.CALL
        self.branch_table[0b00010001] = self.RET
        self.branch_table[0b10100111] = self.CMP
        self.branch_table[0b01010100] = self.JMP
        self.branch_table[0b01010101] = self.JEQ
        self.branch_table[0b01010110] = self.JNE
        
    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def LDI(self):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.reg[operand_a] = operand_b
        self.pc += 3

    def PRN(self):
        operand_a = self.ram[self.pc + 1]
        print(self.reg[operand_a])
        self.pc += 2

    def HLT(self):
        self.running = False

    def ADD(self):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.alu("ADD", operand_a, operand_b)
        self.pc += 3

    def MUL(self):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.alu('MULTIPLY', operand_a, operand_b)
        self.pc += 3

    def PUSH(self):
        operand_a = self.ram[self.pc + 1]
        self.sp -= 1
        value = self.reg[operand_a]
        self.ram[self.sp] = value
        self.pc += 2

    def POP(self):
        operand_a = self.ram[self.pc + 1]
        value = self.ram[self.sp]
        self.reg[operand_a] = value
        self.sp += 1
        self.pc += 2

    def CALL(self):
        return_address = self.pc + 2
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = return_address
        register = self.ram[self.pc + 1]
        dest = self.reg[register]
        self.pc = dest

    def RET(self):
        self.pc = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1

    def CMP(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.alu('COMPARE', reg_a, reg_b)
        self.pc += 3

    def JMP(self):
        reg_a = self.ram[self.pc + 1]
        address = self.reg[reg_a]
        self.pc = address

    def JEQ(self):
        mask = bin(0b00000001 & self.fl)
        if mask == '0b1':
            reg_a = self.ram[self.pc + 1]
            address = self.reg[reg_a]
            self.pc = address
        else:
            self.pc += 2

    def JNE(self):
        mask = bin(0b00000001 & self.fl)
        if mask == '0b0':
            reg_a = self.ram[self.pc + 1]
            address = self.reg[reg_a]
            self.pc = address
        else:
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

        elif op == "COMPARE":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001

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
        self.running = True
    
        while self.running:
            IR = self.ram[self.pc]
            # print(bin(IR))
 
            if IR in self.branch_table:
                # print(self.branch_table[self.ram[self.pc]])
                self.branch_table[IR]()

            else:
                print(f'unknown command {IR}')
                self.running = False
