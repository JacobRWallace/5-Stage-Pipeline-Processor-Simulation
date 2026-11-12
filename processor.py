#Jacob Wallace - R11822561
#=========================================================================================================
#Summer 2026 TTU Principles of Multiple-Processor Systems (CS-5365-202 & D01) 1st Summer Session Project
#5 stage pipeline processor simulation with data hazard detection and forwarding
#=========================================================================================================

#=========================================================================================================
#                                           Overview:
#=========================================================================================================
#1.Programs - creates three instruction sets for different pipeline cases
#2.Forwarding Runs - runs each test with forwarding off and on
#3.Setup Pipeline - stores IF, ID, EX, MEM, and WB for each cycle
#4.Cycle Simulation - moves instructions through the pipeline stages
#5.Hazards - checks source registers for RAW data hazards
#6.Stalls - holds instructions when a needed register is not ready
#7.Forwarding - changes timing when destination registers become ready
#8.Output - prints instructions, pipeline table, stalls, and CPI of all programs
#=========================================================================================================


programs = [ 
    
    #@@ Asa @@ this example gives you the parse of the type of instruction for new entries beq, a1, a2, 
    #0 - branch
    ("Branch Hazard", [ 
        {"op": "BEQ",  "jump": "5", "src1": "R4", "src2": "R5", "out": "true"}, # new, SB beq
        {"op": "LUI", "dest": "R12", "immediate": 400},
        {"op": "SUB", "dest": "R6", "src1": "R7", "src2": "R8"},
        {"op": "AND", "dest": "R9", "src1": "R10", "src2": "R11"},
        {"op": "JAL", "dest": "R1", "immediate": 1000}
    ]),    
    #0.1 - new
    ("Upper Instructions", [ 
        {"op": "LW",  "dest": "R1", "offset": 0, "base": "R2"}, 
        {"op": "LUI", "dest": "R12", "immediate": 400},                         # new, U lui
        {"op": "SUB", "dest": "R6", "src1": "R7", "src2": "R8"},
        {"op": "AND", "dest": "R9", "src1": "R10", "src2": "R11"},
        {"op": "JAL", "dest": "R1", "immediate": 1000}                          # new, UJ jal
    ]),    
    #1 - 1st test: instructions that do not depend on each other
    ("No Hazards", [ 
        {"op": "LW",  "dest": "R1", "offset": 0, "base": "R2"},
        {"op": "ADD", "dest": "R3", "src1": "R4", "src2": "R5"},
        {"op": "SUB", "dest": "R6", "src1": "R7", "src2": "R8"},
        {"op": "AND", "dest": "R9", "src1": "R10", "src2": "R11"},
        {"op": "SW",  "src1": "R12", "offset": 4, "base": "R2"} 
    ]),
    #1.1 - 2nd test: instructions need earlier results
    ("Data Hazards", [
        {"op": "LW",  "dest": "R1", "offset": 0, "base": "R2"}, 
        {"op": "ADD", "dest": "R3", "src1": "R1", "src2": "R4"}, 
        {"op": "SUB", "dest": "R5", "src1": "R3", "src2": "R6"}, 
        {"op": "AND", "dest": "R7", "src1": "R5", "src2": "R8"}, 
        {"op": "SW",  "src1": "R7", "offset": 4, "base": "R2"} 
    ]),
    #1.2 - 3rd test: load-use hazard example w/ additional instruction to show forwarding effect
    ("Load Use Hazards", [ 
        {"op": "LW",  "dest": "R1", "offset": 0, "base": "R2"}, 
        {"op": "ADD", "dest": "R3", "src1": "R1", "src2": "R4"},
        {"op": "ADD", "dest": "R5", "src1": "R3", "src2": "R6"},
        {"op": "SUB", "dest": "R7", "src1": "R5", "src2": "R8"}, 
        {"op": "SW",  "src1": "R7", "offset": 8, "base": "R2"},
        {"op": "ADD", "dest": "R9", "src1": "R1", "src2": "R10"} 
        
    ]), 
]

################# Change Proposed #########################
# Switch to a file input read system, where the program 
# takes a simple assembly file in the following format.
# lw a1, 0(s0)
# add t0, t1, t1
# subi t1, s1, s2
##########################################################
 
results = [] 
 
#2 - each program runs with forwarding off and on 
for item in programs: 
    title=item[0] 
    program=item[1] 
    runs = [] #hold results for forwarding
    
     #setup pipeline stages
    for forwarding in [False, True]:
        instructCount = len(program)
         
        stage = {}
        stages =["IF", "ID", "EX", "MEM", "WB"] 

        #3 - five stages are saved so every cycle can be tracked
        for i in stages: 
            stage[i] = [None] * (instructCount*6) #multiply by 6 to have enough cycles for the program to finish processing

        # variables to track pipeline state
        ready = {} #hazard detection: tracks when registers are ready to be read
        stalls = [] 
        messages = [] 
        cycleCount = 0 
        next=0 
        branched = False
         
        #4 - main clock cycle loop for the simulation
        while True:
            active=False 
        
            #4.1 - checks if the pipeline still has an instruction inside it
            for i in stage:
                if (stage[i][cycleCount] is not None):
                    active=True
                    break
            
            #4.2 - exit when end of program reached        
            if (next >=instructCount and not active):
                break
                 
            cycleCount = cycleCount+1 

            #4.2.1 - MEM and EX move foward
            if (stage["MEM"][cycleCount-1] is not None):
                stage["WB"][cycleCount] = stage["MEM"][cycleCount-1] 
            if (stage["EX"][cycleCount-1] is not None):

                #4.2.2 branch if condition is true and branch functiion called
                if (program[stage["EX"][cycleCount-1]]["op"] == "BEQ"):
                    if (program[stage["EX"][cycleCount-1]]["out"] == "true"):
                        jumpNum = program[stage["EX"][cycleCount-1]]["jump"]
                        print(f"The program branched at cc {cycleCount}, jumping {jumpNum} lines ahead")
                        branched = True
                        break
                

                stage["MEM"][cycleCount] = stage["EX"][cycleCount-1] 
            
            
            
            
            #5 - ID stage checks source registers for hazards
            if (stage["ID"][cycleCount-1] is not None):
                index = stage["ID"][cycleCount-1] #index of the instruction in the program list
                instr = program[index] #instruction data for the current instruction in ID stage
            
                ########################## Change ###############################
                # Instructions needed
                # - SB: beq, bge, blt
                # - U: lui
                # - UJ: jal
                #################################################################
                #5.1 - different instruction types read different registers
                if (instr["op"]=="LW"):
                    sources =[instr["base"]] 
                elif (instr["op"]=="SW"): 
                    sources = [instr["src1"], instr["base"]] 
                elif (instr["op"]=="ADD" or instr["op"]=="SUB" or instr["op"]=="AND" or instr["op"]=="BEQ"):
                    sources = [instr["src1"], instr["src2"]] 
                else: 
                    sources=[] 
                    print(f"invalid instruction in ID at cc {cycleCount}")
                
                #print(f"Cycle {cycleCount}: I{index + 1} sources: {sources}")
                
                stall = False
                stallreg = ""

                #5.2 - stall is needed if a source register is not ready
                for reg in sources: #pull each source register and check if it is ready
                    if (reg in ready and ready[reg] >= cycleCount + 1):
                        stall = True
                        stallreg = reg
                        break
                if (stall):
                    #6 - instruction stays in ID and the stall is saved
                    stage["ID"][cycleCount] = index
                    #print(stage["ID"][cycleCount])
                    stalls.append((cycleCount, index))
                    messages.append(f"Cycle {cycleCount}: I{index + 1} stalled! {stallreg} not ready!")
                else: #no stall is needed and the instruction can move forward
                    #6.1 - no hazard: instruction can move into EX
                    stage["EX"][cycleCount] = index

                     #7 - store instructions do not write to a destination register
                    if (instr["op"] == "SW"): #store does not have a destination register
                        dest = None
                    else:
                        dest = instr.get("dest")
                    
                    
                    if (dest is not None): #if instruction has destination register, update the ready cycle for that register
                        #7.1 - forwarding to make the results available faster by changing the ready cycle for the destination register
                        if (forwarding):
                            if (instr["op"] == "LW"): #load instruction results are ready later than ALU instructions
                                ready[dest] = cycleCount+2 #INC by 3 cycles for faster results
                            else: # ALU instruction results are ready sooner
                                ready[dest] = cycleCount+1 #default
                        
                        else: #7.2 - without forwarding, results are ready later
                            ready[dest] = cycleCount+3 #INC by 3 cycles for faster results
                            
        #4.3 - IF stage move forward only if ID is open
            if (stage["IF"][cycleCount-1] is not None and stage["ID"][cycleCount] is None):
                index = stage["IF"][cycleCount-1]
                stage["ID"][cycleCount] = index
            elif (stage["IF"][cycleCount-1] is not None):
                stage["IF"][cycleCount] = stage["IF"][cycleCount-1]

            #4.4 - new instruction is fetched when IF is open
            if (next < instructCount and stage["IF"][cycleCount] is None):
                stage["IF"][cycleCount] =next
                next = next+1
     
        #8 - store the results for the current run of the program
        result = {} 
        result["stage"] = stage
        result["cycleCount"] = cycleCount 
        result["stalls"] = stalls 
        result["stallMessages"] = messages 
        result["program"] = program 
        result["forwarding"] = forwarding 
        result["branches"] = branched 
        runs.append(result) #append run to list of recorded runs for the program

        print("\n==================================================")
        print(f"PROGRAM: {title}")
        print(f"Forwarding: {'ON' if forwarding else 'OFF'}")
        print("==================================================")
        print("\nPROGRAM:")
         
        index = 0 
        for instr in program: #8.1 - instructions print before the pipeline table
            op = instr["op"]

            #8.2 - stored instruction data changes into assembly text
            if (op == "LW"):
                line = f"LW {instr['dest']}, {instr['offset']}({instr['base']})"
            elif (op == "SW"):
                line = f"SW {instr['src1']}, {instr['offset']}({instr['base']})"
            elif (op == "ADD" or op == "SUB" or op == "AND"):
                line = f"{op} {instr['dest']}, {instr['src1']}, {instr['src2']}"
            elif (op == "BEQ"):
                line = f"{op} {instr['jump']}, {instr['src1']}, {instr['src2']}"
            elif (op == "LUI"):
                line = f"{op} {instr['dest']}, {instr['immediate']}"
            elif (op == "JAL"):
                line = f"{op} {instr['dest']}, {instr['immediate']}"
            else: #error
                line = "[ERROR] Unknown instruction!"

            print(f"I{index + 1}: {line}" )
            index=index+1
         
         
        print("\nTABLE:")
        print(f"Cycle | IF | ID | EX | MEM | WB |")

        #8.3 - table shows each clock cycle and instruction position
        for i in range(1, cycleCount + 1):
            row = f"{i:<5} |"
            for j in ["IF", "ID", "EX", "MEM", "WB"]:
                spot = stage[j][i] #j is the stage, i is the cycle for that stage
                position = f"I{spot + 1}" if spot is not None else "-"
                if (j != "MEM"):
                    row += f" {position:<2} |"
                else:
                    row += f" {position:<3} |"
            print(row)

         #8.4 - stall details explain why hazards happened
        print("\nSTALL DETAILS:")
        if (len(messages)==0):
            print("None")
        else:
            for message in messages:
                print(message) 

        #8.5 - print summary: cycleCount, stalls, and CPI
        print("\nSUMMARY:")
        print(f"Instructions: {len(program)}")
        print(f"Total Cycles: {cycleCount-1}")
        print(f"Stalls: {len(stalls)}")
        print(f"CPI: {cycleCount / len(program):.2f}\n")
    
    resultOff = runs[0] 
    resultOn = runs[1] 
    results.append((title, resultOff, resultOn)) 
 
 
#8.6 - print the results and show how forwarding effected the cycles and stalls
print("\nCOMPARISON SUMMARY:")
print(f"{'Program':<20} | {'No Fwd Cycles':<13} | {'No Fwd Stalls':<13} | {'Fwd Cycles':<10} | {'Fwd Stalls':<10} | {'Branch':<10}") 
for item in results:
 
    title = item[0] #print title
    resultOff = item[1] #print results (forwarding off)
    resultOn = item[2] #print results (forwarding on)
    
    print(f"{title:<20} | {resultOff['cycleCount']:<13} | {len(resultOff['stalls']):<13} | {resultOn['cycleCount']:<10} | {len(resultOn['stalls']):<10} | {resultOn['branches']:<10}") 
