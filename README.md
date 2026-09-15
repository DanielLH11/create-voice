# create-voice

The most powerfull skill to teach AI to talk like you

An agent skill that interviews you, measures how you actually write, and produces a voice profile any agent can read before writing as you. Then it blind-tests that profile against your own writing until you cannot pick yourself out of a lineup.

## Why this one is different

Every voice-cloning skill asks you to describe your writing. That is the wrong instrument. People report their own style badly, and the features that actually identify an author are the ones nobody can consciously report: function-word frequencies, sentence-length variance, punctuation tics.

Four things here that the others do not do.

**The two-layer rule.** A voice has a **lexicon layer** (the words you reach for, your crutch phrases, your jokes) and a **mechanics layer** (sentence length and spread, punctuation, paragraph shape, capitalization). They need different sources. Private chat leaks the lexicon, because nobody edits themselves in a text to their mother. Only deliberate writing shows the mechanics, and transcripts actively lie about them: speech-to-text inserts punctuation you never chose and normalizes away the disfluency that made voice notes attractive in the first place.

So `corpus_stats.py` has a `--transcript` flag that **refuses** to emit sentence length, punctuation, capitalization, accents and emoji. The rule is enforced in code rather than trusted to prose.

**Forced choice over self-report.** Instead of "what is your sentence rhythm", the skill shows three variants of the same content and asks which one is you. Recognition is reliable where description is not.

**The blind test.** The profile is not finished when it is written. The skill takes one of your real samples, writes two imitations from the profile alone, shuffles all three, and asks you to find yours. If you spot yourself instantly, it asks what gave the fakes away, folds that into the anti-voice section, and runs again. It passes when you are wrong or genuinely unsure twice in a row, and it records the tells it never resolved rather than claiming a pass it did not earn.

**Descriptive, not prescriptive.** The profile records how *you* write, including habits that contradict your own agent instructions. When the two disagree, the skill surfaces the conflict as a question instead of quietly editing the measurement to agree with the rule.

## Install

```
npx skills add DanielLH11/create-voice -g -y
```

Then run `/create-voice` in any agent that supports skills.

## What it does

1. **Scope.** Which language, which channels, where the file goes. A voice differs by language, so one profile per language rather than a bilingual hybrid.
2. **Corpus.** A WhatsApp export, a pasted conversation, or any text file. It goes in as the **casual anchor**: it supplies the lexicon and nothing else, so agent output does not end up reading like a text to your mother.
3. **Confirm.** Every crutch phrase the script found gets two questions: is this you, and would you keep it or cut it from your own draft. Frequency proves the habit exists, never that you want it reproduced.
4. **Write under pressure.** Six prompts across registers, including one where you rewrite a paragraph of generic AI prose. What you change is a rejection rule stated in action rather than in theory.
5. **Calibrate.** Twelve forced-choice dimensions.
6. **Draft.** Fills the profile, then scans your agent instruction files for conflicts.
7. **Blind test.** Until it passes.

## The script

`scripts/corpus_stats.py` does the counting, because models cannot count and a skill that asks one to eyeball a transcript produces different numbers every run.

```
python scripts/corpus_stats.py CHAT.txt --list-authors
python scripts/corpus_stats.py CHAT.txt --author "Name" --json out.json
python scripts/corpus_stats.py PASTED.txt --format plain
python scripts/corpus_stats.py VOICE_NOTES.txt --transcript
```

Stdlib only, no dependencies. It parses iOS and Android WhatsApp exports, keeps multi-line messages intact, drops system lines and media placeholders in English and Spanish, and reports sentence-length mean and spread, punctuation per 1000 words, capitalization and accent habits, emoji and laughter rates, and the n-grams that expose crutch phrases.

`--format plain` handles anything else: pasted chats, other exports, old drafts.

## Privacy

The corpus is somebody's private conversation, and the other person did not consent to any of this.

- Only the chosen author's messages are ever printed. Everyone else exists as a count and nothing more.
- Phone numbers, emails and URLs are masked everywhere, including verbatim samples.
- The skill works from the export in a scratch directory and writes no third-party content into the profile.
- Nothing is uploaded. The script is local and offline.

## License

MIT
