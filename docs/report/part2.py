"""Sections 5 and 6 of the report."""


def build(r, figs, ctx):
    # ------------------------------------------------------------------ 5 Architecture and design
    r.h1("5  Architecture and design", key="s5")
    r.h2("5.1  The system in plain terms")
    r.p("A ticket arrives from one of four channels. Before anything else the system checks whether the kill switch is on; if it is, the ticket goes "
        "straight to a human. Otherwise the ticket is cleaned up and screened for text that tries to give the system instructions. Next the system works "
        "out what the ticket is about by comparing it with 500 labelled past tickets, and asks a language model only when that comparison is not clear-cut. "
        "It then searches the 29 articles for the passage that best matches the question. A short piece of ordinary code decides what happens next: "
        "if the ticket is about security, compliance, a feature request or something unclear, or if no article matched, or if confidence is below 0.85, it "
        "goes to a human with a summary and the articles found. Otherwise a language model drafts a reply using only the full text of the best article, "
        "and five checks run on the draft before anything is sent. Any failed check sends the ticket to a human instead. Every step is written to a log "
        "that records what was decided and why. @F:arch@ shows the same flow.")
    r.fig("arch", figs["arch"], "System architecture. Green: model or data steps. Yellow: policy steps in code. Red: the human path. "
          "Purple: storage and the model provider. An editable version is in docs/architecture.drawio.", 160)
    r.h2("5.2  Design decisions and the alternatives rejected")
    r.p("@T:alts@ lists the decisions that shaped the system. Each was taken because of evidence found during the build, not in advance, and four "
        "of them reversed an initial assumption.")
    r.table("alts", "Design decisions, the alternatives considered, and the evidence for the choice.", [
        ["Decision", "Alternative considered", "Why this choice", "Evidence"],
        ["Classify with nearest labelled tickets first; call the model only if the neighbour vote is below 0.85",
         "Ask the language model for intent and confidence on every ticket.",
         "More accurate, cheaper and faster. Confidence comes from two classifiers agreeing, not from a model's self-report.",
         "Nearest-ticket classifier 99.8% (leave-one-out, dev) and 100% (validation) against 97% for the model. Model self-confidence received a negative weight in a fit and was dropped."],
        ["Route in deterministic code on the predicted intent",
         "Let the model decide whether to answer, or read the safety flag from the label.",
         "A rule can be tested, audited and explained to a compliance reviewer. The label does not exist on a live ticket.",
         "0 safety violations in 101 restricted tickets; 87 flagged tickets equal exactly the four restricted intents."],
        ["Show the generator the whole top article (plus a close runner-up)",
         "Show only the best-matching section.",
         "A section can describe the symptom but omit the fix, and the model then improvises from a weaker article.",
         "VAL-0012: retrieval returned only the 'Symptoms' section of the rollback article, and the reply drew on an unrelated article."],
        ["A NO_ANSWER sentinel the model can return, which escalates",
         "Append a refusal sentence when evidence is weak.",
         "The appended sentence was added after good answers too, so a correct reply ended with 'I cannot help'.",
         "Found on VAL-0005; replaced in prompt v2, and v3 raised required-point coverage from 80% to 95% on 100 reference-checked replies."],
        ["Judge replies with a different model family",
         "Judge with the same small model that generated them.",
         "A weak judge was wrong in both directions.",
         "The 8B judge flagged 4 of 50 replies; all four statements were in the source articles. The independent judge found 0 of 50."],
        ["Provider is configuration (base URL, key, model)",
         "Hard-wire one provider.",
         "Credit ran out part-way through the project and a free tier was rate-limited.",
         "Fail-fast on 401 and 402; Retry-After handling on 429; Groq tested as a fallback."],
        ["LangGraph state machine as the orchestrator",
         "A plain Python function (my first version).",
         "The brief's low-level design names LangGraph. The graph makes the early exits explicit: a conditional edge after every step sends an escalated ticket straight to the final step, so the escalation packet, metrics and log are written once on every path.",
         "I first built a plain function and kept the LangChain packages unused; on checking the brief I moved to LangGraph. All 124 tests passed unchanged apart from the routing order."],
        ["Generation returns a JSON object (PR-GN-01 v4.0)",
         "Free text with a NO_ANSWER sentinel (v3.0).",
         "The specification asks for output in a defined structure the code can parse. The model returns {status, answer, cited_docs, reason}; the parser falls back to plain text if the model slips, so a formatting error cannot break a reply.",
         f"{ctx['dv']['structured']:.0f}% of replies on development and {ctx['vl']['structured']:.0f}% on validation were valid JSON. Quality unchanged: 0 hallucinated; required-point coverage {ctx['dv']['j_cov']*100:.0f}% vs {ctx['v3d']['j_cov']*100:.0f}% for v3 on development, {ctx['vl']['j_cov']*100:.0f}% vs {ctx['v3v']['j_cov']*100:.0f}% on validation."],
        ["Hybrid search (dense plus BM25)",
         "Dense embeddings only.",
         "The brief's design specifies hybrid search. BM25 is fused with the dense ranking by reciprocal rank with a low weight (0.15).",
         "On development tickets the keyword weight moved hit@1 by about one point in both directions (90.2% to 91.6%), so it adds no measurable benefit on this 29-article corpus. Kept as designed, with a weight chosen on development data only."],
        ["Confidence and threshold fitted on 'unseen wording' samples",
         "A threshold of 0.80 taken from the brief's illustration.",
         "Half the development tickets have a twin, so plain leave-one-out gives 0.99 confidence everywhere and a threshold does nothing. Removing twins and near-duplicates spreads the confidence and lets the threshold be chosen from data.",
         "Calibration error 0.3 pp; threshold 0.85 is the lowest at which auto-answered tickets are right at least 99% of the time (@T:sweep@)."],
        ["Deterministic security-wording net and a safety-proximity rule",
         "Rely on the intent classifier alone for restricted tickets.",
         "With unseen wording, 3 of 87 restricted tickets (a former employee who still has access) were auto-answered with high confidence. No threshold can fix a confident mistake.",
         "Keyword net escalates clear security language; proximity rule escalates when neighbours include restricted topics. Result: 0 of 87 restricted tickets answered, even with unseen wording."],
        ["Escalate when unsure; draft-for-agent as the first deployment",
         "Maximise automatic replies.",
         "Marcus would rather the system said nothing than something wrong; Sofia asked for a draft, not auto-send.",
         "25% of automatic replies went to tickets labelled escalate (Section 7)."],
    ], [38, 34, 48, 52])
    r.h2("5.3  The limit that shaped the routing design")
    r.p("The hardest design question was how to decide which non-restricted tickets to answer. The labels say 37.8% of tickets should be escalated, "
        "and 17.4 points of that are the restricted intents. The remaining escalations have no obvious pattern, and I tested five signals as predictors "
        "of the label: the intent classifier, the nearest-ticket vote on the route label, the nearest-ticket vote on answerability, the retrieval score, "
        "and a language-model judgement of whether the article answers the question. None beat chance. The retrieval score reached an AUC of 0.51 on "
        "the development set and 0.47 on validation, and the model judge 0.46 and 0.42, worse than guessing. @F:signals@(b) shows why: among tickets with "
        "identical text, the route label agrees only 87.8% of the time and the urgency label 68.5%. A good share of the label noise is "
        "in the data itself, so no model could recover it from the text.")
    r.fig("signals", figs["signals"], "(a) Attempted predictors of 'should escalate' on non-restricted tickets, shown as area under the ROC curve; none exceeds chance (0.5). "
          "(b) Agreement of labels between tickets with identical text. Sources: evaluation/eval_routing.py, eval_retrieval_signal.py, "
          "eval_llm_answerability.py, analyze_label_consistency.py.", 148)
    r.p("I stopped there and recorded it as a limitation rather than tuning a threshold against the labels until the number looked better, which "
        "would have produced a figure that would not survive contact with real tickets. The consequence is the 71 to 75% auto-reply precision "
        "reported in Section 7, and the recommendation to start in draft mode. A related consequence: urgency is assigned and logged but is not "
        "used for routing, and its accuracy (45% validation, 52% dev, against a 55% majority-class baseline) is reported as a failure, not a result.")
    r.p("<b>Can the system decide to say nothing because no article fits?</b> The specification asks retrieval to return nothing rather than something irrelevant. "
        "Two attempts at making that decision better both failed, and the reason is informative. First, a stricter relevance floor: the score of the best article barely separates tickets the documentation "
        "can answer from those it cannot (AUC 0.56 on development, 0.64 on validation; evaluation/eval_floor_answerability.py), so raising the floor from 0.30 to 0.55 loses 45 answerable tickets while the "
        "share of answered tickets that are answerable stays at about 79%. Unanswerable tickets typically retrieve a perfectly relevant article; what they lack is something the article cannot supply "
        "(an action on the customer's account). Second, asking the generator to decline in exactly those cases: the prompt now says so (v4.0), but the 8-billion-parameter model never returned no_answer in "
        "the 580 tickets I ran, consistent with its answerability judgement being no better than chance in the earlier experiment. The floor therefore stays at 0.30, chosen for recall, and the remaining defence "
        "is routing: restricted topics, confidence, and the guardrails. This is the main reason 21 to 26% of automatic replies go to tickets the labels say the documentation cannot answer.")
    r.h2("5.4  Guardrails and the audit log")
    r.p("Five checks run on every draft. The privacy check blocks names, email addresses, account numbers and keys. The grounding check blocks any sentence "
        "whose claims are not in the articles that were actually shown to the model, and a separate check on figures blocks any number, version or duration "
        "that does not appear in those articles or in the customer's own message. The instruction check re-screens the ticket for injected "
        "instructions. The tone check blocks promises about refunds or timelines. The confidence check blocks a reply if the routing floor was not "
        "applied. Any failure escalates and never redacts and sends. The decision log stores, per ticket, the action, the reason code, the sources with "
        "scores, the prompt version, the guardrail results and the requirement IDs that apply, so a reviewer can reconstruct the decision later "
        "(GET /decisions/{ticket_id}).")

    # ------------------------------------------------------------------ 6 Implementation
    r.h1("6  Implementation", key="s6")
    r.h2("6.1  What was built and where it lives")
    r.p("The repository follows the layout the submission guide prescribes. @T:modules@ maps each component to its module and to the tests that exercise it. "
        "The code is about 1,800 lines of Python in src/ and 1,600 in evaluation/, with 124 tests (about 860 lines) that run offline (the model is replaced by a "
        "deterministic stand-in) with one command, pytest tests/ -v.")
    r.table("modules", "Components, their location in the repository, and their tests.", [
        ["Component", "Location", "What it does", "Tests"],
        ["Ingest", "src/ingest.py", "Normalises four channels (api_comments accepted as an alias of docs_comment); never raises on bad input.", "test_ingest.py"],
        ["Classify", "src/classify.py", "Nearest-ticket vote, model fallback, agreement-based confidence.", "test_retrieve_classify_generate.py"],
        ["Retrieve", "src/retrieve.py", "Hybrid search (dense plus BM25, reciprocal rank) over article sections; one passage per article; relevance floor 0.30; stale-article guard.", "same file; test for the stale guard"],
        ["Route", "src/route.py", "Ordered deterministic rules; escalation packet.", "test_route.py"],
        ["Generate", "src/generate.py", "JSON reply (status, answer, cited_docs, reason) from the full article, with a plain-text fallback.", "test_generation_contract.py, test_retrieve_classify_generate.py"],
        ["Guardrails", "src/guardrails.py", "Privacy, grounding, figures, injection, tone, confidence floor.", "test_guardrails.py"],
        ["Pipeline", "src/pipeline.py", "LangGraph state machine: orders the steps; kill switch; writes the log; never raises.", "test_pipeline.py, test_kill_switch.py"],
        ["Response formatter", "src/formatter.py", "Turns a result into the API payload (reply and citations, or escalation packet).", "test_api.py"],
        ["Feedback loop", "src/feedback_loop.py", "POST /feedback: human corrections stored, counted, and added to the neighbour index.", "test_feedback_loop.py"],
        ["Decision log", "src/logging_store.py", "SQLite; decisions and resolution records.", "test_logging.py"],
        ["Provider client", "src/llm.py", "Retries, Retry-After, circuit breaker, fail-fast on 401/402.", "test_pipeline.py (outage cases)"],
        ["API", "src/api.py", "/tickets (alias /process), /feedback, /decisions, /health, /metrics, /admin/kill-switch.", "test_api.py"],
        ["Harness", "evaluation/harness.py", "Unattended run; metrics report; human-review CSV. Exit 0 finished, 2 cannot start.", "test_harness.py"],
        ["Fairness audit", "evaluation/fairness_audit.py", "Segment comparison with intervals and significance tests.", "test_fairness_audit.py"],
        ["Monitoring", "monitoring/", "Prometheus config, alert rules, Grafana dashboard with five required views.", "test_monitoring.py"],
    ], [24, 36, 76, 34])
    r.p("The automated tests are listed in @T:apptests@ in Appendix G, and the prompt register is @T:appprompts@ in Appendix F.")
    r.h2("6.2  What was difficult")
    r.p("Most of the build time went on finding out that something I believed was wrong. @T:bugs@ records the faults that mattered, how each was "
        "found, and the fix. Three were found only because I looked at individual tickets rather than at aggregate scores, which is the main "
        "practical lesson of the build.")
    r.table("bugs", "Faults found during the build, how they were found, and what changed.", [
        ["Fault", "How it was found", "Fix and effect"],
        ["Channel name api_comments in the scaffold; the data says docs_comment.", "Inspecting the ticket schema before writing ingest.", "Real name used, old name an alias. The scaffold would have rejected 15.6% of tickets."],
        ["Classification prompt used 22 invented intent names.", "Comparing prompt classes with ground-truth labels.", "Prompt v2 uses the real 22 labels."],
        ["A reply that ended with a refusal after a good answer.", "Reading VAL-0005 line by line.", "NO_ANSWER sentinel (prompt v2)."],
        ["Reply improvised from the wrong article.", "Reading VAL-0012; retrieval returned only the symptom section.", "Generator sees the whole article."],
        ["Default provider routing took about 11 s median for a short reply.", "Timing the same model through different providers.", "Provider sort by throughput: about 0.4 s median. Same model, same weights."],
        ["Figures in short sentences passed the grounding check ('45 minutes').", "A unit test I wrote for the guardrail failed.", "Figures are checked in every sentence; numbers the customer wrote are allowed."],
        ["The same-family judge produced false hallucination flags.", "Verifying all four flagged statements against the source articles.", "Independent judge model; human second assessor still required."],
        ["Credit exhaustion (HTTP 402) was retried, causing a 25-minute hang.", "A stalled judge run.", "401 and 402 fail fast and open the circuit breaker; Retry-After honoured for 429."],
        ["Safety rule read the ground-truth flag.", "Asking what would exist on a live ticket.", "Rule derived from the predicted intent."],
    ], [60, 48, 62])
    r.h2("6.3  What I would restructure")
    r.p("Three things. First, the evaluation data is split into a development set that doubles as the nearest-ticket index and a small validation set that I "
        "also used while debugging; a cleaner design would keep a third untouched set from the start, because I could not later claim a clean hold-out. "
        "Second, the nearest-ticket index and the article index share a vector store and a loading path, which complicated testing; separating them behind one "
        "interface would let each be replaced independently. Third, the kill switch is a file on one host, which is fine for this project but would "
        "need a shared store for a multi-instance deployment.")
    r.p("Not done, stated plainly: there is no concurrent load test (the harness processes tickets one at a time); the Grafana and Prometheus stack has "
        "configuration and a test that every queried metric is exposed, but I did not run it because Docker was not available in the build environment; "
        "the GitHub Actions workflow runs the same commands I ran locally, but it has not been run on a remote because the repository has no remote yet; and the "
        "resolution records are written but not yet used, so the compounding claim in the PRD is unproven.")
