---
name: chip_semantic_versioning
description: Hardware chip semantic versioning scheme for IC modules. Defines MAJOR.MINOR.PATCH conventions for RTL design and verification changes.
---

This semantic versioning follows the standard three-part MAJOR.MINOR.PATCH format, but adapted for hardware chip development semantics. Versioning is module-independent—each module has its own version number that is shared between both RTL and testbench.

## MAJOR

Increment when making **incompatible** changes to the module interface or functionality:

- Module IO port changes (addition, removal, or renaming of ports)
- Protocol or interface modifications that break backward compatibility
- Architectural changes requiring updates to dependent modules
- Removal or deprecation of existing features

## MINOR

Increment when adding **backward-compatible** functionality:

- New test cases or modifications to test methodology
- Feature enhancements that maintain compatibility with existing designs
- Performance improvements without interface changes
- Addition of optional or configurable features

## PATCH

Increment when making **backward-compatible** bug fixes:

- Bug fixes in RTL logic
- Timing violation fixes
- Documentation updates
- Testbench or script corrections
- Minor changes that do not affect functionality

## Version Examples

| Version | Date       | Description                        |
|---------|------------|------------------------------------|
| 1.0.0   | 2023-01-01 | Initial release                    |
| 1.1.0   | 2023-03-15 | Added new feature X                |
| 1.1.1   | 2023-04-10 | Bug fix for feature Y              |
| 2.0.0   | 2023-06-01 | Interface restructure (breaking)   |
