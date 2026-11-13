"""Sections 1 to 4 of the report."""


def build(r, figs, ctx):
    # ------------------------------------------------------------------ 1 Executive summary
    r.h1("1  Executive summary", key="s1", new_page=False)
    r.p("CloudServe Solutions asked for a chatbot to answer support tickets. Discovery showed that this was the wrong shape of solution. "
        "More than 500 tickets a week reach six agents, first replies take 8 to 12 hours against a two-hour agreement, and only 43.8% of "
        "tickets are resolved at first contact. Yet 71.4% of the tickets in the sample can already be answered from the company's own "
        "29 documentation articles. The answers exist; agents cannot reach them, because customers do not describe problems in documentation "
        "vocabulary and keyword search fails. When agents do escalate, the ticket reaches tier two with no context, which adds 15 to 30 minutes "
        "of re-reading to every escalation.")
    r.p("I built a system that does two things. It retrieves the right article for a ticket and drafts a cited reply that is sent only when the "
        "evidence and confidence are good enough. Otherwise it escalates to a human with a prepared packet: a short summary, the relevant "
        "articles and the reason it did not answer. The routing decision is ordinary deterministic code, not a model's opinion, and every "
        "decision is written to an audit log. The system is a Python pipeline (ingest, classify, retrieve, route, generate, guardrails, "
        "log) behind a FastAPI interface, with an unattended evaluation harness, 106 automated tests, a kill switch, and a Prometheus and "
        "Grafana monitoring configuration.")
    dv, dn, vl = ctx["dv"], ctx["dn"], ctx["vl"]
    r.p(f"<b>What it achieved.</b> On the 500 development tickets the system sent an automatic reply to {dv['auto_pct']:.1f}% and escalated {dv['esc_pct']:.1f}%, against a "
        f"baseline escalation rate of 56.2%. An offline proxy for first-contact resolution (replied automatically and the labels say the "
        f"documentation can answer it) is {dv['proxy']:.1f}%, against a baseline of 43.8% and a target of 60%. On the 80-ticket validation set the same "
        f"proxy is {vl['proxy']:.1f}%, under the target. Auto-reply latency at the 95th percentile is {vl['p95']} ms on validation (target under 3 s). "
        f"No safety-restricted ticket was auto-answered (0 of 101), and also 0 of {dn['safe_n']} when each ticket is classified as if its wording were new. "
        f"No personal data left the system (0 findings in 580 tickets), every citation resolved to a retrieved article, and an independent model judged 0 of 150 sampled replies to contain an unsupported claim.")
    r.p(f"<b>What it did not achieve, and the single most important caveat.</b> About a quarter of the automatic replies ({vl['prec']:.0f} to {dv['prec']:.0f}% precision) went "
        f"to tickets that the labels say should have reached a human, and {ctx['unans_dev_pct']:.0f} to {ctx['unans_val_pct']:.0f}% went to tickets the labels say cannot be answered from "
        f"the documentation. Counting those as tickets that still need a person, the effective escalation rate is {ctx['adj_dev']:.0f}% on the "
        f"development set and {ctx['adj_val']:.0f}% on validation, not 21%. Five different signals failed to predict which tickets should escalate, and identical ticket text carries "
        f"the same route label only 87.8% of the time, so part of this is a property of the labels. A second finding concerns fairness: route accuracy is significantly lower "
        f"for enterprise and standard customers than for business customers (about 12 and 8 points on the development set, wider when wording is new), which exceeds the 5-point target. "
        f"The evaluation also flatters the system in ways stated in Section 7: half the development tickets share their text with another ticket (so I also report a harder "
        f"'unseen wording' setting), the validation set was used while fixing faults, the hidden evaluation set was never available to me, and the second human assessor of reply quality has not yet reviewed any reply.")
    r.p("<b>Recommendation.</b> Do not deploy this as an autonomous responder. Deploy it first as a draft-for-agent tool, which is also what the "
        "tier-one agent in the interviews asked for, and measure agent acceptance on live tickets for several weeks before widening "
        "automation to the intents where measured precision is highest. Section 8 lists what must be true before the system speaks to a real customer.")

    # ------------------------------------------------------------------ 2 The problem
    r.h1("2  The problem", key="s2")
    r.h2("2.1  What was asked for")
    r.p("The head of support, Marcus Adeyemi, described what he wanted in one sentence: \"I picture it answering the easy ones so my people can do "
        "the hard ones.\" The brief that framed the project asked for an AI system that receives tickets from four channels, classifies them, "
        "retrieves knowledge, and either responds or escalates, with every decision logged. Read literally, that is a chatbot with a fallback.")
    r.h2("2.2  What discovery revealed")
    r.p("Five stakeholders were interviewed (Table 1 lists their accounts against the data) and 500 labelled tickets were analysed. The picture that "
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

    # ------------------------------------------------------------------ 3 Discovery findings
    r.h1("3  Discovery findings", key="s3")
    r.p("This section presents the evidence as findings. The full workbook (five interviews, 13 measurements, three disagreements resolved with data) "
        "is Appendix A. Figure 1 summarises the headline numbers.")
    r.fig("disc", figs["disc"], "Headline facts from the 500 development tickets (a) and first-contact resolution by customer tier (b). "
          "Source: data/development_tickets.json, history and label fields.", 150)
    r.h2("3.1  Three findings that changed the design")
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
    r.p("Four disagreements between accounts were settled with data rather than by preference (Table 3). Two are worth drawing out because they "
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

    # ------------------------------------------------------------------ 4 Requirements
    r.h1("4  Requirements", key="s4")
    r.p("The product requirements document (PRD) states 20 functional requirements (FR-01 to FR-20) and ten non-functional requirements "
        "(NFR-01 to NFR-10). Each one cites the evidence that justifies it; this section shows how the findings of Section 3 became requirements. "
        "Version 1.0 had 18 functional requirements. Version 2.0, after the build, changed 11 and added two (Section 9). The IDs below are the "
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
