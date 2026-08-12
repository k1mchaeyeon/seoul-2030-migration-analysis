from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st


# -----------------------------------------------------------------------------
# 기본 설정
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_CANDIDATES = [
    BASE_DIR / "data" / "processed" / "seoul_youth_final_2021_2024.csv",
    BASE_DIR / "data" / "processed" / "seoul_youth_migration_analysis_2021_2024.csv",
]

INFLOW = "#3F6F9F"
OUTFLOW = "#B85C5C"
ACCENT = "#315A7D"
MUTED = "#B8C1CC"
TEXT = "#28323C"
GRID = "#E8EBEF"
JOB = "#657D61"
HOUSING = "#8A6F58"

st.set_page_config(
    page_title="서울 청년 인구이동 분석",
    page_icon="🏙️",
    layout="wide",
)

sns.set_theme(style="whitegrid")
plt.rcParams["font.family"] = ["AppleGothic", "Malgun Gothic", "NanumGothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

st.markdown(
    """
    <style>
    .block-container {max-width: 1100px; padding-top: 1.2rem; padding-bottom: 3rem;}
    h1, h2, h3 {color:#28323C; letter-spacing:-0.025em;}
    [data-testid="stMetric"] {
        background:#FFFFFF; border:1px solid #E3E7EB; border-radius:8px;
        padding:11px 14px; min-height:112px; box-shadow:none;
    }
    [data-testid="stMetricLabel"] {color:#67727E; font-size:.82rem;}
    [data-testid="stMetricValue"] {color:#28323C; font-size:1.65rem; font-weight:750;}
    [data-testid="stAlert"] {border-radius:7px; box-shadow:none;}
    .current-filter {
        padding:12px 16px; background:#F4F6F8; border-left:4px solid #315A7D;
        color:#34404B; margin:.5rem 0 1.5rem;
    }
    .result-box {
        padding:15px 18px; background:#EEF4F8; border-left:4px solid #3F6F9F;
        border-radius:6px; color:#28323C; line-height:1.65; margin:.6rem 0 1rem;
    }
    .policy-box {
        padding:15px 18px; background:#F5F5F2; border-left:4px solid #657D61;
        border-radius:6px; color:#28323C; line-height:1.65; margin:.6rem 0 1rem;
    }
    hr {margin:2.3rem 0; border-color:#E8EBEF;}
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 공통 함수
# -----------------------------------------------------------------------------
def style_axis(ax, title, xlabel="", ylabel="", grid_axis="both"):
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", color=TEXT, pad=14)
    ax.set_xlabel(xlabel, labelpad=9)
    ax.set_ylabel(ylabel, labelpad=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#C8CED5")
    ax.grid(False)
    ax.grid(axis=grid_axis, color=GRID, linewidth=.8)
    ax.set_axisbelow(True)


def migration_status(value):
    if value > 0:
        return "순유입"
    if value < 0:
        return "순유출"
    return "순이동 없음"


def corr_strength(value):
    if pd.isna(value):
        return "계산 불가"
    value = abs(value)
    if value < .2:
        return "거의 관계 없음"
    if value < .4:
        return "약한 관계"
    if value < .6:
        return "보통 관계"
    if value < .8:
        return "강한 관계"
    return "매우 강한 관계"


def corr_direction(value):
    if pd.isna(value) or abs(value) < .001:
        return "뚜렷한 방향 없음"
    return "양의 관계" if value > 0 else "음의 관계"


def safe_corr(frame, x, y):
    valid = frame[[x, y]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(valid) < 3 or valid[x].nunique() < 2 or valid[y].nunique() < 2:
        return np.nan
    return valid[x].corr(valid[y])


def pct_difference(top_value, bottom_value):
    if pd.isna(bottom_value) or bottom_value == 0:
        return np.nan
    return (top_value - bottom_value) / abs(bottom_value) * 100


def add_point_labels(ax, frame, x, y, names, limit=None):
    label_frame = frame.copy()
    if limit and len(label_frame) > limit:
        label_frame["_distance"] = (
            (label_frame[x] - label_frame[x].median()).abs() / (label_frame[x].std() or 1)
            + (label_frame[y] - label_frame[y].median()).abs() / (label_frame[y].std() or 1)
        )
        label_frame = label_frame.nlargest(limit, "_distance")
    for _, row in label_frame.iterrows():
        ax.annotate(
            row[names], (row[x], row[y]), xytext=(4, 4),
            textcoords="offset points", fontsize=8, color=TEXT,
        )


def classify_migration(row):
    age20 = row["20대인구천명당순이동자수"]
    age30 = row["30대인구천명당순이동자수"]
    if pd.isna(age20) or pd.isna(age30):
        return "자료 없음"
    if age20 >= 0 and age30 >= 0:
        return "20·30대 동반 유입형"
    if age20 >= 0 and age30 < 0:
        return "20대 유입·30대 유출형"
    if age20 < 0 and age30 >= 0:
        return "20대 유출·30대 유입형"
    return "20·30대 동반 유출형"


@st.cache_data
def load_data():
    path = next((candidate for candidate in DATA_CANDIDATES if candidate.exists()), None)
    if path is None:
        st.error(
            "분석 CSV를 찾을 수 없습니다. `02_preprocessing.py`를 먼저 실행한 뒤 "
            "결과 파일을 `data/processed` 폴더에 넣어 주세요."
        )
        st.stop()

    frame = pd.read_csv(path)

    required = {
        "연도", "자치구명", "20대순이동자수", "30대순이동자수",
        "20대인구천명당순이동자수", "30대인구천명당순이동자수",
        "전월세월환산주거비중앙값_만원", "전월세거래건수",
        "종사자수", "전체주민등록인구", "일자리집중도_인구천명당종사자수",
        "15_29세_고용률", "30_49세_고용률",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        st.error(
            "최종 대시보드에 필요한 컬럼이 없습니다: " + ", ".join(missing)
            + "\n\n수정된 `02_preprocessing.py`로 데이터를 다시 생성해 주세요."
        )
        st.stop()

    frame["연도"] = pd.to_numeric(frame["연도"], errors="coerce").astype("Int64")
    frame = frame[frame["연도"].between(2021, 2024)].copy()
    return frame


data = load_data()


# -----------------------------------------------------------------------------
# 0. 필터
# -----------------------------------------------------------------------------
st.title("서울 청년 인구이동 분석 대시보드")
st.caption(
    "서울 25개 자치구의 20대·30대 순이동과 전월세 주거비·고용·일자리 환경을 "
    "비교하여 정책 우선 검토 지역을 찾습니다."
)

years = sorted(data["연도"].dropna().astype(int).unique())
districts = sorted(data["자치구명"].dropna().unique())

filter1, filter2, filter3 = st.columns([1, 1, 1.5])
with filter1:
    selected_year = st.selectbox("기준 연도", years, index=len(years) - 1)
with filter2:
    selected_age = st.selectbox("연령대", ["20대", "30대"])
with filter3:
    selected_factor = st.selectbox(
        "분석 지표",
        ["전월세 월환산 주거비", "고용률", "일자리 집중도"],
    )

st.markdown(
    f'<div class="current-filter">현재 분석 기준: <b>{selected_year}년 · '
    f'{selected_age} · {selected_factor}</b></div>',
    unsafe_allow_html=True,
)

year_data = data[data["연도"] == selected_year].copy()
if selected_age == "20대":
    count_col = "20대순이동자수"
    rate_col = "20대인구천명당순이동자수"
    employment_col = "15_29세_고용률"
    employment_name = "15~29세 고용률"
else:
    count_col = "30대순이동자수"
    rate_col = "30대인구천명당순이동자수"
    employment_col = "30_49세_고용률"
    employment_name = "30~49세 고용률"

factor_map = {
    "전월세 월환산 주거비": (
        "전월세월환산주거비중앙값_만원", "전월세 월환산 주거비 중앙값(만원/월)"
    ),
    "고용률": (employment_col, f"거주지 기준 {employment_name}(%)"),
    "일자리 집중도": (
        "일자리집중도_인구천명당종사자수",
        "주민 1,000명당 사업체 종사자 수(명)"
    ),
}
factor_col, factor_axis_label = factor_map[selected_factor]


quadrant = year_data[[
    "자치구명", "20대인구천명당순이동자수", "30대인구천명당순이동자수"
]].dropna().copy()
quadrant["이동유형"] = quadrant.apply(classify_migration, axis=1)


# -----------------------------------------------------------------------------
# 화면 메뉴
# -----------------------------------------------------------------------------
selected_page = st.radio(
    "분석 화면",
    ["현재 현황", "영향 요인", "지역 비교", "정책 검토"],
    horizontal=True,
    label_visibility="collapsed",
)
st.caption("위 메뉴를 클릭하면 필요한 분석 화면만 볼 수 있습니다.")


if selected_page == "현재 현황":
    # -----------------------------------------------------------------------------
    # 1~2. KPI와 산식
    # -----------------------------------------------------------------------------
    st.header("1. 현재 상태")
    total_migration = year_data[count_col].sum()
    average_rate = year_data[rate_col].mean()
    positive_count = int((year_data[rate_col] >= 0).sum())
    negative_count = int((year_data[rate_col] < 0).sum())
    top = year_data.loc[year_data[rate_col].idxmax()]
    bottom = year_data.loc[year_data[rate_col].idxmin()]

    k1, k2, k3 = st.columns(3)
    k1.metric(f"서울 {selected_age} 순이동자", f"{total_migration:+,.0f}명", help="25개 자치구 순이동자 수 합계")
    k2.metric("평균 순이동률", f"{average_rate:+.1f}명", help="자치구 평균, 인구 1,000명당 명")
    k3.metric("순유입 / 순유출 자치구", f"{positive_count}개 / {negative_count}개")
    k4, k5, k6 = st.columns(3)
    k4.metric("최대 순유입 지역", top["자치구명"], f"{top[rate_col]:+.1f}명/1,000명")
    k5.metric("최대 순유출 지역", bottom["자치구명"], f"{bottom[rate_col]:+.1f}명/1,000명")
    k6.metric("분석 자치구", "25개 구", help="서울특별시 전체 자치구")

    st.markdown(
        f'<div class="result-box"><b>현재 상태</b><br>{selected_year}년 서울 {selected_age}는 '
        f'25개 자치구 중 {positive_count}개 구에서 순유입됐으며, '
        f'{top["자치구명"]}의 순이동률이 인구 1,000명당 {top[rate_col]:+.1f}명으로 가장 높았습니다.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("지표 산출 기준 보기"):
        st.markdown(
            rf"""
            **인구 1,000명당 순이동자 수**  
            $\\displaystyle 순이동률=\\frac{{전입자수-전출자수}}{{연앙\ 청년인구}}\\times1,000$

            - 단위: 인구 1,000명당 명 / 양수는 순유입, 음수는 순유출
            - 연앙 청년인구 = (전년도 말 인구 + 해당 연도 말 인구) ÷ 2

            **전월세 월환산 주거비**  
            $\\displaystyle 월환산\ 주거비=월세액+\\frac{{보증금\\times 전월세전환율}}{{12}}$

            - 단위: 만원/월, 자치구·연도별 계약의 중앙값
            - 전세와 월세를 단순 합산하지 않고 동일한 월 비용 단위로 환산
            - 연도 말 법정 전월세전환율 적용: 2021년 3.00%, 2022년 5.25%, 2023년 5.50%, 2024년 5.00%
            - 전월세 자료는 계약자의 연령을 제공하지 않아 전 연령 계약을 포함

            **거주지 기준 고용률**  
            $\\displaystyle 고용률=\\frac{{해당\ 연령대\ 취업자수}}{{해당\ 연령대\ 인구}}\\times100$

            - 단위: %, 20대 분석에는 15~29세, 30대 분석에는 30~49세 고용률 사용
            - 순이동 연령 구간과 정확히 일치하지 않는 한계가 있음

            **일자리 집중도**  

            $\\displaystyle 일자리\\ 집중도=\\frac{{사업체\\ 종사자\\ 수}}{{전체\\ 주민등록인구}}\\times1,000$

            - 단위: 주민 1,000명당 종사자 수(명)
            - 분자는 자치구 소재 사업체의 근무지 기준 종사자 수
            - 분모는 각 연도 말 전체 주민등록인구(외국인 제외)
            """
        )

    st.divider()


if selected_page == "영향 요인":
    # -----------------------------------------------------------------------------
    # 3. 세 환경지표 상관계수 비교
    # -----------------------------------------------------------------------------
    st.header("2. 청년 순이동은 어떤 지역 환경과 관련이 있을까?")
    corr_specs = [
        ("전월세 월환산 주거비", "전월세월환산주거비중앙값_만원"),
        (employment_name, employment_col),
        ("일자리 집중도", "일자리집중도_인구천명당종사자수"),
    ]
    corr_table = pd.DataFrame(
        [{"지표": name, "상관계수": safe_corr(year_data, col, rate_col)} for name, col in corr_specs]
    ).dropna(subset=["상관계수"])

    if corr_table.empty:
        st.warning("유효한 관측값이 부족해 환경지표 상관계수를 계산할 수 없습니다.")
    else:
        strongest = corr_table.loc[corr_table["상관계수"].abs().idxmax()]
        corr_plot = corr_table.sort_values("상관계수")
        colors = [ACCENT if name == strongest["지표"] else MUTED for name in corr_plot["지표"]]
        fig, ax = plt.subplots(figsize=(7.4, 3.1))
        bars = ax.barh(corr_plot["지표"], corr_plot["상관계수"], color=colors)
        ax.axvline(0, color=TEXT, linewidth=1)
        ax.set_xlim(-1, 1)
        ax.bar_label(bars, labels=[f"{corr_strength(v)} {corr_direction(v)}" for v in corr_plot["상관계수"]], padding=4, fontsize=10)
        style_axis(
            ax,
            f"{selected_year}년 {selected_age} 순이동은 {strongest['지표']}과 가장 큰 관련성을 보임",
            "관련성의 방향과 정도  ← 반대 방향 | 같은 방향 →",
            "",
            "x",
        )
        st.pyplot(fig, use_container_width=False)
        plt.close(fig)
        st.caption("막대가 가운데에서 멀수록 두 지표가 함께 움직이는 경향이 큽니다. 이는 원인을 뜻하지 않습니다.")
        st.markdown(
            f'<div class="result-box"><b>분석 결과</b><br>{strongest["지표"]}이 '
            f'{selected_age} 순이동률과 가장 높은 관련성을 보였습니다 '
            f'({corr_strength(strongest["상관계수"])} · {corr_direction(strongest["상관계수"])}).</div>',
            unsafe_allow_html=True,
        )


if selected_page == "영향 요인":
    # -----------------------------------------------------------------------------
    # 4. 선택 지표 산점도
    # -----------------------------------------------------------------------------
    st.subheader("선택 지표 세부 분석")
    relation = year_data[["자치구명", factor_col, rate_col]].replace([np.inf, -np.inf], np.nan).dropna()
    r_value = safe_corr(relation, factor_col, rate_col)

    if len(relation) < 3 or pd.isna(r_value):
        st.warning("선택한 지표의 유효한 자치구 자료가 부족합니다.")
    else:
        point_colors = [INFLOW if value >= 0 else OUTFLOW for value in relation[rate_col]]
        fig, ax = plt.subplots(figsize=(7.2, 4.2))
        ax.scatter(relation[factor_col], relation[rate_col], c=point_colors, s=68, alpha=.88, edgecolor="white")
        if relation[factor_col].nunique() >= 2:
            slope, intercept = np.polyfit(relation[factor_col], relation[rate_col], 1)
            xs = np.linspace(relation[factor_col].min(), relation[factor_col].max(), 100)
            ax.plot(xs, slope * xs + intercept, color=TEXT, linestyle="--", linewidth=1.3)
        ax.axhline(0, color=TEXT, linewidth=1)
        add_point_labels(ax, relation, factor_col, rate_col, "자치구명", limit=10)
        trend_word = "높은" if r_value > 0 else "낮은"
        style_axis(
            ax,
            f"{selected_factor}이 높은 자치구일수록 {selected_age} 순이동률이 {trend_word} 경향 · "
            f"{corr_strength(r_value)} · {corr_direction(r_value)}",
            factor_axis_label,
            f"{selected_age} 인구 1,000명당 순이동자 수(명)",
        )
        st.pyplot(fig, use_container_width=False)
        plt.close(fig)
        st.caption(
            "점 하나는 서울의 자치구 한 곳입니다. 파란색은 순유입, 붉은색은 순유출이며 "
            "점선은 전체 경향을 나타냅니다."
        )
        st.markdown(
            '<div class="policy-box"><b>해석 주의</b><br>상관관계는 자치구 특성이 함께 나타나는 '
            '경향을 보여줄 뿐, 개인의 이사 원인이나 정책 효과를 직접 증명하지 않습니다.</div>',
            unsafe_allow_html=True,
        )

    st.divider()


if selected_page == "지역 비교":
    # -----------------------------------------------------------------------------
    # 5. 상·하위 5개 구 비교
    # -----------------------------------------------------------------------------
    st.header("3. 순이동 상위·하위 지역은 무엇이 다를까?")
    top5 = year_data.nlargest(5, rate_col)
    bottom5 = year_data.nsmallest(5, rate_col)

    comparison_rows = []
    for label, column, unit, group in [
        ("전월세 월환산 주거비", "전월세월환산주거비중앙값_만원", "%", "주거"),
        ("일자리 집중도", "일자리집중도_인구천명당종사자수", "%", "고용·일자리"),
        (employment_name, employment_col, "%p", "고용·일자리"),
    ]:
        top_mean = top5[column].mean()
        bottom_mean = bottom5[column].mean()
        difference = top_mean - bottom_mean if unit == "%p" else pct_difference(top_mean, bottom_mean)
        comparison_rows.append({"지표": label, "차이": difference, "단위": unit, "분류": group})

    comparison = pd.DataFrame(comparison_rows).dropna(subset=["차이"])
    if comparison.empty:
        st.warning("상·하위 지역 특성 비교에 필요한 자료가 부족합니다.")
    else:
        fig, ax = plt.subplots(figsize=(7.4, 3.2))
        comp_colors = [HOUSING if group == "주거" else JOB for group in comparison["분류"]]
        bars = ax.barh(comparison["지표"], comparison["차이"], color=comp_colors)
        ax.axvline(0, color=TEXT, linewidth=1)
        labels = [f"{v:+.1f}{u}" for v, u in zip(comparison["차이"], comparison["단위"])]
        ax.bar_label(bars, labels=labels, padding=4, fontsize=10)
        strongest_diff = comparison.loc[comparison["차이"].abs().idxmax(), "지표"]
        style_axis(
            ax,
            f"{selected_year}년 {selected_age} 순이동 상·하위 지역의 가장 큰 차이는 {strongest_diff}",
            "하위 5개 구 대비 상위 5개 구의 차이  ← 낮음 | 높음 →",
            "",
            "x",
        )
        st.pyplot(fig, use_container_width=False)
        plt.close(fig)

        result_parts = [f"{row['지표']} {row['차이']:+.1f}{row['단위']}" for _, row in comparison.iterrows()]
        st.markdown(
            f'<div class="result-box"><b>분석 결과</b><br>순이동 상위 5개 구는 하위 5개 구와 비교해 '
            f'{", ".join(result_parts)}의 차이를 보였습니다.<br><small>상위: '
            f'{", ".join(top5["자치구명"])} / 하위: {", ".join(bottom5["자치구명"])}</small></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="policy-box"><b>정책 활용</b><br>차이가 큰 환경지표를 우선 점검하되, '
            '이 비교만으로 해당 지표가 순이동의 원인이라고 단정하지 않습니다.</div>',
            unsafe_allow_html=True,
        )

    st.divider()


if selected_page == "지역 비교":
    # -----------------------------------------------------------------------------
    # 6. 20대·30대 사분면
    # -----------------------------------------------------------------------------
    st.header("4. 20대와 30대의 이동 방향이 다른 지역은 어디일까?")
    quadrant = year_data[[
        "자치구명", "20대인구천명당순이동자수", "30대인구천명당순이동자수"
    ]].dropna().copy()
    quadrant["이동유형"] = quadrant.apply(classify_migration, axis=1)
    mixed_mask = quadrant["이동유형"].isin(["20대 유입·30대 유출형", "20대 유출·30대 유입형"])

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.scatter(
        quadrant.loc[~mixed_mask, "20대인구천명당순이동자수"],
        quadrant.loc[~mixed_mask, "30대인구천명당순이동자수"],
        color=MUTED, s=64, alpha=.85,
    )
    ax.scatter(
        quadrant.loc[mixed_mask, "20대인구천명당순이동자수"],
        quadrant.loc[mixed_mask, "30대인구천명당순이동자수"],
        color=ACCENT, s=88, edgecolor=TEXT, linewidth=.7,
    )
    ax.axhline(0, color=TEXT, linewidth=1)
    ax.axvline(0, color=TEXT, linewidth=1)
    add_point_labels(
        ax, quadrant, "20대인구천명당순이동자수", "30대인구천명당순이동자수", "자치구명"
    )
    style_axis(
        ax,
        f"{selected_year}년에는 {int(mixed_mask.sum())}개 구에서 20대와 30대의 이동 방향이 다르게 나타남",
        "20대 인구 1,000명당 순이동자 수(명)",
        "30대 인구 1,000명당 순이동자 수(명)",
    )
    st.pyplot(fig, use_container_width=False)
    plt.close(fig)

    mixed_20_in = quadrant.loc[quadrant["이동유형"] == "20대 유입·30대 유출형", "자치구명"].tolist()
    mixed_30_in = quadrant.loc[quadrant["이동유형"] == "20대 유출·30대 유입형", "자치구명"].tolist()
    st.markdown(
        f'<div class="result-box"><b>혼합형 지역</b><br>20대 유입·30대 유출형: '
        f'{", ".join(mixed_20_in) if mixed_20_in else "없음"}<br>20대 유출·30대 유입형: '
        f'{", ".join(mixed_30_in) if mixed_30_in else "없음"}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="policy-box"><b>정책 활용</b><br>20대 유입·30대 유출형은 초기 청년 유입 이후 '
        '가족 형성기 정착 여건을, 반대 유형은 초기 취업·주거 접근성을 우선 검토할 수 있습니다.</div>',
        unsafe_allow_html=True,
    )

    st.divider()


if selected_page == "현재 현황":
    # -----------------------------------------------------------------------------
    # 7. 자치구 순위
    # -----------------------------------------------------------------------------
    st.header("5. 어느 자치구에서 유입·유출이 가장 큰가?")
    ranking = year_data.sort_values(rate_col).copy()
    top_names = set(year_data.nlargest(5, rate_col)["자치구명"])
    bottom_names = set(year_data.nsmallest(5, rate_col)["자치구명"])
    bar_colors = []
    for _, row in ranking.iterrows():
        if row["자치구명"] in top_names:
            bar_colors.append(INFLOW)
        elif row["자치구명"] in bottom_names:
            bar_colors.append(OUTFLOW)
        else:
            bar_colors.append("#D5DAE0")

    fig, ax = plt.subplots(figsize=(7.4, 6.2))
    bars = ax.barh(ranking["자치구명"], ranking[rate_col], color=bar_colors)
    ax.axvline(0, color=TEXT, linewidth=1)
    ax.bar_label(bars, labels=[f"{v:+.1f}" for v in ranking[rate_col]], padding=3, fontsize=8)
    style_axis(
        ax,
        f"{selected_year}년 {selected_age}는 {top['자치구명']}에서 순유입률이 가장 높고, "
        f"{bottom['자치구명']}에서 가장 낮음",
        "인구 1,000명당 순이동자 수(명)",
        "자치구",
        "x",
    )
    st.pyplot(fig, use_container_width=False)
    plt.close(fig)
    st.caption("자치구별 청년 인구 규모 차이를 보정하기 위해 순이동자 수가 아닌 인구 1,000명당 지표를 사용했습니다.")

    st.divider()


if selected_page == "현재 현황":
    # -----------------------------------------------------------------------------
    # 8. 연도별 지속성
    # -----------------------------------------------------------------------------
    st.header("6. 이러한 이동은 지속되고 있을까?")
    selected_district = st.selectbox(
        "상세 조회 지역",
        ["서울 전체"] + districts,
        help="선택한 지역에 따라 바로 아래 연도별 추이 그래프와 지속성 진단이 바뀝니다.",
    )
    st.caption("이 선택은 아래 연도별 추이와 지속성 진단에만 적용됩니다.")
    if selected_district == "서울 전체":
        trend = data.groupby("연도", as_index=False)[["20대순이동자수", "30대순이동자수"]].sum()
        y20, y30 = "20대순이동자수", "30대순이동자수"
        ylabel = "순이동자 수(명)"
        trend_place = "서울 전체"
    else:
        trend = data[data["자치구명"] == selected_district].sort_values("연도")
        y20, y30 = "20대인구천명당순이동자수", "30대인구천명당순이동자수"
        ylabel = "인구 1,000명당 순이동자 수(명)"
        trend_place = selected_district

    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    for column, label, color in [(y20, "20대", INFLOW), (y30, "30대", OUTFLOW)]:
        ax.plot(trend["연도"], trend[column], marker="o", linewidth=2.2, label=label, color=color)
        for x, y in zip(trend["연도"], trend[column]):
            ax.annotate(f"{y:+,.1f}", (x, y), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8)
    ax.axhline(0, color=TEXT, linewidth=1, linestyle="--")
    ax.set_xticks(trend["연도"])
    ax.legend(title="연령대", frameon=False)
    style_axis(ax, f"{trend_place}의 20대·30대 순이동 변화", "연도", ylabel)
    st.pyplot(fig, use_container_width=False)
    plt.close(fig)

    selected_history_col = y20 if selected_age == "20대" else y30
    history_values = trend[selected_history_col].dropna()
    positive_years = int((history_values > 0).sum())
    negative_years = int((history_values < 0).sum())
    sign_changes = int((np.sign(history_values).diff().fillna(0) != 0).sum())
    if positive_years >= 3:
        persistence = f"{positive_years}년간 순유입이 나타난 지속 유입 지역"
    elif negative_years >= 3:
        persistence = f"{negative_years}년간 순유출이 나타난 지속 유출 지역"
    elif sign_changes >= 2:
        persistence = "순유입·순유출 방향이 자주 바뀐 변동 지역"
    else:
        persistence = "한 방향의 지속성이 뚜렷하지 않은 지역"
    st.markdown(
        f'<div class="result-box"><b>지속성 진단</b><br>{trend_place}은(는) 분석 기간 기준 '
        f'{selected_age} {persistence}입니다.</div>',
        unsafe_allow_html=True,
    )

    st.divider()


if selected_page == "정책 검토":
    # -----------------------------------------------------------------------------
    # 9. 정책 우선 검토 지역
    # -----------------------------------------------------------------------------
    st.header("7. 정책 우선 검토 지역 요약")
    policy = year_data[[
        "자치구명", rate_col, employment_col, "일자리집중도_인구천명당종사자수",
        "전월세월환산주거비중앙값_만원",
    ]].copy()

    # 최근 3개 연도의 선택 연령대 부호도 함께 사용합니다.
    recent_years = sorted(data["연도"].dropna().unique())[-3:]
    recent = data[data["연도"].isin(recent_years)]
    persistent_out = (
        recent.groupby("자치구명")[rate_col]
        .apply(lambda values: values.notna().sum() >= 3 and (values < 0).all())
    )

    employment_q = year_data[employment_col].quantile(.25)
    job_q75 = year_data["일자리집중도_인구천명당종사자수"].quantile(.75)
    rate_q25 = year_data[rate_col].quantile(.25)
    housing_q25 = year_data["전월세월환산주거비중앙값_만원"].quantile(.25)

    policy_rows = []
    for _, row in policy.iterrows():
        district = row["자치구명"]
        types = []
        actions = []
        if bool(persistent_out.get(district, False)):
            types.append("지속 유출")
            actions.append("종합 정착 여건")
        quadrant_type = quadrant.loc[quadrant["자치구명"] == district, "이동유형"]
        if not quadrant_type.empty and quadrant_type.iloc[0] == "20대 유입·30대 유출형":
            types.append("20대 유입·30대 유출")
            actions.append("가족 형성기 주거·생활환경")
        if row[rate_col] < 0 and row[employment_col] <= employment_q:
            types.append("낮은 고용·순유출")
            actions.append("청년 고용 접근성")
        if row[rate_col] <= rate_q25 and row["일자리집중도_인구천명당종사자수"] >= job_q75:
            types.append("높은 일자리·낮은 유입")
            actions.append("주거비·통근·직주 분리")
        if row[rate_col] < 0 and row["전월세월환산주거비중앙값_만원"] <= housing_q25:
            types.append("낮은 주거비·순유출")
            actions.append("교통·생활환경 등 미포함 요인")
        if types:
            policy_rows.append({
                "자치구": district,
                "검토 유형": " / ".join(dict.fromkeys(types)),
                "우선 확인할 정책": " / ".join(dict.fromkeys(actions)),
                f"{selected_age} 순이동률(명/1,000명)": round(row[rate_col], 1),
            })

    policy_table = pd.DataFrame(policy_rows)
    if policy_table.empty:
        st.info("선택 조건의 자동 선별 기준에 해당하는 자치구가 없습니다.")
    else:
        policy_table["검토 기준 수"] = policy_table["검토 유형"].str.count("/") + 1
        policy_table = policy_table.sort_values(
            ["검토 기준 수", f"{selected_age} 순이동률(명/1,000명)"], ascending=[False, True]
        )
        st.dataframe(policy_table, hide_index=True, use_container_width=True)

    st.markdown(
        '<div class="policy-box"><b>활용 범위</b><br>이 표는 정책을 자동 결정하지 않습니다. '
        '지속 유출, 연령대별 방향 차이, 고용·일자리·주거비 조건이 겹치는 지역을 '
        '후속 조사 대상으로 선별하는 참고 자료입니다.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("분석 한계와 데이터 기준"):
        st.markdown(
            """
            - 전월세 거래에는 계약자의 연령 정보가 없어 전 연령 계약을 사용했습니다.
            - 연도만 있는 원자료 특성상 계약 시점별 전환율 대신 연도 말 법정 전환율을 대표값으로 적용했습니다.
            - 20대 순이동은 20~29세, 고용률은 15~29세이며 30대는 각각 30~39세와 30~49세입니다.
            - 일자리 집중도는 근무지 기준 사업체 종사자 수를 연말 주민등록인구 1,000명당 값으로 환산했습니다.
            - 상관관계와 상·하위 집단 비교는 인과관계를 뜻하지 않습니다.
            """
        )

    st.caption(
        "순이동자 수 = 전입자 수 − 전출자 수. 모든 금액은 만원, 주거비는 만원/월, "
        "고용률은 %, 집단 간 고용률 차이는 %p로 표시했습니다."
    )
