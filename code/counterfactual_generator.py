import pandas as pd
import openai
from tqdm import tqdm
import json
import re
from utils import create_gpt_input, call_claude
from prompt import prompt


if __name__ == "__main__":
    pd.set_option('display.max_colwidth', None)

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    with open('mock_data_full_with_cfOutputs.json') as f:
        data = json.load(f)

    # If needed, normalize nested structures
    original_df = pd.json_normalize(data)
    for i in range(5):
        col = f'dailyReflection.text{i}'
        if col in original_df.columns:
            original_df[col] = original_df[col].astype(str).str.replace("'", "\\'", regex=False)

    df = create_gpt_input(original_df)
    api_key = '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'

    # Phase names must align with your columns (paraphrase_0, paraphrase_1, etc.)
    phase_names = [
        "situationSelection",
        "situationModification",
        "attentionalDeployment",
        "cognitiveChange",
        "responseModulation"
    ]

    results = []

    # Process every nth journal to save tokens
    n = 1
    for idx in tqdm(range(0, len(df), n)):
        row = df.iloc[idx]
        journal_id = row["journal_id"]

        # --- Construct prompt using paraphrases ---
        paraphrases = []
        for i, phase in enumerate(phase_names):
            value = row.get(f"paraphrase_{i}", "")
            if pd.notna(value) and str(value).strip() != "":
                paraphrases.append(f"{phase}: {value}")

        if not paraphrases:
            # Skip if there's no input
            continue

        user_input = "\n".join(paraphrases)
        full_prompt = f"{prompt}\n\nInput for the five phases:\n{user_input}"

        # --- Call Claude and parse response ---
        try:
            output = call_claude(full_prompt, api_key)
            print(output)

            try:
                parsed = json.loads(output)  # Expecting list of dicts
            except json.JSONDecodeError:
                # Try literal_eval fallback (Claude sometimes uses Python-style booleans)
                import ast
                parsed = ast.literal_eval(output.replace("true", "True").replace("false", "False"))

            for item in parsed:
                item["journal_id"] = journal_id
                results.append(item)

        except Exception as e:
            print(f"Error on journal_id={journal_id}: {e}")
            results.append({
                "journal_id": journal_id,
                "which_phase": None,
                "original_phase": None,
                "counterfactual": None,
                "error": str(e)
            })

    # --- Final DataFrame ---
    df_results = pd.DataFrame(results)
    print(df_results)

    phase_map = {
    'situationSelection': 0,
    'situationModification': 1,
    'attentionalDeployment': 2,
    'cognitiveChange': 3,
    'responseModulation': 4
    }

    columns_to_clear = [f"counterfactualResults.cfOutputs.stage{i}.generatedCfTexts" for i in range(5)]
    df_updated = original_df.copy()
    for col in columns_to_clear:
        if col in df_updated.columns:
            df_updated.drop(columns=col, inplace=True)

    for i in range(5):
        col = f"counterfactualResults.cfOutputs.stage{i}.generatedCfTexts"
        df_updated[col] = [[] for _ in range(len(df_updated))]

    for _, row in df_results.iterrows():
        try:
            journal_id = row['journal_id']
            phase = row['which_phase']
            cf_text = row['counterfactual']

            if pd.isna(phase) or pd.isna(cf_text):
                print(f"Skipping due to missing phase or cf_text: {phase}, {cf_text}")
                continue

            parts = journal_id.split('_')
            user_id = '_'.join(parts[:2])
            journal_id_part = '_'.join(parts[2:])

            match = df_updated[
                (df_updated['userId'] == user_id) &
                (df_updated['dailyReflection.journalId'] == journal_id_part)
            ]

            if match.empty:
                print(f"No match found for journal_id={journal_id}, user_id={user_id}, journal_part={journal_id_part}")
                continue

            stage_index = phase_map.get(phase)
            if stage_index is None:
                print(f"Unknown phase: {phase}")
                continue

            col_name = f"counterfactualResults.cfOutputs.stage{stage_index}.generatedCfTexts"
            match_index = match.index[0]

            if col_name not in df_updated.columns:
                print(f"Missing column {col_name}")
                continue

            try:
                df_updated.at[match_index, col_name].append(cf_text)
            except Exception as inner_e:
                print(f"Append failed for phase={phase}, text={cf_text}, journal_id={journal_id}: {inner_e}")

        except Exception as e:
            print(f"Error processing row:\n{row}\n{e}")

    #save updated df (with generated counterfactuals filled in)
    df_updated.to_csv('mock_data_full_with_cfOutputs.csv', index=False)