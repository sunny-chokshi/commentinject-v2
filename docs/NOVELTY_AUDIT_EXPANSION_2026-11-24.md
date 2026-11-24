# CommentInject v2: novelty audit, expanded prior-art search (2026-11-24)

This file extends `NOVELTY_AUDIT_2026-11-24.md`. It does not replace it. No other file was changed.

## 1. Method

- **Date of search:** 2026-11-24. The search covers work from 2020 to 2026-11-24, with most attention on 2023–2026.
- **Tools:**
  - a web search engine (standard and extended modes);
  - direct page fetches of arXiv abstract and HTML full-text pages, conference PDFs (NDSS 2026 and IEEE S&P 2025, with text extracted locally using pypdf), and blog and dataset pages.
- **Databases and venues reached:**
  - arXiv (cs.CR, cs.SE, cs.CL, cs.AI, cs.LG);
  - IEEE S&P and NDSS proceedings PDFs;
  - NeurIPS proceedings pages;
  - NAACL Findings (through arXiv);
  - ICSE (through arXiv comments fields);
  - Hugging Face datasets;
  - vendor and industry research blogs (Cloudflare, Legit Security);
  - aggregator pages (ResearchGate, alphaXiv, Pith), used only to find primary sources.
- **Not done:**
  - Google Scholar, Semantic Scholar and OpenReview were not queried through their own interfaces. They were reached only as general web-search results.
  - USENIX, CCS, FSE, ASE and ISSTA 2025–2026 proceedings were not browsed issue by issue. Hits from these venues came only through keyword search.
  - A hand search of those proceedings could still find more work.
- **Verification labels:**
  - **VERIFIED (full)**: Claude opened the full text, HTML or PDF, and checked the specific claims stated here.
  - **VERIFIED (abstract)**: Claude opened the arXiv abstract page or the primary source page only.
  - **UNVERIFIED**: seen only as a search-result snippet, or second-hand through another paper. Do not cite these on the strength of this file.
- **Privacy:** no names of the project owner were used in any query.

## 2. Table of works

Column key:
- **Safe ctrl**: the work evaluates matched safe, patched or benign controls.
- **In-code cmt**: the manipulation is placed in comments inside the code.
- **FPR/SDT**: the work reports false-positive rate (FPR), signal-detection (SDT) parameters, or neither.
- **Overlap**: which part of the v2 claim the work overlaps:
  - A = in-code comment attack on LLM vulnerability detectors;
  - B = matched safe twins and FPR under manipulation;
  - C = SDT d′/c, or "threshold shift vs discrimination loss" framing;
  - D = cost of comment stripping, including on benign comments;
  - E = reconciling null and large effects.

### 2.1 Comment and context attacks on LLM vulnerability detectors and code reviewers

| # | Citation | URL | Date | What it measures | Safe ctrl | In-code cmt | FPR / SDT | Overlap | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | S. Thornton, "LLM Code Reviewers Are Harder to Fool Than You Think" (v1 title; also listed as "Can Adversarial Code Comments Fool AI Security Reviewers…"), arXiv 2602.16741 | https://arxiv.org/abs/2602.16741 | 2026-02-18 | 100 vulnerable samples (Py/JS/Java), 8 comment strategies, 8 models; ΔFNR and McNemar tests. Effects are small and non-significant (p > 0.21). It notes that "backfire" appears only in unpaired analysis. | **No.** The paper states "We capture only false negatives." | Yes | No FPR, no SDT | A, D (stripping tested only on the adversarial condition; it "hurts" weaker models), E | VERIFIED (full) |
| 2 | Wu & Nita-Rotaru, "ALIBI: Adaptive Agentic Attacks on LLM-Based Vulnerability Detectors via Adversarial Code Comments", arXiv 2607.24964 | https://arxiv.org/abs/2607.24964 | 2026-07-27 | Adaptive agentic comment attack on 125 CWE-476 items (MegaVul-derived). ASR is computed only over clean true positives and exceeds 90% on 4 detectors. Defenses D1–D4. | **No.** It does not evaluate benign or patched code. | Yes | No FPR for the detectors or the sanitizer | A, D (sanitization reduces evasion to < 3%, with no cost measured; the paper says "We do not consider removing all comments a viable defense"), E | VERIFIED (full, first 100k chars plus the reference list) |
| 3 | L. Sun, A. Oprea, E. Wong, "Syntax- and Compilation-Preserving Evasion of LLM Vulnerability Detectors" (v1 title: "Semantics-Preserving Evasion…"), arXiv 2602.00305 | https://arxiv.org/abs/2602.00305 | v1 2026-01-30, v2 2026-05-06 | 5,000 C/C++ functions (PrimeVul/BigVul/DiverseVul). There are 4 carrier families, one of which is **comment carriers**. GCG-style optimized strings, conditional ASR, and a "Complete Resistance" metric. | **Partial.** It uses 500 held-out benign functions, not stated to be patched twins. "Benign-class invariance" is 100%. | Yes (optimized token strings in comments, not natural-language persuasion) | Reports **clean FPR and sanitized FPR** (App. B.3, Table 8); no SDT | A, **D (closest prior measurement of stripping cost)**: stripping comments plus preprocessor directives raises TPs (+5.2% Qwen, +8.6% Llama, +0.1% CodeAstra) and changes FPR by −6.6 to +1.8 pp. Partial B. | VERIFIED (full, targeted sections) |
| 4 | Alexopoulos, Alexopoulos, Spinellis, Mitropoulos, "When AI Agrees Too Much: Manipulating Automated Code Review via Bias Injection" (v1: "Measuring and Exploiting Confirmation Bias in LLM-Assisted Security Code Review"), arXiv 2603.18740, to appear at **ICSE 2027** | https://arxiv.org/abs/2603.18740 | v1 2026-03-19 … v5 2026-10-27 | **RQ1:** 247 vulnerable plus 250 patched CrossVul files, 6 LLMs, 5 prompt framings (neutral, weak or strong bug and bug-free), 14,910 queries. It reports detection on vulnerable files and on fixed files (true-negative rate). **Attack study:** 17 CVE reintroductions against Claude Code, with bias placed in the PR description, commit message **and in-code comments**. Redaction defense. | **Yes in RQ1** (paired vulnerable/patched). **No** in the attack study. | RQ1: no (the framing is in the prompt). Attack study: yes (for example "// Authored by senior security engineers.") | Reports both TPR and TNR per framing. **Strong bug-free framing raises fixed-file TNR by 16.8–94.8 pp** (for example GPT-4o-mini 3.2% → 98.0%) while TPR falls. No SDT and no discrimination analysis. The v1 abstract claimed "false positive rates change little", but the current version's table shows large shifts. | **B (paired operating-point shift, different channel)**, A (comments in the attack study, no controls), D (redaction restores 16/17, no benign cost) | VERIFIED (full, v2 and latest HTML) |
| 5 | Shahriar, Cai, Benkraouda, Wang, Celik, "Words Speak Louder Than Code: Investigating Cognitive Heuristics in LLM-Based Code Vulnerability Detection", arXiv 2606.30587, accepted at **IEEE S&P 2027** | https://arxiv.org/abs/2606.30587 | v1 2026-06-29, v2 2026-10-15 | Halo, framing and anchoring cues in the prompt and PR metadata. The code is identical across conditions ("the code snippet remains identical across all conditions"). 8 LLMs, 3 languages, PrimeVul paired. | **Yes** (paired PrimeVul) | **No.** In-code comments appear only as contrasted prior work. | Recall, FPR, precision, F1, "Recall Gap" and "FPR Gap"; no d′, c or AUC | **B and C in substance** (recall and FPR move by nearly equal amounts, so the willingness to flag changes); prompt-only defenses, scored on ASR only | VERIFIED (full, first 100k chars) |
| 6 | Melo, Fogliato, Zhou, Thaker, Wu, "SEVRA-BENCH: Social Engineering of Vulnerabilities in Review Agents", arXiv 2606.13757; HF dataset RedAI4Code/SEVRA | https://arxiv.org/abs/2606.13757 ; https://huggingface.co/datasets/RedAI4Code/SEVRA | v1 2026-06-11, v2 2026-07-06 | About 1,000 (paper) to 2,250 (dataset) malicious PRs that revert security fixes, 15 social-engineering framings, 8 review agents; refusal rate. | **Dataset only:** 347 benign security-fix PRs for a "false-decline rate". The framings are not applied to benign PRs, and the paper does not report FDR. | No (PR title and description) | No SDT | B (partial: a benign split exists but is not crossed with manipulation) | VERIFIED (full HTML plus dataset README) |
| 7 | Gong, Zhang, Jahangirova, Wang, "Adaptive Code Revision Attacks on AI Pull Request Reviewers" (AFCRA), arXiv 2610.05399 | https://arxiv.org/abs/2610.05399 | 2026-10-04 | Iterative code revisions guided by reviewer feedback; 159 exploitable CVEs; Sonnet 5 and GPT-5.5 reviewers. Comment and text attacks serve as baselines, which AFCRA outperforms by 2.5× and 12.5×. | Not in the abstract | Baseline only | No | A (as a baseline), E (adaptivity matters) | VERIFIED (abstract) |
| 8 | Bernstein, Beste, Ayzenshteyn, Schönherr, Mirsky, "Trust Me, I Know This Function: Hijacking LLM Static Analysis using Bias" (Familiar Pattern Attack), **NDSS 2026**; arXiv 2508.17361 | https://www.ndss-symposium.org/wp-content/uploads/2026-f2066-paper.pdf | 2025-08 (arXiv) / NDSS 2026 | Semantics-preserving code-pattern edits that exploit "abstraction bias". | Uses benign P∅ controls for the deception patterns | No (code patterns) | No SDT | Background for A (a non-comment channel) | VERIFIED (full PDF text extracted) |
| 9 | X. Li et al., "Make a Feint to the East While Attacking in the West: Blinding LLM-Based Code Auditors with Flashboom Attacks", **IEEE S&P 2025** | https://cs.nju.edu.cn/fxu/static/papers/featured/flashboom-sp2025.pdf | 2025 | High-attention decoy code snippets, which can be inserted "into the comments area". Blinding success up to 96.3% (CodeLlama). Uses "misleading comments" and "benign renaming" as baselines. | No (vulnerable only) | **Yes, partly** (commented-out decoy code; misleading-comment baseline) | No SDT | A (earliest peer-reviewed comment-area attack on LLM auditors found) | VERIFIED (full PDF text extracted) |
| 10 | Cloudforce One (Cloudflare), "Adversarial deception: a study of indirect prompt code injection" (prompt injection attacks on AI security auditors) | https://www.cloudflare.com/cloudforce-one/research/adversarial-deception-a-study-of-indirect-prompt-code-injection/ | 2026-04-29 | 100 malicious Workers scripts, "Notice to AI" comment lures (1 to 1,000 comments, 5 languages), 7 anonymized models, 18,400 calls. | **No** (malicious only) | Yes | No FPR. Comment removal is recommended as "trivial but highly effective" but not tested. | A, D (an untested claim) | VERIFIED (full page) |
| 11 | H. Li et al., "CoTDeceptor: Adversarial Code Obfuscation Against CoT-Enhanced LLM Code Agents", arXiv 2512.21250 | https://arxiv.org/abs/2512.21250 | 2025-12-24 | Multi-stage obfuscation that evades CoT vulnerability detectors. | Not stated | Not stated | No | Background for A | VERIFIED (abstract) |
| 12 | Ullah et al., "LLMs Cannot Reliably Identify and Reason About Security Vulnerabilities (Yet?)" (SecLLMHolmes), arXiv 2312.12575, IEEE S&P 2024 | https://arxiv.org/abs/2312.12575 | 2023-12 / 2024 | 228 scenarios. Hand-crafted vulnerable/patched pairs. Augmentations include **T4 "Add random code in comments"** plus renaming and library changes. | Yes, for base scenarios (it is not stated whether augmented sets include patched versions) | Only random code in comments, not persuasive comments | States that "all models analyzed have a high FPR"; no SDT; T4 changed ≤ 3/12 answers | B (pairs), A (weak form) | VERIFIED (full, first 100k chars) |
| 13 | Mayraz (Legit Security), "Remote Prompt Injection in GitLab Duo" | https://www.legitsecurity.com/blog/remote-prompt-injection-in-gitlab-duo | 2025-05-20 | Hidden prompts in MR descriptions, comments, commits, issues **and source code** were all obeyed by GitLab Duo. | No | Yes | No | Industry precedent for the in-code channel (not detection accuracy) | VERIFIED (full page) |
| 14 | Isbarov, Suleymanov, Shumailov, Kantarcioglu, "GitInject: Real-World Prompt Injection Attacks in AI-Powered CI/CD Pipelines", arXiv 2606.09935 | https://arxiv.org/abs/2606.09935 | v1 2026-06-07, v2 2026-11-02 | 11 live attack scenarios against AI PR-review and triage agents; the main channel is configuration files. | No | Not stated | Reports utility trade-offs of workflow defenses (details not read) | Background (agent prompt injection) | VERIFIED (abstract) |
| 15 | Nakibly & Babo, "Who Is Prompt-Injecting Coding Agents? An Empirical Study of Hidden AI-Directed Text on GitHub", arXiv 2611.28763 | https://arxiv.org/abs/2611.28763 | 2026-11-21 | About 145M issues, PRs, comments and READMEs. Two thirds of hidden AI-directed text is benign "first-party orchestration". Attacks are rare (about 1 in 3.3M). | n/a | Issue and PR comments; source files not stated | n/a | D (indirect: benign AI-directed text is common, so stripping has a real-world cost) | VERIFIED (abstract) |
| 16 | Munir, Quinzan, Roberts, "Hidden in the Comments: A Context-Injection Attack Surface in Code LLMs", arXiv 2610.05139 | https://arxiv.org/abs/2610.05139 | 2026-10-04 | Insecure instructions in comments push **code generation** to vulnerable outputs (77–92% vs 1.7–5.1% for benign tasks). | Benign tasks as controls | Yes | No SDT | Adjacent (generation, not detection) | VERIFIED (abstract) |
| 17 | Maloyan & Namiot, "Prompt Injection Attacks on Agentic Coding Assistants: A Systematic Analysis…", arXiv 2601.17548 | https://arxiv.org/abs/2601.17548 | 2026-01 | Survey; lists code comments as a delivery vector. | n/a | Yes (as a vector) | n/a | Background | UNVERIFIED (search snippet; also cited by ALIBI) |
| 18 | HACKODE (comment-based attack inducing vulnerable code generation, 75.92% ASR) | none found | 2024–2025? | Code generation | ? | Yes | ? | Adjacent | UNVERIFIED (second-hand, through Thornton and a search snippet; primary source not located) |
| 19 | "Code Poisoning Through Misleading Comments: Jailbreaking Large Language Models via Contextual Deception" (ResearchGate 404610436) | https://www.researchgate.net/publication/404610436 | 2026? | Code generation | ? | Yes | ? | Adjacent | UNVERIFIED (title only) |

### 2.2 Misleading comments and natural language in general code understanding

| # | Citation | URL | Date | What it measures | Safe ctrl | In-code cmt | FPR / SDT | Overlap | Status |
|---|---|---|---|---|---|---|---|---|---|
| 20 | Lam, Wang, Huang, Lyu, "CodeCrash: Exposing LLM Fragility to Misleading Natural Language in Code Reasoning", NeurIPS 2025, arXiv 2504.14119 | https://arxiv.org/abs/2504.14119 | 2025-04-19 (v3 2025-10-11) | Output prediction under misleading comments, prints and hints; 17 LLMs; −23.2% on average | Clean questions as baseline | Yes | No (accuracy task) | A in spirit (comment trust prior), not detection | VERIFIED (abstract) |
| 21 | Macke & Doyle, "Testing the Effect of Code Documentation on Large Language Model Code Understanding", NAACL 2024 Findings, arXiv 2404.03114 | https://arxiv.org/abs/2404.03114 | 2024-04-03 | Incorrect documentation strongly hurts understanding; missing documentation does not | n/a | Yes (docstrings and comments) | No | D (indirect: removing comments costs little for understanding) | VERIFIED (abstract) |
| 22 | Ulfat, Sabit, Hossain, "Measuring LLM Trust Allocation Across Conflicting Software Artifacts" (TRACE), arXiv 2604.03447 | https://arxiv.org/abs/2604.03447 | 2026-04-03 (v2 2026-07-21) | Paired clean and perturbed Java bundles (documentation vs implementation faults); 22,339 responses | **Paired clean/perturbed** | Documentation | No SDT | Methodological cousin of B (paired design), not security | VERIFIED (abstract) |
| 23 | "Impact of Comments on LLM Comprehension of Legacy Code", arXiv 2506.11007 | https://arxiv.org/abs/2506.11007 | 2025-06 | Major comment inaccuracies degrade comprehension; minor ones do not | ? | Yes | ? | D (indirect) | UNVERIFIED (snippet) |
| 24 | "When Comments Mislead: An Empirical Study of Outdated Comments in LLM-Based Code Completion", doi 10.1145/3832783.3834359 | https://doi.org/10.1145/3832783.3834359 | 2026 | Outdated comments pull completions toward old code | ? | Yes | ? | Adjacent | UNVERIFIED (snippet) |

### 2.3 Pre-LLM adversarial robustness of neural code models (identifiers, dead code, comments)

| # | Citation | URL | Date | Notes | Status |
|---|---|---|---|---|---|
| 25 | Z. Yang, J. Shi, J. He, D. Lo, "Natural Attack for Pre-trained Models of Code" (ALERT), ICSE 2022, arXiv 2201.08698 | https://arxiv.org/abs/2201.08698 | 2022-01 | Naturalness-aware identifier substitution on CodeBERT and GraphCodeBERT. **Vulnerability prediction** is one of 3 tasks. No comments, no SDT. Background for A. | VERIFIED (abstract) |
| 26 | Yefet, Alon, Yahav, "Adversarial Examples for Models of Code" (DAMP), OOPSLA 2020, arXiv 1910.07517 | https://arxiv.org/abs/1910.07517 | 2019-10 | Variable renaming and dead-code attacks; one task is bug finding (VarMisuse). | UNVERIFIED (snippet) |
| 27 | Du et al., "An Extensive Study on Adversarial Attack against Pre-trained Models of Code", ESEC/FSE 2023, arXiv 2311.07553 | https://arxiv.org/abs/2311.07553 | 2023-11 | Compares 5 attacks (renaming, dead code) on CodeBERT-class models, including vulnerability detection. | UNVERIFIED (snippet) |
| 28 | Nguyen et al., "Adversarial Attacks on Code Models with Discriminative Graph Patterns" (GraphCodeAttack), arXiv 2308.11161 | https://arxiv.org/abs/2308.11161 | 2023-08 | Vulnerability prediction among the tasks. | UNVERIFIED (snippet) |
| 29 | Springer et al., STRATA, arXiv 2009.13562; Jha & Reddy, CodeAttack, AAAI 2023 | https://arxiv.org/abs/2009.13562 | 2020 / 2023 | Identifier and token attacks on code models (summarization). | UNVERIFIED (snippet) |
| 30 | "Towards Making Deep Learning-based Vulnerability Detectors Robust" (ZigZag), arXiv 2108.00669 | https://arxiv.org/abs/2108.00669 | 2021-08 | Pre-LLM robustness of DL vulnerability detectors. | UNVERIFIED (snippet) |

None of the pre-LLM works found uses persuasive natural-language comments, matched safe twins under attack, or SDT.

### 2.4 Paired vulnerable vs patched evaluation of LLM vulnerability detectors

| # | Citation | URL | Date | Paired? | FPR on patched code? | Manipulation? | Status |
|---|---|---|---|---|---|---|---|
| 31 | Ding et al., "Vulnerability Detection with Code Language Models: How Far Are We?" (PrimeVul), ICSE 2025, arXiv 2403.18624 | https://arxiv.org/abs/2403.18624 | 2024-03-27 | Yes (PrimeVul-Paired, 435 pairs) | Pair-wise metrics (details not re-read) | No | VERIFIED (abstract) |
| 32 | Y. Li et al., "Everything You Wanted to Know About LLM-based Vulnerability Detection But Were Afraid to Ask" (CORRECT), arXiv 2504.13474 | https://arxiv.org/abs/2504.13474 | 2025-04-18 | Yes (2,000 vulnerable/patched pairs) | Precision; false positives traced to reasoning errors | Context added, not adversarial | VERIFIED (abstract) |
| 33 | Huang et al., "Do Fine-Tuned LLMs Understand Vulnerabilities? An Investigation into the Semantic Trap" (TrapEval), arXiv 2601.22655 | https://arxiv.org/abs/2601.22655 | 2026-01-30 (v3 2026-05-21) | Yes (V2P vs V2N) | High false alarms on patched code | Semantics-preserving perturbations (renaming); no comments | VERIFIED (abstract) |
| 34 | Lu et al., "Evaluating and Enhancing the Vulnerability Reasoning Capabilities of LLMs" (DAGVul), arXiv 2602.06687 | https://arxiv.org/abs/2602.06687 | 2026-02-06 | Not stated | Not stated | 26 semantics-preserving transformations | VERIFIED (abstract) |
| 35 | Gao et al., "TREAT: A Code LLMs Trustworthiness / Reliability Evaluation and Testing Framework", arXiv 2510.17163 | https://arxiv.org/abs/2510.17163 | 2025-10-20 | A search snippet says PrimeVul-Paired with P-C/P-V metrics; not confirmed on the abstract page | Not confirmed | Code transformations | VERIFIED (abstract) / pairing UNVERIFIED |
| 36 | Dubniczky et al., "CASTLE: Benchmarking Dataset for Static Code Analyzers and LLMs towards CWE Detection", arXiv 2503.09433 | https://arxiv.org/abs/2503.09433 | 2025-03 | 250 micro-benchmarks; reports false positives | Yes (FPs counted) | No | UNVERIFIED (snippet) |
| 37 | Zhang & Beheshti, "Toward Better Assessment of LLMs' Performance in Clinical Error Detection", MLHC 2026, arXiv 2608.16643 | https://arxiv.org/abs/2608.16643 | 2026-08-17 | **Yes (clean counterpart for each erroneous note)**. 13/15 models below random pairwise discrimination; F1 and pairwise accuracy diverge. | Yes, bias patterns | No (clinical) | VERIFIED (abstract) |

VulDetectBench and SecVulEval were searched but no primary page was opened, so they are not assessed here.

### 2.5 Signal detection theory (d′, c, "criterion vs sensitivity") applied to LLMs

| # | Citation | URL | Date | What it does | Security or code? | Overlap with C | Status |
|---|---|---|---|---|---|---|---|
| 38 | Basta, Haghighi, Kaafar, Beheshti, "Correction or Manipulation? Measuring Epistemic Vigilance in LLM Agents Under User Pressure", arXiv 2610.36453 | https://arxiv.org/abs/2610.36453 | 2026-10-27 | Uses SDT to separate **discrimination** (correction vs manipulation) from **propensity to concede**. Citations made 5/7 models "readier to concede" (a criterion shift) and 4 models worse at discriminating (a sensitivity loss). Instructions mainly shift the criterion. | No (QA and customer-support agents) | **High.** It uses the same "manipulation → criterion shift and/or discrimination loss" framing, including a split by model. | VERIFIED (abstract) |
| 39 | Chen, Zhu, Zheng, Li, "Beyond Accuracy: How Procedural Traces Shift the Decision Criterion of LLM Overseers", arXiv 2609.18204 | https://arxiv.org/abs/2609.18204 | 2026-09-16 | SDT audit of 5 LLM overseers on 19 compliance tasks (4,551 judgments). Detailed traces shift the criterion toward rejection (false alarms); sensitivity stays high. It argues auditors should be judged on criterion and FAR, not accuracy. | No (compliance oversight) | **High** (context manipulation as a criterion shift in an LLM judge; "beyond accuracy" argument) | VERIFIED (abstract) |
| 40 | Dong, Hu, Yin, Chen, Liu, Chen, "Sensitivity or Criterion? Measuring and Moving When Language Models Act" (FlipAct), arXiv 2610.15415 | https://arxiv.org/abs/2610.15415 | 2026-10-11 | 2×2 matched question sets in which knowledge is fixed and the state flips (a matched-twin design). Fitted sensitivity (slope) and criterion (midpoint) across 44 models. Steering shifts the criterion without a sensitivity change. | No (agent tool use) | **Medium-high** (matched-flip design plus sensitivity/criterion split) | VERIFIED (abstract) |
| 41 | J.-P. Cacioli, "LLMs as Signal Detectors: Sensitivity, Bias, and the Temperature-Criterion Analogy", arXiv 2603.14893 | https://arxiv.org/abs/2603.14893 | 2026-03-16 | Pre-registered parametric SDT (unequal variance, z-ROC) over 168k trials. Temperature changes both sensitivity and criterion. | No (factual QA) | Medium (methodological template; warns that the equal-variance d′ assumption fails for LLMs) | VERIFIED (abstract) |
| 42 | "Do LLMs Know What They Know? Measuring Metacognitive Efficiency with Signal Detection Theory", arXiv 2603.25112 | https://arxiv.org/abs/2603.25112 | 2026-03 | Type-2 SDT (meta-d′) for confidence | No | Low | UNVERIFIED (snippet) |
| 43 | Usami et al., "LLM Judges Have Dark Current…", arXiv 2606.15610 | https://arxiv.org/abs/2606.15610 | 2026-06-14 | A search snippet claimed SDT framing for judges. **The abstract page does not use SDT.** Not relevant. | No | None | VERIFIED (abstract), excluded |

**No work was found that reports d′ or c (or an explicit sensitivity/criterion decomposition) for LLM vulnerability detectors or code reviewers under any manipulation.** Several targeted queries (listed at the end) returned nothing. #4 and #5 report the paired TPR/FPR data from which d′ and c could be computed, but neither does so.

### 2.6 Comment stripping and sanitization: evidence on its cost

| Source | What was measured | On benign or natural comments? | On both classes? |
|---|---|---|---|
| #1 Thornton | Stripping under the adversarial condition: detection 93.2% overall, "hurts" DeepSeek and Sonar, helps Opus and GPT-5.2 | **No** (computed against adversarial-condition misses only) | No (vulnerable only) |
| #2 ALIBI | Pre-detector LLM sanitizer, evasion < 3% | No cost measured | No |
| #3 Sun/Oprea/Wong | Regex stripping of comments plus preprocessor directives on **clean natural code**: TP rises 0.1–8.6%; FPR changes −6.6 to +1.8 pp; comments present in 57% of functions | **Yes (natural developer comments)** | **Yes, but unpaired** (500 benign functions, not stated to be patched twins); C/C++; stripping is confounded with preprocessor removal |
| #4 Alexopoulos et al. | Metadata redaction restores 16/17 | No benign cost | No |
| #10 Cloudflare | Recommended, not tested | n/a | n/a |
| #15 Nakibly & Babo | Prevalence of benign AI-directed hidden text (2/3 of findings) | Indirect | n/a |
| #21 Macke & Doyle | Missing documentation barely affects understanding | Indirect (not security) | n/a |

## 3. Revised novelty statement

### 3.1 What is no longer defensible (or never was)

1. **"Adversarial comments against LLM vulnerability detectors"** as a contribution.
   - Prior work: Flashboom (S&P 2025), Thornton (Feb 2026), Sun/Oprea/Wong (Jan 2026, comment carriers), Cloudflare (Apr 2026), Alexopoulos et al. (comments in the attack study, ICSE 2027), ALIBI (Jul 2026).
2. **Comment stripping or sanitization as a defense**, and the observation that stripping changes clean-code behaviour.
   - Thornton reports a stripping cost on weaker models.
   - Sun/Oprea/Wong measured stripping on natural-comment code for **both** TPR and FPR (unpaired, C/C++).
   - The previous audit's gap (b), "what does stripping cost on both classes", is therefore **largely pre-empted** in its general form.
   - Only a paired (safe-twin) Python version remains, and the pilot found **no** doc-condition effect (H3 not supported).
3. **Paired vulnerable/patched evaluation showing that manipulation moves TPR and FPR together** (an operating-point shift).
   - Alexopoulos et al. RQ1 (prompt framing, CrossVul pairs, TNR on patched code rises by up to 94.8 pp) and Words Speak Louder (PR metadata, PrimeVul pairs, "recall and FPR by a near-equal magnitude") both show this.
   - The *general* point that "detection rate alone misleads; with safe controls the attack mostly lowers false alarms" is already demonstrable from their tables.
4. **The SDT framing itself** (criterion shift vs discrimination loss under manipulation, judged beyond accuracy).
   - Correction or Manipulation (Oct 2026), Beyond Accuracy / LLM Overseers (Sep 2026), FlipAct (Oct 2026) and Cacioli (Mar 2026) already use it for LLMs, including the finding that a manipulation causes a criterion shift in some models and a discrimination loss in others.
   - v2 cannot present "threshold shift vs discrimination loss" as a new lens. It can only present it as *applied for the first time we know of* to code-security detection.
5. **Paired evaluation as a methodological correction for LLM detectors.**
   - Prior work: PrimeVul, TrapEval, CORRECT, SecLLMHolmes, and the clinical-error paper (#37), which argues the identical point in another domain.

### 3.2 What still appears defensibly new (phrase it as "to our knowledge")

The search found **no work** that combines all of the following:

- (i) **persuasive natural-language adversarial comments placed inside the code**;
- (ii) the **same comments applied to matched, minimally fixed safe twins**, so FPR under attack is measured per pair;
  - Thornton and ALIBI evaluate vulnerable code only.
  - Sun et al. apply optimized token strings to unpaired benign code and report only invariance of benign predictions.
  - Alexopoulos et al. and Words Speak Louder pair the code but manipulate the prompt or metadata, not comments.
- (iii) **d′ and c with confidence intervals** for LLM vulnerability detectors;
- (iv) a test of whether the effect type (criterion vs discrimination) **differs by model**, as an explicit way to reconcile Thornton's null result with the large effects in v1 and ALIBI.

So the "narrow gap" **survives, but it is narrower than stated on 2026-11-24**:

- Gap (a) survives as **channel-specific**: in-code comments with safe twins and SDT.
- Gap (b) is **mostly pre-empted** (Sun/Oprea/Wong). Keep it only as a paired-design replication.
- Gap (c) survives. One part of the reconciliation is already visible in the literature:
  - ALIBI and Sun et al. report **conditional** ASR over clean true positives;
  - Thornton reports ΔFNR over all samples;
  - so metric choice alone can produce "null" vs "> 90%" readings.
  - v2 should say this explicitly rather than claim it as a finding.

### 3.3 Recommended claim wording for v2

> "Prior work shows that adversarial code comments can suppress LLM vulnerability detection (Flashboom; Thornton; Sun et al.; ALIBI) and that prompt- or metadata-level framing moves both recall and false-positive rate on paired vulnerable/patched code (Alexopoulos et al.; Shahriar et al.). Signal-detection analyses of LLM decisions under manipulation exist outside security (Basta et al.; Chen et al.; Dong et al.; Cacioli). To our knowledge, no study has measured in-code comment attacks on matched safe twins and decomposed the effect into discrimination (d′) and criterion (c). We do this for [N models, N pairs], and we find [criterion shifts in weak models; a discrimination loss in the strongest model tested]."

Do **not** write "first", "novel attack", "new defense", or "we show that detection rate is misleading" without citing #4, #5 and #37.

### 3.4 Must-cite list for any v2 text

**Essential:**
- Thornton 2602.16741
- Wu & Nita-Rotaru, ALIBI 2607.24964
- Sun, Oprea & Wong 2602.00305
- Alexopoulos et al., ICSE 2027, 2603.18740
- Shahriar et al., S&P 2027, 2606.30587
- Li et al., Flashboom, S&P 2025
- Ullah et al., SecLLMHolmes, S&P 2024
- Ding et al., PrimeVul, ICSE 2025
- Basta et al. 2610.36453
- Chen et al. 2609.18204

**Strongly recommended:**
- Melo et al., SEVRA-Bench 2606.13757
- Bernstein et al., NDSS 2026
- Gong et al., AFCRA 2610.05399
- Lam et al., CodeCrash, NeurIPS 2025
- Huang et al., TrapEval 2601.22655
- Li et al., CORRECT 2504.13474
- Dong et al., FlipAct 2610.15415
- Cacioli 2603.14893 (also for the unequal-variance caveat on d′)
- Zhang & Beheshti 2608.16643
- Cloudflare Cloudforce One (2026)
- Mayraz / Legit Security (2025)

**Background:**
- Yang et al., ALERT (ICSE 2022)
- Yefet et al. (OOPSLA 2020)
- Du et al. (FSE 2023)
- Macke & Doyle (NAACL Findings 2024)
- Munir et al. 2610.05139
- Nakibly & Babo 2611.28763
- GitInject 2606.09935

Before citing any item marked UNVERIFIED, open its primary source.

### 3.5 Actions this audit suggests (none taken)

- **Optional reanalysis:**
  - compute d′ and c from Alexopoulos et al. Table II and the Words Speak Louder recall/FPR tables;
  - this would put the prompt and metadata channel on the same SDT scale as v2's comment channel;
  - it is a cheap, citable reconciliation step.
- **Python-only replication of Sun et al.'s stripping-cost finding:** with paired twins, describe it as a replication, not a new result.
- **Before submission:**
  - re-run this search: the area moves monthly (5 of the closest works appeared between Jun and Nov 2026);
  - hand-search the USENIX Security 2026, CCS 2026 and FSE/ASE 2026 proceedings, which were not browsed here.

## 4. Search queries used

1. adversarial comments LLM vulnerability detection misleading comments attack
2. prompt injection code comments AI code reviewer pull request bot attack arXiv
3. signal detection theory d-prime response bias LLM classifier evaluation
4. LLM vulnerability detection paired vulnerable patched false positive rate PrimeVul pairwise evaluation
5. SecLLMHolmes robustness trivial code augmentations variable rename comments LLM vulnerability
6. "comment" removal defense prompt injection code LLM detector cost benign comments
7. misleading code comments effect on LLM program understanding empirical study
8. adversarial attack pre-trained code models vulnerability detection identifier renaming dead code insertion CodeBERT robustness
9. LLM-as-judge signal detection theory sensitivity criterion bias shift manipulation
10. vulnerability detection LLM "d'" OR "d-prime" OR "signal detection" response bias code security
11. LLM vulnerability detector evaded by injected comment "safe" annotation benchmark 2025
12. CodeCrash misleading comments natural language perturbation code reasoning LLM robustness benchmark
13. LLM vulnerability detection robustness semantic-preserving transformations patched counterpart false positives benchmark 2025 2026
14. Flashboom blinding LLM-based code auditors IEEE S&P 2025
15. adversarial comments induce false positives LLM vulnerability detector safe code flagged vulnerable attack
16. signal detection theory sensitivity bias LLM sycophancy OR jailbreak OR "prompt injection" detection d-prime criterion 2025 2026 arXiv
17. effect of code comments on LLM vulnerability detection accuracy removing comments ablation
18. "signal detection" "large language model" code review OR vulnerability OR "security" sensitivity criterion d′ 2026
19. GitLab Duo remote prompt injection hidden comments source code 2025 Legit Security
20. adversarial robustness neural code comment generation summarization attack identifier ALERT MHM Yefet adversarial examples models of code
21. "misleading comments" OR "comment injection" vulnerability detection deep learning robustness 2023 2024 ICSE FSE ASE ISSTA
22. CASTLE benchmark LLM vulnerability detection; VulDetectBench; SecVulEval patched false positives
23. openreview LLM code security review adversarial comments safe twin paired benign false alarm 2026
24. github benchmark adversarial code comments LLM security reviewer vulnerable and fixed pairs dataset
25. comment sanitization defense code agents utility cost benign comments evaluation 2026 arXiv prompt injection source code

Primary pages opened directly (beyond search results): arXiv abs and HTML pages for 2602.16741, 2607.24964, 2602.00305, 2603.18740 (v1, v2, latest), 2606.30587, 2606.13757, 2610.05399, 2609.18204, 2610.15415, 2603.14893, 2606.15610, 2610.36453, 2608.16643, 2510.17163, 2504.13474, 2601.22655, 2602.06687, 2610.05139, 2604.03447, 2512.21250, 2606.09935, 2611.28763, 2312.12575, 2403.18624, 2201.08698, 2404.03114, 2504.14119; the NDSS 2026 FPA PDF; the Flashboom S&P 2025 PDF; the Cloudflare Cloudforce One report; the Legit Security GitLab Duo blog; and the SEVRA Hugging Face README.
