======================================================================
               COUNTERFACTUAL GENERATION PIPELINE (README)
======================================================================

DESCRIPTION:

This script generates *adaptive counterfactuals* for user journal entries
based on the Gross model of emotion regulation. It takes structured input 
data, constructs prompts, sends them to the Claude API, parses responses, 
and stores the generated counterfactuals alongside the original data.

----------------------------------------------------------------------
INPUT:

- File: mock_data_full_with_cfOutputs.json
  A JSON file containing user journal data and five paraphrased sentences 
  for each of the five emotion regulation phases.

----------------------------------------------------------------------
PHASES (Gross Emotion Regulation Model):

Each journal entry includes paraphrases for the following five phases:

  0. situationSelection      
  1. situationModification    
  2. attentionalDeployment  
  3. cognitiveChange      
  4. responseModulation    

Paraphrased fields are expected as:
    paraphrase_0, paraphrase_1, ..., paraphrase_4 in input dataframe

----------------------------------------------------------------------
DEPENDENCIES:

Ensure the following Python packages are installed:

    pandas
    tqdm
    openai

Install via pip if needed.

Additional requirements:
- `utils.py`: should include `create_gpt_input()` and `call_claude()` functions.
- `prompt.py`: should define the string variable `prompt`.

----------------------------------------------------------------------
USAGE:

To run the script:
- make sure you have paraphrase_0, paraphrase_1, ..., paraphrase_4 in mock_data_full_with_cfOutputs.json
- all dependencies

----------------------------------------------------------------------
OUTPUT:

- File: mock_data_full_with_cfOutputs.csv
  This CSV includes the original journal data and new counterfactuals 
  saved under the following columns:

    counterfactualResults.cfOutputs.stage0.generatedCfTexts
    counterfactualResults.cfOutputs.stage1.generatedCfTexts
    counterfactualResults.cfOutputs.stage2.generatedCfTexts
    counterfactualResults.cfOutputs.stage3.generatedCfTexts
    counterfactualResults.cfOutputs.stage4.generatedCfTexts

Each list contains adaptive counterfactuals per phase.

----------------------------------------------------------------------
API KEY:

The Claude API key is currently hardcoded:
    
    api_key = 'sk-ant-api03-...'

Replace this with your own key.
