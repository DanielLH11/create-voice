---
name: create-voice
description: Interview someone and build a voice profile that makes an agent write as them, then blind-test it until they cannot pick their own writing out of a lineup.
disable-model-invocation: true
---

# Create voice

Build a **voice profile**: a file an agent reads before writing as a specific person.

A voice has two layers and they need different sources. The **lexicon layer** is the
words someone reaches for, their crutch phrases, their jokes, their swearing. Speech
and private chat leak it, because nobody edits themselves in a text to their mother.
The **mechanics layer** is sentence length and its spread, punctuation, paragraph
shape, capitalization, prose against bullets. Only deliberate writing shows it, and
transcripts actively lie about it: speech-to-text strips the filler and inserts
punctuation the speaker never chose.

So the corpus supplies the lexicon and the written samples supply the mechanics.
Neither substitutes for the other.

## Rules of engagement

- **One question at a time.** Never present a wall of questions. Each answer decides
  the next question, and a person who is handed ten at once answers all ten badly.
- **Evidence before self-report.** People describe their own writing wrong. Measure
  first, then ask them to confirm or reject what you measured. Never ask someone to
  recall a tic; tics are invisible from the inside.
- **Nothing enters the profile unconfirmed.** A number from the script is evidence a
  habit exists, never evidence they want it reproduced.
- **Describe the person, do not restate agent policy.** The profile records how they
  write. House rules in the agent instruction files record how agents write. These
  are different documents about different subjects, and they will contradict each
  other: someone whose rules ban a construction may use it constantly themselves.
  Record what they do, then resolve the contradiction in step 6 as an explicit
  decision. Never quietly edit the observation to agree with the rule. A profile
  that flinches from what the corpus shows is describing the rules, not the person.
- **Third-party content never leaves the scratchpad.** The export contains someone
  who did not consent to this. Work from it in the scratchpad, quote only the
  subject's own messages, and do not copy the raw export anywhere.

## Steps

### 1. Scope the profile

Ask, in one exchange: which language or languages the profile covers, which channels
the voice gets used in (chat, email, PRs, posts, docs), and where the file should be
written. A voice differs by language, so a profile built from English answers will
mis-model the same person's Spanish. If they name two languages, build one profile
per language rather than a bilingual hybrid, and say so now rather than at the end.

Suggest `~/VOICE.md` as the path only if their agent instructions already point
there. Do not create the file yet.

**Done when** you have a language, a channel list, and an output path.

### 2. Build the corpus

Ask for one conversation with someone they are unguarded with. A WhatsApp export is
the best source; `references/corpus-sources.md` has that path and three others,
ranked, with the exact commands. Take the highest one they can actually do, and have
them put the file in the scratchpad rather than the project.

State the register trap before they choose a chat, not after. A chat with a family
member is the most authentic sample available and the narrowest register they own.
It goes in as the **casual anchor** and supplies the lexicon layer only. If it
becomes the whole profile, every agent output reads like a text to their mother,
including pull request descriptions. The written samples in step 4 are what cover
the other registers.

Then run `scripts/corpus_stats.py`. It lives in this skill's own folder, not in the
working directory, so resolve that folder first and call it by absolute path. It
reports sentence-length mean and spread, punctuation rates per 1000 words,
capitalization and accent habits, emoji and laughter rates, and the n-grams that
expose crutch phrases. These are counts, so let the script produce them. Eyeballing
a transcript gives different numbers every run, which is the whole reason this step
is code.

Pass `--transcript` for anything that came out of speech-to-text. The flag drops
every mechanics statistic, because those describe the transcriber rather than the
speaker. If the report warns that the corpus is under 2000 words, ask for a longer
export before continuing. Below that the spread figures are noise.

**Done when** the report has run against a confirmed author and the numbers are in
front of you.

### 3. Confirm the lexicon

Walk the script's crutch-phrase candidates, one at a time, using the two-question
pattern in `references/calibration-bank.md`: is this you or is it this conversation,
and would you keep it or cut it from your own draft. Do the same for the emoji set,
the laughter form, the shorthand, and the profanity level.

Most candidates will be rejected. That is the step working, not failing.

Then check authorship on the long messages the report offers as gold samples. A chat
export contains text the person did not write: forwarded messages, pasted articles,
assisted drafts. These are the longest messages in any chat, so they sort straight to
the top of the candidate list, and the script cannot tell the difference. Show each
one and ask whether they wrote it themselves. A pasted paragraph promoted to a gold
sample teaches the profile someone else's voice.

**Done when** every candidate is sorted into signature, keep, cut, or not-me, every
gold-sample candidate is confirmed as their own writing, and none is left unasked.

### 4. Collect written samples under pressure

Do not ask them to describe how they write. Make them write, one prompt at a time,
in the target language. Six prompts, roughly two sentences of setup each:

1. **Casual.** Tell a friend about something that happened to you this week.
2. **Explanatory.** Explain something you know well to someone who does not.
3. **Frustrated.** Something you paid for is broken. Write the complaint.
4. **Persuasive.** Convince someone to change their mind about a decision.
5. **Professional.** The same news as prompt 1, but to a client or a manager.
6. **The rewrite.** Hand them a paragraph of competent, generic AI prose on a topic
   they care about and ask them to make it theirs. What they *change* is the highest
   signal in the whole interview: every edit is a rejection rule stated in action
   rather than in theory.

Accept whatever length they give. Do not coach mid-prompt, do not react between
prompts beyond moving on, and never show them your own attempt first.

**Done when** six samples are captured verbatim in the scratchpad.

### 5. Calibrate by forced choice

Run the batteries in `references/calibration-bank.md`. Show three variants of the
same content and ask which one is them. Seed the variants from their own samples,
so only the dimension under test changes.

Recognition is the reliable instrument here. Ask "which of these is you" rather than
"what is your sentence rhythm", every time.

**Done when** every dimension in the bank has an answer or is explicitly recorded as
unsettled.

### 6. Draft the profile

Write the file to the step-1 path, following `references/voice-profile-template.md`.
Fill it only from confirmed evidence: measured numbers, their own samples, choices
they made. Delete any section you cannot fill rather than inventing it.

Write the profile in the language it describes.

Then scan for conflicts before you hand the file over. Read the agent instruction
files that will sit alongside it (`CLAUDE.md`, `AGENTS.md`, `.rules`, and anything
they point at) and compare every house rule about writing against what you measured.
Each disagreement becomes one question, asked one at a time:

> "Your export uses an em dash 1.8 times per 1000 words. Your CLAUDE.md tells agents
> never to use one. Both stay true: you write that way, agents will not. Should an
> agent writing *as you* follow your habit or the house rule?"

Record the observation in Observed either way, the answer in Reproduction rules, and
the pair in Conflicts. An unresolved conflict is recorded as unresolved, never
dropped and never smoothed over by softening the measurement.

**Done when** the file exists, every section it keeps traces back to something in
steps 2 through 5, and every house-rule conflict has a row.

### 7. Blind-test until it passes

The loop nobody else closes. A profile is finished when it fools its owner.

Each round:

1. Take one of their real samples that is not already a gold sample in the profile.
2. Write two imitations of it from the profile alone: same topic, same length, same
   register. Do not re-read the original while writing them.
3. Present all three shuffled and unlabeled. Ask which one they wrote.
4. If they pick correctly, ask what gave the other two away. That answer is the most
   valuable sentence in the entire interview. Record it in the anti-voice section,
   patch the rules it implicates, and run another round with a different sample.

**Pass condition:** two consecutive rounds where they pick wrong, or say they are
genuinely unsure. Stop at five rounds regardless, and record whatever still gives
the fakes away as unresolved tells in the anti-voice section. An honest profile that
names its own gaps beats one that claims a pass it did not earn.

**Done when** the pass condition is met or five rounds have run, and the profile
reflects every tell surfaced along the way.

## Refine

Invoked as `/create-voice refine` with a draft that did not sound like them.

Read the existing profile, then ask which specific lines felt wrong and what they
would have written instead. Diff their version against the draft, and turn each
difference into a rule, a calibration change, or an anti-voice entry. Change only
what the failure touches, then run one round of step 7 to confirm the patch.

Voice drifts. A profile that can only be built once rots.
