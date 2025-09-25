class Constants:
    DEBERTA_INTENT_MAPPING = {
        "Wrong Number": "Misidentification",
        "Accidental Apology": "Misidentification",
        "Misidentification": "Misidentification",
        "Friendly Flattery": "Flattery",
        "Complimenting": "Flattery",
        "Personal Info Seeking": "Personal Info Seeking",
        "Investment Mention": "Financial Gains Opportunity",
        "Investment Offering": "Financial Gains Opportunity",
        "Financial Success Bragging": "Financial Gains Opportunity",
        "asking to switch to WhatsApp for private messaging": "Channel Shifting Proposal",
        "directly requesting to move the chat to Telegram app": "Channel Shifting Proposal",  
        "specifically suggesting to continue talking on Facebook Messenger": "Channel Shifting Proposal",
        "inviting to use WeChat or Line instead of current platform": "Channel Shifting Proposal",
        "proposing to download and use a different messaging platform": "Channel Shifting Proposal",
        "requesting a phone call to continue the conversation privately": "Channel Shifting Proposal",
        "asking for a video call instead of text messaging": "Channel Shifting Proposal",
        "suggesting to switch all communication to email": "Channel Shifting Proposal",
        "mentioning downloading other chat apps for better communication": "Channel Shifting Proposal",
        "Altruistic Manipulation": "Seeking Financial Support",
        "Verification Fee": "Seeking Financial Support",
        "Withdrawal Block": "Seeking Financial Support",
        "Urgent Deposit Request": "Seeking Financial Support",
        "Scarcity Pressure": "Sense of Urgency",
        "Benign": "Genuinity"
    }

    MISTRAL_PROMPT_TEMPLATE = """
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are an expert analyst specializing in the detection of multi-stage **conversational scams**.
    Your primary goal is to identify scams that unfold over several messages, starting with a seemingly innocent message (like a wrong number) and slowly building trust to manipulate the victim financially.
    
    **CRITICAL INSTRUCTIONS:**
    1.  **Focus ONLY on Conversational Scams:** A 'SCAM' verdict requires evidence of a back-and-forth conversation that follows one or more of the known scam tactics defined below.
    
        **Tactic Definitions:**
        - **wrong_number_intro:** The scammer initiates contact by pretending to have texted the wrong person. Examples: "Hi Jessica, is that you?" or "Sorry, I must have the wrong number."
        - **personal_information_seeking:** The scammer asks for personal details (name, job, location, age) to build a profile of the victim and personalize the scam.
        - **rapport_building:** The scammer engages in friendly, everyday conversation to create a false sense of connection and trust before introducing the scam.
        - **flattery_or_romance:** The scammer uses compliments, flattery, or expresses romantic interest to lower the victim's defenses and create an emotional dependency.
        - **financial_support:** The scammer fabricates a story of personal hardship or an emergency to guilt the victim into sending them money for help.
        - **financial_gain_opportunity:** The scammer introduces a fake investment opportunity, often involving cryptocurrency or forex, promising high, guaranteed, and risk-free returns.
        - **fee_pressure:** The scammer creates a reason why the victim must send money to unlock a larger prize or profit, such as a "verification fee," "tax payment," or "withdrawal deposit."
        - **channel_shifting_proposal:** The scammer suggests moving the conversation to a different platform like WhatsApp, Telegram, or Signal to evade SMS monitoring.

    2.  **IGNORE Single-Message Scams:** You MUST classify the following as 'BENIGN', as they are not your target:
        - Standard phishing attempts (e.g., "Your account is locked, click here").
        - Gambling or betting advertisements.
        - Unrealistic job offers or prize notifications ("You've won!").
        - Generic marketing messages.
    3.  **Use the Frequency Clue:** You will receive a `starter_message_frequency` value. A high number (e.g., > 100) is a strong signal that the first message is a bulk-sent scam opener. This should significantly increase your confidence in a 'SCAM' verdict if other tactics are present.
    
    Your response must be a JSON object that strictly follows this format:
    {format_instructions}
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    Analyze the following conversation and its metadata to determine if it is a conversational scam.
    
    **Metadata:**
    - Starter Message Frequency: {frequency}
    
    **Conversation:**
    {conversation}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """

