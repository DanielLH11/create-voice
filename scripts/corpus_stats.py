#!/usr/bin/env python3
"""Stylometric report for one author inside a chat corpus.

Usage:
    python corpus_stats.py CHAT.txt --list-authors
    python corpus_stats.py CHAT.txt --author "Name" [--samples N] [--json OUT.json]
    python corpus_stats.py PASTED.txt --format plain
    python corpus_stats.py VOICE_NOTES.txt --transcript

Formats (--format auto detects between them):
    whatsapp  an "Export chat (without media)" .txt, iOS
              ("[dd/mm/yyyy, hh:mm:ss] Name: text") or Android
              ("dd/mm/yyyy, hh:mm - Name: text")
    plain     any other text. Blank-line-separated blocks, or one message per
              line, with an optional "Name: text" speaker prefix.

--transcript marks the input as speech-to-text and suppresses every mechanics
statistic: punctuation rates, capitalization, accents, sentence length. Those
belong to whoever ran the transcriber, not to the speaker. Only the lexicon
survives.

Only the chosen author's content is ever printed. Other participants are counted
under --list-authors and dropped everywhere else. Phone numbers, emails and URLs
are masked in every verbatim sample.
"""

import argparse
import json
import re
import statistics
import sys
from collections import Counter

BIDI = dict.fromkeys(map(ord, "‎‏‪‫‬⁦⁧⁨⁩"), None)

IOS_LINE = re.compile(
    r"^\[(?P<stamp>[^\]]{6,40})\]\s*(?P<author>[^:]{1,60}):\s(?P<text>.*)$"
)
ANDROID_LINE = re.compile(
    r"^(?P<stamp>\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s?[apAP]\.?\s?[mM]\.?)?)"
    r"\s+-\s+(?P<author>[^:]{1,60}):\s(?P<text>.*)$"
)
IOS_STAMPED = re.compile(r"^\[[^\]]{6,40}\]")
ANDROID_STAMPED = re.compile(r"^\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4},?\s+\d{1,2}:\d{2}")

PLACEHOLDER = re.compile(
    r"^(<[^>]{1,60}>|"
    r"(image|audio|video|sticker|gif|document|contact card|voice message)s?\s+omitted|"
    r"(imagen|audio|vídeo|video|sticker|gif|documento|tarjeta de contacto|mensaje de voz)\s+omitid[oa]|"
    r"multimedia omitido|"
    r"(this|you deleted this) message was deleted|"
    r"(se eliminó este mensaje|se elimino este mensaje|eliminaste este mensaje|mensaje eliminado)|"
    r"(missed (voice|video) call|llamada perdida)|"
    r"null|"
    r"(location|ubicación|ubicacion|live location).{0,40})$",
    re.IGNORECASE,
)

URL = re.compile(r"https?://\S+|www\.\S+")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE = re.compile(r"(?<!\w)(?:\+\d[\d\s().-]{6,}\d)(?!\w)")
NUMBER = re.compile(r"(?<!\w)\d[\d.,:/]*(?!\w)")
WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", re.UNICODE)
SENTENCE_SPLIT = re.compile(r"[.!?…]+|\n+")
LAUGH = re.compile(r"\b(?:(?:ja|je|ji|ha|he|hi){2,}[a-z]*|xd+|k{3,}|lol|lmao|lmfao)\b", re.IGNORECASE)

EMOJI_RANGES = (
    (0x1F300, 0x1FAFF), (0x1F000, 0x1F2FF), (0x2600, 0x27BF),
    (0x2B00, 0x2BFF), (0x1F1E6, 0x1F1FF),
)

PUNCT_MARKS = {
    "period": ".", "comma": ",", "semicolon": ";", "colon": ":",
    "exclamation": "!", "question": "?", "ellipsis": "…",
    "em_dash": "—", "en_dash": "–", "hyphen": "-",
    "open_paren": "(", "quote_double": '"', "quote_single": "'",
    "curly_quote": "“", "inverted_question": "¿",
    "inverted_exclamation": "¡", "ampersand": "&", "slash": "/",
}

STOPWORDS = set("""
a al algo algun alguna algunas alguno algunos ahi ahora alli ante antes aqui asi aun aunque
bien cada como con contra cual cuales cuando cuanto de del desde donde dos e el ella ellas ello
ellos en entre era eran eres es esa esas ese eso esos esta estaba estamos estan estar estas este
esto estos estoy fue fueron ha habia han hasta hay he hemos incluso la las le les lo los mas me
mi mis mucho muy nada ni no nos nosotros o os otra otras otro otros para pero poco por porque
que quien se sea ser si sido sin sobre solo son su sus tambien tan tanto te tiene tienen todo
todos tu tus un una unas uno unos usted ustedes ya yo
about after all also am an and any are as at be because been before being but by can could did
do does doing done down each even for from further had has have having her here hers him his
how i if in into is it its just like more most my nor not now of off on once only or other
our out over own re same she should some such than that the their them then there these they
this those through to too under until up very was we were what when where which while who why
will with would you your
""".split())

SPANISH_MARKERS = [
    "o sea", "en plan", "la verdad", "de hecho", "al final", "a ver", "es que",
    "pues nada", "vale", "venga", "bueno", "total", "encima", "igual", "tipo",
    "rollo", "madre mia", "un poco", "que tal", "por cierto", "osea",
    "joder", "hostia", "tio", "tia", "buah", "sinceramente", "la neta",
]
ENGLISH_MARKERS = [
    "i mean", "you know", "kind of", "sort of", "to be fair", "at the end of the day",
    "basically", "actually", "literally", "honestly", "obviously", "anyway",
    "the thing is", "so yeah", "i guess", "pretty much", "for real", "no worries",
]
SHORTHAND = [
    "q", "k", "xq", "pq", "xfa", "tb", "tmb", "dnd", "bss", "tqm", "tkm", "x", "d",
    "pls", "plz", "thx", "u", "ur", "r", "btw", "imo", "idk", "tbh", "rn",
    "omg", "wtf", "lmk", "ngl", "fyi", "asap",
]
ACCENT_PAIRS = [
    ("también", "tambien"), ("aquí", "aqui"), ("ahí", "ahi"),
    ("allí", "alli"), ("así", "asi"), ("día", "dia"),
    ("días", "dias"), ("adiós", "adios"), ("después", "despues"),
    ("además", "ademas"), ("quizás", "quizas"), ("según", "segun"),
    ("corazón", "corazon"), ("jamás", "jamas"), ("ningún", "ningun"),
    ("algún", "algun"), ("estás", "estas"), ("café", "cafe"),
    ("mañana", "manana"), ("año", "ano"),
]


def is_emoji(ch):
    code = ord(ch)
    return any(lo <= code <= hi for lo, hi in EMOJI_RANGES)


SPEAKER_LINE = re.compile(r"^\s*(?P<author>[^:\n]{1,40}):\s+(?P<text>\S.*)$")

MASK_TOKENS = {"num", "url", "email", "phone"}


def parse_whatsapp(text):
    """Return [(author, text)] for every non-system message in an export."""
    messages = []
    current = None
    for raw in text.splitlines():
        line = raw.rstrip("\r").translate(BIDI)
        match = IOS_LINE.match(line) or ANDROID_LINE.match(line)
        if match:
            if current:
                messages.append(current)
            current = [match.group("author").strip(), match.group("text")]
        elif IOS_STAMPED.match(line) or ANDROID_STAMPED.match(line):
            if current:
                messages.append(current)
            current = None
        elif current is not None:
            current[1] += "\n" + line
    if current:
        messages.append(current)
    return messages


def parse_plain(text):
    """Return [(author or None, text)] for free-form text.

    Blank-line-separated blocks become messages when the file uses them, otherwise
    every non-empty line does. A "Name: text" prefix is honoured only when most
    units carry one, so prose containing a stray colon is not mistaken for dialogue.
    """
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    if len(blocks) < 3:
        blocks = [line.strip() for line in text.splitlines() if line.strip()]

    matches = [SPEAKER_LINE.match(b.split("\n", 1)[0]) for b in blocks]
    labelled = sum(1 for m in matches if m)
    if not blocks or labelled < len(blocks) * 0.5:
        return [(None, b) for b in blocks]

    messages = []
    for block, match in zip(blocks, matches):
        if match:
            rest = block.split("\n", 1)
            body = match.group("text") + ("\n" + rest[1] if len(rest) > 1 else "")
            messages.append([match.group("author").strip(), body])
        else:
            messages.append([None, block])
    return messages


def load(path, fmt):
    """Return [(author, text)] plus the format actually used."""
    with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
        text = handle.read()

    if fmt in ("whatsapp", "auto"):
        messages = parse_whatsapp(text)
        if messages or fmt == "whatsapp":
            return clean(messages), "whatsapp"
    return clean(parse_plain(text)), "plain"


def clean(messages):
    return [
        (a, t) for a, t in messages
        if t.strip() and not PLACEHOLDER.match(t.strip())
    ]


def mask(text):
    text = URL.sub("<url>", text)
    text = EMAIL.sub("<email>", text)
    return PHONE.sub("<phone>", text)


def tokens(text):
    cleaned = NUMBER.sub(" num ", mask(text).lower())
    return WORD.findall(cleaned)


def ngrams(sequences, n, top):
    counter = Counter()
    for seq in sequences:
        for i in range(len(seq) - n + 1):
            counter[" ".join(seq[i:i + n])] += 1
    return counter.most_common(top)


def percentile(values, fraction):
    if not values:
        return 0
    ordered = sorted(values)
    index = min(int(len(ordered) * fraction), len(ordered) - 1)
    return ordered[index]


def analyse(msgs, samples, lexicon_only=False):
    texts = [mask(t) for t in msgs]
    joined = "\n".join(texts)
    all_words = [w for t in texts for w in WORD.findall(t)]
    token_lists = [tokens(t) for t in msgs]
    flat_tokens = [w for seq in token_lists for w in seq]

    sentences = []
    for text in texts:
        for piece in SENTENCE_SPLIT.split(text):
            words = WORD.findall(piece)
            if words:
                sentences.append(len(words))

    msg_lengths = [len(WORD.findall(t)) for t in texts if WORD.findall(t)]
    word_count = max(len(all_words), 1)

    punct = {
        name: round(joined.count(mark) * 1000 / word_count, 2)
        for name, mark in PUNCT_MARKS.items()
    }

    emojis = Counter(ch for ch in joined if is_emoji(ch))
    lower_counts = Counter(w.lower() for w in all_words)

    accents = []
    for accented, plain in ACCENT_PAIRS:
        hits, misses = lower_counts.get(accented, 0), lower_counts.get(plain, 0)
        if hits + misses:
            accents.append((accented, hits, misses))
    accent_total = sum(h for _, h, _ in accents)
    accent_missed = sum(m for _, _, m in accents)

    openers = Counter(seq[0] for seq in token_lists if seq)
    opener_pairs = Counter(" ".join(seq[:2]) for seq in token_lists if len(seq) >= 2)
    closers = Counter(seq[-1] for seq in token_lists if seq)

    content = [
        w for w in flat_tokens
        if w not in STOPWORDS and len(w) > 2 and w not in MASK_TOKENS
    ]
    low = joined.lower()
    marker_hits = {}
    for marker in SPANISH_MARKERS + ENGLISH_MARKERS:
        hits = len(re.findall(r"\b" + re.escape(marker) + r"\b", low))
        if hits:
            marker_hits[marker] = hits
    shorthand_hits = {s: lower_counts[s] for s in SHORTHAND if lower_counts.get(s)}
    laughs = Counter(m.group(0).lower() for m in LAUGH.finditer(joined))

    no_terminal = sum(1 for t in texts if t.strip() and t.strip()[-1] not in ".!?…")
    starts_lower = sum(1 for t in texts if t.strip() and t.strip()[0].islower())
    allcaps = sum(1 for w in all_words if len(w) > 2 and w.isupper())

    longest = sorted(texts, key=lambda t: len(WORD.findall(t)), reverse=True)[:samples]

    mechanics = {
        "message_length_words": {
            "mean": round(statistics.fmean(msg_lengths), 2) if msg_lengths else 0,
            "median": round(statistics.median(msg_lengths), 2) if msg_lengths else 0,
            "p90": percentile(msg_lengths, 0.9),
            "max": max(msg_lengths) if msg_lengths else 0,
        },
        "sentence_length_words": {
            "mean": round(statistics.fmean(sentences), 2) if sentences else 0,
            "stdev_burstiness": round(statistics.pstdev(sentences), 2) if len(sentences) > 1 else 0,
            "median": round(statistics.median(sentences), 2) if sentences else 0,
            "p10": percentile(sentences, 0.1),
            "p90": percentile(sentences, 0.9),
            "count": len(sentences),
        },
        "punctuation_per_1000_words": punct,
        "habits_pct": {
            "messages_without_terminal_punctuation": round(no_terminal * 100 / max(len(texts), 1), 1),
            "messages_starting_lowercase": round(starts_lower * 100 / max(len(texts), 1), 1),
            "allcaps_words_per_1000": round(allcaps * 1000 / word_count, 2),
        },
        "emoji": {
            "per_100_messages": round(sum(emojis.values()) * 100 / max(len(texts), 1), 2),
            "distinct": len(emojis),
            "top": emojis.most_common(15),
        },
        "accents": {
            "written_with_accent": accent_total,
            "written_without": accent_missed,
            "discipline_pct": round(accent_total * 100 / max(accent_total + accent_missed, 1), 1),
            "detail": accents,
        },
    }
    if lexicon_only:
        mechanics = dict.fromkeys(mechanics, None)

    return {
        "lexicon_only": lexicon_only,
        **mechanics,
        "volume": {
            "messages": len(texts),
            "words": word_count,
            "characters": len(joined),
        },
        "laughter": laughs.most_common(10),
        "top_words_content": Counter(content).most_common(40),
        "top_words_all": lower_counts.most_common(25),
        "top_bigrams": ngrams(token_lists, 2, 30),
        "top_trigrams": ngrams(token_lists, 3, 25),
        "top_fourgrams": ngrams(token_lists, 4, 15),
        "openers": openers.most_common(20),
        "opener_pairs": opener_pairs.most_common(20),
        "closers": closers.most_common(20),
        "known_markers": dict(sorted(marker_hits.items(), key=lambda kv: -kv[1])),
        "shorthand": dict(sorted(shorthand_hits.items(), key=lambda kv: -kv[1])),
        "longest_messages": longest,
    }


def render(name, data):
    out = []
    add = out.append
    add("VOICE CORPUS REPORT  |  author: " + name)
    add("=" * 62)

    vol = data["volume"]
    add("\n1. VOLUME\n   %d messages, %d words, %d chars" % (vol["messages"], vol["words"], vol["characters"]))
    if vol["words"] < 2000:
        add("   WARNING: under 2000 words. Stats are noisy; export a longer chat.")

    if data["lexicon_only"]:
        add("\n2-5. MECHANICS  suppressed: this input is a transcript.")
        add("   Sentence length, punctuation, capitalization and accents in a")
        add("   transcript were chosen by the transcriber, not by the speaker.")
        add("   Take those from written samples. This report is lexicon only.")
    else:
        msg, sent = data["message_length_words"], data["sentence_length_words"]
        add("\n2. LENGTH")
        add("   message: mean %s words, median %s, p90 %s, max %s"
            % (msg["mean"], msg["median"], msg["p90"], msg["max"]))
        add("   sentence: mean %s words, stdev %s (burstiness), median %s, p10 %s, p90 %s, n=%s"
            % (sent["mean"], sent["stdev_burstiness"], sent["median"], sent["p10"], sent["p90"], sent["count"]))

        add("\n3. PUNCTUATION per 1000 words")
        items = [kv for kv in sorted(data["punctuation_per_1000_words"].items(), key=lambda kv: -kv[1]) if kv[1]]
        for i in range(0, len(items), 4):
            add("   " + "   ".join("%s=%s" % (k, v) for k, v in items[i:i + 4]))

        hab = data["habits_pct"]
        acc = data["accents"]
        add("\n4. HABITS")
        add("   no terminal punctuation: %s%% of messages" % hab["messages_without_terminal_punctuation"])
        add("   starts lowercase: %s%%" % hab["messages_starting_lowercase"])
        add("   ALLCAPS words per 1000: %s" % hab["allcaps_words_per_1000"])
        add("   accent discipline: %s%% (%d accented vs %d stripped)"
            % (acc["discipline_pct"], acc["written_with_accent"], acc["written_without"]))

        emo = data["emoji"]
        add("\n5. EMOJI  %s per 100 messages, %d distinct" % (emo["per_100_messages"], emo["distinct"]))
        if emo["top"]:
            add("   " + "  ".join("%s x%d" % (e, c) for e, c in emo["top"]))

    if data["laughter"]:
        add("   laughter: " + ", ".join("%s x%d" % (k, v) for k, v in data["laughter"]))

    add("\n6. CRUTCH PHRASES  (candidates, confirm with the user before recording)")
    for label, key in (("bigrams", "top_bigrams"), ("trigrams", "top_trigrams"), ("4-grams", "top_fourgrams")):
        add("   %s: " % label + ", ".join("%s x%d" % (g, c) for g, c in data[key][:12]))
    if data["known_markers"]:
        add("   known markers: " + ", ".join("%s x%d" % (k, v) for k, v in data["known_markers"].items()))
    if data["shorthand"]:
        add("   shorthand: " + ", ".join("%s x%d" % (k, v) for k, v in data["shorthand"].items()))

    add("\n7. VOCABULARY")
    add("   content words: " + ", ".join("%s x%d" % (w, c) for w, c in data["top_words_content"][:25]))
    add("   all words: " + ", ".join("%s x%d" % (w, c) for w, c in data["top_words_all"][:15]))

    add("\n8. OPENERS AND CLOSERS")
    add("   first word: " + ", ".join("%s x%d" % (w, c) for w, c in data["openers"][:12]))
    add("   first pair: " + ", ".join("%s x%d" % (w, c) for w, c in data["opener_pairs"][:10]))
    add("   last word: " + ", ".join("%s x%d" % (w, c) for w, c in data["closers"][:12]))

    if data["longest_messages"]:
        add("\n9. LONGEST MESSAGES  (candidate gold samples)")
        for i, text in enumerate(data["longest_messages"], 1):
            add("   [%d] %s" % (i, text.replace("\n", " / ")))
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("chat", help="path to the chat export or text file")
    parser.add_argument("--author", help="exact participant name to profile")
    parser.add_argument("--list-authors", action="store_true",
                        help="list participants and message counts, then exit")
    parser.add_argument("--format", choices=("auto", "whatsapp", "plain"), default="auto",
                        help="input format (default: auto)")
    parser.add_argument("--transcript", action="store_true",
                        help="input is speech-to-text: report lexicon only, no mechanics")
    parser.add_argument("--samples", type=int, default=10,
                        help="how many of the author's longest messages to print")
    parser.add_argument("--json", dest="json_out", help="also write the full report as JSON")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    messages, used = load(args.chat, args.format)
    if not messages:
        sys.exit("No messages parsed from %s." % args.chat)

    named = [a for a, _ in messages if a]
    counts = Counter(named)
    if args.list_authors or (counts and not args.author):
        print("Parsed %d messages from %s (format: %s)\n" % (len(messages), args.chat, used))
        for author, count in counts.most_common():
            print("  %6d  %s" % (count, author))
        if not args.author:
            print("\nRe-run with --author \"Name\" to profile one participant.")
        return

    if args.author:
        mine = [text for author, text in messages if author == args.author]
        if not mine:
            sys.exit("No messages from %r. Known: %s" % (args.author, ", ".join(counts)))
        name = args.author
    else:
        mine = [text for _, text in messages]
        name = "whole file"

    data = analyse(mine, args.samples, lexicon_only=args.transcript)
    print(render(name, data))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as handle:
            json.dump({"author": name, "format": used, **data}, handle, ensure_ascii=False, indent=2)
        print("\nJSON written to " + args.json_out)


if __name__ == "__main__":
    main()
