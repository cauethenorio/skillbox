# Base LLM-ism ban-list

This is the **BASE** list. During extraction it gets **personalized**: remove any word the person genuinely uses (and note the exception with context), and add personal tics found in the corpus (words that appear suspiciously often and read AI-generated). Per Kobak et al. 2025 (*Science Advances*), weight style **verbs** heaviest — they are the strongest AI tells (e.g. "delves" appeared ~28x more after ChatGPT, "underscores" ~14x, "showcasing" ~11x). Adjectives are a weaker, cluster-based signal.

## English — Tier 1 (strong tells; style verbs weighted heaviest)
delve / delve into, underscore, showcase, leverage (verb), harness, navigate (metaphorical), embark, foster, bolster, garner, streamline, unlock, unveil, tapestry, myriad, plethora, realm, landscape (metaphorical), multifaceted, groundbreaking, revolutionize, synergy, ecosystem (non-technical), resonate, testament.

## English — Tier 2 (suspicious in clusters; 3+ together = a tell)
robust, seamless, cutting-edge, innovative, comprehensive, pivotal, nuanced, compelling, transformative, evolving, imperative, intricate, overarching, unprecedented, vibrant, profound, crucial.

## English — banned phrases
- "it's important to note", "it's worth noting that", "needless to say"
- "in today's fast-paced world", "in an era of", "when it comes to"
- "at its core", "at the end of the day", "the bottom line is"
- scene-setting openers (a sentence that announces the insight before the insight)
- the "Not X, but Y" construction (more than once)
- "In conclusion" / "In summary" as a closer
- sycophantic openers ("Great question!", "Absolutely!") and "I hope this helps"

## English — word → human replacement
| AI word | Human replacement |
|---------|-------------------|
| delve / delve into | look at, dig into, explore |
| leverage (verb) | use |
| harness | use, take advantage of |
| utilize | use |
| underscore | show, highlight, emphasize |
| bolster | strengthen, support, boost |
| garner | get, earn, attract |
| myriad | many |
| plethora | plenty of |
| streamline | simplify, speed up |
| testament | (delete — just state the evidence) |
| tapestry | (delete) |

## Em-dash rule
More than one em-dash per 3-4 paragraphs is above human baseline. Even a single em-dash is a tell if it injects a dramatic explanatory aside mid-sentence. **Fix:** use commas or periods, or restructure. **Do NOT substitute a colon** — a colon is often also a tell. Count em-dashes before claiming overuse.

## Portuguese — base list (starter; refine per person)
- Verbs / words: mergulhar (em), aproveitar (as "leverage"), potencializar, impulsionar, navegar (metaphorical), desvendar, robusto, abrangente, transformador, multifacetado, inovador, crucial.
- Phrases: "vale ressaltar", "vale a pena notar", "é importante notar / destacar", "no mundo de hoje", "em um mundo cada vez mais", "em suma", "no final das contas", "dito isso".

> The Portuguese list is a smaller starting base — AI tells differ by language and corpus. Expand it from the person's own Portuguese samples during Pass 1.

## Pattern-stacking discipline
When several weak signals land on the same phrase (bold + scare-quotes + an em-dash aside on one coined term), that is **one** strong tell, not three. Consolidate overlapping signals into a single finding. Never count the same phrase under multiple flags. Count before claiming overuse.
