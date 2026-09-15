# Corpus sources

Four ways to get the lexicon corpus, ranked. Take the highest one the person can
actually do. Every path ends the same way: a text file, `corpus_stats.py`, a report.

## A. WhatsApp export (primary)

In the app: open the chat, Settings or the contact name, **Export chat**, **Without
media**. iOS shares a `_chat.txt`; Android produces `WhatsApp Chat with <name>.txt`.

The export is capped at roughly 40,000 messages without media, about 10,000 with,
counted backwards from the newest. Without media reaches roughly four times further
back, which is another reason to refuse the media option.

```
python <skill-dir>/scripts/corpus_stats.py <chat.txt> --list-authors
python <skill-dir>/scripts/corpus_stats.py <chat.txt> --author "<Name>" --json <scratch>/corpus.json
```

What the script does with it, in order: reads the file as UTF-8 and strips the
bidirectional control marks WhatsApp injects; matches each line against the iOS
(`[dd/mm/yyyy, hh:mm:ss] Name: text`) and Android (`dd/mm/yyyy, hh:mm - Name: text`)
patterns; treats any line matching neither as a continuation of the previous
message, so multi-line messages survive intact; drops date-stamped lines with no
author, which is what system notices look like; drops media placeholders, deleted
messages, missed calls and location shares in English and Spanish; keeps only the
named author; masks phone numbers, emails and URLs everywhere, including the
verbatim samples.

Prefer this path. It is offline, complete, one file, and already tested against both
export formats.

## B. Pasted or exported text (any source)

Anything that is not a WhatsApp export: a pasted conversation, a Telegram or Slack
export flattened to text, a folder of emails, old blog drafts.

```
python <skill-dir>/scripts/corpus_stats.py <file.txt> --format plain
python <skill-dir>/scripts/corpus_stats.py <file.txt> --format plain --author "<Name>"
```

`plain` splits on blank lines when the file uses them and on newlines otherwise. A
`Name: text` prefix is honoured only when most units carry one, so ordinary prose
with a stray colon is not mistaken for dialogue. With no speaker labels the whole
file is treated as the subject's, so strip other people's words first.

`--format auto` is the default and tries WhatsApp before falling back to plain.

## C. Voice notes (lexicon supplement, needs a decision first)

WhatsApp voice notes export as `.opus` files named `PTT-<date>-WA####.opus`. Nothing
reads them without a speech-to-text step, and this machine has no transcriber
installed, so pick one before promising this path:

- **Local.** `pip install faster-whisper` pulls the runtime and downloads a model,
  a few hundred MB, CPU-only and slow on a laptop. Audio never leaves the machine.
- **Hosted API.** Fast and accurate, needs a key, and it uploads private
  conversation audio to a third party. For a chat with a family member that is a
  real cost, not a footnote.

Then feed the transcript in with the flag that matters:

```
python <skill-dir>/scripts/corpus_stats.py <transcript.txt> --transcript
```

`--transcript` suppresses sentence length, punctuation, capitalization, accents and
emoji, in the report and in the JSON. Those features describe whoever configured the
transcriber. Whisper and its relatives insert punctuation the speaker never chose
and normalize away the disfluency that was the entire reason to want voice notes.
Filler-preserving settings reduce this; they do not fix it.

So audio supplements the lexicon. It never becomes the corpus, and it never touches
the mechanics layer. The flag enforces that rather than trusting anyone to remember.

## D. Browser extraction from WhatsApp Web (fallback, unverified)

For when the phone is out of reach. Untested here, so treat it as a build with its
own verification rather than a working path.

`web.whatsapp.com` needs an authenticated session and site permission granted to the
browser extension. The message list is virtualized, so only what is on screen exists
in the DOM: extraction means scrolling the pane upward in a loop, collecting as you
go, and stopping when the message count stops rising. The useful hook is
`div.copyable-text[data-pre-plain-text]`, whose attribute carries
`[21:14, 12/3/2026] Name: `, with `message-in` and `message-out` distinguishing
direction. Those class names are unversioned and change without notice.

Write whatever you collect to a text file in the WhatsApp export shape and run it
through path A, so one parser stays the only thing that has to be correct.

It cannot reach further back than you are willing to scroll, while path A hands over
up to 40,000 messages in one file. Offer it as a fallback, never as an upgrade.
