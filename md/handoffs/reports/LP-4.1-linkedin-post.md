# LP-4.1 — LinkedIn Introduction Post (final)

> The short LinkedIn feed post that introduces and links to the long-form article
> (`LP-4.1-article-draft-v2.md`). ~150 words; first three lines are the hook (above the
> "see more" fold). Bold-unicode glyphs (𝗤𝘄𝗲𝗻 …) are decorative emphasis — note they are not
> read by screen readers and may render as boxes on older devices; kept to a few key hits.
> Publication timing and final graphics remain owner-gated.

---

Qwen3.5-4B, running on my everyday laptop, matched a cloud model's output quality on real work.

But it fell over — a third of the time.

I'm building **Chat Chronicle** — a local-first tool that pulls my scattered AI chat history (ChatGPT, Claude, Codex, Claude Code) into one searchable archive. To enrich it privately and for free, I needed to know whether small local LLMs are actually "good enough." So I measured.

Five of them — 𝗤𝘄𝗲𝗻𝟯.𝟱-𝟰𝗕, 𝗣𝗵𝗶-𝟰 𝗠𝗶𝗻𝗶, 𝗟𝗹𝗮𝗺𝗮 𝟯.𝟮 (𝟯𝗕 & 𝟭𝗕), 𝗚𝗲𝗺𝗺𝗮 𝟯 𝟰𝗕 — against a cloud model (Gemini 3.5 Flash) on 120 real tasks from my own AI chat history: summaries, work classification, activity extraction, title checks. Same strict JSON contracts for everyone.

The good news: the best local outputs were genuinely indistinguishable from the cloud's. On a laptop. For free. That's a real milestone.

The catch: the best local model produced usable output just 𝟳𝟬% of the time, versus 𝟵𝟯% for the cloud. And an invalid output isn't a bad answer — it's nothing to store.

So the wall isn't quality. It's 𝗿𝗲𝗹𝗶𝗮𝗯𝗶𝗹𝗶𝘁𝘆 — and most "look, it runs locally!" demos only show you the runs that worked.

The full write-up has the scorecard, why they failed (the context window does more damage than model size), and the one measurement habit that changes how you read every local-LLM demo. 👇

If you're running small local LLMs in real work: are you measuring reliability separately from quality?

— — —

📩 With many years of experience in R&D and solution development, I'm available for contract / project work — building exactly this kind of thing (AI solutions, evaluation, honest measurement). If you have a project that's a fit, let's talk.

---

## Notes for posting

- **Cover image:** the reliability-vs-quality scatter (`figures/lp41-reliability-quality.svg`),
  exported to PNG — it doubles as the article cover and the feed card image.
- **Article link:** attach the long-form article so LinkedIn renders the card; the repo URL
  (https://github.com/TzurV/mcp-chat-chronicle) is inside the article, so it does not also need
  to go in the first comment unless preferred.
- **Claim check (verified against results):** "context window does more damage than model size"
  is supported — context-length rejections are the largest failure category in every local arm
  (21–30 each), and Gemma 3 4B (51.7% valid) ranks below the smaller Llama 3.2 3B (59.2%), so
  parameter count does not predict reliability.
- **Evidence for the headline numbers:** best local 70.0% valid (Qwen), cloud 93.3% (Gemini);
  quality-of-valid-outputs indistinguishable at the top (Qwen 0.887 vs Gemini 0.966, with
  several Qwen task dimensions at ceiling).
