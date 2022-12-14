from dataclasses import dataclass
from typing import List
import pandas as pd

@dataclass
class Clean:
    scraped_data: List[dict]
    
    def get_cleaned_data(self):
        
        unique = []
        if self.scraped_data is None:
            raise "Scraped data must be a list if dictionary"
        
        for data in self.scraped_data:
            if len(data.get("required skills")) < 3:
                self.scraped_data.remove(data)
            
            if data in unique:
                continue
            else:
                unique.append(data)
        
        return unique
    
    def to_excel(self, file_name: str, sheet_name: str):
        cleaned_data = self.get_cleaned_data()
        df = pd.DataFrame(cleaned_data)
        writer = pd.ExcelWriter(f'{file_name}.xlsx', engine='xlsxwriter')
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()