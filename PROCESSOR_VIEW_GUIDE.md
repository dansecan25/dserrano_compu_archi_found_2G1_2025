# Processor View - User Guide

## Overview

The Processor View is a visual simulator for the RISC-V pipeline processor, inspired by the RIPES software. It provides a graphical interface to visualize the execution of instructions through the 5-stage pipeline.

## Features

### 1. **Pipeline Visualization**
- **5 Pipeline Stages**: Fetch, Decode, RegFile, Execute, Store
- **Real-time Updates**: Each stage displays the current instruction being processed
- **Visual Feedback**: Active stages are highlighted in green, idle stages are gray
- **Cycle Information**: Shows remaining cycles for each instruction in each stage

### 2. **Register File Display**
- **32 RISC-V Registers** (x0-x31)
- **Live Updates**: Registers are highlighted when updated
- **Value Tracking**: Shows current value of each register
- **Scrollable View**: Easy navigation through all registers

### 3. **Execution Controls**

#### Control Buttons:
- **⟲ Reset**: Reset simulation to cycle 0
- **◀ Step Back**: Go back one cycle
- **▶ Step**: Advance one cycle forward
- **▶▶ Run**: Automatically play through all cycles
- **⏸ Stop**: Pause the automatic playback

#### Speed Control:
- Adjustable slider to control animation speed (100ms - 2000ms per cycle)

### 4. **Status Information**
- **Cycle Counter**: Shows current cycle and total cycles
- **Program Counter (PC)**: Displays current PC value
- **Instruction Info**: Shows completed instructions and register updates

## How to Use

### Step 1: Write Your Code
1. Click the **Editor** button (if not already active)
2. Write your RISC-V assembly code in the text editor
3. Click the **Run** button to execute the simulation

### Step 2: View Pipeline Execution
1. After clicking **Run**, a success message will appear
2. Click the **Processor** button to switch to the processor view
3. The log file will be automatically loaded and displayed

### Step 3: Navigate Through Cycles
- Use **Step** (▶) to advance one cycle at a time
- Use **Step Back** (◀) to go back and review previous cycles
- Use **Run** (▶▶) to automatically play through all cycles
- Adjust the speed slider to control playback speed
- Use **Reset** (⟲) to return to cycle 0

### Step 4: Analyze Execution
- **Watch the Pipeline**: See how instructions flow through each stage
- **Monitor Registers**: Track register values as they change
- **Check PC**: Follow the program counter through jumps and branches
- **Review Completions**: See when instructions complete in the info panel

## Understanding the Display

### Pipeline Stage States

1. **Libre** (Gray):
   - Stage is idle/free
   - No instruction currently processing

2. **Procesando: [instruction] (X ciclos restantes)** (Green):
   - Stage is actively processing an instruction
   - Shows the instruction and remaining cycles

### Color Coding
- **Gray (#3A3A3A)**: Idle stage
- **Green (#4A6A4A)**: Active stage with border highlight (#6ADA6A)
- **White Text**: Current instruction or "Libre"
- **Green Register**: Recently updated register value

### Instruction Info Panel
Shows:
- Current cycle number
- Current PC value
- Completed instruction (if any) with ✓ checkmark
- Register updates in the format: `register_name=value`

## Example Workflow

```assembly
# Example RISC-V code
addi x1, x0, 100    # x1 = 100
addi x2, x0, 50     # x2 = 50
add x3, x1, x2      # x3 = x1 + x2 = 150
```

1. **Write** the code in the Editor
2. Click **Run** - backend executes and generates log.txt
3. Click **Processor** - view loads the log
4. Click **Step** multiple times to see:
   - Cycle 1: `addi x1, x0, 100` enters Fetch
   - Cycle 2: Moves to Decode, next instruction enters Fetch
   - Cycle 3-5: Instruction propagates through pipeline
   - Cycle 5: Instruction completes, x1 is updated to 100

## Technical Details

### Log File Format
The processor view reads `Simulador/log.txt` which contains:
- Instruction list with addresses
- Cycle-by-cycle pipeline state
- Register updates
- PC changes
- Pipeline flushes (for jumps/branches)

### Pipeline Stages Explained
1. **Fetch**: Fetches instruction from memory (1 cycle)
2. **Decode**: Decodes instruction and reads opcode (1 cycle)
3. **RegFile**: Reads register file (1 cycle)
4. **Execute**: Executes operation (variable cycles, typically 2)
5. **Store**: Writes back to registers (1 cycle)

## Troubleshooting

### "Error: Could not load log file"
- Make sure you clicked **Run** in the Editor first
- Check that `Simulador/log.txt` exists
- Verify the backend simulation completed successfully

### Pipeline not updating
- Click **Reset** and try again
- Make sure you clicked **Run** to generate a fresh log
- Check that the log file is not empty

### Registers not showing values
- Register values only update when instructions complete
- Use **Step** to advance through cycles until completion
- Check the Instruction Info panel for register update messages

## Tips for Best Experience

1. **Use Step Mode First**: Step through cycles manually to understand the pipeline flow
2. **Adjust Speed**: Set animation speed based on complexity (slower for detailed analysis)
3. **Watch Register File**: Keep an eye on register updates to track data flow
4. **Use Reset Often**: Reset to cycle 0 to re-analyze execution from the beginning
5. **Check Instruction Info**: The info panel shows completion status and updates

## Keyboard Shortcuts
(Currently not implemented, but planned for future versions)

## Known Limitations

- Cannot edit code while in Processor view (switch back to Editor)
- Step Back recalculates register state (may be slower)
- Large programs (>1000 cycles) may take time to parse

## Future Enhancements

- Breakpoints at specific cycles
- Memory view integration
- Hazard detection visualization
- Branch prediction indicators
- Performance metrics (CPI, IPC)
- Export execution trace

---

**Version**: 1.0
**Last Updated**: December 2025
