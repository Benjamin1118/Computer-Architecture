"""CPU functionality."""

import sys

# command variables
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b00010001
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
DIV = 0b10100011
sp = 7
# E = 0
# L = 0
# G = 0

 
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.reg[sp] = 0xF4
        self.pc = 0
        self.flags = 0
        self.branch_tab = {
            HLT: self.hlt,
            LDI: self.ldi,
            PRN: self.prn,
            POP: self.pop,
            PUSH: self.push,
            CALL: self.call, 
            RET: self.ret, 
            
            # add JMP, JEQ, and JNE to the branch table
            JMP: self.jmp,
            JEQ: self.jeq,
            JNE: self.jne,

            ADD: self.alu,
            SUB: self.alu,
            MUL: self.alu,
            DIV: self.alu

        }
    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def prn(self, operand_a, operand_b = None):
        print(self.reg[operand_a])

    def hlt(self, operand_a = None, operand_b = None):
        sys.exit()

    def ram_write(self, address, value):
        self.ram[address] = value

    def ram_read(self, address):
        return self.ram[address]

    def pop (self, operand_a, operand_b = None):
        self.reg[operand_a] = self.ram_read(self.reg[sp])
        self.reg[sp] += 1

    def push(self, operand_a, operand_b = None):
        self.reg[sp] -=1
        self.ram_write(self.reg[sp], self.pc + 2)

    def call(self, operand_a, operand_b = None):
        self.reg[sp] -=1
        self.ram_write(self.reg[sp], self.pc + 2)
        self.pc = self.reg[operand_a]

    def ret(self, operand_a = None, operand_b = None):
        self.pc = self.ram_read(self.reg[sp])
        self.reg[sp] += 1

    def jmp(self, operand_a, operand_b = None):
        self.pc = self.reg[operand_a]

    def jeq(self, operand_a, operand_b = None):
        if self.flags & 1:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2
    def jne (self, operand_a, operand_b = None):
        if not self.flags & 1:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def load(self, filename):
        """Load a program into memory."""
        address = 0
        with open(filename) as f: 
            for line in f:
                line = line.split('#')
                try:
                    instruction = int(line[0], 2)
                except ValueError:
                    continue
                self.ram[address] = instruction
                address += 1


        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000, 
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB": 
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "CMP":
            self.flags((self.reg[reg_a] < self.reg[reg_b]) << 2) |\
                      ((self.reg[reg_a] > self.reg[reg_b]) << 1) |\
                      ((self.reg[reg_a] == self.reg[reg_b]) << 0)
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
            ir = self.ram[self.pc]
            #instruction_length = ((ir >> 6) & 0b11) +1
            operand_a = self.ram_read(self.pc + 1) # use this for jump JEQ, JNE counter
            operand_b = self.ram_read(self.pc + 2)
            num_operands = ir >> 6

            pc_set = (ir >> 4) & 1

            alu_operations = (ir >> 5) & 1

            if ir in self.branch_tab:
                if alu_operations:
                    self.branch_tab[ir](ir, operand_a, operand_b)
                else:
                    self.branch_tab[ir](operand_a, operand_b)
            else:
                print ("Unsupported operation")

            if not pc_set:
                self.pc += num_operands +1
            # # LDI
            # if ir == LDI:
            #     self.reg[operand_a] = operand_b
            # # PRN
            # elif ir == PRN:
            #     print(self.reg[operand_a])
            # #MUL
            # elif ir == MUL:
            #     self.alu("MUL", operand_a, operand_b)

            # # PUSH
            # elif ir == PUSH:
            #     # decrement SP
            #     self.sp -= 1
            #     address = self.ram[self.pc + 1]
            #     # copy value in given register, to address pointed to by SP
            #     value = self.reg[address]
            #     self.ram[self.sp] = value
                
            # # POP
            # elif ir == POP:
            #     # Copy val from address pointed to by SP to given register
            #     address = self.ram[self.pc + 1]
            #     value = self.ram[self.sp]
            #     self.reg[address] = value
            #     # incrrement SP
            #     self.sp += 1
            # # CALL
            # elif ir == CALL:
            #     return_address = self.pc + 2
            #     self.sp -= 1
            #     self.ram[self.reg[self.sp]] = return_address

            #     reg_num = self.ram[self.pc + 1]
            #     subroutine_address = self.reg[reg_num]

            #     self.pc = subroutine_address

            
            # # RET
            # elif ir == RET:
            #     # Pop value from top of stack and store it in pc
            #     self.pc = self.ram[self.reg[self.sp]]
            #     self.sp += 1
                
            # # HLT    
            # elif ir == HLT:
            #     self.halted = True

            # # CMP
            # elif ir == CMP:
            #     if self.reg[operand_a] == self.reg[operand_b]:
            #         self.flags[-1] = 1
            #     elif self.reg[operand_a] < self.reg[operand_b]:
            #         self.flags[-3] = 1
            #     elif self.reg[operand_a] > self.reg[operand_b]:
            #         self.flags[-2] = 1
            #         #create flag for G, E, L

            # # JMP
            # elif ir == JMP:
            #     address = self.ram[self.pc + 1]
            #     jump_to = self.reg[address]
            #     self.pc = jump_to
            # # JEQ
            # elif ir == JEQ:
            #     # If equal flag is true jump to the address stored in the given register.
            #     if self.flags[-1] == 1:
            #         address == self.ram[self.pc+1]
            #         jump_to = self.reg[address]
            #         self.pc = jump_to
            #     else:
            #         self.pc += 2
            # # JNE
            # elif ir == JNE:
            #     # If E flag is false, jump to the address stored in the given register.
            #     if self.flags[-1] == 0:
            #         address == self.ram[self.pc+1]
            #         jump_to = self.reg[address]
            #         self.pc = jump_to                

            # self.pc += instruction_length


