---
title: Bridge inspector lands
date: 2026-05-15
tags: [ui, graph]
excerpt: Click any node and the pyramid dims everything except the load-bearing prerequisite chain. First visual feedback that actually answers "why am I stuck."
---

Spent the week wiring up the bridge inspector. The interaction: click a node, and the renderer dims everything that isn't on a path from a leaf to the selected node. What you're left with is the prerequisite skeleton holding it up.

Two surprises:

1. **The skeletons are smaller than I expected.** Most "advanced" nodes have 4–6 critical ancestors, not the dozen I was bracing for. The pyramid metaphor exaggerates breadth.
2. **Evidence sparsity shows up immediately.** When the dim happens, nodes with no evidence glow faintly red. You stop reading and start *seeing* the gap.

Next up: persisting selection state per session so the inspector remembers what you were poking at.
