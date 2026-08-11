import pandas as pd
from pathlib import Path


# 1. 폴더 경로 설정

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# processed 폴더가 없으면 새로 만들기
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# 2. 전월세 데이터 전처리

print("\n전월세 데이터 정리 중...")

rent_dir = RAW_DIR / "rent"
rent_files = sorted(rent_dir.glob("*"))
rent_list = []

for file in rent_files:
    if file.suffix.lower() not in [".csv", ".txt"]:
        continue

    print("불러오는 중:", file.name)

    try:
        rent_data = pd.read_csv(
            file,
            encoding="utf-8",
            low_memory=False
        )
    except UnicodeDecodeError:
        rent_data = pd.read_csv(
            file,
            encoding="cp949",
            low_memory=False
        )

    # 분석에 필요한 열만 선택
    rent_data = rent_data[
        [
            "접수년도",
            "자치구명",
            "전월세구분",
            "임대면적",
            "보증금(만원)",
            "임대료(만원)",
            "건물용도"
        ]
    ].copy()

    rent_list.append(rent_data)

if len(rent_list) == 0:
    raise FileNotFoundError("data/raw/rent 폴더에서 전월세 파일을 찾지 못했습니다.")

# 2021~2024년 파일 합치기
rent = pd.concat(rent_list, ignore_index=True)

print("합친 데이터 크기:", rent.shape)

# 숫자로 사용할 열 변환
number_columns = [
    "접수년도",
    "임대면적",
    "보증금(만원)",
    "임대료(만원)"
]

for column in number_columns:
    rent[column] = pd.to_numeric(rent[column], errors="coerce")

# 필요한 정보가 없는 행 제거
rent = rent.dropna(
    subset=["접수년도", "자치구명", "전월세구분"]
).copy()

# 2021~2024년만 선택
rent = rent[rent["접수년도"].between(2021, 2024)].copy()
rent["접수년도"] = rent["접수년도"].astype(int)

# 글자 앞뒤 공백 제거
rent["자치구명"] = rent["자치구명"].astype(str).str.strip()
rent["전월세구분"] = rent["전월세구분"].astype(str).str.strip()

# 전세와 월세만 남기기
rent = rent[rent["전월세구분"].isin(["전세", "월세"])].copy()

# 금액이 음수인 잘못된 행 제외
rent = rent[
    (rent["보증금(만원)"].isna()) |
    (rent["보증금(만원)"] >= 0)
].copy()

rent = rent[
    (rent["임대료(만원)"].isna()) |
    (rent["임대료(만원)"] >= 0)
].copy()

# 전세와 월세를 따로 집계
# 일부 고가 계약의 영향을 줄이기 위해 평균보다 중앙값을 사용
jeonse = rent[rent["전월세구분"] == "전세"].copy()
monthly = rent[rent["전월세구분"] == "월세"].copy()

jeonse_summary = (
    jeonse
    .groupby(["접수년도", "자치구명"], as_index=False)
    .agg(
        전세거래건수=("자치구명", "size"),
        전세보증금중앙값_만원=("보증금(만원)", "median"),
        전세임대면적중앙값=("임대면적", "median")
    )
)

monthly_summary = (
    monthly
    .groupby(["접수년도", "자치구명"], as_index=False)
    .agg(
        월세거래건수=("자치구명", "size"),
        월세보증금중앙값_만원=("보증금(만원)", "median"),
        월세중앙값_만원=("임대료(만원)", "median"),
        월세임대면적중앙값=("임대면적", "median")
    )
)

# 전세와 월세 결과 합치기
rent_summary = pd.merge(
    jeonse_summary,
    monthly_summary,
    on=["접수년도", "자치구명"],
    how="outer"
)

rent_summary = rent_summary.rename(columns={"접수년도": "연도"})

rent_summary = rent_summary.sort_values(
    ["연도", "자치구명"]
).reset_index(drop=True)

# 중앙값 소수점 한 자리까지 표시
rent_round_columns = [
    "전세보증금중앙값_만원",
    "전세임대면적중앙값",
    "월세보증금중앙값_만원",
    "월세중앙값_만원",
    "월세임대면적중앙값"
]

rent_summary[rent_round_columns] = (
    rent_summary[rent_round_columns].round(1)
)

rent_save_path = PROCESSED_DIR / "rent_summary_2021_2024.csv"
rent_summary.to_csv(
    rent_save_path,
    index=False,
    encoding="utf-8-sig"
)

print("전월세 전처리 완료")
print("저장 위치:", rent_save_path)
print("결과 크기:", rent_summary.shape)
print(rent_summary.head())


# 3. 청년 인구 데이터 전처리

print("\n청년 인구 데이터 정리 중...")

population_dir = RAW_DIR / "population"
population_files = list(population_dir.glob("*.xlsx"))

if len(population_files) == 0:
    raise FileNotFoundError("data/raw/population 폴더에서 엑셀 파일을 찾지 못했습니다.")

population = pd.read_excel(population_files[0])

# 첫 번째 데이터 행에는 각 열의 연령대가 적혀 있음
age_row = population.iloc[0]

# 서울특별시 전체 행과 연령대 설명 행을 빼고 25개 자치구만 선택
population = population.iloc[2:].copy()
population = population[population["항목"] == "총인구수 (명)"].copy()

population["행정구역(동읍면)별"] = (
    population["행정구역(동읍면)별"]
    .astype(str)
    .str.strip()
)

population_list = []

for year in range(2021, 2025):
    year_columns = [
        column for column in population.columns
        if str(column).startswith(f"{year}.12")
    ]

    # 같은 연도의 열 중에서 20대와 30대 열을 따로 찾기
    age_20_columns = [
        column for column in year_columns
        if age_row[column] in ["20 - 24세", "25 - 29세"]
    ]

    age_30_columns = [
        column for column in year_columns
        if age_row[column] in ["30 - 34세", "35 - 39세"]
    ]

    if len(age_20_columns) != 2 or len(age_30_columns) != 2:
        raise ValueError(f"{year}년의 20대 또는 30대 인구 열을 정확히 찾지 못했습니다.")

    temp = population[["행정구역(동읍면)별"] + year_columns].copy()

    for column in year_columns:
        temp[column] = pd.to_numeric(temp[column], errors="coerce")

    temp["20대인구"] = temp[age_20_columns].sum(axis=1)
    temp["30대인구"] = temp[age_30_columns].sum(axis=1)
    temp["청년인구"] = temp["20대인구"] + temp["30대인구"]
    temp["연도"] = year

    temp = temp[
        [
            "연도",
            "행정구역(동읍면)별",
            "20대인구",
            "30대인구",
            "청년인구"
        ]
    ]

    population_list.append(temp)

population_summary = pd.concat(population_list, ignore_index=True)

population_summary = population_summary.rename(
    columns={"행정구역(동읍면)별": "자치구명"}
)

population_summary[["20대인구", "30대인구", "청년인구"]] = (
    population_summary[["20대인구", "30대인구", "청년인구"]]
    .fillna(0)
    .astype(int)
)

population_summary = population_summary.sort_values(
    ["연도", "자치구명"]
).reset_index(drop=True)

population_save_path = PROCESSED_DIR / "youth_population_2021_2024.csv"
population_summary.to_csv(
    population_save_path,
    index=False,
    encoding="utf-8-sig"
)

print("청년 인구 전처리 완료")
print("저장 위치:", population_save_path)
print("결과 크기:", population_summary.shape)
print(population_summary.head())


# 4. 청년 순이동 데이터 전처리

print("\n청년 순이동 데이터 정리 중...")

migration_dir = RAW_DIR / "migration"
migration_files = list(migration_dir.glob("*.xlsx"))

if len(migration_files) == 0:
    raise FileNotFoundError("data/raw/migration 폴더에서 엑셀 파일을 찾지 못했습니다.")

migration = pd.read_excel(migration_files[0])

# 서울특별시 전체 행은 빼고 25개 자치구만 사용
migration = migration[
    migration["행정구역(시군구)별"] != "서울특별시"
].copy()

migration["행정구역(시군구)별"] = (
    migration["행정구역(시군구)별"]
    .astype(str)
    .str.strip()
)

# 원본 파일 자체가 순이동자 수 통계이므로 인구 증감으로 다시 계산하지 않음
# 20~24세와 25~29세를 20대로, 30~34세와 35~39세를 30대로 묶음
migration["연령구분"] = migration["연령별"].map(
    {
        "20 - 24세": "20대순이동자수",
        "25 - 29세": "20대순이동자수",
        "30 - 34세": "30대순이동자수",
        "35 - 39세": "30대순이동자수"
    }
)

migration = migration.dropna(subset=["연령구분"]).copy()

year_columns = ["2021", "2022", "2023", "2024"]

for column in year_columns:
    migration[column] = pd.to_numeric(
        migration[column],
        errors="coerce"
    ).fillna(0)

# 연령대별 값을 합치기
migration_summary = (
    migration
    .groupby(
        ["행정구역(시군구)별", "연령구분"],
        as_index=False
    )[year_columns]
    .sum()
)

# 연도 열을 행으로 바꾸기
migration_summary = migration_summary.melt(
    id_vars=["행정구역(시군구)별", "연령구분"],
    value_vars=year_columns,
    var_name="연도",
    value_name="순이동자수"
)

# 20대와 30대를 각각 열로 펼치기
migration_summary = migration_summary.pivot_table(
    index=["연도", "행정구역(시군구)별"],
    columns="연령구분",
    values="순이동자수",
    aggfunc="sum"
).reset_index()

migration_summary.columns.name = None

migration_summary = migration_summary.rename(
    columns={"행정구역(시군구)별": "자치구명"}
)

migration_summary["연도"] = migration_summary["연도"].astype(int)

migration_summary["청년순이동자수"] = (
    migration_summary["20대순이동자수"]
    + migration_summary["30대순이동자수"]
)

migration_number_columns = [
    "20대순이동자수",
    "30대순이동자수",
    "청년순이동자수"
]

migration_summary[migration_number_columns] = (
    migration_summary[migration_number_columns]
    .fillna(0)
    .astype(int)
)

migration_summary = migration_summary[
    [
        "연도",
        "자치구명",
        "20대순이동자수",
        "30대순이동자수",
        "청년순이동자수"
    ]
].sort_values(["연도", "자치구명"]).reset_index(drop=True)

migration_save_path = PROCESSED_DIR / "youth_migration_2021_2024.csv"
migration_summary.to_csv(
    migration_save_path,
    index=False,
    encoding="utf-8-sig"
)

print("청년 순이동 전처리 완료")
print("저장 위치:", migration_save_path)
print("결과 크기:", migration_summary.shape)
print(migration_summary.head())


# 5. 사업체 종사자 데이터 전처리

print("\n사업체 종사자 데이터 정리 중...")

employment_dir = RAW_DIR / "employment"
employment_files = sorted(employment_dir.glob("*"))

# 행정동 코드 앞 4자리와 자치구 연결
district_code = {
    "1101": "종로구",
    "1102": "중구",
    "1103": "용산구",
    "1104": "성동구",
    "1105": "광진구",
    "1106": "동대문구",
    "1107": "중랑구",
    "1108": "성북구",
    "1109": "강북구",
    "1110": "도봉구",
    "1111": "노원구",
    "1112": "은평구",
    "1113": "서대문구",
    "1114": "마포구",
    "1115": "양천구",
    "1116": "강서구",
    "1117": "구로구",
    "1118": "금천구",
    "1119": "영등포구",
    "1120": "동작구",
    "1121": "관악구",
    "1122": "서초구",
    "1123": "강남구",
    "1124": "송파구",
    "1125": "강동구"
}

employment_list = []

for file in employment_files:
    if file.suffix.lower() not in [".csv", ".txt"]:
        continue

    # 파일명에서 연도 찾기
    year = None

    for y in range(2021, 2025):
        if str(y) in file.name:
            year = y
            break

    if year is None:
        continue

    print("불러오는 중:", file.name)

    try:
        employment = pd.read_csv(
            file,
            encoding="utf-8",
            low_memory=False
        )
    except UnicodeDecodeError:
        employment = pd.read_csv(
            file,
            encoding="cp949",
            low_memory=False
        )

    # 2021년과 2022~2024년의 종사자 수 열 이름이 다름
    if year == 2021:
        worker_column = "WOKE_SUM"
    else:
        worker_column = "SURV_PHS_WOKE_SUM"

    needed_columns = ["AD_CD", worker_column]

    for column in needed_columns:
        if column not in employment.columns:
            raise KeyError(f"{file.name}에서 {column} 열을 찾지 못했습니다.")

    temp = employment[needed_columns].copy()

    # 행정동 코드의 앞 4자리를 자치구 코드로 사용
    temp["자치구코드"] = (
        temp["AD_CD"]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str[:4]
    )

    temp["자치구명"] = temp["자치구코드"].map(district_code)

    temp["종사자수"] = pd.to_numeric(
        temp[worker_column],
        errors="coerce"
    )

    temp = temp.dropna(subset=["자치구명", "종사자수"]).copy()

    # 자치구별 종사자 수 합계
    temp = (
        temp
        .groupby("자치구명", as_index=False)["종사자수"]
        .sum()
    )

    temp["연도"] = year
    temp = temp[["연도", "자치구명", "종사자수"]]

    employment_list.append(temp)

if len(employment_list) == 0:
    raise FileNotFoundError("data/raw/employment 폴더에서 사업체 파일을 찾지 못했습니다.")

employment_summary = pd.concat(employment_list, ignore_index=True)
employment_summary["종사자수"] = employment_summary["종사자수"].astype(int)

employment_summary = employment_summary.sort_values(
    ["연도", "자치구명"]
).reset_index(drop=True)

employment_save_path = PROCESSED_DIR / "employment_2021_2024.csv"
employment_summary.to_csv(
    employment_save_path,
    index=False,
    encoding="utf-8-sig"
)

print("사업체 종사자 전처리 완료")
print("저장 위치:", employment_save_path)
print("결과 크기:", employment_summary.shape)
print(employment_summary.head())

# 종사자 수는 실제 일자리 수와 완전히 같은 값이 아니라
# 자치구별 일자리 규모를 간접적으로 보여주는 대리 지표로 사용함


# 6. 네 가지 데이터 합치기

print("\n데이터 합치는 중...")

final_data = pd.merge(
    population_summary,
    migration_summary,
    on=["연도", "자치구명"],
    how="outer"
)

final_data = pd.merge(
    final_data,
    rent_summary,
    on=["연도", "자치구명"],
    how="outer"
)

final_data = pd.merge(
    final_data,
    employment_summary,
    on=["연도", "자치구명"],
    how="outer"
)

final_data = final_data.sort_values(
    ["연도", "자치구명"]
).reset_index(drop=True)

# 공식 순이동률 산식의 분모를 확인하기 전이므로
# 이 파일에서는 순이동률을 임의로 계산하지 않음

final_save_path = PROCESSED_DIR / "seoul_youth_final_2021_2024.csv"
final_data.to_csv(
    final_save_path,
    index=False,
    encoding="utf-8-sig"
)


# 7. 결과 확인

print("\n모든 데이터 정리가 끝났습니다.")
print("저장 위치:", final_save_path)
print("최종 데이터 크기:", final_data.shape)

print("\n연도별 자치구 개수")
print(final_data.groupby("연도")["자치구명"].nunique())

print("\n중복된 연도·자치구 행 개수")
print(final_data.duplicated(["연도", "자치구명"]).sum())

print("\n열별 결측치 개수")
print(final_data.isna().sum())

print("\n최종 데이터 미리보기")
print(final_data.head(10))

if len(final_data) == 100:
    print("\n4개 연도, 25개 자치구가 모두 들어갔습니다.")
else:
    print("\n행 개수가 100개가 아닙니다. 연도별 자치구 개수를 확인해 주세요.")

# 추가 데이터 품질 검증
print("\n숫자 열의 0 개수")
numeric_columns = final_data.select_dtypes(include="number").columns
print((final_data[numeric_columns] == 0).sum())

print("\n문자 형태의 결측값 개수")
fake_missing_values = ["", " ", "-", "없음", "미상", "nan"]

print(
    final_data.astype(str)
    .isin(fake_missing_values)
    .sum()
)

print("\n숫자 데이터 요약")
print(final_data.describe())

final_data["청년인구천명당순이동자수"] = (
    final_data["청년순이동자수"]
    / final_data["청년인구"]
    * 1000
).round(2)

print(
    final_data[
        [
            "연도",
            "자치구명",
            "청년인구",
            "청년순이동자수",
            "청년인구천명당순이동자수",
        ]
    ].head(10)
)

# 추가 데이터를 포함하여 다시 저장
final_data.to_csv(
    PROCESSED_DIR / "seoul_youth_final_2021_2024.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n파생변수 저장 후 최종 데이터 크기")
print(final_data.shape)

print("\n최종 열 목록")
print(final_data.columns.tolist())

# ==================================================
# 거주민 기준 연령별 취업자 수·고용률 전처리
# ==================================================

resident_file = (
    "data/raw/resident_employment/"
    "kosis_시군구_연령별_취업자_고용률_2021_2024.xlsx"
)

resident = pd.read_excel(resident_file)

# 전체 연령 자료 제외
resident = resident[
    resident["연령별"].isin(["15 - 29세", "30 - 49세"])
].copy()

# 자치구명에서 '서울 ' 제거
resident["자치구"] = (
    resident["행정구역별"]
    .str.replace("서울 ", "", regex=False)
    .str.strip()
)

# 실제 반기 데이터 컬럼만 선택
period_columns = [
    col for col in resident.columns
    if str(col).startswith(("2021.", "2022.", "2023.", "2024."))
]

# 반기별 컬럼만 세로 형태로 변환
resident_long = resident.melt(
    id_vars=["자치구", "항목", "연령별"],
    value_vars=period_columns,
    var_name="기간",
    value_name="값"
)

# 기간에서 연도 4자리 추출
resident_long["연도"] = (
    resident_long["기간"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
    .astype(int)
)

# '2021.1/2'에서 연도 추출
resident_long["연도"] = (
    resident_long["기간"]
    .str[:4]
    .astype(int)
)

# 숫자형 변환
resident_long["값"] = pd.to_numeric(
    resident_long["값"],
    errors="coerce"
)

# 상반기와 하반기 값을 연평균으로 계산
resident_yearly = (
    resident_long
    .groupby(
        ["자치구", "연도", "항목", "연령별"],
        as_index=False
    )["값"]
    .mean()
)

# 항목과 연령대를 결합해 컬럼명 생성
column_names = {
    ("취업자 (천명)", "15 - 29세"): "15_29세_취업자_천명",
    ("취업자 (천명)", "30 - 49세"): "30_49세_취업자_천명",
    ("고용률 (%)", "15 - 29세"): "15_29세_고용률",
    ("고용률 (%)", "30 - 49세"): "30_49세_고용률",
}

resident_yearly["변수명"] = resident_yearly.apply(
    lambda row: column_names[(row["항목"], row["연령별"])],
    axis=1
)

# 연령·항목별 값을 각각의 컬럼으로 펼치기
resident_processed = (
    resident_yearly
    .pivot(
        index=["자치구", "연도"],
        columns="변수명",
        values="값"
    )
    .reset_index()
)

resident_processed.columns.name = None

# 보기 좋은 컬럼 순서로 정리
resident_processed = resident_processed[
    [
        "자치구",
        "연도",
        "15_29세_취업자_천명",
        "15_29세_고용률",
        "30_49세_취업자_천명",
        "30_49세_고용률",
    ]
]

# 소수점 한 자리로 정리
value_columns = resident_processed.columns.drop(["자치구", "연도"])
resident_processed[value_columns] = (
    resident_processed[value_columns].round(1)
)

# 저장
output_path = "data/processed/resident_employment_2021_2024.csv"

resident_processed.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

print("\n[거주민 취업자·고용률 전처리 완료]")
print("데이터 크기:", resident_processed.shape)
print(resident_processed.head(10).to_string(index=False))
print("저장 위치:", output_path)

# ⭐️ 기존 최종 데이터와 거주민 고용 데이터 병합 ⭐️

# 병합 기준 열 이름 통일
employment_for_merge = resident_processed.rename(
    columns={"자치구": "자치구명"}
)

# 기존 최종 데이터와 병합
final_with_employment = final_data.merge(
    employment_for_merge,
    on=["연도", "자치구명"],
    how="left",
    validate="one_to_one"
)

# 병합 결과 확인
employment_columns = [
    "15_29세_취업자_천명",
    "15_29세_고용률",
    "30_49세_취업자_천명",
    "30_49세_고용률",
]

print("\n[고용 데이터 병합 완료]")
print("최종 데이터 크기:", final_with_employment.shape)
print(
    "고용 데이터 결측치:\n",
    final_with_employment[employment_columns].isna().sum()
)

print(
    final_with_employment[
        ["연도", "자치구명"] + employment_columns
    ].head(10).to_string(index=False)
)

# 최종 파일 저장
final_output_path = (
    "data/processed/"
    "seoul_youth_migration_final_2021_2024.csv"
)

final_with_employment.to_csv(
    final_output_path,
    index=False,
    encoding="utf-8-sig"
)

print("최종 저장 위치:", final_output_path)