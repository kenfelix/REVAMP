import re

import pytextrank
import spacy

# example text
text = (
    """Graphic Designer / Travel Consultant at Eden Solutions and Resources""".lower()
)
patterns = re.compile(
    "([\(\[].*?[\)\]])|(remote)|(senior)|(junior)|(sr)|(jnr)|(snr)|(jr)|(intern)|(lead)|(jobs)|(job)|(internship)|(\sat\s.*)|(-.*)"
)
text = re.sub(patterns, "", text)

nlp = spacy.load("en_core_web_lg")
nlp.add_pipe("textrank")

doc = nlp(text)
ranks = [phrase.rank for phrase in doc._.phrases if phrase.count == 1]
max_rank = max(ranks)
print(max_rank)

for phrase in doc._.phrases:
    if phrase.rank == max_rank:
        print(phrase.text)
