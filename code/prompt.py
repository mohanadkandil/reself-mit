#csv generation, only vary one phase
prompt = """ Given the definitions of each phase:
0. Situation Selection: Choosing to approach/avoid situations to regulate emotions.
1. Situation Modification: Changing environment to reduce emotional impact.
2. Attentional Deployment: Redirecting focus to influence emotions.
3. Cognitive Change: Reframing interpretation of a situation.
4. Response Modulation: Changing how emotions are expressed (e.g., hiding, drugs, relaxing).

Your task is to
2. generate 5 counterfactuals **for each individual phase** (5 total, in order of sentences passed in: Situation Selection, Situation Modification, Attentional Deployment, Cognitive Change, Response Modulation), by modifying only one of the five Gross model phases while keeping the other four phases unchanged.
Only generate adaptive counterfactuals.

Output format (for each unique (journal_id, which_phase), provide a dictionary):

Your output must follow this structure (JSON array of dictionaries):

[
  {
    "journal_id": 1,
    "which_phase": "situationSelection",
    "original_phase": "Staying at home is stressful and increases my anxiety.", //MUST NOT BE EMPTY, MUST MATCH SENTENCE IN orginal_phrases.
    "counterfactual": "I chose to attend a support group instead of staying home alone.",
  },
  {
    "journal_id": 1,
    "which_phase": "situationSelection",
    "original_phase": "...", //MUST NOT BE EMPTY
    "counterfactual": "...",

  },
  {
    "journal_id": 1,
    "which_phase": "situationSelection",
    "original_phase": "...", //MUST NOT BE EMPTY
    "counterfactual": "...",

  },
  {
    "journal_id": 1,
    "which_phase": "situationModification",
    "original_phase": "...", //MUST NOT BE EMPTY
    "counterfactual": "...",

  },
  ...
  // 25 entries total (5 phases × 5 variations)
]

⚠️ Requirements:
-NOTHING should be missing!!!
- Output only the JSON array.
- Do not include explanation, markdown, or extra commentary.
- All fields must be filled: no empty strings or missing keys.
- Use **double quotes** for all strings and keys.
"""