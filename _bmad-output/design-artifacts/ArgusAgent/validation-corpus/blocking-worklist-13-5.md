# Blocking-finding adjudication worklist — Story 13.2

> DERIVED by `scripts/audit_validation_corpus.py`. Do not hand-edit: re-run the
> script. Every row is a **blocking** (verdict-eligible) finding — the population the
> ≥80% precision gate is measured over. Advisory findings are in
> `adjudication-set.json` and are deliberately absent here: an advisory finding does
> not move a verdict and is not a false accusation, so it is not in the denominator.

**Nothing below is adjudicated.** TP/FP is the named human's call (protocol §2/§4).

## ai-body-runtime — 0 blocking

Pin `4480ffdeb4c56e232d230ebb67572117b72dd754` · python · 15 source files · verdict `RELEASE_READY` (exit 0) · deep 2/3

_No blocking finding, and this member IS byte-reproducible — genuinely nothing to adjudicate._

## agent-markovich — 0 blocking

Pin `a561668636d8dac922b72d548ad92fdcc814a2ac` · python · 65 source files · verdict `INSUFFICIENT_COVERAGE` (exit 3) · deep 24/65

_No blocking finding, and this member IS byte-reproducible — genuinely nothing to adjudicate._

## minions — 0 blocking

Pin `ec63b7293b7036bf910a0d1b5e61aba7dc551526` · python · 583 source files · verdict `INSUFFICIENT_COVERAGE` (exit 3) · deep 221/583

_No blocking finding, and this member IS byte-reproducible — genuinely nothing to adjudicate._

## xagents-webapp — 0 blocking

Pin `33a86525a4981c2725133c3f297ce003c1ef8a2b` · typescript · 862 source files · verdict `INSUFFICIENT_COVERAGE` (exit 3) · deep 513/862

_No blocking finding, and this member IS byte-reproducible — genuinely nothing to adjudicate._

## agent-smith — 0 blocking

Pin `9ab774d7bf5d61da552c61094b2d478f72dfbb6d` · typescript · 435 source files · verdict `INSUFFICIENT_COVERAGE` (exit 3) · deep 72/145

_No blocking finding, and this member IS byte-reproducible — genuinely nothing to adjudicate._

---

**Total blocking findings to adjudicate: 0.** Precision = TP / (TP + FP) over this population, as an exact `Fraction` (AR4). The gate additionally requires 0 blocking false positives on a clean repository, N ≥ 5, and the adjudication run recorded cleared — all four, or the gate stays PROVISIONAL (protocol §5).
