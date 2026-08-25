## Summary of Changes
Briefly describe the purpose of this PR and what has been modified or added.

## Related Issue / Feature ID
Closes # [issue number] (or relates to Feature ID `FEAT-XXX` in `FEATURES.md`)

## Type of Change
- [ ] `feat`: New feature (non-breaking change which adds functionality)
- [ ] `fix`: Bug fix (non-breaking change which fixes an issue)
- [ ] `refactor`: Code refactor with no behavioral changes
- [ ] `perf`: Performance improvement
- [ ] `test`: New or updated tests
- [ ] `docs`: Documentation updates
- [ ] `security`: Security enhancement or patch
- [ ] `chore`: Tooling, build, or dependency updates

## Financial & Ledger Integrity Checklist
If this PR modifies financial models, calculations, or transaction ledgers:
- [ ] Accounting rules strictly adhere to FIFO (or documented standard)
- [ ] Decimal types are used for all monetary calculations (no floats)
- [ ] Corporate actions (bonus, splits, rights, dividends) correctly adjust lots/basis
- [ ] Comprehensive deterministic unit tests added in `backend/tests/accounting/`

## General Checklist
- [ ] Code follows project conventions in `AGENTS.md`
- [ ] Automated tests added/updated and passing locally
- [ ] Type annotations included and type checks passing
- [ ] Documentation updated (`README.md`, `FEATURES.md`, `CHANGELOG.md`, architecture docs)
- [ ] No secrets, keys, or non-template credentials committed

