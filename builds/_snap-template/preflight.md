# Pre-flight -- (name)

`snap.py check` proves the layout is self-consistent, not that it matches
the real blocks. Every block in `tools/snap/parts.json` is `measured: false`
until someone checks it. Before you sit down with Ian:

- Build every step on the real board, batteries OUT. Does each wire end sit
  snug on a block's snap?
- Put the batteries in (Chris). Does each `expect` line happen?
- Does anything depend on which end of a part is +? If yes, check that end.
- Read every page as someone who has not seen the layout.

If a step is wrong, patch `circuit.snap`, then `steps.md`, then run `render`.
