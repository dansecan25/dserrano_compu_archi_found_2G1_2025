"""
Dual Processor View - Shows both processors (with and without hazards) side by side
"""

import tkinter as tk
from tkinter import ttk
import os
from processor_view import ProcessorView, LogParser, PipelineStage
from processor_diagram_hazard import ProcessorDiagramWithHazards


class DualProcessorView(tk.Frame):
    """
    Displays two processors side by side:
    - Left: Processor WITHOUT hazards (reads from Simulador/log.txt)
    - Right: Processor WITH hazards (reads from log_hazard_control.txt)
    Both advance together when Step/Run is pressed
    """

    def __init__(self, parent, log_path_no_hazard, log_path_with_hazard, **kwargs):
        super().__init__(parent, bg='#1A1A1A', **kwargs)

        self.log_path_no_hazard = log_path_no_hazard
        self.log_path_with_hazard = log_path_with_hazard

        # Parsers for both logs
        self.parser_no_hazard = LogParser(log_path_no_hazard)
        self.parser_with_hazard = LogParser(log_path_with_hazard)

        # Shared state
        self.current_cycle = 0
        self.is_running = False
        self.animation_speed = 500

        # Processor diagrams
        self.diagram_no_hazard = None
        self.diagram_with_hazard = None

        # Pipeline stage blocks
        self.top_stages = {}
        self.bottom_stages = {}

        self.setup_ui()

    def setup_ui(self):
        """Setup the dual view interface"""
        # ====== TOP: Unified Control Panel ======
        control_frame = tk.Frame(self, bg='#2A2A2A', height=60)
        control_frame.pack(fill='x', padx=5, pady=5)
        control_frame.pack_propagate(False)

        # Control buttons
        btn_style = {'font': ('Arial', 10), 'bg': '#4A4A4A', 'fg': 'white',
                    'activebackground': '#5A5A5A', 'relief': 'raised', 'bd': 2}

        self.reset_btn = tk.Button(control_frame, text='⟲ Reset', command=self.reset, **btn_style)
        self.reset_btn.pack(side='left', padx=3, pady=10)

        self.step_back_btn = tk.Button(control_frame, text='◀ Step Back',
                                       command=self.step_back, **btn_style)
        self.step_back_btn.pack(side='left', padx=3, pady=10)

        self.step_btn = tk.Button(control_frame, text='▶ Step', command=self.step, **btn_style)
        self.step_btn.pack(side='left', padx=3, pady=10)

        self.run_btn = tk.Button(control_frame, text='▶▶ Run', command=self.run, **btn_style)
        self.run_btn.pack(side='left', padx=3, pady=10)

        self.stop_btn = tk.Button(control_frame, text='⏸ Stop', command=self.stop,
                                 state='disabled', **btn_style)
        self.stop_btn.pack(side='left', padx=3, pady=10)

        # Cycle info
        self.cycle_label = tk.Label(control_frame, text='Cycle: 0',
                                   bg='#2A2A2A', fg='white', font=('Arial', 11, 'bold'))
        self.cycle_label.pack(side='left', padx=20)

        # Speed control
        tk.Label(control_frame, text='Speed:', bg='#2A2A2A', fg='white',
                font=('Arial', 9)).pack(side='left', padx=(20, 5))

        self.speed_scale = tk.Scale(control_frame, from_=100, to=2000, orient='horizontal',
                                   bg='#2A2A2A', fg='white', highlightthickness=0,
                                   length=150, command=self.update_speed)
        self.speed_scale.set(500)
        self.speed_scale.pack(side='left', padx=5)

        # ====== MIDDLE: Two Processors Stacked Vertically with Vertical Scroll ======
        # Create scrollable container
        scroll_container = tk.Frame(self, bg='#1A1A1A')
        scroll_container.pack(fill='both', expand=True, padx=5, pady=5)

        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(scroll_container, orient='vertical')
        v_scrollbar.pack(side='right', fill='y')

        # Canvas for scrolling
        scroll_canvas = tk.Canvas(scroll_container, bg='#1A1A1A', highlightthickness=0,
                                 yscrollcommand=v_scrollbar.set)
        scroll_canvas.pack(side='left', fill='both', expand=True)
        v_scrollbar.config(command=scroll_canvas.yview)

        # Frame inside canvas to hold processors
        processors_container = tk.Frame(scroll_canvas, bg='#1A1A1A')
        scroll_canvas.create_window((0, 0), window=processors_container, anchor='nw')

        # Top: Processor WITHOUT Hazards
        top_frame = tk.Frame(processors_container, bg='#1A1A1A', relief='ridge', bd=2)
        top_frame.pack(side='top', fill='x', pady=(0, 3), padx=5)

        tk.Label(top_frame, text='Pipeline WITHOUT Hazard Control',
                bg='#1A1A1A', fg='#6ADA6A', font=('Arial', 12, 'bold')).pack(pady=5)

        # Pipeline stages for top processor
        top_stages_container = tk.Frame(top_frame, bg='#1A1A1A')
        top_stages_container.pack(fill='x', padx=10, pady=(0, 10))

        stage_names = ['Fetch', 'Decode', 'RegFile', 'Execute', 'Store']
        for i, stage_name in enumerate(stage_names):
            stage_widget = PipelineStage(top_stages_container, stage_name, width=160, height=90)
            stage_widget.grid(row=0, column=i, padx=5, pady=5)
            self.top_stages[stage_name] = stage_widget

        self.top_canvas_frame = tk.Frame(top_frame, bg='#1A1A1A')
        self.top_canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Bottom: Processor WITH Hazards
        bottom_frame = tk.Frame(processors_container, bg='#1A1A1A', relief='ridge', bd=2)
        bottom_frame.pack(side='top', fill='x', pady=(3, 0), padx=5)

        tk.Label(bottom_frame, text='Pipeline WITH Hazard Control',
                bg='#1A1A1A', fg='#DA6A6A', font=('Arial', 12, 'bold')).pack(pady=5)

        # Pipeline stages for bottom processor
        bottom_stages_container = tk.Frame(bottom_frame, bg='#1A1A1A')
        bottom_stages_container.pack(fill='x', padx=10, pady=(0, 10))

        for i, stage_name in enumerate(stage_names):
            stage_widget = PipelineStage(bottom_stages_container, stage_name, width=160, height=90)
            stage_widget.grid(row=0, column=i, padx=5, pady=5)
            self.bottom_stages[stage_name] = stage_widget

        self.bottom_canvas_frame = tk.Frame(bottom_frame, bg='#1A1A1A')
        self.bottom_canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Create canvases for both processors
        self._create_processor_canvases()

        # Configure scroll region after everything is added
        processors_container.update_idletasks()
        scroll_canvas.configure(scrollregion=scroll_canvas.bbox('all'))

        # ====== BOTTOM: Status Information ======
        status_frame = tk.Frame(self, bg='#2A2A2A', height=80)
        status_frame.pack(fill='x', padx=5, pady=(0, 5))
        status_frame.pack_propagate(False)

        tk.Label(status_frame, text='Status Information', bg='#2A2A2A',
                fg='white', font=('Arial', 10, 'bold')).pack(pady=(5, 2))

        # Two status labels stacked
        status_container = tk.Frame(status_frame, bg='#2A2A2A')
        status_container.pack(fill='both', expand=True, padx=10, pady=(0, 5))

        # Top processor status
        self.top_status = tk.Label(status_container, text='No Hazards: Ready',
                                   bg='#1A1A1A', fg='#6ADA6A',
                                   font=('Courier', 9), anchor='w', padx=10, pady=5)
        self.top_status.pack(side='top', fill='x', pady=(0, 2))

        # Bottom processor status
        self.bottom_status = tk.Label(status_container, text='With Hazards: Ready',
                                      bg='#1A1A1A', fg='#DA6A6A',
                                      font=('Courier', 9), anchor='w', padx=10, pady=5)
        self.bottom_status.pack(side='bottom', fill='x', pady=(2, 0))

    def _create_processor_canvases(self):
        """Create the canvas and diagrams for both processors"""
        # Top canvas (no hazards) with horizontal scrollbar
        h_scroll_top = ttk.Scrollbar(self.top_canvas_frame, orient='horizontal')
        
        self.top_canvas = tk.Canvas(
            self.top_canvas_frame,
            bg='#1A1A1A',
            highlightthickness=0,
            height=350,
            width=1200,  # Ancho amplio para ver todos los componentes            
        )

        h_scroll_top.config(command=self.top_canvas.xview)

        self.top_canvas.pack(side='top', fill='both', expand=True)
        h_scroll_top.pack(side='bottom', fill='x')

        # Import ProcessorDiagram for top side
        from processor_diagram import ProcessorDiagram
        self.diagram_no_hazard = ProcessorDiagram(self.top_canvas)

        # Configure scroll region for top canvas
        self.top_canvas.configure(scrollregion=self.top_canvas.bbox('all'))

        # Bottom canvas (with hazards) with horizontal scrollbar
        h_scroll_bottom = ttk.Scrollbar(self.bottom_canvas_frame, orient='horizontal')

        self.bottom_canvas = tk.Canvas(
            self.bottom_canvas_frame,
            bg='#1A1A1A',
            highlightthickness=0,
            height=500,  # Extra height para hazard unit
            width=1100,  # Ancho amplio para ver todos los componentes
        )

        h_scroll_bottom.config(command=self.bottom_canvas.xview)

        self.bottom_canvas.pack(side='top', fill='both', expand=True)
        h_scroll_bottom.pack(side='bottom', fill='x')

        # Create processor with hazards
        self.diagram_with_hazard = ProcessorDiagramWithHazards(self.bottom_canvas)

        # Configure scroll region for bottom canvas
        self.bottom_canvas.configure(scrollregion=self.bottom_canvas.bbox('all'))

    def load_logs(self):
        """Load both log files"""
        success_no_hazard = self.parser_no_hazard.parse()
        success_with_hazard = self.parser_with_hazard.parse()

        if success_no_hazard and success_with_hazard:
            self.current_cycle = 0
            self.update_displays()
            return True
        return False

    def update_speed(self, value):
        """Update animation speed"""
        self.animation_speed = int(value)

    def update_displays(self):
        """Update both processor displays based on current cycle"""
        # Update cycle label
        total_no_hazard = self.parser_no_hazard.get_total_cycles()
        total_with_hazard = self.parser_with_hazard.get_total_cycles()

        self.cycle_label.config(
            text=f"Cycle: {self.current_cycle} (NoHazard: {total_no_hazard}, WithHazard: {total_with_hazard})"
        )

        # Update left processor (no hazards)
        self._update_no_hazard_display()

        # Update right processor (with hazards)
        self._update_with_hazard_display()

    def _update_no_hazard_display(self):
        """Update the processor without hazards"""
        cycle_data = self.parser_no_hazard.get_cycle_data(self.current_cycle)

        if cycle_data is None:
            return

        # Determine active components
        active_components = []
        active_wires = []

        stages = cycle_data['stages']

        # Update pipeline stage blocks
        for stage_name, stage_widget in self.top_stages.items():
            stage_value = stages.get(stage_name, 'Libre')
            stage_widget.update_stage(stage_value)

            if stage_value != "Libre":
                self._add_stage_components(stage_name, active_components, active_wires)

        # Update diagram
        if self.diagram_no_hazard:
            self.diagram_no_hazard.set_active_components(active_components)
            self.diagram_no_hazard.set_active_wires(active_wires)

        # Update status
        info = f"[No Hazards] Cycle {cycle_data['cycle']}: PC={cycle_data['pc']}"
        if cycle_data['completed']:
            info += f" | ✓ {cycle_data['completed']}"
        self.top_status.config(text=info)

    def _update_with_hazard_display(self):
        """Update the processor with hazards"""
        cycle_data = self.parser_with_hazard.get_cycle_data(self.current_cycle)

        if cycle_data is None:
            return

        # Determine active components
        active_components = []
        active_wires = []

        stages = cycle_data['stages']

        # Update pipeline stage blocks
        for stage_name, stage_widget in self.bottom_stages.items():
            stage_value = stages.get(stage_name, 'Libre')
            stage_widget.update_stage(stage_value)

            if stage_value != "Libre":
                self._add_stage_components(stage_name, active_components, active_wires)

        # Detect stalls and forwarding from NOPs
        # NOPs in the pipeline = STALLs (bubbles inserted by hazard control)
        has_stall = False
        has_forwarding = False
        nop_count = 0
        real_instr_count = 0

        for stage_name, stage_value in stages.items():
            if stage_value != "Libre":
                # Check if it's a NOP (stall bubble)
                if "nop" in stage_value.lower():
                    nop_count += 1
                else:
                    real_instr_count += 1

        # STALL: If there are NOPs in the pipeline (hazard control inserted bubbles)
        if nop_count > 0:
            has_stall = True

        # FORWARDING: If there are real instructions in multiple stages
        # (likely using forwarding to avoid more stalls)
        if real_instr_count >= 3:
            has_forwarding = True

        # Update diagram with hazard state
        if self.diagram_with_hazard:
            self.diagram_with_hazard.set_active_components(active_components)
            self.diagram_with_hazard.set_active_wires(active_wires)
            self.diagram_with_hazard.set_hazard_state(stall=has_stall, forwarding=has_forwarding)

            # Activate forwarding paths if forwarding is active
            if has_forwarding:
                # Activate both forwarding paths as examples
                self.diagram_with_hazard.set_forwarding_paths(['Forward_EX_EX', 'Forward_MEM_EX'])
            else:
                self.diagram_with_hazard.set_forwarding_paths([])

        # Update status with hazard information
        info = f"[With Hazards] Cycle {cycle_data['cycle']}: PC={cycle_data['pc']}"
        if cycle_data['completed']:
            info += f" | ✓ {cycle_data['completed']}"

        # Add hazard indicators to status
        hazard_info = []
        if has_stall:
            hazard_info.append("🔴 STALL")
        if has_forwarding:
            hazard_info.append("🟢 FWD")

        if hazard_info:
            info += f" | {' '.join(hazard_info)}"

        self.bottom_status.config(text=info)

    def _add_stage_components(self, stage_name: str, components: list, wires: list):
        """Map pipeline stage to processor components and wires (same as ProcessorView)"""
        stage_mapping = {
            'Fetch': {
                'components': ['PC', 'PC_Adder', 'Inst_Mem', 'IF/ID'],
                'wires': ['PC_to_IMem', 'PC_to_Adder', 'Adder_to_IFID', 'IMem_to_IFID']
            },
            'Decode': {
                'components': ['Control', 'RegFile', 'SignExt', 'ID/EX'],
                'wires': ['IFID_to_Control', 'IFID_to_RegFile', 'RegFile_to_IDEX', 'SignExt_to_IDEX']
            },
            'RegFile': {
                'components': ['ALU_Control', 'ALU', 'Mux_ALU_A', 'Mux_ALU_B', 'EX/MEM'],
                'wires': ['IDEX_to_ALU', 'MuxA_to_ALU', 'MuxB_to_ALU', 'ALU_to_EXMEM']
            },
            'Execute': {
                'components': ['Data_Mem', 'Mux_PC', 'MEM/WB'],
                'wires': ['EXMEM_to_DMem', 'DMem_to_MEMWB']
            },
            'Store': {
                'components': ['Mux_WB'],
                'wires': ['MEMWB_to_Mux', 'WB_to_RegFile']
            }
        }

        if stage_name in stage_mapping:
            mapping = stage_mapping[stage_name]
            components.extend(mapping['components'])
            wires.extend(mapping['wires'])

    def reset(self):
        """Reset both processors to cycle 0"""
        self.stop()
        self.current_cycle = 0

        if self.diagram_no_hazard:
            self.diagram_no_hazard.reset_all()

        if self.diagram_with_hazard:
            self.diagram_with_hazard.reset_all()

        self.update_displays()

    def step(self):
        """Step forward one cycle in BOTH processors"""
        max_cycles = max(
            self.parser_no_hazard.get_total_cycles(),
            self.parser_with_hazard.get_total_cycles()
        )

        if self.current_cycle < max_cycles - 1:
            self.current_cycle += 1
            self.update_displays()

    def step_back(self):
        """Step back one cycle in BOTH processors"""
        if self.current_cycle > 0:
            self.current_cycle -= 1
            self.update_displays()

    def run(self):
        """Run both processors automatically"""
        if not self.is_running:
            self.is_running = True
            self.run_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self._run_cycle()

    def _run_cycle(self):
        """Internal method to run one cycle in animation"""
        max_cycles = max(
            self.parser_no_hazard.get_total_cycles(),
            self.parser_with_hazard.get_total_cycles()
        )

        if self.is_running and self.current_cycle < max_cycles - 1:
            self.current_cycle += 1
            self.update_displays()
            self.after(self.animation_speed, self._run_cycle)
        else:
            self.stop()

    def stop(self):
        """Stop the animation"""
        self.is_running = False
        self.run_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
