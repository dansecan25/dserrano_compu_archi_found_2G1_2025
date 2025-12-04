"""
Processor Diagram with Hazard Detection and Forwarding Unit
Extends the base ProcessorDiagram to add hazard control
"""

import tkinter as tk
from typing import List
from processor_diagram import ProcessorDiagram
from processor_components import HazardUnit, ForwardingPath, create_path


class ProcessorDiagramWithHazards(ProcessorDiagram):
    """
    Extended processor diagram with Hazard Detection Unit and Forwarding Paths
    """

    def __init__(self, canvas: tk.Canvas):
        # Call parent constructor to build base processor
        super().__init__(canvas)

        # Now add hazard-specific components
        self._add_hazard_unit()
        self._add_forwarding_paths()

    def _add_hazard_unit(self):
        """Add the Hazard Detection and Forwarding Unit"""
        # Position hazard unit below the main processor diagram
        # Center it horizontally
        hazard_x = 400
        hazard_y = 350  # Below the main components

        self.components['Hazard_Unit'] = HazardUnit(
            self.canvas,
            hazard_x,
            hazard_y,
            width=200,
            height=100
        )

        # Add connections from pipeline registers to hazard unit
        # These represent control signals

        # From ID/EX to Hazard Unit
        idex_pos = self.components['ID/EX'].get_port('bottom')
        hazard_top = self.components['Hazard_Unit'].get_port('top')

        self.wires['IDEX_to_Hazard'] = ForwardingPath(
            self.canvas,
            create_path((idex_pos[0], idex_pos[1]), (hazard_top[0] - 50, hazard_top[1]), 'vertical_first'),
            name='IDEX_to_Hazard'
        )

        # From EX/MEM to Hazard Unit
        exmem_pos = self.components['EX/MEM'].get_port('bottom')
        self.wires['EXMEM_to_Hazard'] = ForwardingPath(
            self.canvas,
            create_path((exmem_pos[0], exmem_pos[1]), (hazard_top[0], hazard_top[1]), 'vertical_first'),
            name='EXMEM_to_Hazard'
        )

        # From MEM/WB to Hazard Unit
        memwb_pos = self.components['MEM/WB'].get_port('bottom')
        self.wires['MEMWB_to_Hazard'] = ForwardingPath(
            self.canvas,
            create_path((memwb_pos[0], memwb_pos[1]), (hazard_top[0] + 50, hazard_top[1]), 'vertical_first'),
            name='MEMWB_to_Hazard'
        )

    def _add_forwarding_paths(self):
        """Add forwarding paths from later stages back to ALU"""
        alu_pos = self.components['ALU'].get_port('left')

        # Forwarding from EX/MEM back to ALU (EX-EX forwarding)
        exmem_out = self.components['EX/MEM'].get_port('left')
        forward_ex_points = [
            (exmem_out[0] - 10, exmem_out[1] + 100),
            (exmem_out[0] - 30, exmem_out[1] + 100),
            (exmem_out[0] - 30, alu_pos[1] + 30),
            (alu_pos[0] - 15, alu_pos[1] + 30)
        ]
        self.wires['Forward_EX_EX'] = ForwardingPath(
            self.canvas,
            forward_ex_points,
            name='Forward_EX_EX'
        )

        # Forwarding from MEM/WB back to ALU (MEM-EX forwarding)
        memwb_out = self.components['MEM/WB'].get_port('left')
        forward_mem_points = [
            (memwb_out[0] - 10, memwb_out[1] + 100),
            (memwb_out[0] - 40, memwb_out[1] + 100),
            (memwb_out[0] - 40, alu_pos[1] + 40),
            (alu_pos[0] - 20, alu_pos[1] + 40)
        ]
        self.wires['Forward_MEM_EX'] = ForwardingPath(
            self.canvas,
            forward_mem_points,
            name='Forward_MEM_EX'
        )

    def set_hazard_state(self, stall: bool = False, forwarding: bool = False):
        """
        Set the state of the hazard unit
        Args:
            stall: True if pipeline is stalling
            forwarding: True if forwarding is occurring
        """
        if 'Hazard_Unit' in self.components:
            hazard_unit = self.components['Hazard_Unit']
            hazard_unit.set_stall(stall)
            hazard_unit.set_forwarding(forwarding)

            # Activate hazard unit if either is happening
            if stall or forwarding:
                hazard_unit.set_active(True)
            else:
                hazard_unit.set_active(False)

    def set_forwarding_paths(self, active_paths: List[str]):
        """
        Activate specific forwarding paths
        Args:
            active_paths: List of forwarding path names ('Forward_EX_EX', 'Forward_MEM_EX')
        """
        # Deactivate all forwarding paths first
        forwarding_wires = ['Forward_EX_EX', 'Forward_MEM_EX']
        for wire_name in forwarding_wires:
            if wire_name in self.wires:
                self.wires[wire_name].set_active(False)

        # Activate specified paths
        for path_name in active_paths:
            if path_name in self.wires:
                self.wires[path_name].set_active(True)

    def set_state_from_hazard_log(self, state_data: dict):
        """
        Set processor state from hazard log data
        Args:
            state_data: Dictionary with:
                - 'components': list of active component names
                - 'wires': list of active wire names
                - 'stall': boolean indicating if stalled
                - 'forwarding': boolean indicating if forwarding
                - 'forward_paths': list of active forwarding paths
        """
        # Set base components and wires
        self.set_active_components(state_data.get('components', []))
        self.set_active_wires(state_data.get('wires', []))

        # Set hazard unit state
        stall = state_data.get('stall', False)
        forwarding = state_data.get('forwarding', False)
        self.set_hazard_state(stall, forwarding)

        # Set forwarding paths
        forward_paths = state_data.get('forward_paths', [])
        self.set_forwarding_paths(forward_paths)

    def reset_all(self):
        """Override to also reset hazard unit"""
        super().reset_all()
        self.set_hazard_state(False, False)
        self.set_forwarding_paths([])
