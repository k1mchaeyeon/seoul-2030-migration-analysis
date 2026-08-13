from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "processed" / "seoul_youth_master.csv"
RESULT_DIR = BASE_DIR / "results"
RESULT_DIR.mkdir(exist_ok=True)


def migration_type(row):
    if row["20대순이동률"] >= 0 and row["30대순이동률"] >= 0:
        return "동반 유입형"
    if row["20대순이동률"] >= 0 and row["30대순이동률"] < 0:
        return "20대 유입·30대 유출형"
    if row["20대순이동률"] < 0 and row["30대순이동률"] >= 0:
        return "20대 유출·30대 유입형"
    return "동반 유출형"


def main():
    data = pd.read_csv(DATA_PATH)
    data["이동유형"] = data.apply(migration_type, axis=1)

    yearly = data.groupby("연도", as_index=False)[
        ["20대순이동자수", "30대순이동자수", "청년순이동자수"]
    ].sum()
    yearly.to_csv(RESULT_DIR / "연도별_순이동.csv", index=False, encoding="utf-8-sig")

    types = data[["연도", "자치구명", "20대순이동률", "30대순이동률", "이동유형"]]
    types.to_csv(RESULT_DIR / "자치구별_이동유형.csv", index=False, encoding="utf-8-sig")

    corr_rows = []
    factors = [
        "전세환산주거비중앙값_만원", "종사자수",
        "15_29세_고용률", "30_49세_고용률",
    ]
    for year in sorted(data["연도"].unique()):
        part = data[data["연도"] == year]
        for age in ["20대", "30대"]:
            rate = f"{age}순이동률"
            for factor in factors:
                corr_rows.append({
                    "연도": year, "연령대": age, "지표": factor,
                    "상관계수": round(part[[rate, factor]].corr().iloc[0, 1], 3),
                })
    pd.DataFrame(corr_rows).to_csv(
        RESULT_DIR / "연도별_상관관계.csv", index=False, encoding="utf-8-sig"
    )

    recent = data[data["연도"].isin([2022, 2023, 2024])]
    persistence = []
    for district, part in recent.groupby("자치구명"):
        row = {"자치구명": district}
        for age in ["20대", "30대"]:
            values = part.sort_values("연도")[f"{age}순이동률"]
            row[f"{age}_3년유출횟수"] = int((values < 0).sum())
            row[f"{age}_3년평균순이동률"] = round(values.mean(), 2)
        persistence.append(row)
    pd.DataFrame(persistence).to_csv(
        RESULT_DIR / "최근3년_지속성.csv", index=False, encoding="utf-8-sig"
    )
    print("분석 결과를 results 폴더에 저장했습니다.")


if __name__ == "__main__":
    main()
