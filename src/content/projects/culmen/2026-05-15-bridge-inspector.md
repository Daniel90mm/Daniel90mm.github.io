---
title: Bridge inspector lands
date: 2026-05-15
tags: [ui, graph]
math: true
excerpt: Click any node and the pyramid dims everything except the load-bearing prerequisite chain. First visual feedback that actually answers "why am I stuck."
---

Spent the week wiring up the bridge inspector. The interaction: click a node, and the renderer dims everything that isn't on a path from a leaf to the selected node. What you're left with is the prerequisite skeleton holding it up.

Two surprises:

1. **The skeletons are smaller than I expected.** Most "advanced" nodes have 4–6 critical ancestors, not the dozen I was bracing for. The pyramid metaphor exaggerates breadth.
2. **Evidence sparsity shows up immediately.** When the dim happens, nodes with no evidence glow faintly red. You stop reading and start *seeing* the gap.

Next up: persisting selection state per session so the inspector remembers what you were poking at.

## Math sanity check

The "load-bearing ancestor set" for a node $v$ is just the set of leaves reachable by reversing edges:

$$
B(v) \;=\; \{\, u \in L \;:\; u \rightsquigarrow v \,\}
$$

where $L$ is the leaf set and $u \rightsquigarrow v$ means there is a directed path. Cost of the inspector is $O(|E|)$ per click — a single reverse-DFS.

## Inline SVG demo

{{< fig caption="reachable ancestors (filled) vs everything else (dim)" >}}
<svg viewBox="0 0 320 140" xmlns="http://www.w3.org/2000/svg" style="background:#0c0c0c;width:100%;max-width:420px">
  <g fill="none" stroke="#5e5e5e" stroke-width="1">
    <line x1="40"  y1="110" x2="100" y2="60"/>
    <line x1="100" y1="110" x2="100" y2="60"/>
    <line x1="160" y1="110" x2="160" y2="60"/>
    <line x1="220" y1="110" x2="160" y2="60"/>
    <line x1="280" y1="110" x2="220" y2="60"/>
    <line x1="100" y1="60"  x2="160" y2="20"/>
    <line x1="160" y1="60"  x2="160" y2="20"/>
  </g>
  <g font-family="JetBrains Mono, monospace" font-size="10" text-anchor="middle">
    <circle cx="160" cy="20"  r="9" fill="#ff9a3c"/>            <text x="160" y="23" fill="#0c0c0c">v</text>
    <circle cx="100" cy="60"  r="8" fill="#ff9a3c"/>            <text x="100" y="63" fill="#0c0c0c">a</text>
    <circle cx="160" cy="60"  r="8" fill="#ff9a3c"/>            <text x="160" y="63" fill="#0c0c0c">b</text>
    <circle cx="40"  cy="110" r="7" fill="#ff9a3c"/>            <text x="40"  y="113" fill="#0c0c0c">L</text>
    <circle cx="100" cy="110" r="7" fill="#ff9a3c"/>            <text x="100" y="113" fill="#0c0c0c">L</text>
    <circle cx="160" cy="110" r="7" fill="#ff9a3c"/>            <text x="160" y="113" fill="#0c0c0c">L</text>
    <circle cx="220" cy="110" r="7" fill="#262626" stroke="#3a3a3a"/>  <text x="220" y="113" fill="#5e5e5e">·</text>
    <circle cx="280" cy="110" r="7" fill="#262626" stroke="#3a3a3a"/>  <text x="280" y="113" fill="#5e5e5e">·</text>
  </g>
</svg>
{{< /fig >}}
