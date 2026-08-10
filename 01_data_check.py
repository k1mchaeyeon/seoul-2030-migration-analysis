import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "raw"

print("pandas 버전:", pd.__version__)
print("데이터 폴더:", DATA_DIR)

for file in DATA_DIR.rglob("*"):
    if file.is_file():
        print(file)

print("\n===== 파일별 데이터 구조 확인 =====")

for file in DATA_DIR.rglob("*"):
    if not file.is_file() or file.name == ".DS_Store":
        continue

    if file.suffix.lower() not in [".csv", ".txt", ".xlsx"]:
        continue

    print(f"\n[{file.name}]")

    try:
        if file.suffix.lower() == ".xlsx":
            df = pd.read_excel(file)
        else:
            try:
                df = pd.read_csv(file, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(file, encoding="cp949")

        print("행·열 개수:", df.shape)
        print("컬럼명:", df.columns.tolist())
        print(df.head(2))

    except Exception as error:
        print("읽기 실패:", error)