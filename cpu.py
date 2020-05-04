"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """
        Need memory and 8 registers
        """
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.reg[7] = 0xF4
        self.fl = [0] * 8
        self.opcodes = {
            0b00000001: "HLT",
            0b01000111: "PRN",
            0b10000010: "LDI",
            0b10100000: "ADD",
            0b10100010: "MUL",
            0b01000101: "PUSH",
            0b01000110: "POP",
            0b01010000: "CALL",
            0b00010001: "RET",
            0b10100111: "CMP",
            0b01010101: "JEQ",
            0b01010110: "JNE",
            0b01010100: "JMP",
            0b10101000: "AND",
            0b10101010: "OR",
            0b10101011: "XOR",
            0b01101001: "NOT",
            0b10101100: "SHL",
            0b10101101: "SHR",
            0b10100100: "MOD"
        }
        self.branchtable = {
            "HLT": self.hlt,
            "LDI": self.ldi,
            "PRN": self.prn,
            "ALU": self.alu,
            "PUSH": self.push,
            "POP": self.pop,
            "CALL": self.call,
            "RET": self.ret,
            "JEQ": self.jeq,
            "JNE": self.jne,
            "JMP": self.jmp
        }


    def load(self):
        """Load a program into memory."""

        try:
            file = sys.argv[1]
            address = 0
            with open(file) as f:
                # Open and read file
                for line in f:
                    # Remove comments
                    line = line.split("#")[0]
                    # Remove whitespace
                    line = line.strip()
                    # Skip empty lines
                    if line == "":
                        continue

                    value = int(line, 2)

                    # Add instructions to memory
                    self.ram[address] = value
                    address += 1
        except FileNotFoundError:
            print("File not found")
            sys.exit(2)


    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr
        


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl[-1] = 1
            else:
                self.fl[-1] = 0
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
        self.load()

        self.running = True
        
        while self.running:
            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)

            num_operands = (IR >> 6)

            sets_pc = ((IR >> 4) & 0b001) == 1
            is_alu_op = (IR >> 5) & 0b001 == 1
            opcode = self.opcodes[IR]
            # self.trace()
            if not sets_pc:
                self.pc += 1 + num_operands

            if is_alu_op:
                self.alu(opcode, operand_a, operand_b)

            else:
                self.branchtable[opcode](operand_a, operand_b)

            

    def hlt(self, _, __):
        self.running = False

    def prn(self, op_a, _):
        print(self.reg[op_a])
    
    def ldi(self, op_a, op_b):
        self.reg[op_a] = op_b

    def push(self, op_a, _):
        self.reg[7] -= 1
        sp = self.reg[7]
        value = self.reg[op_a]

        self.ram_write(sp, value)
    
    def pop(self, op_a, _):
        sp = self.reg[7]

        value = self.ram_read(sp)

        self.reg[op_a] = value
        self.reg[7] += 1

    def call(self, op_a, _):
        self.reg[7] -= 1
        sp = self.reg[7]
        self.ram_write(sp, self.pc + 2)

        self.pc = self.reg[op_a]

    def ret(self, op_a, _):
        sp = self.reg[7]
        return_address = self.ram_read(sp)
        
        self.pc = return_address

    def jmp(self, op_a, _): # Jump to the address stored in the given register
        self.pc = self.reg[op_a] # Set PC to the address stored in op_a

    def jeq(self, op_a, _): # If equal flag is 1, jump to address at op a
        if self.fl[-1] == 1:
            self.jmp(op_a, _)
        else:
            self.pc += 2
    
    def jne(self, op_a, _): # If equal flag is 0, jump to address at op a
        if self.fl[-1] == 0:
            self.jmp(op_a, _)
        else:
            self.pc += 2