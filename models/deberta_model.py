import pandas as pd
from transformers import pipeline
import time

from utils.constants import Constants

INTENT_LABELS_GENERIC = sorted(list(set(Constants.DEBERTA_INTENT_MAPPING.values())))
MODEL_INTENT_LABELS = sorted(list(set(Constants.DEBERTA_INTENT_MAPPING.keys())))

class DebertaConversationAgent:
    def __init__(self, model_name: str = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0", threshold: float = 0.6, use_context: bool = True, context_window: int = 8):
        self.classifier = pipeline("zero-shot-classification", model=model_name)
        self.threshold = threshold
        self.use_context = use_context
        self.context_window = context_window
        self.chat = []
        self.last_scores_df = pd.DataFrame({"Label": INTENT_LABELS_GENERIC, "Score": [0.0] * len(INTENT_LABELS_GENERIC)})

    def reset(self):
        self.chat.clear()
        self.last_scores_df = pd.DataFrame({"Label": INTENT_LABELS_GENERIC, "Score": [0.0] * len(INTENT_LABELS_GENERIC)})

    def _build_context(self) -> str:
        history = self.chat[-self.context_window:]
        lines = [f"{m['role']}: {m['text']}" for m in history]
        return "\n".join(lines)

    def process_message(self, message: str, role: str):
        message = (message or "").strip()
        if not message:
            return "[empty message ignored]", self.last_scores_df, 0.0

        self.chat.append({"role": role, "text": message})
        
        text_for_model = self._build_context() if self.use_context else message
        
        start_time = time.time()

        
        result = self.classifier(text_for_model,
                                 candidate_labels=MODEL_INTENT_LABELS, 
                                 multi_label=True)
        
        elapsed = (time.time() - start_time)
        
        scores_map = {lab: sc for lab, sc in zip(result["labels"], result["scores"])}
        generic_scores = {}
        for fine, generic in Constants.DEBERTA_INTENT_MAPPING.items():
            score = scores_map.get(fine, 0.0)
            if generic not in generic_scores:
                generic_scores[generic] = score
            else:
                generic_scores[generic] = max(generic_scores[generic], score)
        
        df = pd.DataFrame({
            "Label": INTENT_LABELS_GENERIC,
            "Score": [float(f"{generic_scores.get(lab, 0.0):.3f}") for lab in INTENT_LABELS_GENERIC]
        }).sort_values(by=["Score"], ascending=False)
        self.last_scores_df = df

        flagged = [f"{row['Label']} ({row['Score']:.2f})" for index, row in df.iterrows() if row['Score'] > self.threshold and row['Label'] != 'Genuinity']
        
        
        if flagged:
            status = f"<br><span style='font-size:12px; color:yellow;'>⚠️ Potential signals: {', '.join(flagged)}</span>"
        else:
            status = "<br><span style='font-size:12px; color:greem;'>✅ No strong scam signals</span>"
        display = f"{message}{status}"
        return display, df, elapsed