from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "seoul_youth_migration_analysis_2021_2024.csv"
)
RESULT_DIR = BASE_DIR / "results"

RESULT_DIR.mkdir(exist_ok=True)

data = pd.read_csv(DATA_PATH)


# 1. 연도별 상관관계
yearly_correlation = []

for year in sorted(data["연도"].unique()):
    year_data = data[data["연도"] == year]

    correlation_20 = year_data[
        ["15_29세_고용률", "20대인구천명당순이동자수"]
    ].corr().iloc[0, 1]

    correlation_30 = year_data[
        ["전세보증금중앙값_만원", "30대인구천명당순이동자수"]
    ].corr().iloc[0, 1]

    yearly_correlation.append({
        "연도": year,
        "20대_고용률_상관계수": round(correlation_20, 3),
        "30대_전세보증금_상관계수": round(correlation_30, 3)
    })

yearly_correlation = pd.DataFrame(yearly_correlation)

print("\n[연도별 상관관계]")
print(yearly_correlation.to_string(index=False))

yearly_correlation.to_csv(
    RESULT_DIR / "07_연도별_상관관계.csv",
    index=False,
    encoding="utf-8-sig"
)


# 2. 2024년 20대·30대 이동 유형 분류
data_2024 = data[data["연도"] == 2024].copy()


def classify_migration(row):
    age20 = row["20대인구천명당순이동자수"]
    age30 = row["30대인구천명당순이동자수"]

    if age20 >= 0 and age30 >= 0:
        return "동반 유입형"

    elif age20 >= 0 and age30 < 0:
        return "20대 유입·30대 유출형"

    elif age20 < 0 and age30 >= 0:
        return "20대 유출·30대 유입형"

    else:
        return "동반 유출형"


data_2024["이동유형"] = data_2024.apply(
    classify_migration,
    axis=1
)

migration_type = data_2024[
    [
        "자치구명",
        "20대인구천명당순이동자수",
        "30대인구천명당순이동자수",
        "이동유형"
    ]
].sort_values(
    ["이동유형", "자치구명"]
)

print("\n[2024년 자치구별 이동 유형]")
print(migration_type.to_string(index=False))

print("\n[이동 유형별 자치구 수]")
print(
    migration_type["이동유형"]
    .value_counts()
    .to_string()
)

migration_type.to_csv(
    RESULT_DIR / "08_2024년_자치구별_이동유형.csv",
    index=False,
    encoding="utf-8-sig"
)


# 3. 순이동 상위 5개 구와 하위 5개 구 비교
comparison_columns = [
    "전세보증금중앙값_만원",
    "월세중앙값_만원",
    "월세거래건수",
    "종사자수",
    "15_29세_고용률",
    "30_49세_고용률"
]


def compare_top_bottom(age_name, rate_column):
    top5 = data_2024.nlargest(5, rate_column)
    bottom5 = data_2024.nsmallest(5, rate_column)

    top_average = top5[comparison_columns].mean()
    bottom_average = bottom5[comparison_columns].mean()

    comparison = pd.DataFrame({
        "지표": comparison_columns,
        "상위5개구_평균": top_average.values,
        "하위5개구_평균": bottom_average.values
    })

    comparison["평균차이"] = (
        comparison["상위5개구_평균"]
        - comparison["하위5개구_평균"]
    )

    comparison.insert(0, "연령대", age_name)

    print(f"\n[{age_name} 순이동 상위 5개 구]")
    print(
        top5[
            ["자치구명", rate_column]
        ].to_string(index=False)
    )

    print(f"\n[{age_name} 순이동 하위 5개 구]")
    print(
        bottom5[
            ["자치구명", rate_column]
        ].to_string(index=False)
    )

    print(f"\n[{age_name} 상위·하위 지역 특성 비교]")
    print(comparison.round(2).to_string(index=False))

    return comparison


comparison_20 = compare_top_bottom(
    "20대",
    "20대인구천명당순이동자수"
)

comparison_30 = compare_top_bottom(
    "30대",
    "30대인구천명당순이동자수"
)

comparison_result = pd.concat(
    [comparison_20, comparison_30],
    ignore_index=True
)

comparison_result.to_csv(
    RESULT_DIR / "09_순이동_상하위지역_비교.csv",
    index=False,
    encoding="utf-8-sig"
)


print("\n추가 분석이 완료되었습니다.")
print("결과 저장 위치:", RESULT_DIR)