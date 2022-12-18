from dataclasses import dataclass
import spacy
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
# import pandas as pd

@dataclass
class Clean:
    
    def clean_skills(self, raw_text: str):
        nlp = spacy.load("en_core_web_lg")
        skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)
        annotations = skill_extractor.annotate(raw_text).get("results")
        return annotations
    
    def clean_title(self, raw_title: str):
        return raw_title
    
    # def to_excel(self, file_name: str, sheet_name: str):
    #     cleaned_data = self.get_cleaned_data()
    #     df = pd.DataFrame(cleaned_data)
    #     writer = pd.ExcelWriter(f'{file_name}.xlsx', engine='xlsxwriter')
    #     df.to_excel(writer, sheet_name=sheet_name, index=False)
    #     writer.save()