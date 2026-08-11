from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# import koreanize_matplotlib

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"
RESULT_DIR = BASE_DIR / "results"

RESULT_DIR.mkdir(exist_ok=True)

data = pd.read_csv(
    DATA_DIR / "seoul_youth_migration_analysis_2021_2024.csv"
)

sns.set_theme(style="whitegrid")
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


# 연도별 20대, 30대 순이동자 수
yearly_migration = (
    data.groupby("연도")[
        ["20대순이동자수", "30대순이동자수"]
    ]
    .sum()
    .reset_index()
)

yearly_long = yearly_migration.melt(
    id_vars="연도",
    var_name="연령대",
    value_name="순이동자수"
)

yearly_long["연령대"] = yearly_long["연령대"].replace({
    "20대순이동자수": "20대",
    "30대순이동자수": "30대"
})

plt.figure(figsize=(10, 6))

sns.barplot(
    data=yearly_long,
    x="연도",
    y="순이동자수",
    hue="연령대",
    palette=["#5B8FF9", "#F6BD16"]
)

plt.axhline(0, color="black", linewidth=1)
plt.title("연도별 서울 20대·30대 순이동자 수")
plt.xlabel("연도")
plt.ylabel("순이동자 수(명)")
plt.legend(title="연령대")
plt.tight_layout()

plt.savefig(
    RESULT_DIR / "01_연도별_순이동자수.png",
    dpi=300
)
plt.show()


# 2024년 자치구별 20대 순이동률
data_2024 = data[data["연도"] == 2024].copy()

age20_2024 = data_2024.sort_values(
    "20대인구천명당순이동자수",
    ascending=True
)

colors_20 = [
    "#E76F51" if value < 0 else "#4C78A8"
    for value in age20_2024["20대인구천명당순이동자수"]
]

plt.figure(figsize=(10, 9))

plt.barh(
    age20_2024["자치구명"],
    age20_2024["20대인구천명당순이동자수"],
    color=colors_20
)

plt.axvline(0, color="black", linewidth=1)
plt.title("2024년 자치구별 20대 인구 1,000명당 순이동자 수")
plt.xlabel("인구 1,000명당 순이동자 수")
plt.ylabel("자치구")
plt.tight_layout()

plt.savefig(
    RESULT_DIR / "02_2024년_20대_자치구별_순이동률.png",
    dpi=300
)
plt.show()


# 2024년 자치구별 30대 순이동률
age30_2024 = data_2024.sort_values(
    "30대인구천명당순이동자수",
    ascending=True
)

colors_30 = [
    "#E76F51" if value < 0 else "#59A14F"
    for value in age30_2024["30대인구천명당순이동자수"]
]

plt.figure(figsize=(10, 9))

plt.barh(
    age30_2024["자치구명"],
    age30_2024["30대인구천명당순이동자수"],
    color=colors_30
)

plt.axvline(0, color="black", linewidth=1)
plt.title("2024년 자치구별 30대 인구 1,000명당 순이동자 수")
plt.xlabel("인구 1,000명당 순이동자 수")
plt.ylabel("자치구")
plt.tight_layout()

plt.savefig(
    RESULT_DIR / "03_2024년_30대_자치구별_순이동률.png",
    dpi=300
)
plt.show()


# 20대 순이동률과 15~29세 고용률
plt.figure(figsize=(10, 7))

sns.scatterplot(
    data=data,
    x="15_29세_고용률",
    y="20대인구천명당순이동자수",
    hue="연도",
    palette="viridis",
    s=80
)

sns.regplot(
    data=data,
    x="15_29세_고용률",
    y="20대인구천명당순이동자수",
    scatter=False,
    color="gray",
    line_kws={"linestyle": "--"}
)

correlation_20 = data[
    ["15_29세_고용률", "20대인구천명당순이동자수"]
].corr().iloc[0, 1]

plt.text(
    0.03,
    0.95,
    f"상관계수: {correlation_20:.3f}",
    transform=plt.gca().transAxes,
    fontsize=11,
    verticalalignment="top"
)

plt.axhline(0, color="black", linewidth=0.8)
plt.title("전세보증금과 30대 인구 1,000명당 순이동자 수의 관계")
plt.xlabel("15~29세 고용률(%)")
plt.ylabel("20대 인구 1,000명당 순이동자 수")
plt.legend(title="연도")
plt.tight_layout()

plt.savefig(
    RESULT_DIR / "04_20대순이동률_고용률_산점도.png",
    dpi=300
)
plt.show()


# 30대 순이동률과 전세보증금
plt.figure(figsize=(10, 7))

sns.scatterplot(
    data=data,
    x="전세보증금중앙값_만원",
    y="30대인구천명당순이동자수",
    hue="연도",
    palette="Set2",
    s=80
)

sns.regplot(
    data=data,
    x="전세보증금중앙값_만원",
    y="30대인구천명당순이동자수",
    scatter=False,
    color="gray",
    line_kws={"linestyle": "--"}
)

correlation_30 = data[
    ["전세보증금중앙값_만원", "30대인구천명당순이동자수"]
].corr().iloc[0, 1]

plt.text(
    0.03,
    0.95,
    f"상관계수: {correlation_30:.3f}",
    transform=plt.gca().transAxes,
    fontsize=11,
    verticalalignment="top"
)

plt.axhline(0, color="black", linewidth=0.8)
plt.title("전세보증금과 30대 순이동률의 관계")
plt.xlabel("전세보증금 중앙값(만원)")
plt.ylabel("30대 인구 1,000명당 순이동자 수")
plt.legend(title="연도")
plt.tight_layout()

plt.savefig(
    RESULT_DIR / "05_30대순이동률_전세보증금_산점도.png",
    dpi=300
)
plt.show()


# 주요 변수 상관관계 히트맵
heatmap_columns = [
    "20대인구천명당순이동자수",
    "30대인구천명당순이동자수",
    "전세보증금중앙값_만원",
    "월세중앙값_만원",
    "월세거래건수",
    "종사자수",
    "15_29세_고용률",
    "30_49세_고용률"
]

heatmap_data = data[heatmap_columns].corr()

heatmap_labels = [
    "20대 순이동률",
    "30대 순이동률",
    "전세보증금",
    "월세",
    "월세 거래",
    "종사자 수",
    "15~29세 고용률",
    "30~49세 고용률"
]

heatmap_data.index = heatmap_labels
heatmap_data.columns = heatmap_labels

plt.figure(figsize=(11, 9))

sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".2f",
    cmap="RdBu_r",
    center=0,
    vmin=-1,
    vmax=1,
    linewidths=0.5
)

plt.title("청년 순이동과 주거·고용 변수의 상관관계")
plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()

plt.savefig(
    RESULT_DIR / "06_주요변수_상관관계_히트맵.png",
    dpi=300
)
plt.show()

print("시각화가 완료되었습니다.")
print("저장 위치:", RESULT_DIR)