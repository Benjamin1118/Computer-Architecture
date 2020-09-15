"""CPU functionality."""

import sys

''' Opcodes - Command Variables''' 

HLT = 0b00000001 
LDI = 0b10000010 
PRN = 0b01000111 

POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001

# Add JMP, JEQ, & JNE OpCodes - numeric values stored in register
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
DIV = 0b10100011
MOD = 0b10100100

INC = 0b01100101
DEC = 0b01100110

CMP = 0b10100111

AND = 0b10101000
NOT = 0b01101001
OR = 0b10101010
XOR = 0b10101011
SHL = 0b10101100
SHR = 0b10101101

sp = 7

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.reg[sp] = 0xF4
        self.pc = 0
        self.flags = 0

        self.branch_table = {
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
            DIV: self.alu,
            MOD: self.alu,

            INC: self.alu,
            DEC: self.alu,
            CMP: self.alu,

            AND: self.alu,
            NOT: self.alu,
            OR: self.alu,
            XOR: self.alu,
            SHL: self.alu,
            SHR: self.alu
        }
    
    def ldi(self, op_a, op_b):
        ''' Set the value of register to an integer '''
        self.reg[op_a] = op_b

    def prn(self, op_a, op_b=None):
        ''' prints a specific value '''
        print(self.reg[op_a])

    def prn(self, op_a, op_b = None):
        ''' Prints a specific value '''
        print(self.reg[op_a])

    def hlt(self, op_a = None, op_b = None):
        ''' Halts the CPU and exits emulator '''
        sys.exit()

    def pop(self, op_a, op_b = None):
        ''' Pop value at top of stack and into given register '''
        self.reg[op_a] = self.ram_read(self.reg[sp])
        self.reg[sp] += 1
       
    def push(self, op_a, op_b = None):
        ''' pushes value to stack using arithmetic logic unit (ALU) '''
        self.reg[sp] -=1
        self.ram_write(self.reg[sp], self.reg[op_a])

    def call(self, op_a, op_b = None):
        ''' calls subroutine at address stored in register '''
        self.reg[sp] -=1
        self.ram_write(self.reg[sp], self.pc + 2)
        self.pc = self.reg[op_a]

    
    def ret(self, op_a = None, op_b = None):
        ''' return from subroutine '''
        self.pc = self.ram_read(self.reg[sp])
        self.reg[sp] += 1

    def jmp(self, op_a, op_b = None):
        ''' jump to address stored in given register '''
        self.pc = self.reg[op_a]
    


    def jeq(self, op_a, op_b = None):
        ''' if equal flag is set jump to address in given register '''
        if self.flags & 1:
            self.pc = self.reg[op_a]
        else:
            self.pc += 2
    
    def jne (self, op_a, op_b = None):
        ''' if E flag is clear jump to addres in given register'''
        if not self.flags & 1:
            self.pc = self.reg[op_a]
        else:
            self.pc += 2
   

    def ram_read(self, address):
        ''' reads the CPU object in RAM '''
        return self.ram[address]
    
    def ram_write(self, address, value):
        ''' writes the CPU object in RAM'''
        self.ram[address] = value


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

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == SUB: 
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == DIV:
            self.reg[reg_a] /= self.reg[reg_b]
        # can add MOD, AND, OR, ...
    
        elif op == CMP:
            ''' Compares values in the registers '''
            self.flags = ((self.reg[reg_a] < self.reg[reg_b]) << 2) | \
                      ((self.reg[reg_a] > self.reg[reg_b]) << 1) | \
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
            self.flags,
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
            ir = self.ram_read(self.pc)
            op_a = self.ram_read(self.pc + 1) # use this for jump JEQ, JNE counter
            op_b = self.ram_read(self.pc + 2)
            num_operands = ir >> 6

            pc_set = (ir >> 4) & 1

            alu_operations = (ir >> 5) & 1

            if ir in self.branch_table:
                if alu_operations:
                    self.branch_table[ir](ir, op_a, op_b)
                else:
                    self.branch_table[ir](op_a, op_b)
            else:
                print("Unsupported operation")

            if not pc_set:
                self.pc += num_operands + 1

