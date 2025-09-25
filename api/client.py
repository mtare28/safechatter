import gradio as gr
import pandas as pd
import requests
import json
import random

from utils.constants import Constants

API_BASE_URL = "http://0.0.0.0:8081"
DEBERTA_PROCESS_URL = f"{API_BASE_URL}/deberta/process"
DEBERTA_RESET_URL = f"{API_BASE_URL}/deberta/reset"
MISTRAL_INVOKE_URL = f"{API_BASE_URL}/api/mistral/invoke"

INTENT_LABELS_GENERIC = sorted(list(set(Constants.DEBERTA_INTENT_MAPPING.values())))


def styled_message(text, role, flagged_list):
    """Create a styled chat bubble with hover tooltips for potential scam signals"""
    if role == "Sender":
        bubble_color = "#DCF8C6"  # Light green
        text_color = "#37474F"  # Blue gray
        justify = "flex-start"
        border_color = "#A8D8A8"  # Slightly darker green for border
        tooltip_bg = "#2D2D2D"  # Dark tooltip background
        tooltip_text = "#FFFFFF"  # White tooltip text
    else:
        bubble_color = "#34B7F1"  # Blue
        text_color = "#FFFFFF"  # White
        justify = "flex-end"
        border_color = "#2196F3"  # Slightly darker blue for border
        tooltip_bg = "#2D2D2D"  # Dark tooltip background
        tooltip_text = "#FFFFFF"  # White tooltip text

    # Configure tooltip content and status indicator based on flagged signals
    if flagged_list:
        tooltip_content = f"⚠️ Potential signals: {', '.join(flagged_list)}"
        status_indicator = "🔍"  # Small indicator that there's something to hover
    else:
        tooltip_content = "✅ No strong scam signals"
        status_indicator = "✅"

    # Generate unique ID for this specific message to avoid conflicts
    unique_id = f"bubble_{random.randint(10000, 99999)}"

    on_hover_js = f"""
        var bubble = document.getElementById('{unique_id}');
        var tooltip = document.getElementById('{unique_id}_tooltip');
        var container = document.getElementById('chat-container').children[0]; // The scrollable div
        
        var bubbleRect = bubble.getBoundingClientRect();
        var containerRect = container.getBoundingClientRect();
        
        var tooltipHeight = tooltip.offsetHeight > 0 ? tooltip.offsetHeight : 60;

        // Check if there's enough space above the bubble *within the container*
        if ((bubbleRect.top - containerRect.top) < tooltipHeight) {{
            // Not enough space, show tooltip below
            tooltip.style.bottom = 'auto';
            tooltip.style.top = '100%';
            tooltip.style.marginTop = '8px';
            tooltip.style.marginBottom = '0px';
            tooltip.querySelector('.arrow-down').style.display = 'none';
            tooltip.querySelector('.arrow-up').style.display = 'block';
        }} else {{
            // Enough space, show tooltip above (default)
            tooltip.style.top = 'auto';
            tooltip.style.bottom = '100%';
            tooltip.style.marginBottom = '8px';
            tooltip.style.marginTop = '0px';
            tooltip.querySelector('.arrow-up').style.display = 'none';
            tooltip.querySelector('.arrow-down').style.display = 'block';
        }}
        tooltip.style.opacity='1';
        tooltip.style.visibility='visible';
    """

    return f"""
    <div style='display:flex; justify-content:{justify}; margin:5px 0;'>
        <div id='{unique_id}' style='background-color:{bubble_color} !important; 
                    padding:10px 14px; border-radius:12px; max-width:70%; 
                    word-wrap:break-word; color:{text_color} !important; 
                    position:relative; cursor:pointer;
                    border: 2px solid {border_color}; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    transition: box-shadow 0.2s ease;'
             onmouseenter="{on_hover_js}"
             onmouseleave="document.getElementById('{unique_id}_tooltip').style.opacity='0'; document.getElementById('{unique_id}_tooltip').style.visibility='hidden';">

            <span style='color:{text_color} !important;'>{text}</span>
            <span style='font-size:10px; margin-left:5px; opacity:0.7;'>{status_indicator}</span>

            <!-- Custom hover tooltip with unique ID - Shows potential scam signals -->
            <div id='{unique_id}_tooltip' class='tooltip-top' style='position:absolute; bottom:100%; left:50%; transform:translateX(-50%);
                        background-color:{tooltip_bg}; color:{tooltip_text}; padding:8px 12px;
                        border-radius:6px; font-size:12px; 
                        opacity:0; visibility:hidden; transition:all 0.3s ease;
                        pointer-events:none; z-index:1000; margin-bottom:8px;
                        box-shadow:0 4px 12px rgba(0,0,0,0.3);
                        max-width:300px; min-width:120px; width:auto;
                        white-space:normal; word-wrap:break-word; text-align:center;'>
                {tooltip_content}
                <!-- Tooltip arrow for top position -->
                <div class='arrow-down' style='position:absolute; top:100%; left:50%; transform:translateX(-50%);
                            border:6px solid transparent; border-top-color:{tooltip_bg};'></div>
                <!-- Tooltip arrow for bottom position (hidden by default) -->
                <div class='arrow-up' style='position:absolute; bottom:100%; left:50%; transform:translateX(-50%);
                            border:6px solid transparent; border-bottom-color:{tooltip_bg}; display:none;'></div>
            </div>
        </div>
    </div>

    <style>
    #{unique_id}:hover {{
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }}
    </style>
    """


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 💬 Conversation Scam Detector")

    chat_state = gr.State([])
    history_state = gr.State([])  # For storing HTML chat bubbles

    with gr.Row():
        with gr.Column(scale=3):
            # Replace gr.Chatbot with gr.HTML for custom chat bubbles with hover tooltips
            chat_html = gr.HTML(label="Conversation", 
                                value="<div style='font-family:sans-serif;height: 400px; overflow-y: auto; border: 1px solid #E0E0E0; border-radius: 8px; padding: 10px;'></div>",
                elem_id="chat-container")
            reset_btn = gr.Button("🗑️ Reset Chat (new session)")
            sender_msg = gr.Textbox(placeholder="Sender message…", label="Sender", scale=1)
            receiver_msg = gr.Textbox(placeholder="Receiver message…", label="Receiver", scale=1)
        with gr.Column(scale=2):
            gr.Markdown("### 📊 Probabilities for Current Message")
            pred_time_label = gr.Markdown("⏱️ Prediction time: 0.00s")
            score_table = gr.Dataframe(headers=["Trait", "Score"],
                                       datatype=["str", "number"],
                                       interactive=False,
                                       value=pd.DataFrame({
                                           "Trait": INTENT_LABELS_GENERIC,
                                           "Score": [0.0] * len(INTENT_LABELS_GENERIC)}),
                                       wrap=True,
                                       max_height=300
                                       )
            gr.Markdown("### 🤖 LLM Inference (Session-Level)")
            freq_box = gr.Number(label="Frequency of Starter Message", value=0, precision=0)
            llm_out = gr.Dataframe(headers=['Verdict', 'Confidence Score', 'Traits'],
                                   datatype=["str", "number", 'str'],
                                   interactive=False, wrap=True
                                  , column_widths=["25px", "50px", "75px"])
            llm_btn = gr.Button("Run LLM Inference")


    def on_send(message: str, history: list, current_chat_state: list, role: str):
        """
        Called when a user sends a message. Makes a POST request to the /deberta/process endpoint.
        Implements hover tooltips showing potential scam signals.
        """
        if not message.strip():
            return history, pd.DataFrame(columns=["Trait",
                                                  "Score"]), current_chat_state, "", "⏱️ Prediction time: 0.00s", "<div style='font-family:sans-serif;'></div>"

        # Prepare the payload for the API
        payload = {
            "message": message,
            "role": role,
            "history": current_chat_state
        }

        try:
            response = requests.post(DEBERTA_PROCESS_URL, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()

            # Extract data from the response
            result_text = message  # Use the original message text instead of display_html
            scores = data["scores"]
            elapsed = data["inference_time"]
            updated_history = data["updated_history"]

            # Get flagged items for hover tooltip - extract from API response or simulate based on scores
            flagged = []
            threshold = 0.6  # Same threshold as original code for flagging potential signals

            # Check if API returns flagged information directly
            if "flagged" in data and data["flagged"]:
                flagged = data["flagged"]
            else:
                # Simulate flagging based on scores (matching original logic)
                if "scores" in data and isinstance(data["scores"], list):
                    for score_item in data["scores"]:
                        if isinstance(score_item, dict) and "Score" in score_item and "Label" in score_item:
                            if score_item["Label"].lower() != "genuinity" and score_item["Score"] >= threshold:
                                flagged.append(f"{score_item['Label']} ({score_item['Score']:.2f})")
                elif isinstance(scores, list):
                    # Alternative: work with the scores DataFrame format
                    for score_row in scores:
                        if isinstance(score_row, dict) and "Score" in score_row and "Label" in score_row:
                            if score_row["Label"].lower() != "genuinity" and score_row["Score"] >= threshold:
                                flagged.append(f"{score_row['Label']} ({score_row['Score']:.2f})")

            # Create styled message bubble with hover tooltip showing potential signals
            styled_text = styled_message(result_text, role, flagged)
            history = (history or []) + [styled_text]
            history_html = f"<div id='chat-scroll-area' style='font-family:sans-serif; height: 400px; overflow-y: auto; border: 1px solid #E0E0E0; border-radius: 8px; padding: 10px;'>{''.join(history)}</div>"

            df = pd.DataFrame(scores)
            df = df.rename(columns={'Label': 'Trait'})
            return history, df, updated_history, "", f"⏱️ Prediction time: {elapsed:.2f}s", history_html

        except requests.exceptions.RequestException as e:
            gr.Warning(f"API Error: Could not connect to the DeBERTa model. Details: {e}")
            return history, pd.DataFrame(columns=["Trait",
                                                  "Score"]), current_chat_state, message, "⏱️ API Error", "<div style='font-family:sans-serif;'>" + "".join(
                history or []) + "</div>"


    def on_reset():
        """
        Called when the reset button is clicked. Makes a POST request to the /deberta/reset endpoint.
        Resets both chat state and HTML display.
        """
        try:
            requests.post(DEBERTA_RESET_URL)
        except requests.exceptions.RequestException as e:
            gr.Warning(f"API Error: Could not reset conversation state on server. Details: {e}")

        # Reset the UI state - clear chat bubbles and tooltips
        empty_df = pd.DataFrame({"Trait": INTENT_LABELS_GENERIC, "Score": [0.0] * len(INTENT_LABELS_GENERIC)})
        empty_llm_df = pd.DataFrame([], columns=['Verdict', 'Confidence Score', 'Traits'])
        return [], [], empty_df, empty_llm_df, "<div id='chat-scroll-area' style='font-family:sans-serif; height: 400px; overflow-y: auto; border: 1px solid #E0E0E0; border-radius: 8px; padding: 10px;'></div>", 0


    def run_llm_inference(current_chat_state: list, freq: int):
        """
        Called when the LLM Inference button is clicked. Makes a POST request to the /api/mistral/invoke endpoint.
        """
        if not current_chat_state:
            return "Cannot run LLM on an empty conversation."

        # Format the conversation history into a single string
        conv_text = "\n".join([f"{m['role'].upper()}: '{m['text']}'" for m in current_chat_state])

        # Prepare the payload for the LangServe endpoint
        payload = {
            "input": {
                "conversation": conv_text,
                "frequency": freq
            }
        }

        try:
            response = requests.post(MISTRAL_INVOKE_URL, json=payload)
            response.raise_for_status()
            data = response.json()

            # The actual model output is inside the 'output' key for LangServe
            result = data.get('output', {})

            # Format the result for display in Markdown
            verdict = result.get('label', 'N/A')
            confidence = result.get('confidence', 0.0)
            tactics = ", ".join(result.get('tactics', [])) or "None"
            df = pd.DataFrame({'Verdict': [verdict], 'Confidence Score': [confidence], 'Traits': [tactics]})

            return df
        except requests.exceptions.RequestException as e:
            gr.Warning(f"❌ LLM call failed: {e}")
            return pd.DataFrame(columns=['Verdict', 'Confidence Score', 'Traits'])
        except (KeyError, json.JSONDecodeError) as e:
            gr.Warning(f"❌ Failed to parse LLM response: {e}\n\nRaw Response:\n{response.text}")
            return pd.DataFrame(columns=['Verdict', 'Confidence Score', 'Traits'])


    # Test function to demonstrate hover functionality with mock flagged signals
    def test_hover_demo():
        """Test function to show how hover tooltips work with potential signals"""
        test_messages = [
            ("Hello, want to make easy money?", "Sender",
             ["Financial gains opportunity (0.85)", "Sense of Urgency situation (0.72)"]),
            ("That sounds suspicious", "Receiver", []),
            ("Contact me on WhatsApp for details", "Sender", ["Channel shifting proposal (0.91)"]),
        ]

        demo_html = "<div style='font-family:sans-serif;'>"
        for text, role, flagged in test_messages:
            demo_html += styled_message(text, role, flagged)
        demo_html += "</div>"
        return demo_html


    # --- Connect UI Components to Functions ---
    sender_msg.submit(on_send, inputs=[sender_msg, history_state, chat_state, gr.State("Sender")],
                      outputs=[history_state, score_table, chat_state, sender_msg, pred_time_label, chat_html])
    receiver_msg.submit(on_send, inputs=[receiver_msg, history_state, chat_state, gr.State("Receiver")],
                        outputs=[history_state, score_table, chat_state, receiver_msg, pred_time_label, chat_html])
    reset_btn.click(on_reset, inputs=[], outputs=[history_state, chat_state, score_table, llm_out, chat_html, freq_box])
    llm_btn.click(run_llm_inference, inputs=[chat_state, freq_box], outputs=[llm_out])

if __name__ == "__main__":
    demo.launch(share=True)