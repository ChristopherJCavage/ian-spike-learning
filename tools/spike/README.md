# SPIKE App block index

Derived from the live web app. Not LEGO artwork. Not a dumped PDF.

```
python3 tools/spike_extract.py              # fetch current bundle, rewrite blocks.json
python3 tools/spike_extract.py --from-dir DIR
python3 tools/blocks.py fixtures
```

- `blocks.json` — 88 Word Blocks (shape, message, defaults, colours, hub, extension, Python), 33 Icon Block opcodes, hub facts, category colours.
- `fixtures/` — `good-*` must check clean and draw; `bad-*` must raise the code in its `# expect:` line. `bad-boolean-as-statement.spike` is the Distance Sensor table bug. `bad-icon-hats-chained.spike` is two colour hats in one row.

The bundle's 147 `flipper*_*` strings are **not** 147 blocks: 90 are real
definition classes, 21 are hyphenated field names, 8 are test blocks, and
the rest are legacy opcodes kept for project migration. `blocks.json`
records each group under `not_blocks` and `legacy`, and `stats` carries
arithmetic that has to add up. See `context/spike-blocks.md`.
