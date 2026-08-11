from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# 전처리가 끝난 최종 데이터 불러오기
data = pd.read_csv(
    PROCESSED_DIR
    / "seoul_youth_migration_final_2021_2024.csv"
)

print("데이터 크기:", data.shape)
print("컬럼 수:", len(data.columns))

# 1. 연도별 20대·30대 순이동자 수

age_migration_by_year = (
    data.groupby("연도")[
        ["20대순이동자수", "30대순이동자수"]
    ]
    .sum()
)

print("\n[연도별 20대·30대 순이동자 수]")
print(age_migration_by_year)


# 2. 연령대별 인구 1,000명당 순이동자 수

data["20대인구천명당순이동자수"] = (
    data["20대순이동자수"]
    / data["20대인구"]
    * 1000
).round(2)

data["30대인구천명당순이동자수"] = (
    data["30대순이동자수"]
    / data["30대인구"]
    * 1000
).round(2)

print("\n[20대·30대 인구 1,000명당 순이동자 수]")
print(
    data[
        [
            "연도",
            "자치구명",
            "20대인구천명당순이동자수",
            "30대인구천명당순이동자수",
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# 3. 연도별 순이동률 상위·하위 자치구

for year in sorted(data["연도"].unique()):
    year_data = data[data["연도"] == year]

    print(f"\n[{year}년 20대 순이동률 상위 5개 구]")
    print(
        year_data.nlargest(
            5, "20대인구천명당순이동자수"
        )[
            [
                "자치구명",
                "20대인구천명당순이동자수",
            ]
        ].to_string(index=False)
    )

    print(f"\n[{year}년 20대 순이동률 하위 5개 구]")
    print(
        year_data.nsmallest(
            5, "20대인구천명당순이동자수"
        )[
            [
                "자치구명",
                "20대인구천명당순이동자수",
            ]
        ].to_string(index=False)
    )

    print(f"\n[{year}년 30대 순이동률 상위 5개 구]")
    print(
        year_data.nlargest(
            5, "30대인구천명당순이동자수"
        )[
            [
                "자치구명",
                "30대인구천명당순이동자수",
            ]
        ].to_string(index=False)
    )

    print(f"\n[{year}년 30대 순이동률 하위 5개 구]")
    print(
        year_data.nsmallest(
            5, "30대인구천명당순이동자수"
        )[
            [
                "자치구명",
                "30대인구천명당순이동자수",
            ]
        ].to_string(index=False)
    )


# 4. 전체 기간 상관관계

migration_columns = [
    "20대인구천명당순이동자수",
    "30대인구천명당순이동자수",
]

housing_job_columns = [
    "전세보증금중앙값_만원",
    "월세보증금중앙값_만원",
    "월세중앙값_만원",
    "전세거래건수",
    "월세거래건수",
    "종사자수",
    "15_29세_취업자_천명",
    "15_29세_고용률",
    "30_49세_취업자_천명",
    "30_49세_고용률",
]

analysis_columns = migration_columns + housing_job_columns

correlation = data[analysis_columns].corr()

migration_correlation = correlation.loc[
    migration_columns,
    housing_job_columns,
]

print("\n[20대·30대 순이동률과 주거·일자리 변수의 상관계수]")
print(migration_correlation.round(3).to_string())

# 5. 연도별 상관관계

for year in sorted(data["연도"].unique()):
    year_data = data[data["연도"] == year]

    yearly_correlation = year_data[
        migration_columns + housing_job_columns
    ].corr()

    result = yearly_correlation.loc[
        migration_columns,
        housing_job_columns,
    ]

    print(f"\n[{year}년 순이동률 상관계수]")
    print(result.round(3).to_string())


# 6. 분석용 파생변수가 포함된 파일 저장

analysis_output_path = (
    PROCESSED_DIR
    / "seoul_youth_migration_analysis_2021_2024.csv"
)

data.to_csv(
    analysis_output_path,
    index=False,
    encoding="utf-8-sig",
)

print("\n분석 데이터 저장 위치:", analysis_output_path)