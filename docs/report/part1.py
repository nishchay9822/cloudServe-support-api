"""Sections 1 to 4 of the report."""


def build(r, figs, ctx):
    # ------------------------------------------------------------------ 1 Executive summary
    r.h1("1  Executive summary", key="s1", new_page=False)
    dv, dn, vl = ctx["dv"], ctx["dn"], ctx["vl"]
    r.p("CloudServe asked for a chatbot. Discovery showed the real problem is delivery: 71.4% of tickets can already be answered from the company's own 29 articles, but agents cannot find them, "
        "first replies take 8 to 12 hours, only 43.8% of tickets are resolved at first contact, and escalations reach tier two with no context. I built a retrieval-first pipeline that classifies each ticket, "
        "finds the right article, and either sends a cited reply or escalates to a person with a prepared packet. Routing is deterministic code, guardrails can block any reply, and every decision is logged. "
        "It is a FastAPI service with an unattended evaluation harness, a kill switch, and Prometheus and Grafana monitoring.")
    r.p(f"<b>Achieved.</b> On 500 development tickets the system replied automatically to {dv['auto_pct']:.0f}% and escalated {dv['esc_pct']:.0f}%, against a baseline escalation rate of 56%. A proxy for first-contact resolution "
        f"is {dv['proxy']:.1f}% (baseline 43.8%, target 60%), and {vl['proxy']:.1f}% on 80 validation tickets. The 95th-percentile reply time is {vl['p95']} ms (target under 3 s). No restricted ticket was answered automatically "
        f"(0 of 101, and 0 of {dn['safe_n']} when each ticket is classified as if its wording were new), no personal data left the system, every citation resolved, and an independent model found no unsupported claim in 150 sampled replies.")
    r.p(f"<b>The most important caveat.</b> About a quarter of automatic replies ({vl['prec']:.0f} to {dv['prec']:.0f}% precision) go to tickets the labels say needed a person, and {ctx['unans_dev_pct']:.0f} to {ctx['unans_val_pct']:.0f}% go to tickets the "
        f"documentation cannot answer. Counting those as escalations, the effective rate is {ctx['adj_dev']:.0f}% on development and {ctx['adj_val']:.0f}% on validation, not 21%, and above the 30% target. No signal I tried could predict which "
        f"tickets need a person, because the labels are partly noise. The results are also flattered: half the development tickets repeat another's text, the validation set was used while debugging, the hidden set was never available, "
        f"and the human second review of replies is still pending. Enterprise and standard customers trail business customers in routing accuracy by 8 to 13 points in every run, above the 5-point target.")
    r.p("<b>Recommendation.</b> Roll out first as a draft-for-agent tool and measure acceptance on live tickets for several weeks before any automatic sending. Section 8 lists what must be true before the system speaks to a real customer.")

    # ------------------------------------------------------------------ 2 The problem
    r.h1("2  The problem", key="s2")
    r.h2("2.1  What was asked for")
    r.p("The head of support, Marcus Adeyemi, described what he wanted in one sentence: \"I picture it answering the easy ones so my people can do "
        "the hard ones.\" The brief that framed the project asked for an AI system that receives tickets from four channels, classifies them, "
        "retrieves knowledge, and either responds or escalates, with every decision logged. Read literally, that is a chatbot with a fallback.")
    r.h2("2.2  What discovery revealed")
    r.p("Five stakeholders were interviewed (@T:asked@ lists their accounts against the data) and 500 labelled tickets were analysed. The picture that "
        "emerged differs from the brief in four ways.")
    r.table("asked", "What was asked for compared with what the evidence showed.", [
        ["", "What the client asked for", "What the evidence showed", "Source"],
        ["Goal", "A chatbot that answers the easy tickets.", "A delivery problem. 71.4% of tickets are answerable from existing articles, so the content exists.", "Ticket labels; Ines Varga"],
        ["Cause of slow replies", "Not stated. Implied: too few agents, too many tickets.", "Agents skip documentation because keyword search fails on vocabulary mismatch, and keep private snippet files instead.", "Sofia Restrepo; Ines Varga"],
        ["Escalations", "A cost: each costs about four times a resolved ticket.", "They arrive with no context. Tier two re-reads the thread and re-asks questions, adding 15 to 30 minutes each.", "Daniel Okonkwo"],
        ["Safety", "Not stated beyond fear of 'confidently wrong' answers.", "17.4% (87 of 500) of tickets must never be auto-answered: security, compliance, feature and unclear requests.", "Ticket labels; Daniel Okonkwo"],
        ["Fairness", "Not mentioned; one agent suspects non-fluent tickets fare worse.", "Not confirmed in outcomes (FCR 45.8% non-fluent vs 43.2% fluent) but retrieval may still be weaker for them. Enterprise tickets resolve worst (FCR 37.3%).", "Ticket history fields"],
        ["Accountability", "An audit trail for the autumn compliance review.", "Every automated decision needs a reconstructable record: what, why, with which sources and prompt version.", "Marcus Adeyemi"],
    ], [24, 42, 70, 30])
    r.h2("2.3  Why the gap matters")
    r.p("A generative chatbot would add a new failure mode, the confident wrong answer, on top of a problem that is not about generation. "
        "Marcus named that failure as his primary fear, and an engineer-customer screenshotting a wrong automated answer is exactly what he said "
        "would signal failure. The better design makes the existing answers reachable, shows where each answer came from so the technical "
        "writer can tell a documentation error from a system error, refuses to answer when the evidence is thin, and hands difficult tickets to "
        "people with the work already started. That reframing drove the requirements in Section 4 and the architecture in Section 5.")
    r.p("The problem statement that closed Stage 1 reads, in short: CloudServe does not lack answers, it lacks a way of reaching customers with the answers "
        "it already has, and when it must escalate it strips the context that tier two needs. The business case is straightforward. "
        "At roughly 4x cost per escalation and a 56.2% escalation rate, each percentage point moved from escalated to resolved is material, and "
        "the metric Marcus is actually judged on is first-contact resolution, which sits 21 points below the 65% industry benchmark.")

    r.h2("2.4  What CloudServe measures, and what the project is held to")
    r.p("The brief gives the numbers CloudServe brought to its first meeting and the targets the project is judged against. @T:client@ sets them beside what the ticket data showed, "
        "because two of the figures quoted in interviews were slightly off, and because the client's own goal and the project target differ. Marcus quoted a satisfaction score of 3.2 and the data says 2.97; "
        "the client wants 65% first-contact resolution while the project target is 60%. Where this report says a target was met or missed it uses the project target, and it takes the baseline from the data, not from the interview.")
    r.table("client", "CloudServe's measures: where they are, what the client wants, the project target, and what the data showed.", [
        ["Measure", "Client's figure today", "Client's goal", "Project target", "Ticket data (500 tickets)"],
        ["Tickets per week", "Over 500", "No target; volume rising faster than headcount", "n/a", "n/a (a sample, not a rate)"],
        ["First reply", "8 to 12 hours", "Under 2 hours (the service agreement)", "Under 5 minutes", "Median resolution time 216 minutes"],
        ["Resolved on first contact", "42%", "65% or better", "60% or better", "43.8%"],
        ["Customer satisfaction", "3.2 / 5", "4.2 / 5", "4.0 or better", "2.97 / 5"],
        ["Escalation rate", "58%", "No target stated", "30% or lower", "56.2%"],
        ["Repeat contacts", "Not measured", "Not stated", "Halved", "21.6%"],
        ["Agent attrition", "Rising", "Stable", "Not in scope", "Not in the data"],
    ], [34, 30, 38, 28, 40])

    # ------------------------------------------------------------------ 3 Discovery findings
    r.h1("3  Discovery findings", key="s3")
    r.p("This section presents the evidence as findings. The full workbook (five interviews, 13 measurements, three disagreements resolved with data) "
        "is a separate deliverable (docs/Stage_1_Discovery_Workbook_Filled.docx). @F:disc@ summarises the headline numbers.")
    r.fig("disc", figs["disc"], "Headline facts from the 500 development tickets (a) and first-contact resolution by customer tier (b). "
          "Source: data/development_tickets.json, history and label fields.", 150)
    r.h2("3.1  Three findings that changed the design")
    r.p("@T:findings@ lists the three findings that changed the design, with the evidence for each and the decision it forced.")
    r.table("findings", "Findings that changed the design, with evidence and the decision each one forced.", [
        ["#", "Finding", "Evidence", "Design consequence"],
        ["F1", "The answers already exist. The failure is delivery.",
         "71.4% (357/500) of tickets are answerable from the 29 articles. Sofia estimated 70% from experience and the data confirms it. Ines: agents do not use the articles because search fails on vocabulary.",
         "Retrieval-first architecture. Semantic search over the articles, replies written only from retrieved text, citations on every reply. Not a free-form generator."],
        ["F2", "A fixed share of tickets must never be auto-answered.",
         "87 of 500 (17.4%) carry the must-not-auto-respond flag. They are exactly the four intents security_incident, compliance_request, feature_request and unclear_request (100% escalation, longest resolution times of 516 to 786 minutes).",
         "A hard routing rule on the predicted intent, checked before confidence. The flag itself is ground truth and does not exist on a live ticket, so it is used only for scoring."],
        ["F3", "Escalations lose context, and tier two repeats the work.",
         "Daniel: escalations arrive as the raw ticket; a summary plus relevant articles plus the reason for uncertainty would make him 'twice as fast'. 56.2% of tickets escalate, many on intents that are mostly answerable (deployment_failure 59% escalated, 70% answerable).",
         "Every escalation carries a packet: summary, retrieved sources and a reason code. Measured completeness: 100% (every escalation in both runs)."],
    ], [8, 38, 66, 54])
    r.h2("3.2  Where accounts disagreed and the data decided")
    r.p("Four disagreements between accounts were settled with data rather than by preference (@T:disagree@). Two are worth drawing out because they "
        "changed what was measured later. First, the tier-one agent believed non-fluent tickets have the worst outcomes and that nobody had noticed. "
        "The outcome fields do not support that (non-fluent first-contact resolution 45.8% against 43.2%), but the retrieval step depends on phrasing, "
        "so the fairness audit in Section 8 tests retrieval quality by fluency as well as outcomes. Second, the customer assumed enterprise accounts "
        "receive the best service. The data shows the opposite: enterprise first-contact resolution is 37.3% and 62.7% of enterprise tickets "
        "escalate. A system that helps only with simple tickets would therefore leave the worst-served tier exactly where it is, and it makes enterprise "
        "performance a segment to watch in every later evaluation.")
    r.table("disagree", "Disagreements between accounts and how the ticket data settled them.", [
        ["Question", "Accounts", "What the data says", "Consequence"],
        ["How many tickets are repeat or answerable?", "Sofia: about 70%. Marcus: would be guessing.", "71.4% answerable; 21.6% are repeat contacts.", "Delivery problem, not a knowledge problem."],
        ["Do non-fluent tickets fare worse?", "Sofia: yes, unnoticed. Marcus: no data.", "Not in outcomes: FCR 45.8% vs 43.2%, CSAT 3.04 vs 2.95.", "Monitor; retrieval quality by fluency tested in the audit."],
        ["How many escalations are avoidable?", "Daniel: about half. Marcus sees only the rate.", "56.2% escalate. Several intents escalate often despite 67 to 75% answerability.", "Directionally right: a findability gap."],
        ["Do enterprise customers get better service?", "Ravi: faster answers. Marcus: different agreement.", "Enterprise FCR 37.3%, 484 min average, 62.7% escalated; worst of the tiers.", "Enterprise is a protected segment in evaluation."],
    ], [38, 42, 52, 38])
    r.h2("3.3  Things nobody mentioned")
    r.p("Three omissions mattered. Nobody mentioned the documentation-comment channel, which carries 15.6% of tickets and later proved to be the "
        "channel whose name differs between the brief and the data (Section 6). Nobody quantified repeat contact (21.6%, one ticket in five). "
        "And nobody described the restricted categories as a share of volume; at 17.4% they are too large to treat as an edge case.")

    r.h2("3.4  How the evidence was gathered, and what it left open")
    r.p("Discovery ran in two passes. The five interviews were read for what each person claimed, what they appeared not to know, and what could be checked in the data; that produced a list of questions "
        "(for example whether non-fluent tickets really fare worse) that the 500 tickets could answer. The tickets were then measured in 13 ways (volume by channel and intent, first-contact resolution, escalation, repeat contact, "
        "safety-flagged share, outcomes by tier and fluency), and every disagreement between accounts was settled with a number rather than with whoever sounded more sure. "
        "The problem statement at the end of the workbook mentions no technology, so that a stakeholder could check it against what they had said.")
    r.p("Discovery left four things open, and each came back during the build. First, the labels: the 'should escalate' route and the urgency are partly noise, which discovery could not see because it did not test whether identical "
        "tickets carried identical labels. Second, the data are templated, so every measure taken from them is easier than real tickets would be. Third, discovery could not measure satisfaction or repeat contact "
        "after an automatic reply, because there were no live customers. Fourth, the agents' private snippet files were deliberately excluded because of their stale content, so what agents actually say to customers was never observed. "
        "Discovery therefore settled what the problem was and left how well the solution works to the evaluation in Section 7.")

    r.h2("3.5  What each stakeholder shaped")
    r.p("Every person interviewed changed something in the design, and @T:stake@ records what, so that the interviews can be traced to the requirements and not just summarised. "
        "The pattern worth noticing is that the two people closest to the work (the tier-one agent and the tier-two engineer) asked for help rather than replacement, "
        "which is why the first deployment recommended in Section 10 is a draft for the agent to review.")
    r.table("stake", "What each stakeholder told us, what the data showed about it, and the requirement it shaped.", [
        ["Stakeholder", "What they told us", "What the data or build showed", "What it shaped"],
        ["Marcus Adeyemi, Head of Support", "First-contact resolution is the number that matters; his fear is a confidently wrong answer; he needs explainability for an autumn compliance review.", "First-contact resolution is 43.8% (he said 42%). Satisfaction is 2.97, lower than the 3.2 he quoted.", "FR-07 (escalate rather than guess), FR-11 (guardrails), FR-12 (decision log), NFR-05"],
        ["Sofia Restrepo, tier-one agent", "About 70% of tickets are ones she has answered before; the bottleneck is finding the answer, not knowing it; she wants a draft, not auto-send.", "71.4% of tickets are answerable from the documentation. Non-fluent tickets do not have worse outcomes.", "FR-04 (retrieval first), the draft-for-agent recommendation, the fairness audit"],
        ["Daniel Okonkwo, tier-two engineer", "Half of what reaches him could have been resolved earlier; escalations arrive with no context; security, billing disputes and data residency must never be auto-answered.", "56.2% of tickets escalate; 87 of 500 must never be auto-answered; escalations carried no context.", "FR-06 and FR-22 (restricted topics), FR-08 (escalation packet), FR-21 (human-confirmed learning)"],
        ["Ines Varga, technical writer", "Agents do not use the 29 articles because keyword search fails; she wants to know which article an answer came from; feature requests have no article.", "Retrieval by meaning finds the expected article first for about 90% of answerable tickets.", "FR-04, FR-05 (return nothing when nothing fits), FR-09 (citations), the stale-article guard"],
        ["Ravi Menon, customer", "Accepts automation if it is honest: cites the source, states uncertainty, says it is automated; urgency matters.", "Urgency cannot be recovered from ticket text (about half correct), so it is logged but not used for routing.", "FR-09 (disclosure line), FR-02 (urgency as a logged field, not a target)"],
    ], [30, 52, 46, 42])

    # ------------------------------------------------------------------ 4 Requirements
    r.h1("4  Requirements", key="s4")
    r.p("The product requirements document (PRD) states 20 functional requirements (FR-01 to FR-20) and ten non-functional requirements "
        "(NFR-01 to NFR-10). Each one cites the evidence that justifies it; this section shows how the findings of Section 3 became requirements. "
        "Version 1.0 had 18 functional requirements. Version 2.0, after the build, changed 11 and added two (Section 9). @T:reqs@ traces the key requirements to their evidence and to how each is verified. The IDs below are the "
        "version 2.0 IDs and are the ones used in the decision log, the prompt register and the tests.")
    r.table("reqs", "Key requirements, their origin in the evidence, and how each is verified.", [
        ["ID", "Requirement (short form)", "Evidence it follows from", "How verified", "Result"],
        ["FR-02", "Classify every ticket into one of the 22 real intents.", "Ticket labels; Marcus did not know the breakdown.", "Per-class precision, confusion matrix.", f"{dv['intent']:.1f}% dev, {dn['intent']:.1f}% unseen wording, {vl['intent']:.0f}% val"],
        ["FR-03", "Calibrated confidence per classification.", "Marcus: 'I would rather it said nothing than said something wrong.'", "Calibration bands on unseen-wording samples.", f"Calibration error {ctx['sel']['ece_pp']} pp (n=1500)"],
        ["FR-04, FR-05", "Semantic search of the 29 articles; return nothing when nothing is relevant.", "F1; Ines: no article for feature requests.", "Retrieval hit@k against expected documents.", f"hit@1 {dv['hit1']:.1f}% dev, {vl['hit1']:.1f}% val"],
        ["FR-06", "Never auto-respond to restricted intents.", "F2; Daniel.", "Safety violations on labelled tickets.", "0 of 101"],
        ["FR-07", "Deterministic routing: restricted intent or wording, confidence threshold (0.85, from data), evidence.", "Marcus; calibration.", "Unit tests; harness route accuracy.", f"{vl['route']:.0f}% val, {dv['route']:.0f}% dev"],
        ["FR-08", "Escalation packet: summary, sources, reason.", "F3; Daniel.", "Completeness check on every escalation.", "100%"],
        ["FR-09, FR-10", "Cite the article used; do not answer without evidence.", "Ines; Ravi.", "Citation resolves; independent judge.", "100%; 0 of 150 hallucinated"],
        ["FR-11", "Five guardrails on every outbound reply.", "Marcus's primary fear; GDPR.", "Unit tests; harness blocks.", f"{dv['blocks'] + vl['blocks']} blocks across the two runs"],
        ["FR-12", "Persistent decision log, one record per ticket.", "Autumn compliance review.", "Log count equals tickets processed.", "Reconciles on every run"],
        ["FR-13", "Store resolution records for resolved tickets.", "Compounding value of the resolution graph.", "Records written per run.", "Written; never read (unproven)"],
        ["FR-19, FR-20", "Configurable provider; kill switch.", "Added after the build: credit exhaustion; governance framework.", "Outage drill; kill-switch drill.", "80/80 escalated; effect under 2 s"],
        ["NFR-01", "Auto-reply p95 latency under 3 s.", "Customers on chat feel the slowest case.", "Harness percentile.", f"{vl['p95']} ms val; {dv['p95']} ms dev"],
        ["NFR-04", "Zero personal data in outbound text.", "GDPR; Daniel.", "PII scan of every reply.", "0 findings"],
        ["NFR-06", "Under 5 pp variation across tiers and fluency.", "Ravi; Sofia.", "Fairness audit (Section 8).", "Not demonstrated either way"],
    ], [16, 46, 42, 36, 30])
    r.p("Three requirements deserve a comment because they changed. FR-03 first assumed the model's own confidence could be used; Section 5 explains why it "
        "cannot. FR-06 first read the ground-truth flag at run time, which is impossible in production, and was rewritten to depend on the predicted intent. "
        "NFR-03 requires two independent assessors of reply quality. One is an independent model; the second, a person, has not yet done the review, so that "
        "requirement is only partly met, and Section 7 says so.")
    r.h2("4.1  Scope and priorities")
    r.p("The document has 22 functional requirements (17 Must, 4 Should, 1 Could) and 10 non-functional requirements. Each Must requirement either protects a customer (restricted topics, privacy, grounding, the audit log, graceful failure) or "
        "is needed for the unattended run to be assessed at all. The Should and Could items are the learning loop (FR-13, FR-21), the configurable provider (FR-19), the HTTP interface and monitoring. "
        "Out of scope, deliberately: answering feature requests, roadmap questions and novel incidents; automating security, billing-dispute or compliance replies; building a new knowledge base; "
        "and replacing agents. Those exclusions come straight from the interviews and from the 17.4% of tickets flagged as never to be auto-answered.")
    r.h2("4.2  Traceability from evidence to code and test")
    r.p("The brief says someone will pick a requirement at random and ask which discovery evidence produced it, then pick a prompt and ask which requirement it serves. @T:trace@ shows the chain for the main requirements: from the finding "
        "through the requirement to the module or prompt that implements it, the test that checks it, and the measured result. The decision log carries the same identifiers: each record lists the requirement IDs and the prompt versions that produced the decision.")
    r.table("trace", "Traceability from discovery evidence to requirement, implementation, test and measured result.", [
        ["Evidence", "Requirement", "Implemented in", "Checked by", "Result"],
        ["F1: 71.4% of tickets answerable from the 29 articles (Sofia, Ines, ticket labels)", "FR-04, FR-09, FR-10", "src/retrieve.py; prompt PR-GN-01 v4.0 in src/generate.py", "test_retrieve_classify_generate.py, test_generation_contract.py; judge on 150 replies", f"hit@1 {ctx['dv']['hit1']:.0f}% dev; 0 hallucinated"],
        ["F2: 87 of 500 tickets must never be auto-answered (ticket flag, Daniel)", "FR-06, FR-22", "src/route.py safety rules; src/guardrails.py security wording", "test_route.py, test_guardrails.py; harness safety count", "0 of 101 restricted tickets answered; 0 of 87 with unseen wording"],
        ["F3: escalations arrive with no context (Daniel)", "FR-08", "route.build_escalation_context; prompt PR-RO-01 v1.0", "harness checks every escalation for summary, sources and reason", "100% complete"],
        ["Marcus: 'confidently wrong' is the fear; he needs explainability for the compliance review", "FR-11, FR-12, NFR-05", "src/guardrails.py; src/logging_store.py", "test_guardrails.py, test_logging.py; log reconciles with tickets", "0 unsupported claims in 150 judged replies; log reconciles on every run"],
        ["Ravi: accepts automation if it is honest, cites its source and says it is automated", "FR-09", "citations resolved against the retrieved articles; disclosure line appended to every reply", "citation-resolution check in the harness", "100% of citations resolve"],
        ["Build finding: the model provider's credit ran out mid-evaluation", "FR-14, FR-19, FR-20", "src/llm.py (fail fast, retry, breaker, cache); kill switch in src/pipeline.py", "test_llm_failures.py, test_kill_switch.py; outage drill", "80 of 80 escalated, 0 replies during the drill"],
    ], [38, 22, 40, 40, 30])
