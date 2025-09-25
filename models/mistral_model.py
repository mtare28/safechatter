from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_ollama import OllamaLLM

from io_models.mistral_nemo import ConversationInput, ConversationalScamVerdict
from utils.constants import Constants

class MistralConversationAgent:
    def __init__(self):
        model = 'mistral-nemo:12b'
        self.llm = OllamaLLM(model=model
                    , num_gpu=99
                    , num_ctx=4096)
        self.output_parser = JsonOutputParser(pydantic_object=ConversationalScamVerdict)
        self.prompt = PromptTemplate(
            template= Constants.MISTRAL_PROMPT_TEMPLATE, 
            input_variables=["conversation", "frequency"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
    def inference_mistral(self):
        chain = self.prompt | self.llm| self.output_parser
        return chain.with_types(input_type=ConversationInput)