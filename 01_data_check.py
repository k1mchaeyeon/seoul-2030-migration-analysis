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

# 거주민 기준 연령별 취업자·고용률 원본 확인
resident_file = (
    "data/raw/resident_employment/"
    "kosis_시군구_연령별_취업자_고용률_2021_2024.xlsx"
)

resident_raw = pd.read_excel(resident_file)

print("\n[거주민 취업자·고용률 원본]")
print("데이터 크기:", resident_raw.shape)
print("컬럼:", resident_raw.columns.tolist())
print(resident_raw.head(10).to_string())