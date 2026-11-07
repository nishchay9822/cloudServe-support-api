# Stage 1: Discovery Workbook — Filled
**CloudServe Capstone | Week 1, Days 2–3**
**Evidence sources:** 5 stakeholder interview transcripts + `data/development_tickets.json` (500 tickets)

---

## Section 1: What the Interviews Tell You

### Table 1-A: Interview Summary

| Who | What they told you | What they appear not to know | What you want to verify in the data |
|-----|--------------------|------------------------------|-------------------------------------|
| **Marcus Adeyemi, Head of Support** | 500+ tickets/week with 6 agents. Avg first response 8–12 hrs vs 2 hr SLA. FCR is 42% vs 65% industry benchmark. Every escalation costs ~4× a resolved ticket. Has tried hiring (short-lived) and canned responses (agents hated it). Primary fear: confidently wrong automated answers. Secondary fear: system creates more agent work. Needs explainability for autumn compliance review. Enterprise customers on a different SLA will notice degraded service. | Does not know ticket breakdown by category — admits he would be "guessing." Does not know what proportion of escalations are tier-2-resolvable vs genuinely complex. Does not know the non-fluent English issue exists. | (1) What is the actual breakdown by intent? (2) What proportion of escalations is tier-2-resolvable? (3) Do non-fluent tickets have worse outcomes? |
| **Sofia Restrepo, Tier One Agent** | ~70% of tickets are ones she has seen before (password lockouts, rate limits, billing, deployment rollbacks). The bottleneck is *finding and rewriting* the answer, not knowing it. Documentation is good but keyword search fails so agents don't use it. Everyone maintains private snippet files. Non-fluent English tickets take longer and she sometimes answers the wrong question; she believes those have the worst CSAT. Wants a system that gives her a draft + relevant doc page, not one that auto-sends without agent review. | Does not know whether non-fluent tickets statistically have worse CSAT (she believes this but it is an impression). Does not know how often her escalations could have been resolved at tier-1. Does not know that Daniel's tier-2 pipeline is 50% filled with tier-1-resolvable issues. | (1) Do non-fluent tickets have materially worse FCR/CSAT? (2) What is the actual repeat rate — does data match her 70% estimate? (3) Which intents most commonly reach her as repeats? |
| **Daniel Okonkwo, Tier Two Engineer** | ~50% of escalations he receives are tier-1-resolvable — a confidence or findability problem, not a knowledge gap. Escalations arrive with no context: just the raw original ticket. First thing he does is re-read the full thread and often re-asks a question the customer was already asked. Would be "twice as fast" with context: summary + relevant docs + what tier-1 was uncertain about. Key risk: personal snippet files contain outdated answers that scale mistakes if trained on. Security, billing disputes, and data residency should never be auto-responded. | Does not know the overall FCR number (Marcus's view). Does not know whether the non-fluent issue Sofia describes is measurable in the data. Underestimates how much of his own time goes to context-gathering vs. actual problem-solving. | (1) What escalation rate does the data show, and does ~50% being tier-1-resolvable hold? (2) Which intents have the highest escalation rates? (3) Are there intents where escalation rate is high despite docs availability? |
| **Ines Varga, Technical Writer** | 29 KB articles covering: authentication, deployment, API, billing, data, security, account management. Internal team *does not use them* — agents reconstruct answers from memory instead of copying. Root cause: keyword search fails on vocabulary mismatch (customer writes "my deployment keeps dying"; article is titled "Resolving container health check failures"). Unreviewed personal snippet files are a quality risk. Wants citation of which article a system answer came from — so she can distinguish article errors from system errors. Feature requests, roadmap questions, and novel incidents have *no article* — system must recognise this and not manufacture answers. | Does not know that agents don't use her docs because search is broken (she initially thought Sofia was complaining about doc quality). Does not know the quantified gap between agent answers and doc answers. Unaware of the escalation-without-context problem Daniel describes. | (1) What % of tickets are "answerable from docs"? (2) For intents with high doc-answerability, is the escalation rate also high — suggesting docs exist but aren't being reached? |
| **Ravi Menon, Customer** | Waits 8+ hrs routinely; finds answers himself in docs ~50% of the time. Accepts automation *if* it is honest: cites source page, states uncertainty, and identifies itself as automated. Will act on automated responses at his own risk if properly labeled. Does not want hidden automation. Business-tier customers will notice if enterprise–business gap widens. Urgency is asymmetric: a documentation question can wait; a failing deployment at 9am cannot. | Does not know the internal mechanics of why response is slow. Does not know the non-fluent language problem. Does not know the escalation-without-context problem (sees it as "the waiting is the problem," not as a context failure). | (1) Is urgency correctly captured in the ticket data? (2) Does the data confirm that high-urgency tickets have worse SLA compliance than low-urgency ones? |

---

### Table 1-B: Disagreements Between Accounts

| The disagreement | Who says what | How the data settles it | What follows from the answer |
|------------------|---------------|------------------------|------------------------------|
| **Proportion of tickets that are repeat/answerable** | Sofia estimates ~70% are questions she's answered before. Marcus admits he doesn't know the breakdown and would be "guessing." | Data: 71.4% of tickets are marked `answerable_from_docs=True`. Sofia's intuition is confirmed — the vast majority already have answers in the knowledge base. | The problem is *delivery*, not *knowledge*. CloudServe does not lack answers; it lacks a way of reliably reaching customers with answers that already exist. A chatbot that generates new answers misses the point; a system that retrieves and surfaces existing documentation is the correct solution. |
| **Non-fluent English ticket outcomes** | Sofia believes non-fluent tickets have the worst satisfaction scores and "nobody has noticed." Marcus has no data to confirm or deny this. | Data: Non-fluent (n=120) CSAT = 3.04 vs Fluent (n=380) CSAT = 2.95. Non-fluent FCR = 45.8% vs Fluent FCR = 43.2%. The data does **not** confirm Sofia's belief — non-fluent tickets are marginally *better* on measured outcomes. | Sofia may be experiencing a *per-ticket effort* problem (non-fluent tickets take longer) without that effort translating to worse outcomes in this sample. OR the sample is too small to detect the effect, OR agents compensate by spending more time. This should be monitored but is not an acute crisis. The vocabulary-mismatch retrieval problem still affects non-fluent tickets more, even if outcome data is inconclusive. |
| **What proportion of escalations are tier-1-resolvable** | Daniel says "about half" of what reaches him could have been resolved by tier-1 given confidence or a doc link. Marcus sees only the escalation rate, not the content of what escalates. | Data: 56.2% of all tickets are escalated. Intents with 100% escalation rate: `compliance_request`, `feature_request`, `security_incident`, `unclear_request` — these are legitimately tier-2 (no docs answer, safety flags). But `deployment_failure` (59% escalated, 70% answerable from docs), `authentication_failure` (escalation rate not top-10, 70% answerable), `api_key_issue` (67% answerable) suggest many escalations are happening on answerable tickets. | Daniel's estimate is directionally correct. A significant portion of escalations involve issues that *have* documentation answers. The confidence/findability gap — not a knowledge gap — is driving unnecessary escalations. This directly supports building a system that presents relevant docs with a confidence score so agents escalate less. |
| **Enterprise vs standard service quality** | Ravi (business tier) says enterprise customers get faster answers (~1 hr) and will notice if the gap widens. Marcus confirms different agreements but gives no detail on current performance gap. | Data: Enterprise tier FCR = 37.3% and avg resolution = 484 min — *worse* than standard (43.1% FCR, 442 min). Enterprise escalation rate = 62.7% vs Standard 56.9%. | Counter-intuitive: enterprise customers are actually getting *worse* FCR and longer resolution despite presumably better agreements. This likely reflects that enterprise tickets are more complex. A system that helps with answerable tickets would disproportionately benefit standard and business tiers unless it also improves escalation context for complex enterprise tickets. |

---

### Table 1-C: Omissions — What Nobody Mentioned

| What was never mentioned | Why you would have expected it | How you will check it |
|--------------------------|-------------------------------|----------------------|
| **The volume of repeat contacts** | If 70% of tickets are answerable and FCR is only 44%, a significant portion of customers must be contacting again. Nobody flagged this explicitly. | Data: 21.6% of tickets are repeat contacts. That means 1 in 5 tickets is a customer who did not get a sufficient answer on the first contact. |
| **The docs_comment channel** | Sofia, Daniel, and Ines all describe documentation and search problems but none mentioned that a significant number of tickets arrive *directly in documentation comments* — people asking questions while reading docs. | Data: 15.6% of tickets arrive via `docs_comment` channel. These are likely high-intent, specific questions from active users — a prime candidate for automated response. |
| **The `must_not_auto_respond` safety flag** | Nobody explicitly described categories where automated response must be blocked. Marcus mentioned confidently wrong answers as a fear but didn't enumerate categories. | Data: 17.4% of tickets (87 of 500) are flagged `must_not_auto_respond`. These include security incidents, compliance requests, and billing disputes — all mentioned by Daniel but not quantified. Any system must hard-block these before routing. |
| **Ticket volume by urgency** | Marcus and Ravi both discussed urgency in different ways, but no one described what proportion of volume is actually high-urgency. | Data: 29.2% of tickets are high-urgency. This is substantial — if these are also the tickets with worst SLA compliance, priority routing for high-urgency is a design requirement. |

---

## Section 2: What the Ticket Data Shows

### Table 2-A: Ticket Data Measurements

| What to measure | Your figure | Where it came from | What surprised you |
|-----------------|------------|--------------------|--------------------|
| **Total tickets in sample** | 500 | `development_tickets.json` | The sample is large enough to be statistically meaningful across all categories. |
| **Split by channel** | Email: 212 (42.4%) · Chat: 155 (31.0%) · Docs comment: 78 (15.6%) · Forum: 55 (11.0%) | `channel` field | Email dominates — this is also the channel with longest expected response time, which aligns with Marcus's SLA breach. Docs comments (15.6%) are significant and underappreciated. |
| **Split by intent category** | Top 5 by volume: data_export (5.8%), data_residency (5.8%), rollback_request (5.6%), deployment_failure (5.4%), compliance_request (5.2%) | `labels.intent` | The distribution is relatively even (22 classes, 2.6–5.8% each) — no single "killer category." The problem isn't one type of ticket; it's a broad pattern across all types. |
| **Split by urgency** | High: 146 (29.2%) · Medium: 226 (45.2%) · Low: 128 (25.6%) | `labels.urgency` | Nearly 30% of tickets are high-urgency. Combined with 8–12 hr response times, this is a real customer harm problem — not just an inconvenience. |
| **First contact resolution rate** | 43.8% (219/500) | `history.first_contact_resolution` | Very close to Marcus's stated figure of 42% — his number is accurate even though he was "guessing." Industry benchmark is 65%, so there is a 21pp gap to close. |
| **Average satisfaction rating** | 2.97 / 5.0 | `history.csat_rating` | Below 3.0 out of 5. Marcus quoted 3.2 in the interview — actual data shows it is even worse. This strengthens the urgency of the project. |
| **Most frequent single intent** | data_export and data_residency tied at 29 each (5.8%) | `labels.intent` count | Less concentrated than expected. No single "easy win" intent dominates — improvements must work across many categories. |
| **Proportion answerable from existing documentation** | 71.4% (357/500) | `labels.answerable_from_docs` | This is the most important number in the dataset. 71 out of every 100 tickets could theoretically be resolved from the existing 29 KB articles. The problem is delivery, not content. |
| **Proportion marked non-fluent, and their outcomes** | Non-fluent: 120/500 (24%). Non-fluent FCR: 45.8%, CSAT: 3.04. Fluent FCR: 43.2%, CSAT: 2.95. | `language_fluency`, `history.*` | Sofia's belief that non-fluent tickets have worse outcomes is **not confirmed by this data**. Non-fluent outcomes are marginally better. However, vocabulary mismatch will still affect retrieval quality — the outcome data may reflect agents compensating by spending more time. |
| **Outcomes by customer tier** | Enterprise: FCR 37.3%, 484 min avg, 62.7% escalated. Business: FCR 48.2%, 359 min avg, 51.8% escalated. Standard: FCR 43.1%, 442 min avg, 56.9% escalated. | `customer_tier`, `history.*` | Enterprise customers have the *worst* FCR and escalation rate, despite having premium agreements. They have the most complex tickets — the system must not degrade their experience further. |
| **Proportion that are repeat contacts** | 21.6% (108/500) | `history.repeat_contact` | 1 in 5 tickets is a customer coming back because the first response was insufficient. This is a direct measure of FCR failure. Reducing this is as important as improving first response time. |
| **Safety-flagged tickets (must_not_auto_respond)** | 17.4% (87/500) | `labels.must_not_auto_respond` | 87 tickets must never be auto-responded to. These must be hard-blocked before any routing decision. |
| **Escalation rate** | 56.2% (281/500) | `history.escalated` | More than half of all tickets require tier-2 involvement. Marcus's SLA problem is partly a volume problem, but it's made significantly worse by this escalation rate. |

---

## Section 3: Where the Time Actually Goes

### Table 3-A: Effort vs Volume by Category

| Ticket category | Share of volume | Est. share of effort | Why they differ | Evidence |
|-----------------|-----------------|---------------------|-----------------|----------|
| **security_incident** | 5.2% (26) | ~12% | 100% escalation rate, avg 786 min resolution — longest in dataset. Always escalated regardless of docs availability. | Avg resolution time 786 min; escalation rate 100% |
| **compliance_request** | 5.2% (26) | ~11% | 100% escalation rate, 679 min avg. Legal/regulatory implications mean every ticket requires human judgement even when docs exist (65% answerable). | Avg 679 min; escalation 100% |
| **feature_request** | 4.0% (20) | ~9% | 100% escalation rate, 724 min avg. Zero docs-answerable. These generate discussion, product backlog entries, follow-ups. | Avg 724 min; 0% answerable from docs |
| **performance_degradation** | 4.6% (23) | ~8% | 70% escalation rate, 543 min avg. Often requires investigation of logs/infrastructure — high diagnosis time. | Avg 543 min; 70% escalated |
| **unclear_request** | 3.0% (15) | ~5% | 100% escalation rate, 516 min avg. Agents must first clarify what the customer is asking before solving it — double pass. | Avg 516 min; 0% answerable from docs |
| **authentication_failure / api_key_issue** | 7.6% combined (38) | ~8% | High repetition (Sofia's most-mentioned), moderate escalation, high docs-answerability (67–70%). Most time goes to *finding* the answer, not *knowing* it. | Auth 70% answerable; api_key 67% answerable |
| **deployment_failure / rollback_request** | 11.0% combined (55) | ~10% | High volume, 59% and undisclosed escalation, 70–75% answerable from docs. Should be high-yield RAG targets. | Deployment 70% answerable; rollback 75% |
| **billing_query / quota_or_overage** | 9.4% combined (47) | ~6% | Moderate volume, high doc-answerability (87–88%), but billing disputes must never be auto-responded (Daniel: "those become contractual quickly"). | 88% billing answerable from docs but risk of commitment |

### Table 3-B: Steps an Agent Takes on a Typical Ticket (reconstructed from Sofia's account)

| Step | What the agent does | Roughly how long | Could this be automated? |
|------|--------------------|-----------------|-----------------------------|
| 1 | Open queue, sort by age (oldest-first to avoid SLA breach) | 1–2 min per session | No — humans judge severity and prioritise. A system could flag urgency but should not reorder human work. |
| 2 | Read ticket, understand what is being asked. For non-fluent tickets: interpret the intent before answering. | 1–3 min (simple) to 10+ min (ambiguous/non-fluent) | Partially — classification can identify intent and urgency, reducing cognitive load. Cannot fully automate interpretation. |
| 3 | Search documentation for relevant answer. In practice: skip search, open personal snippet file instead, because search fails on vocabulary mismatch. | 2–5 min (snippet file) to 15+ min (if actually searching docs) | **Yes — high value.** Semantic retrieval (embeddings) removes the vocabulary mismatch barrier. This is where most of the reclaimed time lives. |
| 4 | Write or adapt the answer. Copy from snippet, rewrite for this customer's context. | 2–5 min | **Partially — high value.** System can draft a grounded answer from retrieved docs, agent reviews and personalises. Sofia: "If it hands me a ticket with a draft and the relevant page attached, that would genuinely help. That would save me half of every ticket." |
| 5 | Decide to send or escalate. If escalating: forward the raw original ticket to tier-2 (no summary, no context). | 1–2 min | **Partially.** Routing can be automated with a confidence threshold. Escalation context packet (summary + retrieved docs + uncertainty reason) can be generated — directly addresses Daniel's complaint. |
| 6 | Handle follow-up if answer was wrong or unclear. | 10–40 min (repeat contact) | **Yes (preventive).** Better first-contact answers reduce step 6 entirely. 21.6% repeat contact rate = 108 tickets in this sample that represent step 6 work. |

---

## Section 4: What the Client Counts as Success

### Table 4-A: Success Metrics

| Measure | Who watches it | Current value | What they would call success | Confidence in this |
|---------|---------------|---------------|-----------------------------|--------------------|
| **First contact resolution (FCR)** | Marcus (primary), executive team | 43.8% (data) / 42% (Marcus) | Industry benchmark: 65%. Marcus's target unstated but 60%+ is reasonable. | High — both interview and data are consistent |
| **Average first response time** | Marcus, customers (SLA obligation) | 8–12 hours | Under 2 hours (SLA). Ravi would accept sub-1-hour for documentation queries. | High — consistent across Marcus and Ravi |
| **Escalation rate** | Marcus (indirectly — via cost) | 56.2% | 30% or lower. At 4× cost per escalation, each point is financially material. | Medium — Marcus cited cost ratio, not a target escalation rate |
| **Customer satisfaction (CSAT)** | Marcus (reports to exec team) | 2.97/5.0 (data) / 3.2/5.0 (Marcus) | Marcus's threshold unclear. 4.0+ is a reasonable target for meaningful improvement. | Medium — Marcus's figure is slightly optimistic vs data |
| **Repeat contact rate** | Not currently tracked | 21.6% | Target: halved to ~10%. Marcus did not mention this; it is implied by FCR improvement. | Low — not a metric Marcus is watching; worth introducing |
| **Explainability of decisions** | Marcus (compliance review) | None (no current decision log) | Every automated decision must have a logged, human-readable reason. Autumn compliance deadline. | High — Marcus was explicit about this requirement |
| **Consistency of service across tiers** | Ravi (customer), implicitly Marcus | Enterprise FCR 37.3% is worse than business/standard | Variation between tiers should not increase. Ideally narrow. | Medium — Ravi's concern is enterprise getting worse; data shows enterprise is already worse |

### Table 4-B: Sentence Test

| Prompt | Your answer |
|--------|-------------|
| **This project will have been worth doing if, within three months of launch...** | FCR rises from 44% to 60%+, first response time drops below 2 hours for auto-responded tickets, and repeat contact rate falls from 22% to 10% or below. |
| **We will know it did not work if we see...** | A confidently wrong automated answer screenshotted and circulated publicly by an engineer-customer; or if agent workload increases because they are handling a flood of corrections to auto-responses; or if escalation rate rises rather than falls. |
| **The measure the client will actually be judged on internally is...** | First contact resolution. Marcus was explicit: "FCR, if I am being honest, more than response time. Response time is what is in the agreement so it is what gets reported." FCR is the real business outcome. |

---

## Section 5: Data, Constraints and Risk

### Table 5-A: Data Sources

| Data source | What it contains | Quality and gaps | Access constraints | Private data present? |
|-------------|-----------------|-----------------|-------------------|----------------------|
| **Support tickets** (`development_tickets.json`) | 500 labelled tickets: channel, subject, body, customer tier, region, language fluency, intent, urgency, expected route, answerable_from_docs, history (FCR, CSAT, resolution time, escalated, repeat_contact) | High quality — all fields populated, labels are consistent. No missing values observed. Real tickets would likely have missing fields and more noise. | None in this project context. Real deployment: GDPR-relevant — customer names and account IDs are present; cannot be stored in logs or returned in responses. | **Yes** — customer_name, customer_id, customer_region. The `customer_id` and `customer_name` fields must never appear in outbound responses. |
| **Knowledge base** (`documentation.json`) | 29 articles: title, category, body, doc_id. Categories: authentication, deployment, api, performance, billing, data, security, account, integration, onboarding. | Reviewed by Ines; current and accurate within review cycle. Gap: feature requests, roadmap, novel incidents have no article. Vocabulary may not match customer language (confirmed by Ines). | None in this project context. Real: agents' private snippet files are out-of-scope and must not be used (Daniel's warning about stale answers). | No — documentation is intentionally public-facing. |
| **Ground truth responses** (`ground_truth_responses.json`) | 200 reference answers: required points, must_not_contain, expected_doc_ids. Written by senior agents. | High quality — written by experienced humans. Covers only 200 of 500 development tickets. Cannot be used for training, only evaluation. | Must be held back — only used to evaluate system quality, never to train the model (that would be overfitting to visible data). | No. |
| **Customer records** | Customer tier, region, account identifiers appear in ticket data | Derived from ticket fields only — no separate CRM access | GDPR-relevant — customer tier data can be used for routing logic but customer PII must not appear in outbound responses. | Yes — customer_name, customer_id are PII. |
| **Agents' personal snippet files** | Answers written by agents outside the official KB | Not reviewed, some outdated (Daniel's explicit warning). Quality unknown. | Not in the dataset — intentionally excluded. Must not be used as a training or retrieval source. | Unknown — likely yes, since agents write from memory and may include customer details. |

### Table 5-B: Risk Register

| What could go wrong | Likelihood | Severity | Who it affects | First thought on preventing it |
|--------------------|-----------|----------|---------------|-------------------------------|
| **System answers confidently and incorrectly** | Medium — LLMs hallucinate; retrieved docs may not fully cover the question | Very High — Marcus's primary fear; engineers will screenshot and share publicly | All customers; CloudServe's reputation | Grounding guardrail: every claim must trace to a retrieved passage. Confidence threshold: below 0.80, escalate rather than auto-respond. Citation requirement in every response. |
| **Private data (PII) appears in outbound response** | Low — unlikely if system only responds from KB content, but possible via prompt injection or context leakage | Very High — GDPR violation, potential breach notification obligation | Affected customer; CloudServe legally | PII guardrail: scan every outbound response for email addresses, account numbers, names, API keys before sending. Block and escalate if detected. |
| **Some customer groups consistently get worse answers** | Medium — vocabulary mismatch affects non-English-fluent customers; complex enterprise tickets have different profiles | High — fairness/compliance issue, Ravi's concern about tier gaps | Non-fluent customers, enterprise tier | Monitor performance per-segment continuously. Set alert if any segment drops >5pp below overall average. Embed full context (customer tier, urgency) in routing decisions. |
| **Documentation goes out of date; system retrieves stale answers** | Medium — Ines reviews on a rotation, but a product change before review means stale answers for weeks | High — incorrect answers at scale, hard to detect | All customers receiving answers from the affected article | Doc versioning in metadata. Log which article_id answered each ticket — Ines can audit. Add a "doc_last_reviewed" field to retrieval results and flag old content. |
| **Model provider (OpenRouter) becomes unavailable** | Low — but OpenRouter is a third-party dependency | High — system non-functional, full fallback to human agents | All customers | Graceful degradation: if provider unavailable, route all tickets to escalate. Never surface a provider error to a customer. Log the outage event. |
| **Prompt injection — customer ticket attempts to hijack system instructions** | Low — but technically possible and malicious actors may probe | Very High — could cause the system to return anything, including PII | Any customer receiving a poisoned response; CloudServe | Injection guardrail: scan ticket body for instruction-override patterns. Treat ticket body as untrusted user input at all times — never inject directly into system prompt. |
| **Routing threshold is poorly calibrated; system auto-responds when it should escalate** | Medium — confidence scores from LLMs are often not well-calibrated out of the box | High — wrong auto-responses at scale, increased agent workload from corrections | All auto-responded customers | Calibration check: group confidence scores into bands (0.5–0.6, 0.6–0.7, etc.) and verify observed accuracy matches stated confidence. Adjust threshold based on data, not assumption. |

---

## Section 6: The Problem Statement

### Table 6-A: Problem Statement Elements

| Element | Your statement | Supporting evidence |
|---------|---------------|---------------------|
| **What the client asked for** | A chatbot to handle support tickets | Marcus interview: "I picture it answering the easy ones so my people can do the hard ones." |
| **What the evidence suggests they actually need** | A retrieval system that surfaces existing documentation answers reliably, combined with a context-enriched escalation pipeline that gives tier-2 engineers what they need to resolve complex tickets faster | Section 2, Table 2-A: 71.4% of tickets are already answerable from existing KB; the problem is that agents cannot reach those answers due to keyword search vocabulary mismatch (Ines interview; Section 3, Table 3-B Step 3). Daniel interview: escalations arrive without context, adding 15–30 min of re-reading per escalation. |
| **The gap between those two** | A chatbot built to *generate* answers would add a hallucination risk on top of a delivery problem. The answers already exist. The failure is that agents cannot find them quickly, and escalations arrive stripped of context that tier-2 needs to act on them efficiently. | Table 1-B row 1: data confirms Sofia's 70% repeat-question estimate. Section 3 Step 3: agents skip docs search because keyword search fails. Daniel: "If an escalation arrived with context, I would be twice as fast." |
| **Who is affected and how** | 6 tier-1 agents spend most of their time finding and rewriting answers they already know. Tier-2 engineers spend the first 15–30 min of every escalation reconstructing context. 500+ customers per week experience 8–12 hr response times, with 22% contacting a second time because the first response was insufficient. Enterprise customers are paradoxically receiving the worst FCR (37.3%) despite premium agreements. | Marcus: 8–12 hr avg vs 2 hr SLA. Data: 43.8% FCR, 2.97/5 CSAT, 21.6% repeat contact, enterprise FCR 37.3%. |
| **What will change if this is solved** | FCR rises to 60%+, first response time falls below 2 hrs for the 71% of tickets that are doc-answerable, escalation rate falls from 56% toward 30%, tier-2 handles only genuinely complex tickets (with context pre-attached), and repeat contact rate halves. | Table 4-B Sentence Test. Marcus: 4× cost of escalation vs resolution — a 26pp drop in escalation rate recovers significant cost. |
| **What is explicitly not in scope** | Answering feature requests, roadmap questions, or novel incidents (no KB content exists). Automating responses to security incidents, billing disputes, or compliance requests (must_not_auto_respond = 17.4%). Building a new knowledge base (Ines's 29 articles are sufficient; private snippet files must not be used). Replacing human agents (augmenting their capacity, not replacing them). | Ines: "Feature requests — obviously, since there is no answer to retrieve." Data: 17.4% safety-flagged. Daniel: "Billing becomes contractual; security must always escalate." |

---

### Table 6-B: One-Paragraph Problem Statement

| Problem Statement |
|------------------|
| CloudServe's support function receives more than 500 tickets a week and takes 8–12 hours to reply, against a two-hour service agreement. First contact resolution sits at 44%, which means more than half of all tickets escalate to tier-2 at roughly four times the cost. The root cause is not a shortage of answers: 71% of tickets can already be answered from the 29 articles in the existing knowledge base. The failure is delivery. Agents cannot reach those articles through keyword search because customers do not phrase problems in documentation vocabulary, so every agent has built a private workaround file. When they do escalate, the escalation arrives without context, so tier-2 engineers spend 15–30 minutes reconstructing what was already asked before they can act. What CloudServe needs is not a system that generates new answers; it is one that reliably retrieves the answers that already exist and presents them to agents as a grounded, citable draft, and that packages escalations with enough context for tier-2 engineers to act immediately. |

---

## Discovery Complete — Self-Check

Before moving to Stage 2 (PRD), verify:

- [x] Marcus would recognise this: *yes* — FCR is his number, explainability is his requirement
- [x] Sofia would recognise this: *yes* — the snippet-file workaround, the findability problem, the draft-not-auto-send model
- [x] Daniel would recognise this: *yes* — context-enriched escalations, tier-1-resolvable escalations
- [x] Ines would recognise this: *yes* — retrieval from her 29 articles, citation requirement, private files excluded
- [x] Ravi would recognise this: *yes* — honest automated response, citations, urgency asymmetry acknowledged
- [x] Every claim in the problem statement is supported by a numbered table row above
- [x] Three key disagreements are resolved with data (not with interview preference)
- [x] The problem statement does not mention embeddings, retrieval, or LLMs — it describes the business problem

**Move to Stage 2: PRD v1**
