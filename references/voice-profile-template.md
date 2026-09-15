# Voice profile template

Copy this structure into the output file. Every line of it must come from confirmed
evidence: a number the script measured, a sample the person wrote, or a choice they
made out loud. Delete any section you could not fill rather than guessing at it.

Write the profile in the language it describes. A Spanish voice profile written in
English describes a translation, not a voice.

---

# Voice: <name>

Built <YYYY-MM-DD> from <corpus: N messages, M words> plus <K> written samples.
Languages: <es, en>. Registers covered: <casual, explanatory, professional, ...>.

**This file describes how <name> writes. It is not agent policy.** House rules for
how agents write live in the agent instruction files and are a separate thing, even
when the two contradict each other. Keep the description honest and resolve the
contradiction in the Conflicts section below, never by editing the description.

Read this before writing anything as <name>. Run the self-check at the bottom
before showing a draft.

## Observed

What the corpus and the samples show, stated as fact. Checkable only. A trait
someone could argue about is a preference and belongs further down. Record traits
that contradict house rules here anyway; that is what this section is for.

**Never does**
- <e.g. never uses a semicolon>
- <e.g. never closes a casual message with a period, 93.8% of messages>

**Always does**
- <e.g. always capitalizes the first word even when skipping terminal punctuation>
- <e.g. always answers first, context after>

## Reproduction rules

What an agent writing as <name> actually does. The default for every line is "match
Observed". List only the deliberate departures, each with the reason and who decided
it, so a later reader can tell a decision from a drift.

| Trait | Observed | Agent does | Why |
| --- | --- | --- | --- |
| <em dash> | <uses occasionally> | <never> | <house rule, his call on YYYY-MM-DD> |

## Conflicts with house rules

Every place the measured voice disagrees with the agent instruction files, listed
whether or not it was resolved. An unresolved row is useful; a hidden one is not.

| Trait | Voice says | House rule says | Resolution |
| --- | --- | --- | --- |
| <trait> | <observed, with the number> | <the rule, and which file> | <which wins, or unresolved> |

## Calibration

Numbers from the corpus and the written samples. The casual-anchor row comes from
the chat export and is the only row measured rather than estimated. Mark estimated
rows as such.

| Register | Where it shows up | Sentence words, mean / spread | Paragraph | Openers |
| --- | --- | --- | --- | --- |
| Casual (measured) | <WhatsApp, DMs> | <8.4 / 5.5> | <1 line> | <lowercase, no greeting> |
| Explanatory | <docs, long Slack> | <x / y> | <n lines> | <...> |
| Professional | <email, PRs> | <x / y> | <n lines> | <...> |
| Frustrated | <...> | <x / y> | <n lines> | <...> |
| Persuasive | <...> | <x / y> | <n lines> | <...> |

Punctuation per 1000 words, casual anchor: <period X, comma Y, question Z, ...>.
Habits: <lowercase starts N%, no terminal punctuation N%, accent discipline N%>.

## Lexicon

**Signature phrases.** Confirmed as his, wants them kept.
- <"al final" (x3 in corpus)> - <when he reaches for it>

**Crutch words to keep.** Frequent, confirmed, and load-bearing in casual registers.
- <phrase> - <which registers it belongs in, which it does not>

**Crutch words to cut.** Frequent in speech, unwanted in writing. An agent must not
reproduce these even though the corpus is full of them.
- <phrase> - <why he rejects it>

**Banned.** Words and constructions he will not sign his name to.
- <word or pattern>

**Laughter, emoji, shorthand.** Measured rates, plus the rule for where they apply.
- Laughter: <form and rate, e.g. "jajaja", 12 per 100 messages, casual only>
- Emoji: <rate, the specific set, registers allowed>
- Shorthand: <q, xq, tb ...> - <allowed registers>

**Profanity.** <the level, the specific words, which registers>

## Signature moves

Structural habits that survive across registers. Three to six, each one a thing an
imitator would have to do on purpose.
- <e.g. states the conclusion first, then one reason, then stops>
- <e.g. corrects himself mid-message in a follow-up rather than editing>

## Anti-voice

What a competent imposter produces. Concrete failures observed during the blind
test, not generic AI-slop warnings.
- <e.g. balanced two-sided paragraphs; he picks a side>
- <e.g. tidy closers; he just stops>
- <what gave the fakes away in round 1, round 2, ...>

## Gold samples

Three to five verbatim samples, labeled by register, each with one line on what it
demonstrates. These carry more signal than every rule above, so keep them exact.
Never include another person's messages.

### <register> - <what it demonstrates>
> <verbatim sample>

## Draft self-check

Run this against a draft before showing it. Each item is a yes or no.
- [ ] Sentence lengths land in the calibration band for this register, spread included
- [ ] No banned word, no cut-crutch, no forbidden punctuation
- [ ] Opener matches the register's pattern
- [ ] Ending stops where he stops, not where a summary would go
- [ ] Reads closer to the gold sample for this register than to the anti-voice
- [ ] <profile-specific check>
