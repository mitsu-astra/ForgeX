"""
Example ZIP Handler for Mixed Content (Images + CSVs)
This demonstrates how to handle ZIP files containing both images and CSV data
"""

import zipfile
import io
from pathlib import Path
from typing import Dict, List, Tuple
from fastapi import UploadFile
import pandas as pd

class MixedZIPHandler:
    """
    Handles ZIP files containing:
    - Images (PNG, JPG) → Inspection data
    - CSV files → Production/Economic data
    """

    def __init__(self):
        self.allowed_image_extensions = {'.png', '.jpg', '.jpeg'}
        self.allowed_csv_extensions = {'.csv'}
        self.max_image_size = 50 * 1024 * 1024  # 50MB
        self.max_csv_size = 20 * 1024 * 1024    # 20MB

    async def extract_and_categorize(self,
                                     zip_file: UploadFile,
                                     output_dir: Path) -> Dict:
        """
        Extract ZIP and categorize files by type

        Returns:
        {
            'images': [
                {'filename': 'img1.png', 'path': '/path/to/img1.png', 'size': 12345},
                ...
            ],
            'production_csvs': [
                {'filename': 'model_1.csv', 'path': '/path/to/model_1.csv',
                 'model_type': 'model_1', 'rows': 3000},
                ...
            ],
            'economic_csvs': [
                {'filename': 'costs.csv', 'path': '/path/to/costs.csv', 'rows': 1},
                ...
            ],
            'skipped': [
                {'filename': 'readme.txt', 'reason': 'unsupported_type'},
                ...
            ]
        }
        """
        result = {
            'images': [],
            'production_csvs': [],
            'economic_csvs': [],
            'skipped': []
        }

        # Read ZIP file
        zip_content = await zip_file.read()

        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_ref:
            for file_info in zip_ref.filelist:
                # Skip directories
                if file_info.is_dir():
                    continue

                filename = Path(file_info.filename).name
                extension = Path(filename).suffix.lower()
                file_size = file_info.file_size

                # Skip hidden files and __MACOSX
                if filename.startswith('.') or '__MACOSX' in file_info.filename:
                    continue

                # === HANDLE IMAGES ===
                if extension in self.allowed_image_extensions:
                    if file_size > self.max_image_size:
                        result['skipped'].append({
                            'filename': filename,
                            'reason': 'image_too_large',
                            'size': file_size
                        })
                        continue

                    # Extract image
                    image_path = output_dir / 'images' / filename
                    image_path.parent.mkdir(parents=True, exist_ok=True)

                    with zip_ref.open(file_info) as source:
                        image_path.write_bytes(source.read())

                    result['images'].append({
                        'filename': filename,
                        'path': str(image_path),
                        'size': file_size
                    })

                # === HANDLE CSVs ===
                elif extension in self.allowed_csv_extensions:
                    if file_size > self.max_csv_size:
                        result['skipped'].append({
                            'filename': filename,
                            'reason': 'csv_too_large',
                            'size': file_size
                        })
                        continue

                    # Extract CSV
                    csv_path = output_dir / 'csv' / filename
                    csv_path.parent.mkdir(parents=True, exist_ok=True)

                    with zip_ref.open(file_info) as source:
                        csv_path.write_bytes(source.read())

                    # Detect CSV type
                    csv_type, model_type = self._detect_csv_type(csv_path)

                    if csv_type == 'production':
                        df = pd.read_csv(csv_path)
                        result['production_csvs'].append({
                            'filename': filename,
                            'path': str(csv_path),
                            'model_type': model_type,
                            'rows': len(df),
                            'columns': len(df.columns)
                        })
                    elif csv_type == 'economic':
                        df = pd.read_csv(csv_path)
                        result['economic_csvs'].append({
                            'filename': filename,
                            'path': str(csv_path),
                            'rows': len(df),
                            'columns': len(df.columns)
                        })
                    else:
                        result['skipped'].append({
                            'filename': filename,
                            'reason': 'unknown_csv_format'
                        })

                # === SKIP OTHER FILES ===
                else:
                    result['skipped'].append({
                        'filename': filename,
                        'reason': 'unsupported_extension',
                        'extension': extension
                    })

        return result

    def _detect_csv_type(self, csv_path: Path) -> Tuple[str, str]:
        """
        Detect if CSV is production data (Model 1/2/3) or economic data

        Returns: (csv_type, model_type)
        - csv_type: 'production', 'economic', or 'unknown'
        - model_type: 'model_1', 'model_2', 'model_3', or None
        """
        try:
            # Read just the header
            df = pd.read_csv(csv_path, nrows=0)
            columns = df.columns.tolist()
            num_columns = len(columns)

            # Check for Model 1 (10 columns)
            if num_columns == 10:
                model_1_keys = ['Demand', 'Total parts', 'Drilling Util', 'Milling Util']
                if all(key in columns for key in model_1_keys):
                    return ('production', 'model_1')

            # Check for Model 2 (16 columns)
            elif num_columns == 16 or num_columns == 17:
                model_2_keys = ['Demand', 'Entities In Part 1', 'Drilling Utilization']
                if all(key in columns for key in model_2_keys):
                    return ('production', 'model_2')

            # Check for Model 3 (77 columns)
            elif num_columns >= 70:
                model_3_keys = ['Time_Now', 'Blanking_Util', 'Press1_Util', 'Cell1_Util']
                if all(key in columns for key in model_3_keys):
                    return ('production', 'model_3')

            # Check for Economic data
            economic_keys = ['scrap_cost', 'rework_cost', 'contribution_margin']
            if any(key.lower() in [col.lower() for col in columns] for key in economic_keys):
                return ('economic', None)

            return ('unknown', None)

        except Exception as e:
            print(f"Error detecting CSV type: {e}")
            return ('unknown', None)


# ============ EXAMPLE USAGE ============

"""
Example ZIP structure that this handler supports:

batch_inspection_data.zip
  ├── images/
  │   ├── product_001.png
  │   ├── product_002.png
  │   └── product_003.png
  ├── production_data/
  │   ├── model_1_data.csv       # Auto-detected as Model 1
  │   └── model_3_data.csv       # Auto-detected as Model 3
  ├── economic_data.csv          # Auto-detected as economic
  ├── readme.txt                 # Skipped
  └── .DS_Store                  # Skipped

OR flat structure:

batch_data.zip
  ├── img1.png
  ├── img2.png
  ├── img3.png
  ├── process_data.csv           # Auto-detected
  └── costs.csv                  # Auto-detected

Result:
{
  "images": [
    {"filename": "product_001.png", "path": "/uploads/batch_123/images/product_001.png", "size": 125000},
    {"filename": "product_002.png", "path": "/uploads/batch_123/images/product_002.png", "size": 130000},
    {"filename": "product_003.png", "path": "/uploads/batch_123/images/product_003.png", "size": 128000}
  ],
  "production_csvs": [
    {
      "filename": "model_1_data.csv",
      "path": "/uploads/batch_123/csv/model_1_data.csv",
      "model_type": "model_1",
      "rows": 3000,
      "columns": 10
    },
    {
      "filename": "model_3_data.csv",
      "path": "/uploads/batch_123/csv/model_3_data.csv",
      "model_type": "model_3",
      "rows": 605620,
      "columns": 77
    }
  ],
  "economic_csvs": [
    {
      "filename": "economic_data.csv",
      "path": "/uploads/batch_123/csv/economic_data.csv",
      "rows": 1,
      "columns": 8
    }
  ],
  "skipped": [
    {"filename": "readme.txt", "reason": "unsupported_extension", "extension": ".txt"},
    {"filename": ".DS_Store", "reason": "hidden_file"}
  ]
}
"""
