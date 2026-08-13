from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_DIR = BASE_DIR / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

YEARS = list(range(2021, 2025))
# 연도·자치구 간 비교에 금리 변동이 섞이지 않도록 고정한 분석용 가정을 사용한다.
JEONSE_CONVERSION_RATE = 0.05
DISTRICTS = [
    "종로구", "중구", "용산구", "성동구", "광진구", "동대문구", "중랑구",
    "성북구", "강북구", "도봉구", "노원구", "은평구", "서대문구", "마포구",
    "양천구", "강서구", "구로구", "금천구", "영등포구", "동작구", "관악구",
    "서초구", "강남구", "송파구", "강동구",
]

DISTRICT_CODE = {
    f"{1101 + i:04d}": district for i, district in enumerate(DISTRICTS)
}


def read_table(path, **kwargs):
    if path.suffix.lower() == ".xlsx":
        return pd.read_excel(path, **kwargs)
    try:
        return pd.read_csv(path, encoding="utf-8", low_memory=False, **kwargs)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp949", low_memory=False, **kwargs)


def save(frame, name):
    path = OUT_DIR / name
    frame.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"저장: {name} {frame.shape}")


def make_population():
    path = next((RAW_DIR / "population").glob("*.xlsx"))
    raw = pd.read_excel(path)
    age_row = raw.iloc[0]
    raw = raw.iloc[2:].copy()
    raw = raw[raw["항목"] == "총인구수 (명)"].copy()
    raw["자치구명"] = raw["행정구역(동읍면)별"].astype(str).str.strip()

    rows = []
    for year in range(2020, 2025):
        year_cols = [c for c in raw.columns if str(c).startswith(f"{year}.12")]
        age20 = [c for c in year_cols if age_row[c] in ["20 - 24세", "25 - 29세"]]
        age30 = [c for c in year_cols if age_row[c] in ["30 - 34세", "35 - 39세"]]
        if len(age20) != 2 or len(age30) != 2:
            raise ValueError(f"{year}년 연령별 인구 열을 확인해 주세요.")
        temp = raw[["자치구명"] + age20 + age30].copy()
        temp[age20 + age30] = temp[age20 + age30].apply(pd.to_numeric, errors="coerce")
        temp["20대인구"] = temp[age20].sum(axis=1)
        temp["30대인구"] = temp[age30].sum(axis=1)
        temp["연도"] = year
        rows.append(temp[["연도", "자치구명", "20대인구", "30대인구"]])

    data = pd.concat(rows, ignore_index=True).sort_values(["자치구명", "연도"])
    for age in ["20대", "30대"]:
        data[f"{age}연앙인구"] = (
            data.groupby("자치구명")[f"{age}인구"].shift(1) + data[f"{age}인구"]
        ) / 2
    data["청년인구"] = data["20대인구"] + data["30대인구"]
    data = data[data["연도"].isin(YEARS)].copy()
    return data.sort_values(["연도", "자치구명"]).reset_index(drop=True)


def make_migration():
    path = next((RAW_DIR / "migration").glob("*.xlsx"))
    raw = pd.read_excel(path)
    raw["행정구역(시군구)별"] = raw["행정구역(시군구)별"].astype(str).str.strip()
    raw = raw[raw["행정구역(시군구)별"].isin(DISTRICTS)].copy()
    raw["연령대"] = raw["연령별"].map({
        "20 - 24세": "20대순이동자수", "25 - 29세": "20대순이동자수",
        "30 - 34세": "30대순이동자수", "35 - 39세": "30대순이동자수",
    })
    raw = raw.dropna(subset=["연령대"])
    year_cols = [str(y) for y in YEARS]
    raw[year_cols] = raw[year_cols].apply(pd.to_numeric, errors="coerce")
    data = raw.melt(
        id_vars=["행정구역(시군구)별", "연령대"], value_vars=year_cols,
        var_name="연도", value_name="순이동자수",
    )
    data = data.pivot_table(
        index=["연도", "행정구역(시군구)별"], columns="연령대",
        values="순이동자수", aggfunc="sum",
    ).reset_index()
    data.columns.name = None
    data = data.rename(columns={"행정구역(시군구)별": "자치구명"})
    data["연도"] = data["연도"].astype(int)
    data["청년순이동자수"] = data["20대순이동자수"] + data["30대순이동자수"]
    return data


def make_rent():
    use_cols = ["접수년도", "자치구명", "전월세구분", "보증금(만원)", "임대료(만원)"]
    parts = []
    for path in sorted((RAW_DIR / "rent").glob("*")):
        if path.suffix.lower() not in [".csv", ".txt"]:
            continue
        print("전월세:", path.name)
        part = read_table(path, usecols=use_cols)
        parts.append(part)
    data = pd.concat(parts, ignore_index=True)
    data = data[data["접수년도"].isin(YEARS) & data["자치구명"].isin(DISTRICTS)].copy()
    data["전월세구분"] = data["전월세구분"].astype(str).str.strip()
    for col in ["보증금(만원)", "임대료(만원)"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
        data.loc[data[col] < 0, col] = pd.NA

    jeonse = data[data["전월세구분"] == "전세"].groupby(
        ["접수년도", "자치구명"], as_index=False
    ).agg(
        전세거래건수=("자치구명", "size"),
        전세보증금중앙값_만원=("보증금(만원)", "median"),
    )
    monthly = data[data["전월세구분"] == "월세"].groupby(
        ["접수년도", "자치구명"], as_index=False
    ).agg(
        월세거래건수=("자치구명", "size"),
        월세보증금중앙값_만원=("보증금(만원)", "median"),
        월세중앙값_만원=("임대료(만원)", "median"),
    )

    # 전세는 보증금 그대로, 월세는 연간 월세를 고정 전환율로 환산한 보증금을 더한다.
    # 계약별로 먼저 환산한 뒤 자치구·연도별 중앙값을 계산한다.
    valid_jeonse = (data["전월세구분"] == "전세") & (data["보증금(만원)"] > 0)
    valid_monthly = (
        (data["전월세구분"] == "월세")
        & (data["보증금(만원)"] >= 0)
        & (data["임대료(만원)"] > 0)
    )
    converted = data[valid_jeonse | valid_monthly].copy()
    converted["전세환산주거비_만원"] = np.where(
        converted["전월세구분"] == "전세",
        converted["보증금(만원)"],
        converted["보증금(만원)"]
        + converted["임대료(만원)"] * 12 / JEONSE_CONVERSION_RATE,
    )
    housing = converted.groupby(["접수년도", "자치구명"], as_index=False).agg(
        주거거래건수=("자치구명", "size"),
        전세환산주거비중앙값_만원=("전세환산주거비_만원", "median"),
    )
    housing["주거비전환율_퍼센트"] = JEONSE_CONVERSION_RATE * 100

    result = jeonse.merge(monthly, on=["접수년도", "자치구명"], how="outer")
    result = result.merge(housing, on=["접수년도", "자치구명"], how="outer")
    return result.rename(columns={"접수년도": "연도"})


def make_workers():
    rows = []
    for path in sorted((RAW_DIR / "employment").glob("*.csv")):
        year = next((y for y in YEARS if str(y) in path.name), None)
        if year is None:
            continue
        worker_col = "WOKE_SUM" if year == 2021 else "SURV_PHS_WOKE_SUM"
        print("사업체:", path.name)
        raw = read_table(path, usecols=["AD_CD", worker_col])
        raw["자치구코드"] = raw["AD_CD"].astype(str).str.replace(".0", "", regex=False).str[:4]
        raw["자치구명"] = raw["자치구코드"].map(DISTRICT_CODE)
        raw["종사자수"] = pd.to_numeric(raw[worker_col], errors="coerce")
        temp = raw.dropna(subset=["자치구명", "종사자수"]).groupby(
            "자치구명", as_index=False
        )["종사자수"].sum()
        temp["연도"] = year
        rows.append(temp[["연도", "자치구명", "종사자수"]])
    return pd.concat(rows, ignore_index=True)


def make_resident_employment():
    path = next((RAW_DIR / "resident_employment").glob("*.xlsx"))
    raw = pd.read_excel(path)
    raw["자치구명"] = raw["행정구역별"].astype(str).str.replace("서울 ", "", regex=False).str.strip()
    rows = []
    for year in YEARS:
        half_cols = [f"{year}.1/2", f"{year}.2/2"]
        temp = {"연도": year}
        for age, name in [("15 - 29세", "15_29세_고용률"), ("30 - 49세", "30_49세_고용률")]:
            selected = raw[(raw["항목"] == "고용률 (%)") & (raw["연령별"] == age)].copy()
            selected[name] = selected[half_cols].apply(pd.to_numeric, errors="coerce").mean(axis=1)
            selected["연도"] = year
            rows.append(selected[["연도", "자치구명", name]])
    age20 = pd.concat([x for x in rows if "15_29세_고용률" in x], ignore_index=True)
    age30 = pd.concat([x for x in rows if "30_49세_고용률" in x], ignore_index=True)
    return age20.merge(age30, on=["연도", "자치구명"], how="outer")


def check_data(data):
    key = ["연도", "자치구명"]
    if len(data) != 100 or data.duplicated(key).any():
        raise ValueError("최종 데이터는 연도별 25개 자치구, 총 100행이어야 합니다.")
    counts = data.groupby("연도")["자치구명"].nunique()
    if not (counts == 25).all():
        raise ValueError(f"자치구 수가 맞지 않습니다.\n{counts}")
    missing = data.isna().sum()
    if missing.any():
        raise ValueError(f"결측치를 확인해 주세요.\n{missing[missing > 0]}")


def main():
    population = make_population()
    migration = make_migration()
    rent = make_rent()
    workers = make_workers()
    resident = make_resident_employment()

    save(population, "youth_population_2021_2024.csv")
    save(migration, "youth_migration_2021_2024.csv")
    save(rent, "rent_summary_2021_2024.csv")
    save(workers, "workers_2021_2024.csv")
    save(resident, "resident_employment_2021_2024.csv")

    data = population.merge(migration, on=["연도", "자치구명"], validate="one_to_one")
    data = data.merge(rent, on=["연도", "자치구명"], validate="one_to_one")
    data = data.merge(workers, on=["연도", "자치구명"], validate="one_to_one")
    data = data.merge(resident, on=["연도", "자치구명"], validate="one_to_one")
    data["20대순이동률"] = data["20대순이동자수"] / data["20대연앙인구"] * 1000
    data["30대순이동률"] = data["30대순이동자수"] / data["30대연앙인구"] * 1000
    data["청년연앙인구"] = data["20대연앙인구"] + data["30대연앙인구"]
    data["청년순이동률"] = data["청년순이동자수"] / data["청년연앙인구"] * 1000
    rate_cols = ["20대순이동률", "30대순이동률", "청년순이동률"]
    data[rate_cols] = data[rate_cols].round(2)
    check_data(data)
    save(data.sort_values(["연도", "자치구명"]), "seoul_youth_master.csv")
    print("전처리가 끝났습니다.")


if __name__ == "__main__":
    main()
