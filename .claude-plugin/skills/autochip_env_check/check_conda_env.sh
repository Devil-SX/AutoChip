#!/bin/bash
#==============================================================================
# Chip Verification Environment Checker
#
# Checks conda environments for cocotb and torchbit packages.
# Usage: bash scripts/check_env.sh
#==============================================================================

set -e

#------------------------------------------------------------------------------
# Helper functions
#------------------------------------------------------------------------------

print_header() {
    echo ""
    echo "=============================================="
    echo "$1"
    echo "=============================================="
}

print_section() {
    echo ""
    echo "=== $1 ==="
}

check_conda() {
    if command -v conda &> /dev/null; then
        local conda_version=$(conda --version 2>/dev/null || echo "unknown")
        echo "[OK] Conda installed: $conda_version"
        return 0
    else
        echo "[X] Conda not found"
        echo ""
        echo "Please install conda (miniconda or anaconda):"
        echo ""
        echo "Option 1: Miniconda (recommended for most systems)"
        echo "  https://docs.conda.io/en/latest/miniconda.html"
        echo ""
        echo "Option 2: Anaconda (required for CentOS7)"
        echo "  https://docs.conda.io/en/latest/index.html"
        echo ""
        echo "Note: CentOS7 can only install Anaconda (Miniconda not supported)"
        return 1
    fi
}

# Get package version from conda list JSON output
get_package_version() {
    local json_data="$1"
    local package_name="$2"

    # Use Python to reliably parse JSON and extract version
    echo "$json_data" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for pkg in data:
        if pkg.get('name') == '$package_name':
            print(pkg.get('version', ''))
            break
except:
    pass
" 2>/dev/null || echo ""
}

#------------------------------------------------------------------------------
# Main logic
#------------------------------------------------------------------------------

main() {
    print_header "Chip Verification Environment Checker"

    # Step 1: Check conda
    print_section "1. Checking Conda Installation"
    if ! check_conda; then
        exit 1
    fi

    # Step 2: Get conda environments
    print_section "2. Discovering Conda Environments"

    local envs=()

    # Parse conda env list output
    while IFS= read -r line; do
        # Skip comments, empty lines, and the separator
        [[ "$line" =~ ^#.*$ ]] && continue
        [[ "$line" =~ ^[[:space:]]*$ ]] && continue
        [[ "$line" =~ --- ]] && continue

        # Extract env name (first non-whitespace token)
        if [[ "$line" =~ ^[[:space:]]*([^[:space:]]+) ]]; then
            local env_name="${BASH_REMATCH[1]}"

            # Only add if not already in list (avoid duplicates)
            if [[ ! " ${envs[@]} " =~ " ${env_name} " ]]; then
                envs+=("$env_name")
            fi
        fi
    done < <(conda env list)

    local total_envs=${#envs[@]}
    echo "Found $total_envs environment(s)"

    # Step 3: Check each environment
    print_section "3. Checking Package Availability"

    # Table header
    printf "\n%-20s | %-12s | %-12s | %-12s | %-20s | %s\n" "Environment" "Cocotb" "Torchbit" "JSONSchema" "Compatibility" "Status"
    printf "%-20s-+-%-12s-+-%-12s-+-%-12s-+-%-20s-+-%s\n" "--------------------" "------------" "------------" "------------" "--------------------" "------------------"

    local ready_envs=()
    local ready_env_versions=()
    local recommended_env=""

    for env_name in "${envs[@]}"; do
        # Get all packages at once using conda list
        local packages_json=$(conda list -n "$env_name" --json 2>/dev/null || echo "{}")

        local cocotb_version=$(get_package_version "$packages_json" "cocotb")
        local torchbit_version=$(get_package_version "$packages_json" "torchbit")
        local jsonschema_version=$(get_package_version "$packages_json" "jsonschema")

        local cocotb_status=""
        local torchbit_status=""
        local jsonschema_status=""
        local compat_status=""
        local status_note=""

        if [ -n "$cocotb_version" ]; then
            cocotb_status="$cocotb_version"
        else
            cocotb_status="-"
        fi

        if [ -n "$torchbit_version" ]; then
            torchbit_status="$torchbit_version"
        else
            torchbit_status="-"
        fi

        if [ -n "$jsonschema_version" ]; then
            jsonschema_status="$jsonschema_version"
        else
            jsonschema_status="-"
        fi

        # Check version compatibility
        if [ -n "$cocotb_version" ] && [ -n "$torchbit_version" ] && [ -n "$jsonschema_version" ]; then
            # Extract major version numbers
            local cocotb_major=$(echo "$cocotb_version" | cut -d. -f1)
            local torchbit_major=$(echo "$torchbit_version" | cut -d. -f1)

            if [ "$cocotb_major" = "$torchbit_major" ]; then
                compat_status="✓ Compatible"

                # Check for recommended version (torchbit >= 2.0.0)
                local torchbit_major_num=$(echo "$torchbit_major" | sed 's/[^0-9]//g')
                if [ "$torchbit_major_num" -ge 2 ]; then
                    status_note="READY (recommended)"
                    ready_envs+=("$env_name")
                    ready_env_versions+=("cocotb:${cocotb_version}, torchbit:${torchbit_version}, jsonschema:${jsonschema_version}")
                    if [ -z "$recommended_env" ]; then
                        recommended_env="$env_name"
                    fi
                else
                    status_note="Ready (old version)"
                    ready_envs+=("$env_name")
                    ready_env_versions+=("cocotb:${cocotb_version}, torchbit:${torchbit_version}, jsonschema:${jsonschema_version}")
                fi
            else
                compat_status="✗ Version mismatch"
                status_note="Incompatible (major $cocotb_major vs $torchbit_major)"
            fi
        elif [ -n "$cocotb_version" ] && [ -n "$torchbit_version" ]; then
            compat_status="-"
            status_note="Missing jsonschema"
        elif [ -n "$cocotb_version" ]; then
            compat_status="-"
            status_note="Missing torchbit, jsonschema"
        elif [ -n "$torchbit_version" ]; then
            compat_status="-"
            status_note="Missing cocotb, jsonschema"
        elif [ -n "$jsonschema_version" ]; then
            compat_status="-"
            status_note="Missing cocotb, torchbit"
        else
            compat_status="-"
            status_note="Not suitable"
        fi

        printf "%-20s | %-12s | %-12s | %-12s | %-20s | %s\n" "$env_name" "$cocotb_status" "$torchbit_status" "$jsonschema_status" "$compat_status" "$status_note"
    done

    # Step 4: Summary and recommendations
    print_section "4. Summary"

    local ready_count=${#ready_envs[@]}

    if [ $ready_count -eq 0 ]; then
        echo "[X] No suitable environment found!"
        echo ""
        echo "To set up a chip verification environment:"
        echo "  1. Install conda (Miniconda or Anaconda for CentOS7):"
        echo "     - Miniconda: https://docs.conda.io/en/latest/miniconda.html"
        echo "     - Anaconda:  https://docs.conda.io/en/latest/index.html"
        echo "  2. Create a new conda environment:"
        echo "     conda create -n chip-verify python=3.10"
        echo "  3. Activate it:"
        echo "     conda activate chip-verify"
        echo "  4. Install cocotb:"
        echo "     pip install cocotb"
        echo "  5. Install torchbit (from local source):"
        echo "     pip install /path/to/torchbit"
        echo "  6. Install jsonschema:"
        echo "     pip install jsonschema"
        echo ""
        echo "Version Compatibility:"
        echo "  - torchbit 2.x.x ↔ cocotb 2.x.x (recommended)"
        echo "  - torchbit 1.x.x ↔ cocotb 1.x.x (legacy)"
        echo "  - jsonschema (any version)"
        echo "  - jsonschema (any version)"
    elif [ $ready_count -eq 1 ]; then
        echo "[OK] Found suitable environment: ${ready_envs[0]}"
        echo ""
        echo "To use this environment:"
        echo "  conda activate ${ready_envs[0]}"
    else
        echo "[OK] Found $ready_count suitable environment(s):"
        for i in "${!ready_envs[@]}"; do
            echo "  -> ${ready_envs[$i]} (${ready_env_versions[$i]})"
        done
        echo ""
        echo "Recommended: $recommended_env"
        echo "  conda activate $recommended_env"
        echo ""
        echo "Version Compatibility:"
        echo "  - torchbit 2.x.x ↔ cocotb 2.x.x (recommended)"
        echo "  - torchbit 1.x.x ↔ cocotb 1.x.x (legacy)"
        echo "  - jsonschema (any version)"
    fi

    echo ""
}

# Run main function
main "$@"
