---
name: create_spec
description: Create a hardware module specification document for an AutoChip project. This command checks the project structure, generates an initial specification based on defined standards, and writes the document to the appropriate location.
argument-hint: [original spec text]
---

# Step 1

Check if the project has a `.autochip` directory and the required configuration files according to `autochip_proj_arch`. If not, create the project structure as defined by the skill.

# Step 2

Generate an initial version of the hardware module specification document following the standards defined in the `spec_optimizer` skill. Present the proposal and any details requiring confirmation to the user for discussion. If the user approves, proceed to Step 3.

# Step 3

Write the documentation to the appropriate location within the project structure and update the metadata.
