# Matchmaker rejection-bias fixtures

Fixture scenarios to prove the matchmaker defaults to rejection instead of
rationalizing weak matches. For use in matchmaker prompt tuning and
adversarial testing.

## Required scenarios

### 1. No plausible project match
Spaghetti: "I should learn Rust for embedded work."
Projects: web portfolio, pulse oximeter, bibliography manager.
Expected: zero matches. No rationalizing "embedded" -> "pulse oximeter uses C."

### 2. Weak lexical overlap only
Spaghetti: "Graph-based data structures for dependency resolution."
Projects: bibliography manager (has "data" and "graphs" as words but no
structural overlap).
Expected: zero matches. Lexical overlap without conceptual fit is not a match.

### 3. Unrelated project documents
Spaghetti: "Home automation with Zigbee and MQTT."
Projects: fnirs (biophotonics), pulse oximeter (medical device).
Expected: zero matches. Different domains entirely.

### 4. One genuine multi-project match
Spaghetti: "PCA for multivariate signal denoising."
Projects: fnirs (multichannel optical signals), pulse oximeter (AC/DC
separation across wavelengths).
Expected: two matches, both with medium-to-high confidence and specific
rationales.

## Testing protocol

The matchmaker should **reject by default**. For each scenario:
1. Run matchmaker with the given inputs.
2. Verify the output contains exactly the expected number of matches.
3. Verify all proposed matches include concrete rationales, not generic
   usefulness claims.
4. Verify no matches are proposed where the rationale is vague.

For the multi-project scenario, also verify that both matches are independently
justified - not one rationale copied to both.
