from pathlib import Path

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# 컬러 팔레트
COLORS = {
    "mint": "#35D6B4",
    "magenta": "#F04E98",
    "lemon": "#F4E44D",
    "purple": "#8B6CEF",
    "blue": "#4D96FF",
    "orange": "#FF8A4C",
    "navy": "#25324B",
    "gray": "#6B7280",
    "light_mint": "#E8FAF5",
    "light_pink": "#FDEAF3",
    "light_lemon": "#FFFBE0"
}

CHART_PALETTE = [
    COLORS["mint"],
    COLORS["magenta"],
    COLORS["lemon"],
    COLORS["purple"],
    COLORS["blue"],
    COLORS["orange"]
]

sns.set_theme(
    style="whitegrid",
    palette=CHART_PALETTE,
    rc={
        "axes.edgecolor": "#E5E7EB",
        "axes.labelcolor": COLORS["navy"],
        "axes.titlecolor": COLORS["navy"],
        "xtick.color": COLORS["gray"],
        "ytick.color": COLORS["gray"],
        "grid.color": "#EEF0F4",
        "grid.linewidth": 0.8
    }
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "seoul_youth_migration_analysis_2021_2024.csv"
)


st.set_page_config(
    page_title="서울 청년 인구이동 분석",
    page_icon="🏙️",
    layout="wide"
)

def style_chart(ax, title, xlabel="", ylabel=""):
    ax.set_title(
        title,
        loc="left",
        fontsize=14,
        fontweight="bold",
        color=COLORS["navy"],
        pad=16
    )

    ax.set_xlabel(xlabel, labelpad=10)
    ax.set_ylabel(ylabel, labelpad=10)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#DDE1E8")
    ax.spines["bottom"].set_color("#DDE1E8")

    ax.grid(
        axis="y",
        color="#EEF0F4",
        linewidth=0.8
    )

    ax.set_axisbelow(True)

st.markdown(
    """
    <style>
    /* 전체 콘텐츠 너비와 여백 */
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* 기본 글자 */
    html, body, [class*="css"] {
        color: #25324B;
    }

    /* 메인 제목 */
    h1 {
        color: #25324B;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.04em;
        margin-bottom: 0.4rem !important;
    }

    /* 섹션 제목 */
    h2, h3 {
        color: #25324B;
        font-weight: 750 !important;
        letter-spacing: -0.025em;
    }

    h3 {
        margin-top: 1.5rem !important;
    }

    /* 설명 문구 */
    p {
        line-height: 1.7;
    }

    /* 지표 카드 */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E8EAF0;
        border-top: 4px solid #35D6B4;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 14px rgba(37, 50, 75, 0.06);
    }

    [data-testid="stMetricLabel"] {
        color: #6B7280;
        font-size: 0.9rem;
    }

    [data-testid="stMetricValue"] {
        color: #25324B;
        font-weight: 800;
    }

    /* 탭 */
    button[data-baseweb="tab"] {
        background-color: #F5F6F8;
        border-radius: 10px;
        padding: 10px 18px;
        margin-right: 6px;
        color: #6B7280;
        font-weight: 650;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #E8FAF5;
        color: #167D68;
    }

    /* 안내 박스 */
    [data-testid="stAlert"] {
        border-radius: 12px;
        border: none;
        line-height: 1.65;
    }

    /* 데이터 표 */
    [data-testid="stDataFrame"] {
        border: 1px solid #E8EAF0;
        border-radius: 12px;
        overflow: hidden;
    }

    /* 입력 요소 */
    [data-baseweb="select"] > div {
        border-radius: 10px;
        border-color: #DDE1E8;
    }

    /* 구분선 */
    hr {
        margin-top: 2.5rem;
        margin-bottom: 2.5rem;
        border-color: #ECEEF2;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH)
    return data


data = load_data()

sns.set_theme(style="whitegrid")
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


st.title("🏙️ 서울 청년 인구이동 분석 대시보드")
st.caption(
    "2021년부터 2024년까지 서울시 25개 자치구의 "
    "20대·30대 인구이동과 주거 및 고용 지표를 분석합니다."
)


# 사이드바
st.sidebar.header("조회 조건")

selected_year = st.sidebar.selectbox(
    "연도를 선택하세요",
    sorted(data["연도"].unique()),
    index=3
)

selected_age = st.sidebar.radio(
    "연령대를 선택하세요",
    ["20대", "30대"]
)

year_data = data[data["연도"] == selected_year].copy()

if selected_age == "20대":
    count_column = "20대순이동자수"
    rate_column = "20대인구천명당순이동자수"
    employment_column = "15_29세_고용률"
    employment_name = "15~29세 고용률"
    main_color = "#4C78A8"

else:
    count_column = "30대순이동자수"
    rate_column = "30대인구천명당순이동자수"
    employment_column = "30_49세_고용률"
    employment_name = "30~49세 고용률"
    main_color = "#59A14F"


# 주요 지표
total_migration = int(year_data[count_column].sum())
average_rate = year_data[rate_column].mean()

top_district = year_data.loc[
    year_data[rate_column].idxmax(),
    "자치구명"
]

bottom_district = year_data.loc[
    year_data[rate_column].idxmin(),
    "자치구명"
]

st.subheader(f"{selected_year}년 {selected_age} 인구이동 현황")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "서울 전체 순이동자 수",
    f"{total_migration:,}명"
)

col2.metric(
    "자치구 평균 순이동자 수",
    f"{average_rate:.1f}명",
    help="해당 연령대 인구 1,000명당 순이동자 수의 자치구 평균입니다."
)

col3.metric(
    "순유입 상위 지역",
    top_district
)

col4.metric(
    "순이동 하위 지역",
    bottom_district
)


st.divider()


# 연도별 순이동자 수
st.subheader("연도별 20대·30대 순이동자 수")

yearly_data = (
    data.groupby("연도")[
        ["20대순이동자수", "30대순이동자수"]
    ]
    .sum()
    .reset_index()
)

yearly_long = yearly_data.melt(
    id_vars="연도",
    var_name="연령대",
    value_name="순이동자수"
)

yearly_long["연령대"] = yearly_long["연령대"].replace({
    "20대순이동자수": "20대",
    "30대순이동자수": "30대"
})

fig1, ax1 = plt.subplots(figsize=(10, 5))

sns.barplot(
    data=yearly_long,
    x="연도",
    y="순이동자수",
    hue="연령대",
    palette=["#4C78A8", "#F2B134"],
    ax=ax1
)

ax1.axhline(0, color="black", linewidth=1)
ax1.set_xlabel("연도")
ax1.set_ylabel("순이동자 수(명)")
ax1.set_title("연도별 서울 20대·30대 순이동자 수")
ax1.legend(title="연령대")

st.pyplot(fig1)
plt.close(fig1)


# 자치구별 그래프와 순위
left, right = st.columns([2, 1])

with left:
    st.subheader(
        f"{selected_year}년 자치구별 {selected_age} 순이동 현황"
    )

    district_data = year_data.sort_values(
        rate_column,
        ascending=True
    )

    bar_colors = [
        "#E76F51" if value < 0 else main_color
        for value in district_data[rate_column]
    ]

    fig2, ax2 = plt.subplots(figsize=(10, 9))

    ax2.barh(
        district_data["자치구명"],
        district_data[rate_column],
        color=bar_colors
    )

    ax2.axvline(0, color="black", linewidth=1)
    ax2.set_xlabel("인구 1,000명당 순이동자 수")
    ax2.set_ylabel("자치구")
    ax2.set_title(
        f"{selected_year}년 자치구별 "
        f"{selected_age} 인구 1,000명당 순이동자 수"
    )

    st.pyplot(fig2)
    plt.close(fig2)


with right:
    st.subheader("순이동 상위 5개 구")

    top5 = year_data.nlargest(
        5,
        rate_column
    )[["자치구명", rate_column]].copy()

    top5.columns = [
        "자치구",
        "인구 1,000명당 순이동자 수"
    ]

    top5["인구 1,000명당 순이동자 수"] = (
        top5["인구 1,000명당 순이동자 수"].round(2)
    )

    st.dataframe(
        top5,
        hide_index=True,
        uwidth="stretch"
    )

    st.subheader("순이동 하위 5개 구")

    bottom5 = year_data.nsmallest(
        5,
        rate_column
    )[["자치구명", rate_column]].copy()

    bottom5.columns = [
        "자치구",
        "인구 1,000명당 순이동자 수"
    ]

    bottom5["인구 1,000명당 순이동자 수"] = (
        bottom5["인구 1,000명당 순이동자 수"].round(2)
    )

    st.dataframe(
        bottom5,
        hide_index=True,
        width="stretch"
    )


st.divider()

# 고용 지표와 순이동 관계
st.subheader(f"{employment_name}과 {selected_age} 순이동의 관계")

correlation = data[
    [employment_column, rate_column]
].corr().iloc[0, 1]

fig3, ax3 = plt.subplots(figsize=(10, 6))

sns.scatterplot(
    data=data,
    x=employment_column,
    y=rate_column,
    hue="연도",
    palette="viridis",
    s=80,
    ax=ax3
)

sns.regplot(
    data=data,
    x=employment_column,
    y=rate_column,
    scatter=False,
    color="gray",
    line_kws={"linestyle": "--"},
    ax=ax3
)

ax3.axhline(0, color="black", linewidth=0.8)
ax3.set_xlabel(f"{employment_name}(%)")
ax3.set_ylabel(
    f"{selected_age} 인구 1,000명당 순이동자 수"
)
ax3.set_title(
    f"{employment_name}과 {selected_age} 순이동의 관계"
)

ax3.text(
    0.03,
    0.95,
    f"상관계수: {correlation:.3f}",
    transform=ax3.transAxes,
    fontsize=11,
    verticalalignment="top"
)

ax3.legend(title="연도")

st.pyplot(fig3)
plt.close(fig3)

if selected_age == "20대":
    st.info(
        "15~29세 고용률이 높은 자치구일수록 "
        "20대 순유입이 높은 경향이 나타납니다. "
        "다만 상관관계만으로 인과관계를 단정할 수는 없습니다."
    )

else:
    st.info(
        "30~49세 고용률과 30대 순이동의 관계는 "
        "20대보다 뚜렷하지 않습니다. "
        "30대 순이도은 2023년 이후 전세보증금과 양의 상관관계가 "
        "나타났지만, 상관관계만으로 주거비가 이동의 원인이라고 "
        "단정할 수는 없습니다."
    )


st.divider()

st.divider()


# 추가 인사이트 분석
st.subheader("이동 패턴 심층 분석")
st.caption(
    "연도별 관계 변화와 자치구별 이동 유형을 통해 "
    "20대와 30대의 이동 차이를 비교합니다."
)

tab1, tab2, tab3 = st.tabs([
    "연도별 관계 변화",
    "연령대별 이동 유형",
    "상·하위 지역 특성"
])


# 1. 연도별 상관관계
with tab1:
    yearly_correlation = []

    for year in sorted(data["연도"].unique()):
        year_data_corr = data[data["연도"] == year]

        correlation_20 = year_data_corr[
            ["15_29세_고용률", "20대인구천명당순이동자수"]
        ].corr().iloc[0, 1]

        correlation_30 = year_data_corr[
            ["전세보증금중앙값_만원", "30대인구천명당순이동자수"]
        ].corr().iloc[0, 1]

        yearly_correlation.append({
            "연도": year,
            "20대 고용률": correlation_20,
            "30대 전세보증금": correlation_30
        })

    yearly_correlation = pd.DataFrame(yearly_correlation)

    correlation_long = yearly_correlation.melt(
        id_vars="연도",
        var_name="분석 항목",
        value_name="상관계수"
    )

    fig5, ax5 = plt.subplots(figsize=(10, 5))

    sns.lineplot(
        data=correlation_long,
        x="연도",
        y="상관계수",
        hue="분석 항목",
        marker="o",
        linewidth=2.5,
        palette={
            "20대 고용률": COLORS["mint"],
            "30대 전세보증금": COLORS["magenta"]
        },
        ax=ax5
    )

    ax5.axhline(0, color="black", linewidth=0.8)
    ax5.set_ylim(-1, 1)
    ax5.set_xticks(yearly_correlation["연도"])
    ax5.set_title("연도별 주요 변수와 순이동의 상관계수")
    ax5.set_ylabel("상관계수")
    ax5.legend(title="분석 항목")

    st.pyplot(fig5)
    plt.close(fig5)

    st.dataframe(
        yearly_correlation.round(3),
        hide_index=True,
        width="stretch"
    )

    st.info(
        "20대 순이동과 청년층 고용률은 모든 연도에서 "
        "양의 상관관계가 나타났습니다. 반면 30대 순이동과 "
        "전세보증금의 관계는 2023년 이후 크게 높아졌습니다."
    )


# 2. 선택 연도의 이동 유형
with tab2:
    type_data = data[data["연도"] == selected_year].copy()

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

    type_data["이동유형"] = type_data.apply(
        classify_migration,
        axis=1
    )

    type_count = (
        type_data["이동유형"]
        .value_counts()
        .reset_index()
    )

    type_count.columns = ["이동유형", "자치구 수"]

    left_type, right_type = st.columns([1, 2])

    with left_type:
        st.write(f"**{selected_year}년 유형별 자치구 수**")

        st.dataframe(
            type_count,
            hide_index=True,
            width="stretch"
        )

    with right_type:
        type_table = type_data[
            [
                "자치구명",
                "20대인구천명당순이동자수",
                "30대인구천명당순이동자수",
                "이동유형"
            ]
        ].copy()

        type_table.columns = [
            "자치구",
            "20대 순이동",
            "30대 순이동",
            "이동유형"
        ]

        st.dataframe(
            type_table.sort_values("이동유형").round(2),
            hide_index=True,
            width="stretch"
        )

    if selected_year == 2024:
        st.info(
            "2024년에는 25개 자치구 중 18개 구에서 "
            "20대 유입과 30대 유출이 동시에 나타났습니다. "
            "20대와 30대의 이동 지역이 서로 다르다는 점이 "
            "서울 청년 인구이동의 주요 특징입니다."
        )


# 3. 선택 연령대 상·하위 지역 비교
with tab3:
    comparison_columns = {
        "전세보증금중앙값_만원": "전세보증금(만원)",
        "월세중앙값_만원": "월세(만원)",
        "월세거래건수": "월세 거래 건수",
        "종사자수": "종사자 수",
        "15_29세_고용률": "15~29세 고용률(%)",
        "30_49세_고용률": "30~49세 고용률(%)"
    }

    top5 = year_data.nlargest(5, rate_column)
    bottom5 = year_data.nsmallest(5, rate_column)

    comparison = pd.DataFrame({
        "지표": comparison_columns.values(),
        "상위 5개 구 평균":
            top5[list(comparison_columns.keys())].mean().values,
        "하위 5개 구 평균":
            bottom5[list(comparison_columns.keys())].mean().values
    })

    comparison["평균 차이"] = (
        comparison["상위 5개 구 평균"]
        - comparison["하위 5개 구 평균"]
    )

    st.write(
        f"**{selected_year}년 {selected_age} 순이동 수치 "
        "상위·하위 5개 구의 특성 비교**"
    )

    st.dataframe(
        comparison.round(2),
        hide_index=True,
        width="stretch"
    )

    if selected_year == 2024 and selected_age == "20대":
        st.info(
            "20대 순이동 상위 5개 구는 하위 5개 구보다 "
            "15~29세 고용률이 평균 11.58%p 높고, "
            "종사자 수도 평균 170,148명 많았습니다."
        )

    elif selected_year == 2024 and selected_age == "30대":
        st.info(
            "30대 순이동 수치 상위 5개 구는 하위 5개 구보다 "
            "전세보증금이 평균 21,351만 원 높고, "
            "종사자 수도 평균 255,460명 많았습니다. "
            "이는 집값이 30대 유입의 원인이라는 뜻은 아니며, "
            "지역별 특성이 함께 반영된 결과일 수 있습니다."
        )

# 자치구 상세 조회
st.subheader("자치구 상세 조회")
st.caption(
    "선택한 자치구의 연도별 순이동 변화와 주요 지표를 확인합니다."
)

selected_district = st.selectbox(
    "자치구를 선택하세요",
    sorted(data["자치구명"].unique())
)

district_detail = data[
    data["자치구명"] == selected_district
].sort_values("연도")

col5, col6 = st.columns(2)

with col5:
    fig4, ax4 = plt.subplots(figsize=(8, 5))

    ax4.plot(
        district_detail["연도"],
        district_detail["20대인구천명당순이동자수"],
        marker="o",
        markersize=7,
        linewidth=2.5,
        label="20대",
        color=COLORS["mint"]

    )

    ax4.plot(
        district_detail["연도"],
        district_detail["30대인구천명당순이동자수"],
        marker="o",
        markersize=7,
        linewidth=2.5,
        label="30대",
        color=COLORS["magenta"]
    )

    ax4.axhline(0, color=COLORS["navy"], linewidth=1, linestyle="--", alpha=0.7)
    ax4.set_xticks(district_detail["연도"])
    ax4.legend()

    st.pyplot(fig4)
    plt.close(fig4)


with col6:
    detail_columns = [
        "연도",
        "20대인구천명당순이동자수",
        "30대인구천명당순이동자수",
        "전세보증금중앙값_만원",
        "월세중앙값_만원",
        "15_29세_고용률",
        "30_49세_고용률"
    ]

    detail_table = district_detail[detail_columns].copy()

    detail_table.columns = [
        "연도",
        "20대 순이동",
        "30대 순이동",
        "전세보증금(만원)",
        "월세(만원)",
        "15~29세 고용률",
        "30~49세 고용률"
    ]

    st.dataframe(
        detail_table.round(2),
        hide_index=True,
        width="stretch"
    )


st.divider()

st.caption(
    "순이동자 수는 전입자 수에서 전출자 수를 뺀 값입니다. "
    "양수는 순유입, 음수는 순유출을 의미합니다."
)