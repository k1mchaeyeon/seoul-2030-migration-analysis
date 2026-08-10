from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# 전처리가 끝난 최종 데이터 불러오기
data = pd.read_csv(
    PROCESSED_DIR / "seoul_youth_final_2021_2024.csv"
)

# 연도별 20대·30대 순이동자 수 합계
age_migration_by_year = (
    data.groupby("연도")[["20대순이동자수", "30대순이동자수"]]
    .sum()
)

print("\n연도별 20대·30대 순이동자 수")
print(age_migration_by_year)

# 연령대별 인구 1,000명당 순이동자 수 계산
data["20대인구천명당순이동자수"] = (
    data["20대순이동자수"] / data["20대인구"] * 1000
).round(2)

data["30대인구천명당순이동자수"] = (
    data["30대순이동자수"] / data["30대인구"] * 1000
).round(2)

# 계산 결과 확인
print("\n20대·30대 인구 1,000명당 순이동자 수")
print(
    data[
        [
            "연도",
            "자치구명",
            "20대인구천명당순이동자수",
            "30대인구천명당순이동자수",
        ]
    ].head(10)
)

# 연도별 20대 순이동률 상위·하위 자치구 확인
for year in sorted(data["연도"].unique()):
    year_data = data[data["연도"] == year]

    print(f"\n[{year}년 20대 순이동률 상위 5개 구]")
    print(
        year_data.nlargest(
            5, "20대인구천명당순이동자수"
        )[["자치구명", "20대인구천명당순이동자수"]]
        .to_string(index=False)
    )

    print(f"\n[{year}년 20대 순이동률 하위 5개 구]")
    print(
        year_data.nsmallest(
            5, "20대인구천명당순이동자수"
        )[["자치구명", "20대인구천명당순이동자수"]]
        .to_string(index=False)
    )

    print(f"\n[{year}년 30대 순이동률 상위 5개 구]")
    print(
        year_data.nlargest(
            5, "30대인구천명당순이동자수"
        )[["자치구명", "30대인구천명당순이동자수"]]
        .to_string(index=False)
    )

    print(f"\n[{year}년 30대 순이동률 하위 5개 구]")
    print(
        year_data.nsmallest(
            5, "30대인구천명당순이동자수"
        )[["자치구명", "30대인구천명당순이동자수"]]
        .to_string(index=False)
    )

    # 분석에 사용할 변수
analysis_columns = [
    "20대인구천명당순이동자수",
    "30대인구천명당순이동자수",
    "전세보증금중앙값_만원",
    "월세보증금중앙값_만원",
    "월세중앙값_만원",
    "전세거래건수",
    "월세거래건수",
    "종사자수",
]

# 전체 기간 상관계수 계산
correlation = data[analysis_columns].corr()

# 20대·30대 순이동률과 다른 변수의 상관계수만 추출
migration_correlation = correlation.loc[
    [
        "20대인구천명당순이동자수",
        "30대인구천명당순이동자수",
    ],
    [
        "전세보증금중앙값_만원",
        "월세보증금중앙값_만원",
        "월세중앙값_만원",
        "전세거래건수",
        "월세거래건수",
        "종사자수",
    ],
]

print("\n20대·30대 순이동률과 주거·일자리 변수의 상관계수")
print(migration_correlation.round(3))

# 연도별 상관관계 확인
housing_job_columns = [
    "전세보증금중앙값_만원",
    "월세보증금중앙값_만원",
    "월세중앙값_만원",
    "전세거래건수",
    "월세거래건수",
    "종사자수",
]

for year in sorted(data["연도"].unique()):
    year_data = data[data["연도"] == year]

    yearly_correlation = year_data[
        [
            "20대인구천명당순이동자수",
            "30대인구천명당순이동자수",
        ]
        + housing_job_columns
    ].corr()

    result = yearly_correlation.loc[
        [
            "20대인구천명당순이동자수",
            "30대인구천명당순이동자수",
        ],
        housing_job_columns,
    ]

    print(f"\n[{year}년 순이동률 상관계수]")
    print(result.round(3))