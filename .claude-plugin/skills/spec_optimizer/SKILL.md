---
name: spec_optimizer
description: Defines the required structure and conventions for IC module specification documentation, including versioning, interface tables, and verification methodology.
---

This SKILL defines the documentation structure for a hardware module. The specification must include the following sections.

## Required Sections

### Version Description

Follow semantic versioning specification (MAJOR.MINOR.PATCH format).

### Module Name

The name of the hardware module being documented.

### Submodules

List any submodules and their relationships.

### Module Interface (IO)

Interface signals must follow the table format below:

| name | direction | bitwidth | valid voltage | description |
|------|-----------|----------|---------------|-------------|
| clk  | input     | 1        | posedge       | Clock signal |
| rst_n| input     | 1        | low           | Active low reset signal |
| data_in | input  | 8        | -             | Input data bus |
| data_in_vld | input | 1        | high          | Input data valid signal |
| data_in_rdy | output | 1       | high          | Input data ready signal |

**Signal Ordering Guidelines:**

- **GOOD**: Group by semantic meaning (e.g., `data_in`, `data_in_vld`, `data_in_rdy`; or group by connection target like `addr_rd`, `addr_rd_vld`, `data_rd`, `data_rd_vld` for buffer connections)
- **BAD**: Group by direction only (all inputs together, all outputs together)

### Verification Plan

The verification plan must include:

1. **Input/Output Data Structures** - Definition of data formats and stimulus generation strategy
2. **Python Golden Model** - Reference implementation approach
3. **Testbench Design** - Testbench architecture and methodology
4. **Test Case Design** - Test case definitions and dependency relationships
5. **Test Report Metrics** - Including feature coverage, code coverage, etc.

**Test Case Template:**

| Test Case ID | Test Case Name | Description | Input Data Description | Expected Output | Dependency |
|--------------|----------------|-------------|------------------------|-----------------|------------|
| TC_001       | Basic Functionality Test | Verify basic module functionality | Input standard data set | Output matches Golden Model | None |
| TC_002       | Boundary Condition Test | Test module behavior at boundaries | Input max/min values | Module handles boundary values correctly | TC_001 |

---

## Optional but Recommended Sections

### Interface Timing Diagrams

Waveform descriptions showing protocol timing relationships.

### Core Numerical Analysis

Mathematical formulas for internal variables and calculations.

### Functional Pseudocode

Python-like pseudocode describing module behavior.

### State Machine Description

If the module contains a state machine, document:
- State definitions
- State transition conditions
- State transition diagram
