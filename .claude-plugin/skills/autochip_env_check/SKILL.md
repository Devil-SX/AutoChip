---
name: autochip_env_check
description: Check and validate the AutoChip development environment dependencies including chip simulators (Verilator/VCS/SimVision) and Python packages (torchbit, cocotb, jsonschema) in conda environments
---

This skill checks whether the development environment required to run AutoChip Agent is properly configured. If the environment is not set up correctly, the skill provides step-by-step guidance to help users complete the configuration.

# Step 1: Check Environment

### Chip Simulation Tools (at least one required)
- **Verilator** (version must be 5.038)
- **VCS**
- **SimVision**

### Python Runtime Environment (required)
- **torchbit** 2.x
- **cocotb** 2.x
- **jsonschema** (required for IC project schema validation)

### Check Method

Use the `find` command to recursively search the project directory for `.autochip/env.yaml`. If it exists, read the file and compare the timestamp with the current time. If the difference exceeds 6 hours, perform the environment check and proceed with Step 1/2/3. Otherwise, skip Step 1/2/3 and return that the environment is correct.

Example content for `.autochip/env.yaml`:

```yaml
last_checked: 2024-06-01T12:00:00Z
status:
  verilator:
    path: "<verilator_path>"
    version: "5.038"
  vcs:
    path: "not installed"
    version: "not installed"
  simvision:
    path: "not installed"
    version: "not installed"
  python_env:
    python_bin_path: "<python_bin_path>"
    python_env_type: "conda" # conda | system | uv
    python_version: "3.8.10"
    torchbit: "2.1.0"
    cocotb: "2.7.0"
    jsonschema: "4.17.3"
```

- **Conda environments**: Invoke [check script](check_conda_env.sh) to scan all conda environments and identify suitable environments
- **Command line check**: Use command line tools or scripts to check the installation status of each dependency

# Step 2: Configure Environment

If all environment requirements are met, skip Step 2. Otherwise, guide the user to install the required dependencies.

# Step 3: Output Configuration

First, check if `.autochip/env.yaml` exists in the project. If it does, update its configuration and timestamp. Otherwise, use `find` to check if the `.autochip` directory exists:
- If the `.autochip` directory exists, create `env.yaml` in it
- If the `.autochip` directory does not exist, create the `.autochip` directory in the current location, then create `env.yaml` inside it

