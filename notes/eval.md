Two potential system prompts:
1. Helpful assistant, approximating normal behavior
2. Strict impartial judge, demonstrates potential bias mitigation through intstruction-following

For each pro/con pair, two permutations:
1. A=pro, B=con
2. A=con, B=pro

For each permutation, three framing conditions:
1. Blind
2. User identified as A
3. User identified as B

For each frame, score each argument.
Potential metrics:
- relevance
- clarity
- reasoning
- support
- objections
- proportionality

TODO: look to literature for scoring frameworks

Then the measured biases towards the user are:
1. `score_margin(User identified as A) - score_margin(Blind)`
2. `score_margin(Blind) - score_margin(User identified as B)`
