import pandas as pd
import re 
def read_custom_vocabulary(file_path):
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)

        if "Custom vocabulary" in df.columns:
            # Extract values from the "custom vocabulary" column
            custom_vocabulary = df["Custom vocabulary"].tolist()

            # Normalize and filter the list
            normalized_list = []
            for item in custom_vocabulary:
                # Normalize by removing all punctuation except apostrophes
                normalized_item = re.sub(r'[^\w\s\']', '', str(item))
                # Filter out items with 7 or more words
                words = normalized_item.split()
                if len(words) < 7:
                    normalized_list.append(normalized_item)

            return normalized_list
        else:
            print("Error: 'custom vocabulary' column not found.")
            return None

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None