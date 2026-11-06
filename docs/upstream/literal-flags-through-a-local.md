# Draft: flags held in a local constant

Not filed. Applies to lookahead-lint (LA005), leakguard (LG004, LG009) and overfit-gauntlet
(LA04), which treat a keyword that is not a literal as unsafe.

    randomise = False
    train, test = train_test_split(rows, test_size=0.3, shuffle=randomise, random_state=0)

is flagged although the split is unshuffled, for example `corpus/v1/files/fcd1b3331e2.py:14`.
The same happens with `label=stamp` in `resample`. Those clean twins are the tools' false
positives at L1 and L2.

monte-neo inlines names assigned one constant (`_InlineConstants` in `verify/lint.py`), which is
why its paired-at-the-site rate is the same at L0 and L1 (24/46) while five of the other six
tools drop. A pass like that would fix these false positives and recover the L1 misses of
`shift(lag)` and `rolling(center=flag)`.
