# Open Questions

These questions are intentionally unresolved. They are research targets, not requirements disguised as facts.

## Operation

1. What is the minimum executable primitive set?
2. Is recomposition fundamental, or can it emerge from simpler operations?
3. Can a machine discover useful operation combinations without a semantic task objective?
4. What makes one state transition more useful than another without importing a human goal model?

## Representation

5. When should the machine change representation rather than operate longer on the existing representation?
6. Can executable representations themselves become reusable learned structures across held-out tasks?
7. What makes a relation operational rather than merely descriptive?

## Context and experience

8. Can useful context be inferred from machine-observable state/event history rather than supplied by the environment?
9. What context representation is sufficient to separate regimes without becoming an overfit task label?
10. Does contextual credit improve cumulative regret and recovery, not merely persistence of a selected operator?
11. What minimum persistent state is required for experience to alter future operation?
12. Which state should survive, decay, or be discarded?

## Learning

13. Can learning alter operation policy while the machine remains continuously active?
14. How do we distinguish useful adaptation from accidental drift or candidate-space enumeration?
15. What evidence shows that changed operation structure was learned rather than memorized?
16. When does history-dependent selection become reusable learning rather than contextual bandit behavior?

## Reflection

17. Can a single live process reify its actual execution machinery rather than an external description of it?
18. Can the running process causally install a modified evaluator/transition mechanism without restarting?
19. What is the smallest safe probe/commit mechanism required for online causal reflection?
20. After causal reflection, does modifying the proposer/modifier add measurable capability or only a new search layer?

## Exploration and closure

21. How can the system detect that its current operation regime is becoming self-confirming?
22. How can it discover information or operations that its current regime does not know to value?
23. How much destabilization is useful before exploration becomes noise?

## Resource allocation

24. Is computation allocation simply a consequence of operation policy rather than a primary attention mechanism?
25. Can a machine adapt computation spend from downstream consequences without a human-style depth objective?
26. Can operation value be estimated from downstream state change rather than a fixed reward?

## Generality

27. Is generality better described as capability composition than general intelligence?
28. What is the smallest reusable operational substrate that transfers across unrelated environments?
29. Does a general machine need a general world model, or can it construct local models as needed?

## Validation / kill tests

30. What experiment would show that the entire system is merely an elaborate search procedure?
31. What experiment would show that contextual credit provides no benefit once supplied labels are removed?
32. What experiment would show that learned executable structure gives no transfer beyond fresh search?
33. What experiment would show that causal reflection adds no capability beyond ordinary external hot-swap?
34. What experiment would show that a proposed machine-native primitive is only a vocabulary choice rather than an irreducible mechanism?

## Reflection substrate — newly separated questions

35. What exactly is the smallest reflected mechanism: compound dispatch, evaluator, or full transition semantics?
36. What object-language representation is sufficient to reify the relevant environment and continuation state without leaving critical structure opaque?
37. What installation semantics are required: jump, resume, tail transfer, or explicit level shift?
38. When does a host-language bootstrap hook remain part of the fixed substrate rather than becoming a hidden non-machine special case?
39. Can the dispatch-only reflection seam be implemented on an independent substrate with the same abstract transition semantics?
40. Does causal dispatch reflection provide any capability beyond ordinary rebinding under matched controls?
