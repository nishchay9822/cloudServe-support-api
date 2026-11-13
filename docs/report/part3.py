"""Sections 7 to 10, the AI-use declaration and the appendices."""


def build(r, figs, ctx):
    c = ctx
    # ------------------------------------------------------------------ 7 Evaluation
    r.h1("7  Evaluation", key="s7")
    r.h2("7.1  Method and provenance")
    r.p(f"Three data sets were used. The <b>development set</b> (500 labelled tickets) was run end to end with leave-one-out: when a ticket is classified, "
        f"its own entry is removed from the nearest-ticket index, so the system never sees its own answer. The <b>validation set</b> (80 labelled tickets) "
        f"is the unattended gate run required by the build specification. The <b>hidden evaluation set was not available to me and was used zero times</b>; "
        f"nothing in this report is a hidden-set result. Reference answers exist for 200 tickets and were used only to assess reply quality, never to build the system.")
    r.p(f"The development run finished on {c['dev_date']} using the final pipeline logic; later changes to the provider client and the judge (error handling and "
        f"token budgets) do not alter routing or generation. The validation gate used for every figure below finished on {c['gate_date']} on the model "
        f"{c['model']}, with the repository at commit {c['commit']} and these prompt versions: PR-CL-01 v2.0, PR-GN-01 v3.0, PR-RO-01 v1.0 and PR-EV-01 v1.0. "
        f"Both runs processed every ticket with no per-ticket error, and the decision log reconciled exactly with the number of tickets processed (500 of 500 and 80 of 80).")
    r.p("The development set is reported in two settings. <b>Plain leave-one-out</b> removes only the ticket itself from the neighbour index. Because about half the "
        "tickets have a same-text twin, that setting is easy. <b>Unseen wording</b> (run with --novel-cap 0.90) removes every same-text twin and every neighbour above 0.90 "
        "cosine similarity, which simulates a ticket phrased in a way the system has not seen. A hidden set drawn from the same population may behave like either, so both are reported, "
        "and the confidence and threshold are fitted on the harder setting.")
    r.note("The brief says the validation tickets should not be looked at or tuned against while building, and that the final assessment uses a hidden set of 120 tickets. I did not follow the first rule. The validation set is not a clean hold-out. I used it repeatedly while debugging (for example tickets VAL-0005 and VAL-0012 led directly to two "
           "prompt and retrieval changes in Section 6), so its results are optimistic by an unknown amount. The development numbers are leave-one-out but the "
           "development tickets also served as the nearest-ticket index, and half of them share their exact text with another ticket.")
    r.h2("7.2  Business outcomes")
    r.p("Business outcomes come first because they are the reason the project exists. There are no live customers here, so each is an offline proxy computed from "
        "the tickets' own labels and history fields, and each is labelled as one. Table 8 sets every measure against its baseline and target. "
        "The two headline measures are the escalation rate and first-contact resolution.")
    r.table("results", "Results against baseline and target. Baselines from the interviews, with the dataset value in brackets. 'Achieved' is development / validation unless stated.", [
        ["Measure", "Baseline", "Target", "Achieved", "Confidence", "Notes"],
        ["First-contact resolution (proxy)", "42% (43.8%)", "60%", f"{c['fcr_dev']:.1f}% / {c['fcr_val']:.1f}%", "Low to medium",
         f"Proxy: replied automatically and the labels say the documentation answers it. 95% intervals {c['fcr_dev_ci']} and {c['fcr_val_ci']}; the validation interval spans the target. By the brief's own formula (tickets closed without escalation over all tickets) the figure is {c['brief_fcr_dev']:.1f}% / {c['brief_fcr_val']:.1f}%, which I do not use as the headline because it counts replies that may not resolve the ticket."],
        ["Mean time to first reply", "8 to 12 h", "under 5 min", f"Auto-replies: mean {c['mean_dev_ms']/1000:.2f} s / {c['mean_val_ms']/1000:.2f} s, median {c['med_dev']} s / {c['med_val']} s", "High for system time; none for the human leg",
         "Applies to the 78 to 79% of tickets answered automatically. Escalated tickets still wait for a person; their reply time was not measured and has not been shown to change."],
        ["Repeat contacts", "not measured (21.6% in the data)", "halved", "Not measured", "None", "Needs the same customer raising the same issue within seven days after a reply. Not observable offline."],
        ["Satisfaction proxy", "3.2 / 5 (2.97)", "4.0", "Not measured", "None",
         "No customers and no human rubric scoring was done. Judge coverage of required points (95%, n=100) is a quality indicator, not satisfaction."],
        ["Escalation rate", "58% (56.2%)", "30% or lower", f"{c['esc_dev']:.1f}% / {c['esc_val']:.1f}%; adjusted {c['adj_dev']:.1f}% / {c['adj_val']:.1f}%", "Medium",
         "Adjusted = escalations plus automatic replies to tickets the labels say are not answerable from the documentation (see text). The adjusted figure misses the target."],
        ["Classification precision", "n/a", "85% per class", f"Lowest class {c['minprec_dev']:.1f}% / {c['minprec_val']:.0f}%", "Low to medium",
         "All 22 classes pass. Flattered by duplicated ticket text; nearest-ticket classifier."],
        ["Hallucination rate", "n/a", "5% or lower", "0 of 150 (0 of 50 val, 0 of 100 dev)", "Medium",
         "One independent model assessor; 95% upper bound about 2.5%. The second, human assessor has not reviewed any reply."],
        ["Citation accuracy", "n/a", "95% or better", f"100% resolve; {c['vl']['cite']:.1f}% / {c['dv']['cite']:.1f}% cite the expected article", "Medium",
         "'Resolve' means the cited id is a retrieved article. Whether a citation supports its sentence rests on the judge."],
        ["Latency p95 (auto-reply)", "n/a", "under 3 s", f"{c['p95_dev_ms']} ms / {c['p95_val_ms']} ms", "High for sequential load",
         "Paid OpenRouter. On the Groq free tier p95 was 11 s (misses). No concurrent load test."],
        ["Private data in output", "n/a", "0", "0 in 580 tickets", "Medium", "Pattern-based scan; cannot recognise an ordinary name that belongs to someone else."],
        ["Cross-group variation", "n/a", "under 5 points", f"Tier {c['gaps']['customer_tier']:.1f}, region {c['gaps']['region']:.1f}, channel {c['gaps']['channel']:.1f}, length {c['gaps']['ticket_length']:.1f}, fluency {c['gaps']['language_fluency']:.1f} pp", "Medium",
         "Route accuracy. The tier gap is statistically significant (enterprise and standard below business) and exceeds the target; other dimensions are not significant (Section 8)."],
    ], [26, 18, 17, 38, 21, 50])
    r.fig("outcomes", figs["outcomes"], "Escalation rate (a) and first-contact resolution proxy (b) against baseline and target. "
          "'Adjusted' counts automatic replies to tickets labelled not answerable from the documentation as still needing a person.", 150)
    r.p(f"<b>Escalation.</b> The system escalates {c['esc_dev']:.1f}% of development tickets and {c['esc_val']:.1f}% of validation tickets against a baseline of about 56%, "
        f"which on the face of it beats the 30% target. I do not think that is the right reading. Of the {c['auto_dev']} automatic replies on the development set, {c['unans_dev']} "
        f"({c['unans_dev_pct']:.0f}%) went to tickets the labels say are not answerable from the documentation, and on validation {c['unans_val']} of {c['auto_val']} "
        f"({c['unans_val_pct']:.0f}%) did. A reply to such a ticket is unlikely to resolve it, so a person will probably still be needed. Counting those as escalations gives "
        f"{c['adj_dev']:.1f}% and {c['adj_val']:.1f}%, which is a large improvement on 56% but does not reach 30%. This is the figure I would put in front of the client.")
    r.p(f"<b>First-contact resolution.</b> The proxy is {c['fcr_dev']:.1f}% on development and {c['fcr_val']:.1f}% on validation, against a baseline of 43.8% and a target of 60%. "
        f"The development figure clears the target; the validation figure is {60 - c['fcr_val']:.1f} points under it, and with only 80 tickets the interval ({c['fcr_val_ci']}) comfortably contains 60%. "
        f"The honest summary is that the system plausibly moves resolution from the mid-40s to around 60%, but this evaluation cannot show it reaches 60% in production. "
        f"The proxy also assumes an automatic reply to an answerable ticket resolves it, which is exactly what a person would need to confirm in a live trial.")
    r.p("<b>Time to first reply.</b> For automatic replies the system takes about 0.4 seconds, so the 8 to 12 hour wait disappears for 78 to 79% of tickets. "
        "But the wait for the remaining tickets is unchanged by this system, and a tier-two engineer will receive escalations with context, which the "
        "interviews suggest should shorten handling time, though I have not measured it. <b>Customer satisfaction</b> was not measured at all; I did not "
        "have customers or a scored rubric, and I will not report a number I do not have.")
    r.h2("7.3  Technical performance")
    r.p(f"Table 9 gives the technical detail. The classification result is the strongest and also the least informative in the plain setting: the nearest-ticket classifier reaches "
        f"{c['dv']['intent']:.1f}% on development with leave-one-out, but 254 of the 500 development tickets share their exact text with another ticket because the data generator reuses templates. "
        f"With twins and near-duplicates removed it falls to {c['dn']['intent']:.1f}%, and the lowest class precision to {c['dn']['minprec']:.0f}% (onboarding tickets mistaken for configuration help), "
        f"below the 85% per-class target for that one class in that harsher setting. Retrieval is the more transferable result: the correct article is first for {c['dv']['hit1']:.1f}% of answerable "
        f"development tickets and {c['vl']['hit1']:.1f}% of validation tickets, and within the top five for {c['dv']['hit5']:.1f}% and {c['vl']['hit5']:.1f}%. These use the hybrid retriever; "
        f"in development testing the keyword component changed hit@1 by about a point in either direction, so it adds no measurable benefit on this 29-article corpus.")
    dv, dn, vl = c["dv"], c["dn"], c["vl"]
    f1 = lambda x: f"{x:.1f}%"
    r.table("runs", "Technical results for the evaluation runs (OpenRouter, Llama 3.1 8B generator). Development is shown with plain leave-one-out and with unseen wording.", [
        ["Measure", "Development, plain", "Development, unseen wording", "Validation, n=80"],
        ["Tickets processed / errors / log reconciles", "500 / 0 / yes", "500 / 0 / yes", "80 / 0 / yes"],
        ["Intent accuracy", f1(dv["intent"]), f1(dn["intent"]), f1(vl["intent"])],
        ["Lowest per-class precision", f1(dv["minprec"]), f1(dn["minprec"]), f1(vl["minprec"])],
        ["Retrieval hit@1 / hit@3 / hit@5", f"{dv['hit1']:.1f} / {dv['hit3']:.1f} / {dv['hit5']:.1f}%", f"{dn['hit1']:.1f} / {dn['hit3']:.1f} / {dn['hit5']:.1f}%", f"{vl['hit1']:.1f} / {vl['hit3']:.1f} / {vl['hit5']:.1f}%"],
        ["Automatic replies / escalations", f"{dv['auto']} / {dv['esc']}", f"{dn['auto']} / {dn['esc']}", f"{vl['auto']} / {vl['esc']}"],
        ["Route accuracy", f1(dv["route"]), f1(dn["route"]), f1(vl["route"])],
        ["Auto-reply precision (false automatic replies)", f"{dv['prec']:.1f}% ({dv['fa']})", f"{dn['prec']:.1f}% ({dn['fa']})", f"{vl['prec']:.1f}% ({vl['fa']})"],
        ["Over-escalation (should have answered)", str(dv["oe"]), str(dn["oe"]), str(vl["oe"])],
        ["Safety violations / restricted tickets", f"{dv['viol']} / {dv['safe_n']}", f"{dn['viol']} / {dn['safe_n']}", f"{vl['viol']} / {vl['safe_n']}"],
        ["Guardrail and screen blocks", dv["blocks_txt"], dn["blocks_txt"], vl["blocks_txt"]],
        ["Citations resolving to a retrieved article", "100%", "100%", "100%"],
        ["Cited the expected article", f1(dv["cite"]), f1(dn["cite"]), f1(vl["cite"])],
        ["Escalations with a complete context packet", f"100% ({dv['esc_n']})", f"100% ({dn['esc_n']})", f"100% ({vl['esc_n']})"],
        ["Auto-reply latency mean / p50 / p95", f"{dv['mean']:.0f} / {dv['p50']} / {dv['p95']} ms", f"{dn['mean']:.0f} / {dn['p50']} / {dn['p95']} ms", f"{vl['mean']:.0f} / {vl['p50']} / {vl['p95']} ms"],
        ["Tokens per ticket", str(dv["tok"]), str(dn["tok"]), str(vl["tok"])],
        ["Resolution records written", str(dv["resrec"]), str(dn["resrec"]), str(vl["resrec"])],
    ], [56, 38, 42, 34])
    r.p(f"<b>Routing.</b> Route accuracy is {dv['route']:.1f}% on development, {dn['route']:.1f}% with unseen wording and {vl['route']:.1f}% on validation. The errors are mostly one kind: the system answered a ticket the labels say should "
        f"have gone to a human ({dv['fa']} of 500, {dn['fa']} of 500 and {vl['fa']} of 80), while it rarely refused a ticket it should have answered ({dv['oe']}, {dn['oe']} and {vl['oe']}). "
        "That asymmetry is by design, since a wrong automatic reply costs more than an extra escalation for restricted tickets, but it keeps auto-reply precision at "
        f"{vl['prec']:.0f} to {dv['prec']:.0f}%. The routing safeguards matter most in the unseen-wording setting: without the security-wording net and the safety-proximity rule, 3 of 87 restricted "
        "tickets were auto-answered there (a former employee who still has access, mistaken for an account-access ticket); with them, none are. "
        "<b>Urgency</b> is assigned and logged but not predicted well (below the 55% majority-class baseline in the earlier runs); I report this as a failure and do not use urgency for routing.")
    r.p("<b>Cost and speed.</b> A ticket uses about 900 tokens. At OpenRouter's listed prices for the generator (USD 0.02 per million input and 0.04 per million output tokens, "
        "retrieved 12 November 2026) that is about two thousandths of a US cent per ticket. Retrieval and the nearest-ticket classifier add no per-call cost, which supports NFR-07. "
        f"Auto-reply latency at the 95th percentile is {c['vl']['p95']} ms on validation. The model provider matters more than the model: the same model took about 11 seconds to answer a short prompt under "
        "default provider routing and about 0.4 seconds when providers were sorted by throughput. On Groq's free tier, rate limits pushed the 95th percentile to 11 seconds (Figure 5).")
    r.fig("latency", figs["latency"], "Auto-reply latency by provider on the 80-ticket validation set. The free Groq tier waits out rate limits and misses the 3-second target.", 110)
    r.h3("Reply quality and the judge")
    r.p("Hallucination needs human judgement to establish properly. I used a model from a different family as the first assessor and have not yet had a second, human, assessor. "
        "The history of this measurement matters more than its final value, because it shows how easily a judge misleads (Table 10).")
    r.table("judge", "How the reply-quality measurement changed as the judge improved.", [
        ["Assessor", "Sample", "Result", "What I learned"],
        ["Same-family 8B model", "50 validation replies", "4 flagged (8%)", "All four flagged statements were present in the cited articles: false positives. A weak judge is wrong in both directions."],
        ["openai/gpt-4o-mini (independent)", "50 validation replies", "0 hallucinated, 0 prohibited", "The reference figure for validation."],
        ["openai/gpt-4o-mini, with reference answers", "100 development replies", "0% hallucinated, 0% prohibited, 95% required-point coverage", "Coverage was 80% under the earlier prompt and rose to 95% under v3."],
        ["openai/gpt-oss-120b (on Groq)", "50 validation replies", "0 hallucinated, 0 prohibited", "Agreement with the OpenRouter judge from a third model family."],
        ["Human second assessor", "none yet", "pending", "Required by NFR-03. A review sheet is written by the harness for this purpose."],
    ], [38, 32, 42, 58])
    r.h3("Calibration and the threshold")
    sel = c["sel"]
    r.p("The routing threshold is only meaningful if stated confidence matches observed accuracy. With plain leave-one-out that cannot be shown, because confidence is 0.99 on nearly every ticket "
        "(Section 7.1). I therefore fitted the confidence on the unseen-wording setting: every development ticket was classified three times, with twins removed and neighbours above 0.97, 0.90 and "
        f"0.85 similarity removed (1,500 samples). The nearest-neighbour vote share maps to observed accuracy as 0.99 above 0.85, 0.98 for 0.75 to 0.85, 0.77 for 0.60 to 0.75 and 0.42 below 0.60; "
        "when the vote is unclear the model is asked and the combined confidence uses whether it agrees with the neighbours. "
        f"On these samples the expected calibration error is {sel['ece_pp']} pp (Table 11). That is inside the 5-point governance condition, but it is measured on simulated unseen wording, not on live traffic.")
    r.table("calib", "Reliability of the final confidence on 1,500 unseen-wording samples.", [["Confidence band", "n", "Stated", "Observed"]] +
            [[b["band"], str(b["n"]), f"{b['stated']:.3f}", f"{b['observed']:.3f}"] for b in sel["reliability"]], [50, 30, 40, 40])
    r.p(f"The brief asks for a threshold determined from data and a stated trade-off. Table 12 sweeps the threshold over the same samples. Below 0.80 every ticket is answered; at 0.85 about 0.6% "
        f"of tickets are escalated and the auto-answered tickets are classified correctly {sel['sweep'][5]['intent_accuracy_of_auto']*100:.1f}% of the time; at 0.90 about 5% are escalated for a further 0.5-point gain. "
        f"I chose <b>{sel['chosen']}</b>, the lowest threshold at which auto-answered tickets are right at least 99% of the time, meaning at most one automatic reply in a hundred addresses the wrong problem. "
        "A different business could reasonably choose 0.90, trading 5% more escalations for one fewer wrong reply in about 200. The sweep also shows what no threshold can fix: six restricted tickets "
        "(2.3%) are misclassified with high confidence at every threshold, which is why the security-wording net and the safety-proximity rule exist.")
    rows = [["Threshold", "Auto-reply rate", "Intent accuracy of auto-answered", "Restricted tickets misclassified as ordinary"]]
    for x in sel["sweep"]:
        rows.append([str(x["threshold"]), f"{x['auto_rate']*100:.1f}%", "n/a" if x["intent_accuracy_of_auto"] is None else f"{x['intent_accuracy_of_auto']*100:.1f}%", f"{x['restricted_leaks']} ({x['restricted_leak_rate']*100:.1f}%)"])
    r.table("sweep", "Confidence threshold sweep on 1,500 unseen-wording samples (evaluation/calibrate.py). Chosen: " + str(sel["chosen"]) + ".", rows, [30, 36, 54, 50])
    r.h2("7.4  Governance conditions")
    r.p("The governance conditions either hold or they do not. Private data: zero occurrences in 580 tickets. Decision logging: exact reconciliation on every run. "
        "Confidence calibration: within 5 points (0.3 pp) on simulated unseen wording, and untested on live traffic. Quality across customer groups: <b>not met</b> for customer tier, where enterprise and "
        "standard customers receive significantly less accurate routing than business customers (Section 8). A system that fails any of these is not deployable as it stands, and the tier gap is the open question.")
    r.h2("7.5  The limits of what was measured")
    r.p("The figures above should be treated with caution because of the following, each of which I can state but not remove. (1) The data are synthetic and templated; "
        "half the development tickets repeat another's text, which inflates classification and perhaps retrieval. (2) The validation set was used while fixing faults, "
        "so it is not a clean hold-out, and the hidden set was never run. (3) The business outcomes are label-based proxies, not customer outcomes; satisfaction "
        "was not measured. (4) Route and urgency labels are partly noise: identical text agrees on the route label only 87.8% of the time, which puts a ceiling on "
        "any route accuracy figure. (5) The judge is a model; the human second assessor is outstanding. (6) Calibration is measured on simulated unseen wording, not live traffic. "
        "(7) Latency was measured one ticket at a time on a single laptop. (8) The 95% intervals on first-contact resolution are about 8 points wide on 500 tickets and about 20 on 80. (9) The threshold and confidence are calibrated on simulated unseen wording from the same development tickets, not on live traffic.")
    r.p("What I am most confident of: the safety routing (0 of 101 restricted tickets answered), the privacy result, the audit log, the graceful degradation under provider "
        "outage, and retrieval quality. What I am least confident of: the first-contact resolution figure, the cause of the tier disparity, and anything involving real customers.")

    # ------------------------------------------------------------------ 8 Governance and risk
    r.h1("8  Governance and risk", key="s8")
    r.p("The completed Governance Framework (risk register with owners, fairness audit, guardrails, incident procedure, kill switch and declaration) is a separate "
        "workbook, docs/Governance_Framework.docx. This section summarises it and adds the evidence behind it.")
    r.h2("8.1  Risk register")
    r.p("Twelve risks are tracked: the eight the framework lists and four found during the build. Table 13 gives the rating after mitigation and the principal control for each; "
        "Figure 6 places them on a likelihood and impact grid. The highest-rated risks are those where a measurement in this project is weak: R-09 (automatic replies to tickets "
        "that should have gone to a human), R-11 (the evaluation overstating real performance) and R-05 (stale documentation). Owners in the workbook are proposed roles from the "
        "interviews and the author; none has accepted them.")
    r.table("risks", "Risk register summary (full text in the Governance Framework workbook).", [
        ["ID", "Risk", "Likelihood / impact", "Principal control in the design", "Evidence"],
        ["R-01", "Confident, wrong answer", "Medium / very high", "Full-article grounding, NO_ANSWER, figure checks, confidence floor", "0 of 150 judged replies hallucinated"],
        ["R-02", "Private data in output", "Low / very high", "Privacy guardrail blocks and escalates, never redacts", "0 findings in 580 tickets"],
        ["R-03", "Input treated as instruction", "Low / very high", "Screen before any model call; data-not-instructions prompting; recheck", "Unit tests; no red team"],
        ["R-04", "Some groups served worse", "High / high", "Fairness audit with intervals and tests; per-tier monitoring recommended", "Tier disparity confirmed; others not"],
        ["R-05", "Documentation goes stale", "High over time / high", "Citations traceable; articles older than 180 days never quoted", "Guard tested; corpus all 0 days old"],
        ["R-06", "Provider unavailable", "High / medium", "Retries, circuit breaker, fail-fast, configurable provider, drill", "80 of 80 escalated, 0 replies"],
        ["R-07", "Latency under load", "Medium / medium", "Provider sorted by throughput; alert", f"{c['vl']['p95']} ms p95; no load test"],
        ["R-08", "Cost rises", "Low / low", "Tokens logged per decision; spend cap", "About 900 tokens per ticket"],
        ["R-09", "Replies to tickets needing a human", "High / medium to high", "Safety intents always escalate; draft-first rollout", "71 to 75% precision"],
        ["R-10", "Credential exposed", "Medium / high", "Gitignored .env, placeholders, history scan, rotate keys", "0 secrets in history"],
        ["R-11", "Evaluation overstates", "High / high", "Leave-one-out, separate validation, stated limits, shadow mode", "254 of 500 duplicate texts"],
        ["R-12", "Learning loop scales mistakes", "Low today / medium", "Records are write-only; confirmed resolutions only if used", "Not yet used"],
    ], [10, 34, 30, 60, 36])
    r.fig("risk", figs["risk"], "Risks placed by likelihood and impact with mitigations in place. Shading: green low, amber medium, red high.", 110)
    r.h2("8.2  Fairness audit")
    r.p("The audit segments the 500 development tickets by tier, English fluency, ticket length, region and channel, and the 80 validation tickets likewise. For each segment it "
        "reports the share answered automatically, a resolution proxy, the rate of automatic replies that should have escalated, retrieval quality, and route accuracy "
        "with a 95% interval and a significance test against the best segment. A gap counts as a finding only if it is above the 5-point target and statistically "
        "distinguishable from noise on at least 30 tickets. Figure 7 shows route accuracy by segment and Table 14 the findings.")
    r.fig("fair", figs["fair"], "Route accuracy with 95% intervals by segment, 500 development tickets (plain leave-one-out). The dashed line is the overall rate.", 115)
    fd, fn = c["fair_dev"], c["fair_dn"]

    def worst(seg, key="gap_pp"):
        g, s_ = max(seg["groups"].items(), key=lambda kv: kv[1][key])
        return g.split(" (")[0], s_

    def cell(dim):
        g1, a = worst(fd[dim]); g2, b = worst(fn[dim])
        return f"{g1} {a['gap_pp']:.1f} pp below best (p = {a['p_vs_best']:.3f}); unseen wording: {g2} {b['gap_pp']:.1f} pp (p = {b['p_vs_best']:.3f})"

    def qcell(dim):
        g, a = worst(fd[dim], "quality_gap_pp")
        return f"{g} {a['quality_gap_pp']:.1f} pp lower hit@1 (p = {a['quality_p_vs_best']:.3f})"
    r.table("fairsum", "Fairness findings. Gaps are to the best segment in each dimension; p is a two-sided two-proportion test (not corrected for multiple comparisons).", [
        ["Dimension", "Largest gap in route accuracy", "Largest retrieval-quality gap", "Reading"],
        ["Customer tier", cell("customer_tier"), qcell("customer_tier"),
         "<b>Confirmed, above the 5-point target in both settings.</b> Enterprise and standard have higher false-automatic-reply rates (24.1% and 20.2% vs 15.2% for business). Cause not identified: the share of tickets labelled 'escalate' is similar across tiers (38.6%, 39.1%, 35.4%)."],
        ["English fluency", cell("language_fluency"), qcell("language_fluency"),
         "Not significant. Retrieval is weaker for non-fluent tickets, the direction the framework predicts, but only borderline. The 19-ticket validation group looked about 28 points worse and did not replicate on the 120 development tickets."],
        ["Ticket length", cell("ticket_length"), qcell("ticket_length"),
         "Nothing significant in the final system. An earlier run showed a borderline retrieval gap for short tickets that did not persist."],
        ["Region", cell("region"), qcell("region"),
         "Asia-Pacific lowest; not significant. Its tickets are labelled 'escalate' more often (46.2% vs 31.8% in Europe), so the system answers more tickets it should not."],
        ["Channel", cell("channel"), qcell("channel"),
         "Docs-comment lowest; not significant. 47.4% of its tickets carry an 'escalate' label (32 to 42% elsewhere)."],
    ], [22, 52, 36, 56])
    r.p("The honest reading has three parts. First, there is one confirmed disparity. Enterprise and standard customers receive less accurate routing than business customers, "
        "and the gap exceeds the 5-point target in both evaluation settings, so NFR-06 is not met for tier. With roughly ten comparisons made, only the unseen-wording enterprise result survives a "
        "Bonferroni correction (p = 0.002 against 0.005); the others should be read as likely but not certain. I did not identify the cause, and I did not engineer around it, because "
        "changing routing for one tier on this evidence would be fitting noise in synthetic labels. The practical recommendation is to monitor the false-automatic-reply rate per tier from the first "
        "day and to consider a stricter policy for enterprise tickets. Second, no other dimension shows a significant gap, but the 95% intervals span roughly 10 to 20 points, so this "
        "audit could only have detected gaps of about 10 points or more; 'not significant' does not mean 'fair'. Third, the segments differ mainly in how many of their tickets carry an escalate "
        "label, so part of what looks like unequal treatment is the system answering where the labels expected a person. A fair assessment needs live tickets and a larger sample per segment.")
    r.h2("8.3  Decision logging, kill switch and incident response")
    r.p("<b>Decision logging.</b> Every decision is written to a SQLite log with the action, reason, sources and scores, prompt version, guardrail results and requirement "
        "IDs. The count of logged decisions equalled the number of tickets processed on every run, including the provider-outage run, and tests assert that malformed input, "
        "provider failure and the kill switch each still produce a retrievable record. The log is not tamper-evident and has no retention policy; a production system under "
        "GDPR would need both.")
    r.p("<b>Kill switch.</b> A flag file, an environment variable or an authenticated API call sends every new ticket to a human with its context packet and no model call. "
        "It takes effect on the next ticket. The drill (tests/test_kill_switch.py) holds a ticket mid-generation, switches on over HTTP, confirms the next ticket escalates in "
        "under two seconds with a logged reason, confirms the in-flight ticket finishes normally, and confirms that switching off restores automatic replies. It "
        "has not been drilled by a person unfamiliar with the system, and it is a file on one host, so a multi-instance deployment would need a shared store.")
    r.p("<b>Incident response.</b> The six-step procedure (detect, contain, assess, notify, remediate, review) is written in the workbook so that someone unfamiliar with the "
        "system can follow it at two in the morning. It gives the exact command to engage the kill switch, the SQL query to list every automatic reply in a time window, the "
        "people who must be told, the 72-hour regulator deadline if personal data left the system, and the conditions for lifting the switch.")
    r.h2("8.4  Monitoring")
    r.p("The monitoring configuration (monitoring/) provides a Prometheus scrape of the API's /metrics endpoint, five alert rules mapped to risks, and a Grafana dashboard with the "
        "five views the specification requires: tickets per hour by channel and outcome, the auto-answered share, latency at the median and 95th percentile, guardrail activations by "
        "type, and the confidence distribution. A test checks that every metric the dashboard and alerts query is actually exposed. I did not run the stack because Docker was not "
        "available in the build environment, so the dashboard layout has not been seen rendering.")
    r.h2("8.5  The declaration")
    r.p("This system must never send an automated reply for a security, compliance, feature or unclear request, or any reply containing personal data or an unsupported claim. "
        "That is enforced by deterministic routing on the predicted intent, by guardrails that block and escalate, and by a kill switch. The most likely way it could still cause harm is a "
        "well-written, grounded but incomplete answer to a ticket that needed a person. I would not deploy it without first running it in draft mode on live tickets, completing the "
        "human review of replies, load-testing it, agreeing owners, rotating all keys, and deciding with the head of support whether to restrict automation to the intents with the best measured precision.")

    # ------------------------------------------------------------------ 9 Requirements revision
    r.h1("9  The requirements revision", key="s9")
    r.p("The build forced 13 changes to the PRD: 11 requirements changed and 2 were added; none were removed. After re-reading the brief's design figures I made four further changes (the last four rows of Table 15). These are in the code, the tests and this report but are <b>not yet in the PRD v2.0 document or its revision log</b>, which should become v2.1. Version 1.0 is untouched and version 2.0 carries a revision log in the "
        "official template (docs/Stage_5_PRD_Revision_Log.docx). Table 15 lists the substantive changes; every one was triggered by a specific observation made during the build, not by "
        "a preference.")
    r.table("changes", "Substantive requirement changes between PRD v1.0 and v2.0.", [
        ["ID", "Change", "What triggered it"],
        ["FR-01", "Channel is docs_comment (api_comments kept as an alias).", "The data's channel name differs from the scaffold; the scaffold would have rejected 15.6% of tickets."],
        ["FR-02", "22 real intent classes; urgency assigned but no accuracy target.", "Invented class names in my first prompt; urgency labels not recoverable from text (68.5% self-agreement)."],
        ["FR-03", "Confidence from classifier agreement, not model self-report.", "Self-report received a negative weight; two-classifier agreement was right every time on 300 dev tickets."],
        ["FR-04", "Search by section, but show the model the whole article.", "VAL-0012: the section omitted the fix and the reply improvised from another article."],
        ["FR-06", "Safety rule uses predicted intent, not the ground-truth flag.", "The flag does not exist on a live ticket; the flagged tickets equal four intents."],
        ["FR-07", "Ordered deterministic rules; precision limit recorded (71 to 75%).", "Five predictors of 'should escalate' all failed (Section 5.3)."],
        ["FR-09", "Independent model plus human assessor; NO_ANSWER sentinel.", "Same-family judge false positives; appended refusals (VAL-0005)."],
        ["FR-11", "Figures checked in every sentence; customer's own numbers allowed.", "My unit test let '45 minutes' pass; two correct replies were wrongly blocked."],
        ["FR-13", "Records written; compounding claim withdrawn.", "Nothing reads the records."],
        ["FR-14", "Explicit degradation: fail-fast on 401 and 402, circuit breaker.", "Credit exhaustion caused a 25-minute hang."],
        ["NFR-01", "Verification records the provider setting.", "11 s versus 0.4 s depending on provider routing."],
        ["FR-19 (new)", "Configurable provider; exhausted credit is a non-transient failure.", "OpenRouter credit ran out; the free tier was rate-limited."],
        ["FR-20 (new)", "Kill switch.", "Required by the governance framework; absent from v1."],
        ["FR-21 (proposed)", "Feedback loop: POST /feedback; a correction changes the neighbour index and is counted on the dashboard.", "The brief's high-level design lists the feedback loop as a cross-cutting concern; the PRD and my first build omitted it."],
        ["FR-22 (proposed)", "Security-wording screen and safety-proximity rule in routing.", "With unseen wording 3 of 87 restricted tickets were auto-answered with high confidence."],
        ["FR-03, FR-07 (revised again)", "Confidence calibrated on unseen wording; threshold 0.85 chosen from data; routing order confidence, then evidence.", "Replaying routing showed the 0.80 threshold changed nothing; the brief's decision tree puts confidence before evidence."],
        ["FR-04, FR-15 (revised again)", "Hybrid dense plus BM25 search; LangGraph orchestrator; /tickets endpoint; response formatter.", "The brief's low-level design names each of them."],
    ], [20, 76, 74])
    r.p("<b>What I decided not to change.</b> I kept the under-5-point fairness target even though several development gaps exceed it, because relaxing it would hide a real "
        "finding. I did not tune the routing further after five signals failed, because more tuning would have fitted label noise. I did not change the 100% validation intent "
        "accuracy claim into a stronger one, because duplicated text explains it. I kept the four always-escalate intents hard-coded because they match the discovery evidence exactly.")
    r.p("<b>What the revision taught me.</b> The assumptions that failed were not the technical ones. I assumed a model's confidence would be usable; it was not. I assumed the labels "
        "were a clean target; part of them is noise. I assumed a single provider was a safe dependency; it was the thing that stopped the project twice. The pattern is that each wrong "
        "assumption was found by reading individual cases, and each right decision was made by measuring something I would rather not have measured.")

    # ------------------------------------------------------------------ 10 Conclusions
    r.h1("10  Conclusions", key="s10")
    r.p("The project set out to turn a chatbot request into something CloudServe could trust. The result is a working retrieval-first support pipeline that answers about four tickets in five "
        "in under a second, refuses the tickets it must not answer, escalates the rest with context, logs every decision, and degrades safely when its model provider fails. "
        "Measured against the framework's three tiers, the governance conditions that can be checked hold, the technical measures meet their targets on this data, and the business "
        "outcomes are encouraging but are proxies. The system is not ready to answer customers on its own.")
    r.h2("10.1  What I got wrong")
    r.bullets([
        "I invented intent labels and a channel name in the first scaffold and only found the mismatch by reading the data; I should have profiled the data before writing any prompt.",
        "I treated model confidence as usable. It is not, and the calibration I eventually built rests on one populated band.",
        "I used the validation set while debugging, so I have no clean hold-out and cannot say how optimistic the validation figures are.",
        "I claimed a learning loop (resolution records) in the PRD that nothing reads.",
        "I ignored the brief's instruction not to look at or tune against the validation tickets while building; I used them to debug, so the validation figures are optimistic.",
        "My first confidence threshold did nothing: the classifier's confidence was 0.99 for nearly every ticket, so any threshold below 1.0 routed identically. I only found out when I replayed routing at different thresholds, and fixed it by calibrating on simulated unseen wording.",
        "I relied on one provider for both generation and judging, and the project stopped when its credit ran out.",
    ])
    r.h2("10.2  What I would do next")
    r.bullets([
        "Run in draft-for-agent mode on live tickets for several weeks, measuring agent acceptance, edit distance and repeat contact, before any automatic sending.",
        "Complete the human review of replies and report inter-assessor agreement, as NFR-03 requires.",
        "Feed resolved tickets into the nearest-ticket index and show with a before and after measurement whether resolution improves, which is the only way to support the compounding claim.",
        "Collect a mid-confidence test set to calibrate the routing threshold, and restrict automation to the intents with the strongest measured precision.",
        "Re-run the fairness audit on live data with enough tickets per segment to detect a 5-point gap, and add per-segment alerts to the dashboard.",
        "Load-test the pipeline, run the Prometheus and Grafana stack, and move the kill switch to a shared store.",
    ])
    r.h2("10.3  What remains uncertain")
    r.p("Whether the proxies translate into real resolution; whether the fairness gaps in direction are real; whether a language model with messier input behaves as it did here; and whether "
        "the retrieval quality holds when the documentation changes. These can only be answered on live data, which is why the recommendation is a staged rollout.")
    r.h2("10.4  Declaration of AI tool use")
    r.p("This project was built with substantial AI assistance. The coding assistant Kiro drafted most of the source code, tests, evaluation scripts, workbook text and this report in "
        "conversation with the author. The author set the goals and constraints, supplied the data and credentials, chose the project dates, and made the decisions recorded in this report, "
        "and is responsible for the submission. Because the assistant wrote much of the text, the author should read and confirm every number and claim before submission; items needing the author's "
        "own action are the human second assessment of replies, the effort log hours, and confirmation of risk owners. At run time the system calls language models: Llama 3.1 8B "
        "Instruct for generation and fallback classification (OpenRouter), GPT-4o-mini and GPT-OSS-120B as independent judges, Qwen3.8-27B as a generator on the Groq fallback, "
        "and the all-MiniLM-L6-v2 embedding model locally. No hidden-set data was exposed to any model. Third-party libraries are listed in requirements.txt, and no external code was knowingly copied.")

    # ------------------------------------------------------------------ Appendices
    r.h1("Appendices", key="app")
    r.h2("Appendix A  Full fairness table, 500 development tickets")
    rows = [["Dim.", "Segment", "n", "Auto", "Resol.", "False auto", "hit@1", "Route acc (95% CI)", "Gap pp", "p"]]
    for dim, d in ctx["fair_dev"].items():
        for g, s in d["groups"].items():
            rows.append([dim.replace("customer_", "").replace("language_", "").replace("ticket_", ""), g, s["n"], f"{s['auto_rate']*100:.1f}%",
                         f"{s['resolution_rate']*100:.1f}%", f"{s['false_auto_rate']*100:.1f}%", f"{s['quality_hit_at_1']*100:.1f}%",
                         f"{s['route_accuracy']*100:.1f}% ({s['route_ci95'][0]*100:.0f}-{s['route_ci95'][1]*100:.0f})", s["gap_pp"], s["p_vs_best"]])
    r.table("appfair", "Segment results (evaluation/results/fairness_dev.json). Auto = auto-reply rate; Resol. = resolution proxy; False auto = automatic replies that should have escalated. The validation equivalent is fairness_val.json.", rows, [16, 26, 9, 15, 17, 16, 14, 30, 9, 12])
    r.h2("Appendix B  Prompt register")
    r.table("appprompts", "Active prompts and version history (prompts/README.md).", [
        ["ID", "Version", "Purpose", "File", "History"],
        ["PR-CL-01", "v2.0", "Intent and urgency classification", "prompts/build/classify_v2.txt", "v1 used invented labels; v2 uses the real 22."],
        ["PR-GN-01", "v3.0", "Grounded generation with citations", "prompts/build/generate_v3.txt", "v1 appended refusals; v2 NO_ANSWER sentinel; v3 covers all applicable steps (coverage 80% to 95%)."],
        ["PR-RO-01", "v1.0", "Escalation context packet", "prompts/build/route_v1.txt", "Unchanged."],
        ["PR-EV-01", "v1.0", "Reply-quality assessment", "prompts/evaluation/eval_v1.txt", "Unchanged."],
    ], [18, 14, 44, 52, 42])
    r.pagebreak()
    r.h2("Appendix C  Test inventory")
    r.table("apptests", "Automated tests (pytest tests/ -v).", [["File", "Tests", "Covers"]] + ctx["tests_rows"], [54, 16, 100])
    r.h2("Appendix D  How to reproduce")
    r.p("From a clean checkout: python3 -m venv venv; source venv/bin/activate; pip install -r requirements.txt; cp .env.example .env and set the provider key; "
        "pytest tests/ -v; then python evaluation/harness.py --input data/validation_tickets.json --output evaluation/results/run_001.json. "
        "The fairness audit is python evaluation/fairness_audit.py --run evaluation/results/dev_run.json --tickets data/development_tickets.json --out evaluation/results/fairness_dev. "
        "The monitoring stack is started with docker compose -f monitoring/docker-compose.yml up -d after the API is running. Python 3.9 to 3.11 is required.")
    r.h2("Appendix E  Other deliverables")
    r.p("Stage workbooks in docs/: Stage_1_Discovery_Workbook_Filled.docx, Stage_2_PRD_v1.docx and Stage_2_PRD_v2_0.docx, Stage_3_Prompt_Library.docx, Stage_4_Sprint_Plan.docx, "
        "Stage_5_PRD_Revision_Log.docx, Governance_Framework.docx, and the effort log. Architecture notes: docs/architecture.md and docs/architecture.drawio.")
