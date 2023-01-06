from app.utils.cleaned import Clean

c = Clean()

j = c.clean_skills("""1-3 years of working experience as a Data Analyst or in a similar position
Have development experience with Business Intelligence tools like Looker and/or Tableau
High proficiency in SQL and Excel
Microsoft Office suit (full professional proficiency)
Google Suite(full professional proficiency)
Strong knowledge of and experience with reporting packages
Knowledge of databases, system security and troubleshooting
Data management & interpretation
Logical Reasoning & sound conclusion
Power BI
Data analysis
Nice To Have
Bachelor’s Degree in CS, Statistics, Business, Economics, or related field
Experience in the Fintech or Banking industry
Benefits""")

print(j)