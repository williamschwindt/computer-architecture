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
        
    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def LDI(self):
        # print('LDI ran')
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        print(operand_a)
        print(operand_b)
        self.reg[operand_a] = operand_b
        self.pc += 3

    def PRN(self):
        # print('PRN ran')
        operand_a = self.ram[self.pc + 1]
        print(self.reg[operand_a])
        self.pc += 2

    def HLT(self):
        # print('HLT ran')
        self.running = False

    def ADD(self):
        # print('add ran')
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.alu("ADD", operand_a, operand_b)
        self.pc += 3

    def MUL(self):
        # print('MUL ran')
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.alu('MULTIPLY', operand_a, operand_b)
        self.pc += 3

    def PUSH(self):
        # print('PUSH ran')
        operand_a = self.ram[self.pc + 1]
        self.sp -= 1
        value = self.reg[operand_a]
        self.ram[self.sp] = value
        self.pc += 2

    def POP(self):
        # print('POP ran')
        operand_a = self.ram[self.pc + 1]
        value = self.ram[self.sp]
        self.reg[operand_a] = value
        self.sp += 1
        self.pc += 2

    def CALL(self):
        print('CALL ran')
        return_address = self.pc + 2
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = return_address
        register = self.ram[self.pc + 1]
        dest = self.reg[register]
        self.pc = dest

    def RET(self):
        # print('RET ran')
        # print('retrurn address', self.ram[self.reg[self.sp]])
        # print('stack pointer', self.reg[self.sp])
        self.pc = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1
        
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
        print(self.ram)
        """Run the CPU."""
        self.running = True
        print('run started')
    
        while self.running:
            IR = self.ram[self.pc]
            # print(IR)
 
            if IR in self.branch_table:
                # print(self.branch_table[self.ram[self.pc]])
                self.branch_table[IR]()

            else:
                print('Run ended')
                print(f'unknown command {IR}')
                self.running = False
