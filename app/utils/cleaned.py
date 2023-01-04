import re
from dataclasses import dataclass

import pytextrank
import spacy
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
from spacy.matcher import PhraseMatcher


@dataclass
class Clean:
    def clean_skills(self, raw_text: str):
        skills = []
        nlp = spacy.load("en_core_web_lg")
        skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)
        annotations = skill_extractor.annotate(raw_text)
        results = annotations.get("results")
        for result in results:
            matches = results.get(result)
            for match in matches:
                skills.append(match.get("doc_node_value"))
        return skills

    def clean_title(self, raw_title: str):
        text = raw_title.lower()
        patterns = re.compile(
            "([\(\[].*?[\)\]])|(remote)|(senior)|(junior)|(sr)|(jnr)|(snr)|(jr)|(intern)|(lead)|(jobs)|(job)|(internship)|(\sat\s.*)|(-.*)"
        )
        text = re.sub(patterns, "", text)

        nlp = spacy.load("en_core_web_lg")
        nlp.add_pipe("textrank")

        doc = nlp(text)
        ranks = [phrase.rank for phrase in doc._.phrases if phrase.count == 1]
        if ranks != []:
            max_rank = max(ranks)

            for phrase in doc._.phrases:
                if phrase.rank == max_rank:
                    return phrase.text
        return None

    # def to_excel(self, file_name: str, sheet_name: str):
    #     cleaned_data = self.get_cleaned_data()
    #     df = pd.DataFrame(cleaned_data)
    #     writer = pd.ExcelWriter(f'{file_name}.xlsx', engine='xlsxwriter')
    #     df.to_excel(writer, sheet_name=sheet_name, index=False)
    #     writer.save()