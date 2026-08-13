from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "processed" / "seoul_youth_master.csv"
OUT_DIR = BASE_DIR / "results" / "ppt"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BLUE = "#3976A8"
LIGHT_BLUE = "#9DBCD2"
RED = "#C45F52"
LIGHT_RED = "#E3AAA2"
GREEN = "#5B8E71"
ORANGE = "#C97945"
GRAY = "#D7DDE3"
DARK = "#26333D"
TEXT = "#4D5A64"
GRID = "#E7EBEF"
WHITE = "#FFFFFF"

plt.rcParams.update({
    "font.family": "AppleGothic",
    "axes.unicode_minus": False,
    "figure.facecolor": WHITE,
    "axes.facecolor": WHITE,
    "axes.titleweight": "bold",
    "axes.titlesize": 20,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})


def clean_axis(ax, grid="y"):
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#BCC5CC")
    ax.grid(False)
    ax.grid(axis=grid, color=GRID, linewidth=.8)
    ax.tick_params(axis="both", length=0, colors=TEXT)
    ax.set_axisbelow(True)


def title(fig, headline, note=None):
    fig.text(.07, .94, headline, fontsize=23, fontweight="bold", color=DARK, ha="left")
    if note:
        fig.text(.07, .895, note, fontsize=11, color=TEXT, ha="left")


def source(fig, text="KOSIS·서울 열린데이터광장, 2021~2024", note=None):
    if note:
        fig.text(.07, .025, note, fontsize=7.5, color="#7C8790", ha="left")
    fig.text(.93, .025, f"자료: {text}", fontsize=8, color="#7C8790", ha="right")


def save(fig, filename):
    path = OUT_DIR / filename
    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print("저장:", path)


def chart_01_yearly_flow(data):
    yearly = data.groupby("연도")[["20대순이동자수", "30대순이동자수"]].sum()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=.1, right=.94, bottom=.13, top=.82)
    x = np.arange(len(yearly))
    width = .34
    bars20 = ax.bar(x - width / 2, yearly["20대순이동자수"], width, color=BLUE, label="20대")
    bars30 = ax.bar(x + width / 2, yearly["30대순이동자수"], width, color=RED, label="30대")
    ax.axhline(0, color=DARK, linewidth=1)
    ax.bar_label(bars20, labels=[f"{v/10000:+.1f}만" for v in yearly["20대순이동자수"]], padding=5, fontsize=11, color=BLUE)
    ax.bar_label(bars30, labels=[f"{v/10000:+.1f}만" for v in yearly["30대순이동자수"]], padding=5, fontsize=11, color=RED)
    ax.set_xticks(x, [f"{year}년" for year in yearly.index])
    ax.set_ylabel("순이동자수(명)")
    ax.legend(frameon=False, ncol=2, loc="upper right")
    clean_axis(ax)
    title(fig, "20대는 매년 들어오고, 30대는 매년 나갔다", "두 연령대를 합치면 30대의 큰 유출이 잘 보이지 않는다")
    source(fig, "KOSIS 인구이동통계, 2021~2024")
    save(fig, "01_20대와30대_연도별순이동.png")


def chart_02_absolute_flow(data):
    year = data[data["연도"] == 2024]
    highlight = {"노원구", "양천구", "관악구", "강동구"}
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.75))
    fig.subplots_adjust(left=.1, right=.95, bottom=.13, top=.79, wspace=.4)

    for ax, age, color in [(axes[0], "20대", BLUE), (axes[1], "30대", RED)]:
        column = f"{age}순이동자수"
        part = year.sort_values(column)
        colors = []
        for _, row in part.iterrows():
            if row["자치구명"] in highlight:
                colors.append(BLUE if row[column] >= 0 else RED)
            else:
                colors.append(LIGHT_BLUE if row[column] >= 0 else LIGHT_RED)
        bars = ax.barh(part["자치구명"], part[column], color=colors, height=.72)
        ax.axvline(0, color=DARK, linewidth=1)
        span = max(abs(part[column].min()), abs(part[column].max()))
        for bar, value in zip(bars, part[column]):
            if abs(value) < span * .055:
                continue
            ax.text(
                value + (span * .018 if value >= 0 else -span * .018),
                bar.get_y() + bar.get_height() / 2,
                f"{value:+,.0f}",
                ha="left" if value >= 0 else "right", va="center",
                fontsize=7.2, color=TEXT,
            )
        ax.set_title(age, loc="left", color=color, fontsize=16)
        ax.set_xlabel("순이동자수(명)")
        ax.tick_params(axis="y", labelsize=7.5)
        ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        ax.set_xlim(part[column].min() - span * .18, part[column].max() + span * .18)
        clean_axis(ax, grid="x")

    title(fig, "구마다 20대와 30대의 이동 방향이 달랐다", "2024년 25개 자치구 순이동자수 · 진한색은 대시보드에서 비교한 지역")
    source(fig, "KOSIS 인구이동통계, 2024")
    save(fig, "02A_2024_자치구별_순이동자수_절대값.png")


def chart_02_rate_extremes(data):
    year = data[data["연도"] == 2024]
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.75))
    fig.subplots_adjust(left=.1, right=.95, bottom=.13, top=.78, wspace=.38)
    for ax, age, color in [(axes[0], "20대", BLUE), (axes[1], "30대", RED)]:
        col = f"{age}순이동률"
        part = pd.concat([year.nsmallest(4, col), year.nlargest(4, col)]).drop_duplicates().sort_values(col)
        colors = [LIGHT_RED if value < 0 else LIGHT_BLUE for value in part[col]]
        bars = ax.barh(part["자치구명"], part[col], color=colors)
        ax.axvline(0, color=DARK, linewidth=1)
        limit = max(abs(part[col].min()), abs(part[col].max()))
        for bar, value in zip(bars, part[col]):
            if abs(value) >= limit * .12:
                ax.text(
                    value - np.sign(value) * limit * .025,
                    bar.get_y() + bar.get_height() / 2,
                    f"{value:+.1f}",
                    ha="right" if value > 0 else "left", va="center",
                    fontsize=9, color=WHITE, fontweight="bold",
                )
            else:
                ax.text(
                    value + (limit * .025 if value >= 0 else -limit * .025),
                    bar.get_y() + bar.get_height() / 2,
                    f"{value:+.1f}",
                    ha="left" if value >= 0 else "right", va="center",
                    fontsize=9, color=DARK,
                )
        ax.set_xlim(part[col].min() - limit * .2, part[col].max() + limit * .2)
        ax.set_title(age, loc="left", color=color, fontsize=16)
        ax.set_xlabel("인구 1,000명당 순이동(명)")
        clean_axis(ax, grid="x")
    title(fig, "인구 규모를 고려해도 연령대별 유입·유출 지역은 달랐다", "2024년 연령대별 순이동률 상위 4개·하위 4개 자치구")
    source(fig, "KOSIS 인구이동통계·주민등록인구, 2024")
    save(fig, "02_2024_순이동률_상하위지역.png")


def migration_type(row):
    a20, a30 = row["20대순이동률"], row["30대순이동률"]
    if a20 >= 0 and a30 >= 0:
        return "동반 유입"
    if a20 >= 0 and a30 < 0:
        return "20대 유입·30대 유출"
    if a20 < 0 and a30 >= 0:
        return "20대 유출·30대 유입"
    return "동반 유출"


def chart_03_quadrant(data):
    year = data[data["연도"] == 2024].copy()
    year["이동유형"] = year.apply(migration_type, axis=1)
    color_map = {
        "동반 유입": GREEN,
        "20대 유입·30대 유출": BLUE,
        "20대 유출·30대 유입": ORANGE,
        "동반 유출": RED,
    }
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=.12, right=.94, bottom=.14, top=.78)
    for group, part in year.groupby("이동유형"):
        ax.scatter(part["20대순이동률"], part["30대순이동률"], s=85, color=color_map[group], label=f"{group} ({len(part)}개)", alpha=.9)
    ax.axhline(0, color=DARK, linewidth=1)
    ax.axvline(0, color=DARK, linewidth=1)
    highlight = {"노원구", "양천구", "관악구", "강동구", "강남구"}
    offsets = {
        "노원구": (6, 6), "양천구": (6, -12), "관악구": (6, 6),
        "강동구": (6, 6), "강남구": (6, 6),
    }
    for _, row in year[year["자치구명"].isin(highlight)].iterrows():
        ax.annotate(
            row["자치구명"], (row["20대순이동률"], row["30대순이동률"]),
            xytext=offsets[row["자치구명"]], textcoords="offset points",
            fontsize=9, color=DARK, fontweight="bold",
            bbox=dict(boxstyle="round,pad=.18", facecolor=WHITE, edgecolor="none", alpha=.88),
        )
    ax.set_xlabel("20대 인구 1,000명당 순이동(명)")
    ax.set_ylabel("30대 인구 1,000명당 순이동(명)")
    ax.legend(frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(.5, -0.27))
    clean_axis(ax)
    title(fig, "18개 구에서 20대는 들어오고 30대는 나갔다", "20대와 30대를 나눠 봐야 지역 차이가 보인다")
    source(fig, "KOSIS 인구이동통계·주민등록인구, 2024", "※ 자치구명은 발표에서 설명할 대표 지역만 표시")
    save(fig, "03_2024_20대30대_이동유형.png")


def scatter(ax, data, x, y, highlight, xlabel, color, label_offsets=None):
    ax.scatter(data[x], data[y], s=45, color=GRAY, edgecolor=WHITE)
    chosen = data[data["자치구명"].isin(highlight)]
    ax.scatter(chosen[x], chosen[y], s=90, color=color, edgecolor=WHITE, zorder=3)
    label_offsets = label_offsets or {}
    for _, row in chosen.iterrows():
        offset = label_offsets.get(row["자치구명"], (5, 5))
        ax.annotate(row["자치구명"], (row[x], row[y]), xytext=offset, textcoords="offset points", fontsize=9, color=DARK)
    slope, intercept = np.polyfit(data[x], data[y], 1)
    xs = np.linspace(data[x].min(), data[x].max(), 100)
    ax.plot(xs, slope * xs + intercept, color=DARK, linestyle="--", linewidth=1)
    ax.axhline(0, color=DARK, linewidth=1)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("인구 1,000명당 순이동(명)")
    clean_axis(ax)
    return data[x].corr(data[y])


def chart_04_relationships(data):
    year = data[data["연도"] == 2024]
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.75))
    fig.subplots_adjust(left=.08, right=.95, bottom=.13, top=.76, wspace=.28)
    r20 = scatter(
        axes[0], year, "15_29세_고용률", "20대순이동률",
        ["영등포구", "양천구", "노원구"], "20대 참고 고용률(15–29세, %)", BLUE,
        {"영등포구": (5, 5), "노원구": (5, 7), "양천구": (5, -14)},
    )
    r30 = scatter(
        axes[1], year, "전세환산주거비중앙값_만원", "30대순이동률",
        ["강동구", "관악구", "강남구"], "전세환산 주거비 중앙값(만원)", RED,
        {"강동구": (5, 5), "관악구": (5, 5), "강남구": (5, 5)},
    )
    axes[0].set_title(f"20대 최대 관련 지표: 참고 고용률  r={r20:.2f}", loc="left", fontsize=14, color=BLUE)
    axes[1].set_title(f"30대 최대 관련 지표: 전세환산 주거비  r={r30:.2f}", loc="left", fontsize=14, color=RED)
    title(fig, "20대 고용률은 함께 움직였고, 30대 주거비는 예상과 반대였다", "2024년 서울 25개 구 비교 · 상관관계만으로 원인을 판단할 수 없음")
    source(
        fig,
        "KOSIS·서울 열린데이터광장, 2024",
        "※ 고용률 연령 구간은 순이동 연령과 다름 · 전세환산 주거비는 5.0% 고정 전환율 적용",
    )
    save(fig, "04_2024_연령대별_관련지표.png")


def chart_05_district_comparison(data):
    year = data[data["연도"] == 2024].set_index("자치구명")
    districts = ["노원구", "양천구", "관악구", "강동구"]
    metrics = [
        ("20대순이동률", "20대 순이동률", "인구 1,000명당(명)", "rate"),
        ("30대순이동률", "30대 순이동률", "인구 1,000명당(명)", "rate"),
        ("전세환산주거비중앙값_만원", "전세환산 주거비 중앙값", "만원", "condition"),
        ("15_29세_고용률", "20대 참고 고용률(15–29세)", "%", "condition"),
        ("30_49세_고용률", "30대 참고 고용률(30–49세)", "%", "condition"),
        ("종사자수", "사업체 종사자수(절대값)", "명", "condition"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(12, 6.75))
    fig.subplots_adjust(left=.095, right=.96, bottom=.12, top=.76, hspace=.72, wspace=.42)
    district_colors = {"노원구": BLUE, "양천구": ORANGE, "관악구": GREEN, "강동구": "#8A6F9E"}
    for ax, (column, name, unit, kind) in zip(axes.flat, metrics):
        part = year.loc[districts, column].sort_values()
        colors = [district_colors[district] for district in part.index]
        bars = ax.barh(part.index, part.values, color=colors)
        if kind == "rate":
            ax.axvline(0, color=DARK, linewidth=1)
        else:
            ax.axvline(year[column].median(), color="#D7A83F", linewidth=1.8, linestyle="--")
        span = max(abs(part.min()), abs(part.max()), 1)
        for bar, value in zip(bars, part):
            label = f"{value:+.1f}" if kind == "rate" else (f"{value:,.0f}" if column == "종사자수" else f"{value:,.1f}" if unit == "%" else f"{value:,.0f}")
            if kind == "condition":
                x, ha, label_color = value - span * .025, "right", WHITE
            elif kind == "rate" and abs(value) > span * .23:
                x, ha, label_color = value / 2, "center", WHITE
            else:
                x = value + (span * .025 if value >= 0 else -span * .025)
                ha = "left" if value >= 0 else "right"
                label_color = DARK
            ax.text(x, bar.get_y() + bar.get_height() / 2, label, ha=ha, va="center", fontsize=8, color=label_color, fontweight="bold" if label_color == WHITE else "normal")
        if column == "종사자수":
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value/10000:.0f}만"))
            ax.set_xlim(0, part.max() * 1.18)
        ax.set_title(name, loc="left", fontsize=11.5)
        ax.set_xlabel(unit)
        ax.tick_params(axis="y", labelsize=8.5)
        clean_axis(ax, grid="x")
    title(fig, "네 지역은 이동 모습과 주거·일자리 조건이 달랐다", "노원·양천(동반 유출), 관악(20대 유입·30대 유출), 강동(동반 유입) 비교")
    source(
        fig,
        "KOSIS·서울 열린데이터광장, 2024",
        "※ 노란 점선은 서울 25개 구 중앙값 · 고용률은 참고 연령 구간 · 종사자수는 근무지 기준 절대값",
    )
    save(fig, "05_대표자치구_이동환경비교.png")


def main():
    data = pd.read_csv(DATA_PATH)
    chart_01_yearly_flow(data)
    chart_02_absolute_flow(data)
    chart_02_rate_extremes(data)
    chart_03_quadrant(data)
    chart_04_relationships(data)
    chart_05_district_comparison(data)
    print("PPT용 시각화를 모두 만들었습니다.")


if __name__ == "__main__":
    main()
