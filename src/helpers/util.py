from typing import Dict, List
import pandas as pd

def output_excel_data(path: str, data: List[Dict[str, str]]):
    df = pd.DataFrame(data)
    df.to_excel(path, index=False)
