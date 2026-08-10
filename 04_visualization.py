import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 전처리가 완료된 통합 데이터 불러오기
data = pd.read_csv("data/processed/seoul_youth_final_2021_2024.csv")

# 인구 1,000명당 순이동자 수 계산
data["20대인구천명당순이동자수"] = (
    data["20대순이동자수"] / data["20대인구"] * 1000
).round(2)

data["30대인구천명당순이동자수"] = (
    data["30대순이동자수"] / data["30대인구"] * 1000
).round(2)


# 연도는 범주형으로 사용
data["연도"] = data["연도"].astype(str)

# 그래프 기본 스타일
sns.set_theme(style="whitegrid")
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.figsize"] = (10, 7)

# 1. 20대 순이동률과 월세 거래 건수의 관계
plt.figure(figsize=(11, 7))

sns.scatterplot(
    data=data,
    x="월세거래건수",
    y="20대인구천명당순이동자수",
    hue="연도",
    palette="Set2",
    s=100,
    alpha=0.8,
)

# 순이동률 0 기준선
plt.axhline(0, color="gray", linestyle="--", linewidth=1)

plt.title("서울 자치구별 월세 거래 건수와 20대 순이동률")
plt.xlabel("월세 거래 건수")
plt.ylabel("20대 인구 1,000명당 순이동자 수")
plt.legend(title="연도")
plt.tight_layout()
plt.show()