# Claude Code Plugins

This directory contains Claude Code skill definitions for the AutoChip project.

## Directory Structure

```
.claude-plugin/
└── skills/
    ├── chip_verification.md    # Chip verification with cocotb/torchbit
    └── chisel.md                # Chisel/Scala hardware construction
```

## Available Skills

### Chip Verification (`chip_verification.md`)
- **Purpose**: Comprehensive guidance for chip verification using cocotb and torchbit
- **When to use**: Writing testbenches, designing golden models, debugging verification issues
- **Supporting materials**:
  - Reference docs: `chip_verification/reference/`
  - Scripts: `chip_verification/scripts/`
  - Templates: `chip_verification/template/`

### Chisel (`chisel.md`)
- **Purpose**: Chisel/Scala hardware construction language with mill build tool
- **When to use**: Writing Chisel modules, generating SystemVerilog, mill build issues
- **Supporting materials**:
  - Reference docs: `chisel/reference/`
  - Scripts: `chisel/scripts/`
  - Templates: `chisel/template/`

## Path Resolution

Skills reference their supporting materials using absolute paths from the repository root. This allows skills to be located in `.claude-plugin/skills/` while maintaining access to their original supporting directories.

For example, the chip_verification skill references:
- Reference docs: `/home/sdu/AutoChip/chip_verification/reference/`
- Scripts: `/home/sdu/AutoChip/chip_verification/scripts/`
- Templates: `/home/sdu/AutoChip/chip_verification/template/`

## Adding New Skills

To add a new skill:

1. Create skill file: `.claude-plugin/skills/<skill-name>.md`
2. Add YAML frontmatter:
   ```yaml
   ---
   name: Skill Name
   description: When to use this skill
   ---
   ```
3. Document skill content and usage patterns
4. Create supporting directories if needed (reference/, scripts/, template/)
5. Update path references to use absolute paths from repository root
6. Test skill activation with relevant queries

See `docs/skill-integration.md` for detailed integration guidelines.
