from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import StrMethodFormatter
import numpy as np
import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "processed" / "seoul_youth_master.csv"

BLUE = "#3976A8"
RED = "#C45F52"
YELLOW = "#D7A83F"
DARK = "#26333D"
TEXT = "#5B6974"
GRID = "#E8EDF1"
COLORS = ["#3976A8", "#C97945", "#5B8E71", "#8A6F9E", "#B4953F"]

st.set_page_config(page_title="서울 20·30대 순이동 비교 대시보드", page_icon="🏙️", layout="wide")
plt.rcParams.update({
    "font.family": "AppleGothic",
    "axes.unicode_minus": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

st.markdown("""
<style>
.stApp {background:#F5F7F9;}
[data-testid="stHeader"], [data-testid="stToolbar"] {display:none;}
.block-container {max-width:1540px; padding:1.35rem 1.8rem 2.4rem;}
h1,h2,h3 {color:#26333D; letter-spacing:-.035em;}
h1 {font-size:2.35rem !important; margin-bottom:.55rem !important;}
h2 {font-size:1rem !important; margin:0 !important;}
[data-testid="stCaptionContainer"] {color:#75828D; font-size:1.05rem;}
[data-testid="stMetric"] {
    background:#FFFFFF; border:1px solid #DFE5EA; border-radius:10px;
    padding:12px 14px; min-height:102px; box-shadow:none;
}
[data-testid="stMetricLabel"] {font-size:.78rem; color:#73808A;}
[data-testid="stMetricValue"] {font-size:1.25rem; color:#26333D;}
[data-testid="stVerticalBlockBorderWrapper"] {
    background:#FFFFFF !important; border-color:#D7E0E7 !important; border-radius:20px !important;
    padding:10px 14px;
}
[data-testid="stVerticalBlockBorderWrapper"] > div {background:#FFFFFF !important; border-radius:18px;}
[data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"]:has(h4) {
    background:#FFFFFF !important;
    border:1px solid #D7E0E7 !important;
    border-radius:20px !important;
    padding:18px 22px 20px !important;
    box-shadow:none !important;
    height:100% !important;
}
[data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"]:has(h4) img {
    border-radius:14px !important;
}
[data-testid="stHorizontalBlock"]:has(h4) {
    align-items:stretch !important;
}
[data-testid="stHorizontalBlock"]:has(h4) > [data-testid="stColumn"] {
    display:flex !important;
}
[data-testid="stHorizontalBlock"]:has(h4) > [data-testid="stColumn"] > [data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"]:has(h4) > [data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] {
    width:100% !important;
    height:100% !important;
}
.flow {display:flex; gap:10px; justify-content:flex-end; align-items:center; flex-wrap:nowrap; margin-top:.05rem;}
.flow span {background:#E6F0F6; color:#3E647D; padding:14px 18px; border-radius:30px; font-size:.92rem; font-weight:700; white-space:nowrap;}
.flow .arrow {background:transparent; padding:0; color:#7F9CB0; font-size:1.35rem;}
.filter-title {font-size:.72rem; color:#6D7A84; margin-bottom:2px;}
.static-label {font-size:1rem; color:#65737E; margin:.05rem 0 .55rem;}
.static-filter {height:64px; border:1px solid #D4DEE6; border-radius:13px; background:#FFFFFF; padding:17px 20px; color:#26333D; font-size:1.08rem; display:flex; justify-content:space-between; align-items:center;}
.kpi-grid {display:grid; gap:12px; margin:14px 0;}
.kpi-card {background:#FFFFFF; border:1px solid #D7E0E7; border-radius:16px; padding:18px 20px; min-height:170px; position:relative;}
.kpi-card.focus {border-color:#E78A7B; box-shadow:inset 0 3px 0 #E45F43;}
.kpi-label {font-size:1.05rem; color:#26333D; font-weight:750; margin-bottom:15px;}
.kpi-main {display:grid; grid-template-columns:1fr 1fr; gap:16px;}
.kpi-main > div + div {border-left:1px solid #E1E7EB; padding-left:16px;}
.kpi-caption {font-size:.78rem; color:#74818B; margin-bottom:7px;}
.kpi-value {font-size:1.62rem; font-weight:700; color:#26333D; line-height:1.25; word-break:keep-all;}
.kpi-value.negative {color:#E45F43;}
.kpi-value.positive {color:#1767B7;}
.kpi-detail {display:flex; gap:8px 14px; flex-wrap:wrap; margin-top:16px; color:#667681; font-size:.88rem;}
.kpi-detail b {color:#36444E;}
.kpi-compare {display:grid; gap:12px;}
.kpi-age-row {display:grid; grid-template-columns:48px 1fr 1fr; align-items:center; gap:12px; padding:10px 0; border-top:1px solid #E8EDF1;}
.kpi-age-row:first-child {border-top:0; padding-top:0;}
.kpi-age-label {font-size:.86rem; font-weight:750; color:#40505C;}
.kpi-age-value {font-size:1.1rem; font-weight:700; line-height:1.25;}
.kpi-age-value.negative {color:#E45F43;}
.kpi-age-value.positive {color:#1767B7;}
.kpi-age-meta {font-size:.75rem; color:#74818B; margin-top:3px;}
.focus-badge {position:absolute; right:16px; top:14px; padding:4px 10px; border:1px solid #E45F43; border-radius:7px; color:#D9442E; background:#FFF7F5; font-size:.78rem; font-weight:700;}
.section-head {display:flex; align-items:center; gap:12px; margin:17px 0 9px; color:#183D67; font-weight:750; font-size:1.12rem;}
.section-no {background:#123F73; color:#FFFFFF; border-radius:7px; padding:6px 10px; font-size:1rem; letter-spacing:.03em;}
.panel-question {font-size:.95rem; color:#728291; margin:4px 0 14px;}
.policy-grid {display:grid; gap:12px; margin-top:0;}
.policy-card {background:#FFFFFF; border:1px solid #D7E0E7; border-radius:16px; padding:18px 20px; min-height:var(--policy-min-height, 265px); position:relative;}
.policy-card.focus {border-color:#E78A7B; box-shadow:inset 0 3px 0 #E45F43;}
.policy-name {font-size:1.15rem; font-weight:780; color:#23323C; padding-bottom:10px; border-bottom:1px solid #E5EAEE;}
.policy-type {font-size:.82rem; color:#5E6D78; margin:9px 0 10px;}
.policy-title {font-size:.9rem; font-weight:750; margin:8px 0 5px;}
.policy-clues {font-size:.84rem; color:#586772; line-height:1.55; min-height:76px;}
.policy-tags {display:flex; flex-wrap:wrap; gap:6px; margin-top:8px;}
.policy-tag {display:inline-block; padding:7px 10px; border-radius:8px; background:#E7F1F6; color:#2F6686; font-size:.8rem; font-weight:700;}
.insight-box {margin:15px 0 2px; padding:16px 19px; border-left:4px solid #3976A8; border-radius:9px; background:#EDF4F8; color:#354651; font-size:.94rem; line-height:1.55;}
.insight-box b {color:#174D75;}
.footnote {font-size:.74rem; color:#6F7D87; margin-top:14px; padding:11px 14px; border:1px solid #D7E0E7; border-radius:10px; background:#FFFFFF; text-align:center;}
div[data-testid="stSelectbox"], div[data-testid="stMultiSelect"] {background:transparent;}
div[data-baseweb="select"] > div {min-height:58px; border-radius:12px !important; border:1px solid #D4DEE6 !important; background:#F8FAFB !important; font-size:1.02rem; padding-left:10px; box-shadow:none !important;}
div[data-testid="stSelectbox"] label, div[data-testid="stMultiSelect"] label {font-size:1rem; color:#65737E; padding-bottom:.35rem;}
span[data-tag] {background:#E6F0F6 !important; color:#315F7B !important; border-radius:9px !important;}
span[data-tag] button {color:#315F7B !important;}
[role="listbox"][aria-label^="자치구 복수 선택"] [role="presentation"]:has(> [data-key="__select_all__"]) {display:none !important;}
[role="listbox"][aria-label^="자치구 복수 선택"] [role="presentation"]:has(> [data-key="__select_all__"]) ~ [role="presentation"] {margin-top:-40px !important;}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"] {align-items:flex-end; gap:18px;}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stColumn"] {min-width:0;}
[data-testid="stPopover"] button {width:58px !important; min-width:58px !important; max-width:58px !important; height:58px; min-height:58px; padding:0 !important; border:1px solid #D4DEE6; border-radius:50%; background:#F8FAFB; color:#315F7B; font-size:1.2rem; font-weight:800; box-shadow:none;}
[data-testid="stPopover"] button:hover {border-color:#8FAFC3; color:#174D75;}
@media(max-width:800px) {.kpi-grid,.policy-grid {grid-template-columns:1fr !important;} .block-container {padding-top:4rem;} .kpi-main {grid-template-columns:1fr;} .kpi-main > div + div {border-left:0; padding-left:0;}}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(path, modified_ns):
    # modified_ns를 캐시 키에 포함해 전처리 CSV가 바뀌면 자동으로 다시 읽는다.
    _ = modified_ns
    return pd.read_csv(path)


def clean_axis(ax, grid="both"):
    ax.set_facecolor("white")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#BEC7CE")
    ax.grid(False)
    ax.grid(axis=grid, color=GRID, linewidth=.8)
    ax.tick_params(axis="both", length=0, colors=TEXT, labelsize=8)
    ax.set_axisbelow(True)


def movement_type(row):
    a20, a30 = row["20대순이동률"], row["30대순이동률"]
    if a20 >= 0 and a30 >= 0:
        return "20·30대 동반 유입형"
    if a20 >= 0 and a30 < 0:
        return "20대 유입·30대 유출형"
    if a20 < 0 and a30 >= 0:
        return "20대 유출·30대 유입형"
    return "20·30대 동반 유출형"


def rate_description(rate):
    if rate > 0:
        return f"{abs(rate):.1f}명 순유입", f"인구 대비 약 {abs(rate) / 10:.2f}% 순유입"
    if rate < 0:
        return f"{abs(rate):.1f}명 순유출", f"인구 대비 약 {abs(rate) / 10:.2f}% 순유출"
    return "순이동 없음", "인구 대비 0.00%"


def policy_diagnosis(row, history, year_data, selected_age):
    out20 = int((history["20대순이동률"] < 0).sum())
    out30 = int((history["30대순이동률"] < 0).sum())
    clues = []
    policies = []

    if row["전세환산주거비중앙값_만원"] >= year_data["전세환산주거비중앙값_만원"].median():
        clues.append("전세환산 주거비가 서울 중앙값 이상")
        policies.append("정착형 주택" if row["30대순이동률"] < 0 else "주거비 지원")
    if selected_age == "20대":
        selected_outflow = row["20대순이동률"] < 0
    elif selected_age == "30대":
        selected_outflow = row["30대순이동률"] < 0
    else:
        selected_outflow = row["20대순이동률"] < 0 or row["30대순이동률"] < 0

    if row["종사자수"] < year_data["종사자수"].median():
        clues.append("사업체 종사자수(절대값)가 서울 중앙값 미만")
        if selected_outflow:
            policies.extend(["지역 일자리 연계", "업무지 접근성 개선"])
    elif selected_outflow:
        clues.append("사업체 종사자수는 서울 중앙값 이상이지만 순유출 발생")
        policies.extend(["직주 불일치 점검", "통근·주거 연계"])
    employment_columns = []
    if selected_age in ["20대", "20대·30대 비교"]:
        employment_columns.append(("15_29세_고용률", "20대 참고 고용률(15–29세)"))
    if selected_age in ["30대", "20대·30대 비교"]:
        employment_columns.append(("30_49세_고용률", "30대 참고 고용률(30–49세)"))
    for column, label in employment_columns:
        if row[column] < year_data[column].median():
            clues.append(f"{label}이 서울 중앙값 미만")
            policies.append("취업 연계")
    if row["20대순이동률"] >= 0 and row["30대순이동률"] < 0:
        policies.append("가족형 주거")

    clue_text = ", ".join(clues) if clues else "주거·고용 지표가 서울 중간 수준과 유사"
    policy_list = list(dict.fromkeys(policies)) or ["유입 여건 유지", "지표 변화 모니터링"]
    return out20, out30, clue_text, policy_list


def get_condition_metrics(selected_age):
    metrics = [("전세환산주거비중앙값_만원", "전세환산 주거비 중앙값", "만원")]
    if selected_age in ["20대", "20대·30대 비교"]:
        metrics.append(("15_29세_고용률", "20대 참고 고용률(15–29세)", "%"))
    if selected_age in ["30대", "20대·30대 비교"]:
        metrics.append(("30_49세_고용률", "30대 참고 고용률(30–49세)", "%"))
    metrics.append(("종사자수", "사업체 종사자수(절대값)", "명"))
    return metrics


if not DATA_PATH.exists():
    st.error("분석 데이터를 찾을 수 없습니다. `python 02_preprocessing.py`를 먼저 실행해 주세요.")
    st.stop()

data = load_data(str(DATA_PATH), DATA_PATH.stat().st_mtime_ns)
required_columns = {
    "연도", "자치구명", "20대순이동자수", "30대순이동자수", "청년순이동자수",
    "20대순이동률", "30대순이동률", "청년순이동률", "전세환산주거비중앙값_만원",
    "종사자수", "15_29세_고용률", "30_49세_고용률",
}
missing_columns = sorted(required_columns - set(data.columns))
if missing_columns:
    st.error("전처리 데이터가 이전 형식입니다. 터미널에서 `python 02_preprocessing.py`를 한 번 실행해 주세요.")
    st.caption("부족한 열: " + ", ".join(missing_columns))
    st.stop()
years = sorted(data["연도"].unique())
districts = sorted(data["자치구명"].unique())

head_left, head_right = st.columns([1.3, 1])
with head_left:
    st.title("서울 20·30대 순이동 비교 대시보드")
    st.caption("선택한 자치구의 순이동과 주거비·고용 환경을 비교해 먼저 살펴볼 항목을 찾습니다")
with head_right:
    st.markdown(
        '<div class="flow"><span>① 현상 발견</span><span class="arrow">→</span><span>② 지속성 비교</span>'
        '<span class="arrow">→</span><span>③ 관련 여건 비교</span><span class="arrow">→</span><span>④ 우선 검토</span></div>',
        unsafe_allow_html=True,
    )

with st.container(border=True):
    f1, f2, f3, f4 = st.columns([1, 1.25, 2.5, .42])
    with f1:
        selected_year = st.selectbox(
            "기준 연도", years, index=len(years) - 1,
            help="선택한 연도로 KPI, 지역 여건, 상관관계를 다시 계산합니다.",
        )
    with f2:
        selected_age = st.selectbox(
            "연령대", ["20대", "30대", "20대·30대 비교"], index=2,
            help="비교 모드에서는 20대와 30대의 순이동자수·순이동률·서울 순위를 합치지 않고 각각 보여줍니다.",
        )
    with f3:
        selected_districts = st.multiselect(
            "자치구 복수 선택", districts,
            default=["노원구", "양천구", "관악구"], max_selections=4,
            placeholder="최대 4개 자치구 선택",
            help="1~4개 자치구를 같은 기준으로 비교합니다. 선택 구는 KPI·추이·여건·검토카드에 모두 반영됩니다.",
        )
    with f4:
        st.markdown('<div class="static-label">지표 안내</div>', unsafe_allow_html=True)
        with st.popover("?"):
            st.markdown("##### 지표 정의·계산식")
            st.markdown("""
**순이동자수(명)**  
= 전입자수 − 전출자수. 양수는 순유입, 음수는 순유출입니다.

**연령대 기준**  
20대=20–29세, 30대=30–39세입니다. 비교 모드는 두 연령대 값을 합산하지 않고 나란히 보여줍니다.

**연앙인구(명)**  
= (전년도 12월 인구 + 해당 연도 12월 인구) ÷ 2.

**순이동률(‰)**  
= 순이동자수 ÷ 같은 연령대 연앙인구 × 1,000.  
‰는 인구 1,000명당 몇 명이 순유입·순유출됐는지를 뜻합니다.
예: -19.9‰는 `인구 1,000명당 19.9명 순유출`, 인구 대비 약 1.99% 순유출을 뜻합니다.

**전세환산 주거비(만원)**  
• 전세 계약 = 보증금  
• 월세 계약 = 보증금 + (월세 × 12 ÷ 0.05)  
각 계약을 먼저 환산한 뒤 연도·자치구별 **중앙값**을 사용합니다. 5.0%는 연도 간 비교를 위한 고정 분석 가정이며 법정 상한이나 개별 계약의 실제 전환율을 뜻하지 않습니다.
[전월세전환율 공식 근거·한국부동산원](https://www.reb.or.kr/reb/cm/cntnts/cntntsView.do?cntntsId=1190&mi=9808)

**전세환산 주거비 산출 거래건수(건)**  
= 위 계산에 사용한 유효한 전세·월세 계약 수. 전세는 보증금 0 초과, 월세는 임대료 0 초과 계약만 사용합니다.

**고용률(%)**  
20대 참고지표는 15–29세, 30대 참고지표는 30–49세입니다. 연간값은 (상반기 고용률 + 하반기 고용률) ÷ 2입니다. 순이동 연령과 정확히 같지 않아 해석 단서로만 사용합니다.

**사업체 종사자수(명)**  
= 해당 자치구 사업체에 근무하는 종사자수의 합계. 전체 연령·근무지 기준 절대값이며 별도 비율을 계산하지 않습니다.

**서울 중앙값**  
= 해당 연도 25개 자치구 값의 중앙값.

**서울 순위**  
= 선택 연령대 순이동률을 내림차순으로 나열한 순위. 순유입률이 높을수록 1위에 가깝습니다.

**집중 확인 대상**  
= 선택한 자치구 중 실제 순유출이 발생했고 순이동률이 가장 낮은 구. 비교 모드에서는 20대·30대 중 더 낮은 순이동률로 판단합니다. 선택 구가 모두 순유입이면 집중 확인 대상을 지정하지 않습니다.

**이동 유형**  
20대·30대 순이동률의 양·음 조합으로 `동반 유입`, `20대 유입·30대 유출`, `20대 유출·30대 유입`, `동반 유출`로 구분합니다. 0 이상은 유입, 0 미만은 유출로 판정합니다.

**최근 3년 지속성**  
= 선택 연도를 포함한 최근 3개 연도 중 순이동률이 0 미만인 연도 수. 2021·2022년을 선택하면 확보된 연도만 사용합니다.

**Pearson 상관계수 r**  
= cov(X,Y) ÷ (σX×σY). -1~1 범위의 선형 관련성이며, 개인의 이사 원인이나 정책 효과를 증명하지 않습니다.
산점도는 현재 선택 연령·연도에서 비교 지표 중 |r|이 가장 큰 하나를 자동 표시합니다.

**우선 검토 항목**  
선택 구 값을 서울 25개 구 중앙값과 비교해 만든 탐색 순서입니다. 인과적 처방이나 정책 효과를 뜻하지 않습니다.
            """)

if not selected_districts:
    st.warning("비교할 자치구를 하나 이상 선택해 주세요.")
    st.stop()

year_data = data[data["연도"] == selected_year].copy()
selected_rows = year_data[year_data["자치구명"].isin(selected_districts)].copy()
if selected_age == "20대":
    count_col, rate_col = "20대순이동자수", "20대순이동률"
elif selected_age == "30대":
    count_col, rate_col = "30대순이동자수", "30대순이동률"
else:
    count_col, rate_col = None, None

metrics = get_condition_metrics(selected_age)
if selected_age == "20대·30대 비교":
    relation_specs = [
        ("전세환산주거비중앙값_만원", "전세환산 주거비 중앙값", "만원", "20대순이동률", "20대"),
        ("15_29세_고용률", "20대 참고 고용률(15–29세)", "%", "20대순이동률", "20대"),
        ("종사자수", "사업체 종사자수(절대값)", "명", "20대순이동률", "20대"),
        ("전세환산주거비중앙값_만원", "전세환산 주거비 중앙값", "만원", "30대순이동률", "30대"),
        ("30_49세_고용률", "30대 참고 고용률(30–49세)", "%", "30대순이동률", "30대"),
        ("종사자수", "사업체 종사자수(절대값)", "명", "30대순이동률", "30대"),
    ]
else:
    relation_specs = [(column, name, unit, rate_col, selected_age) for column, name, unit in metrics]

relation_results = []
for column, name, unit, related_rate_col, related_age in relation_specs:
    relation_results.append((abs(year_data[column].corr(year_data[related_rate_col])), column, name, unit, related_rate_col, related_age))
_, relation_column, relation_name, relation_unit, relation_rate_col, relation_age_label = max(relation_results, key=lambda item: item[0])
corr = year_data[relation_column].corr(year_data[relation_rate_col])
age_label = selected_age

if selected_age == "20대·30대 비교":
    selected_rows["집중진단률"] = selected_rows[["20대순이동률", "30대순이동률"]].min(axis=1)
    selected_rows["집중진단연령"] = np.where(
        selected_rows["20대순이동률"] <= selected_rows["30대순이동률"], "20대", "30대"
    )
    target = selected_rows.sort_values("집중진단률").iloc[0]
    target_rate = target["집중진단률"]
    target_age_label = target["집중진단연령"]
else:
    target = selected_rows.sort_values(rate_col).iloc[0]
    target_rate = target[rate_col]
    target_age_label = selected_age
focus_enabled = target_rate < 0
target_name = target["자치구명"]
district_colors = {district: COLORS[i] for i, district in enumerate(selected_districts)}
available_years = [year for year in years if year <= selected_year]
recent_years = available_years[-3:]

st.markdown('<div class="section-head"><span class="section-no">01</span> 선택 자치구 이동 현황</div>', unsafe_allow_html=True)
kpi_cards = []
for district in selected_districts:
    row = selected_rows[selected_rows["자치구명"] == district].iloc[0]
    focus = focus_enabled and district == target_name
    if selected_age == "20대·30대 비교":
        age_rows = []
        for short_age, age_count_col, age_rate_col in [
            ("20대", "20대순이동자수", "20대순이동률"),
            ("30대", "30대순이동자수", "30대순이동률"),
        ]:
            age_rate = row[age_rate_col]
            age_rank = int((year_data[age_rate_col] > age_rate).sum() + 1)
            age_class = "negative" if age_rate < 0 else "positive"
            age_rate_text, age_percent_text = rate_description(age_rate)
            age_rows.append(
                f'<div class="kpi-age-row"><div class="kpi-age-label">{short_age}</div>'
                f'<div><div class="kpi-age-value {age_class}">{row[age_count_col]:+,.0f}명</div>'
                f'<div class="kpi-age-meta">순이동자수</div></div>'
                f'<div><div class="kpi-age-value {age_class}">{age_rate_text}</div>'
                f'<div class="kpi-age-meta">{age_percent_text} · 서울 {age_rank}위</div></div></div>'
            )
        kpi_body = f'<div class="kpi-compare">{"".join(age_rows)}</div>'
        kpi_detail = f'<div class="kpi-detail"><span>{movement_type(row)}</span></div>'
    else:
        row_rank = int((year_data[rate_col] > row[rate_col]).sum() + 1)
        value_class = "negative" if row[rate_col] < 0 else "positive"
        rate_text, rate_percent_text = rate_description(row[rate_col])
        kpi_body = (
            f'<div class="kpi-main"><div><div class="kpi-caption">{selected_year} {age_label} 순이동자수(명)</div>'
            f'<div class="kpi-value {value_class}">{row[count_col]:+,.0f}명</div></div>'
            f'<div><div class="kpi-caption">{age_label} 인구 1,000명당</div>'
            f'<div class="kpi-value {value_class}">{rate_text}</div></div></div>'
        )
        kpi_detail = f'<div class="kpi-detail"><span>{rate_percent_text}</span><span>서울 <b>{row_rank}위</b></span><span>{movement_type(row)}</span></div>'
    kpi_cards.append(
        f'<div class="kpi-card {"focus" if focus else ""}">'
        f'{"<span class=\"focus-badge\">집중 확인</span>" if focus else ""}'
        f'<div class="kpi-label">{district}</div>{kpi_body}{kpi_detail}</div>'
    )
st.markdown(
    f'<div class="kpi-grid" style="grid-template-columns:repeat({len(kpi_cards)}, minmax(0, 1fr));">'
    + "".join(kpi_cards) + '</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="section-head"><span class="section-no">02</span> 지속성과 지역 여건 비교</div>', unsafe_allow_html=True)
trend_col, condition_col = st.columns([1, 1.08])
with trend_col:
    with st.container(border=True):
        st.markdown("#### 2021–2024 순이동률 추이")
        st.markdown('<div class="panel-question">선택한 자치구별 방향성과 20·30대 차이를 확인합니다</div>', unsafe_allow_html=True)
        district_count = len(selected_districts)
        ncols = min(district_count, 2)
        nrows = int(np.ceil(district_count / ncols))
        trend_height = 3.8 if nrows == 1 else 5.1
        fig, axes = plt.subplots(nrows, ncols, figsize=(6.2, trend_height), squeeze=False, sharex=True)
        axes = axes.ravel()
        for i, district in enumerate(selected_districts):
            ax = axes[i]
            history = data[(data["자치구명"] == district) & (data["연도"] <= selected_year)].sort_values("연도")
            if selected_age == "20대·30대 비교":
                ax.plot(history["연도"], history["20대순이동률"], marker="o", linewidth=2, markersize=4.5, color=BLUE, label="20대")
                ax.plot(history["연도"], history["30대순이동률"], marker="o", linewidth=2, markersize=4.5, color="#E16448", linestyle="--", label="30대")
            else:
                color = BLUE if selected_age == "20대" else "#E16448"
                ax.plot(history["연도"], history[rate_col], marker="o", linewidth=2.2, markersize=4.5, color=color, label=selected_age)
            ax.axhline(0, color="#9DB0BE", linewidth=.9, linestyle=(0, (3, 3)))
            ax.set_title(district, loc="left", fontsize=10, fontweight="bold", color=district_colors[district], pad=4)
            ax.set_xticks(available_years)
            ax.set_ylabel("인구 1,000명당 순이동(명)", fontsize=8)
            clean_axis(ax)
            ax.spines["bottom"].set_visible(False)
        for ax in axes[district_count:]:
            ax.set_visible(False)
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(handles, labels, frameon=False, ncol=2, fontsize=8.5, loc="upper right", bbox_to_anchor=(.98, .99))
        fig.tight_layout(pad=1.1, rect=(0, 0, 1, .94))
        st.pyplot(fig, width="stretch")
        plt.close(fig)

with condition_col:
    with st.container(border=True):
        st.markdown(f"#### 지역 여건 비교 ({selected_year})")
        st.markdown('<div class="panel-question">선택한 자치구의 실제 값을 서울 중앙값과 나란히 비교합니다</div>', unsafe_allow_html=True)
        condition_height = trend_height
        fig, axes = plt.subplots(len(metrics), 1, figsize=(6.5, condition_height), squeeze=False)
        axes = axes.ravel()
        offsets = np.linspace(-.16, .16, len(selected_districts))
        for ax, (column, name, unit) in zip(axes, metrics):
            values = year_data[column]
            median = values.median()
            span = values.max() - values.min()
            pad = max(span * .12, abs(median) * .03, .5)
            ax.axvline(median, color=YELLOW, linewidth=2, zorder=1)
            for offset, district in zip(offsets, selected_districts):
                value = selected_rows.loc[selected_rows["자치구명"] == district, column].iloc[0]
                ax.scatter(value, offset, s=55, color=district_colors[district], edgecolor="white", linewidth=.8, zorder=3)
            ax.set_xlim(values.min() - pad, values.max() + pad)
            ax.set_ylim(-.34, .34)
            ax.set_yticks([])
            ax.set_title(f"{name} ({unit})", loc="left", fontsize=9, fontweight="bold", color=DARK, pad=2)
            clean_axis(ax, grid="x")
            ax.spines["bottom"].set_visible(False)
            ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}" if unit != "%" else "{x:.1f}"))
        legend_handles = [
            Line2D([0], [0], marker="o", color="none", markerfacecolor=district_colors[d], markeredgecolor="white", markersize=7, label=d)
            for d in selected_districts
        ]
        legend_handles.append(Line2D([0], [0], color=YELLOW, linewidth=2, label="서울 중앙값"))
        fig.legend(handles=legend_handles, frameon=False, ncol=min(3, len(legend_handles)), fontsize=8, loc="upper right", bbox_to_anchor=(.98, .995))
        fig.tight_layout(pad=.85, h_pad=.75, rect=(0, 0, 1, .92))
        st.pyplot(fig, width="stretch")
        plt.close(fig)

direction = "양의" if corr > 0 else "음의"
target_rate_text, target_percent_text = rate_description(target_rate)
if focus_enabled:
    focus_message = (
        f'선택 구 중 <b>{target_name}</b>의 {target_age_label}가 인구 1,000명당 '
        f'<b>{target_rate_text}</b>({target_percent_text})로 가장 낮아 우선 확인 대상입니다.'
    )
else:
    focus_message = "선택한 자치구와 연령대가 모두 순유입 상태여서 집중 확인 대상 없이 변화 추이를 모니터링합니다."
st.markdown(
    f'<div class="insight-box"><b>핵심 메시지</b> · {selected_year}년 {age_label} 기준, '
    f'{focus_message} '
    f'서울 25개 구에서 <b>{relation_age_label} 순이동률</b>과 비교한 지표 중 <b>{relation_name}</b>의 관련성이 가장 크며 '
    f'(r={corr:.2f}, {direction} 관계), 이 결과는 원인 판정이 아니라 다음에 확인할 항목을 정하는 단서입니다.</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="section-head"><span class="section-no">03</span> 서울 전체 관계와 선택 구 해석</div>', unsafe_allow_html=True)
relation_col, policy_col = st.columns([.9, 1.65])
with relation_col:
    with st.container(border=True):
        st.markdown("#### 서울 전체 관계와 선택 구 위치")
        st.markdown(
            f'<div class="panel-question">자동 선택: <b>{relation_age_label} 순이동 × {relation_name}</b> · 연령대별 후보 중 |r| 최대</div>',
            unsafe_allow_html=True,
        )
        relation = year_data[["자치구명", relation_column, relation_rate_col]].dropna()
        fig, ax = plt.subplots(figsize=(5.2, 4.55))
        ax.scatter(relation[relation_column], relation[relation_rate_col], s=38, color="#B8C4CD", alpha=.72, edgecolors="white", linewidths=.6)
        label_offsets = [(7, 8), (7, -14), (7, 8), (7, -14), (7, 16)]
        for i, district in enumerate(selected_districts):
            row = relation[relation["자치구명"] == district]
            edge = "#28343D" if focus_enabled and district == target_name else "white"
            ax.scatter(row[relation_column], row[relation_rate_col], s=105, color=district_colors[district], edgecolors=edge, linewidths=1.3, zorder=3)
            if not row.empty:
                offset = label_offsets[i % len(label_offsets)]
                ax.annotate(
                    district,
                    (row[relation_column].iloc[0], row[relation_rate_col].iloc[0]),
                    xytext=offset,
                    textcoords="offset points",
                    fontsize=8,
                    color="#44525D",
                    bbox=dict(boxstyle="round,pad=.18", facecolor="white", edgecolor="none", alpha=.9),
                )
        slope, intercept = np.polyfit(relation[relation_column], relation[relation_rate_col], 1)
        xs = np.linspace(relation[relation_column].min(), relation[relation_column].max(), 100)
        ax.plot(xs, slope * xs + intercept, color="#91A6B5", linestyle=(0, (4, 4)), linewidth=1.25)
        ax.text(.02, .97, f"Pearson r = {corr:.2f}", transform=ax.transAxes, ha="left", va="top", fontsize=8.5, color=TEXT)
        ax.axhline(0, color="#9DB0BE", linewidth=1, linestyle=(0, (3, 3)))
        ax.set_xlabel(f"{relation_name}({relation_unit}) →", fontsize=9)
        ax.set_ylabel(f"{relation_age_label} 인구 1,000명당 순이동(명) →", fontsize=9)
        if relation_unit == "명":
            ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        clean_axis(ax)
        ax.spines["bottom"].set_visible(False)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)

with policy_col:
    policy_cards = []
    for district in selected_districts:
        row = selected_rows[selected_rows["자치구명"] == district].iloc[0]
        history = data[(data["자치구명"] == district) & (data["연도"].isin(recent_years))].sort_values("연도")
        out20, out30, clues, policies = policy_diagnosis(row, history, year_data, selected_age)
        if selected_age == "20대":
            persistence = f"최근 {len(recent_years)}년 중 20대 {out20}년 순유출"
        elif selected_age == "30대":
            persistence = f"최근 {len(recent_years)}년 중 30대 {out30}년 순유출"
        else:
            persistence = f"최근 {len(recent_years)}년 중 20대 {out20}년·30대 {out30}년 순유출"
        clue_items = "".join(f"<div>• {item}</div>" for item in [persistence] + clues.split(", "))
        policy_tags = "".join(f'<span class="policy-tag">{policy}</span>' for policy in policies[:3])
        focus = focus_enabled and district == target_name
        policy_cards.append(
            f'<div class="policy-card {"focus" if focus else ""}">'
            f'{"<span class=\"focus-badge\">집중 확인</span>" if focus else ""}'
            f'<div class="policy-name" style="color:{district_colors[district]}">{district}</div>'
            f'<div class="policy-type">{movement_type(row)}</div>'
            f'<div class="policy-title" style="color:{district_colors[district]}">해석 근거</div>'
            f'<div class="policy-clues">{clue_items}</div>'
            f'<div class="policy-title" style="color:{district_colors[district]}">우선 검토</div>'
            f'<div class="policy-tags">{policy_tags}</div></div>'
        )
    policy_columns = len(policy_cards) if len(policy_cards) <= 3 else 2
    policy_min_height = 485 if len(policy_cards) <= 3 else 280
    st.markdown(
        f'<div class="policy-grid" style="grid-template-columns:repeat({policy_columns}, minmax(0, 1fr)); --policy-min-height:{policy_min_height}px;">'
        + "".join(policy_cards) + '</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="footnote">※ 전세환산 주거비는 전 연령 계약을 5.0% 고정 전환율로 환산한 중앙값이며, '
    '사업체 종사자수는 근무지 기준 전체 연령 절대값입니다. '
    '20대 참고 고용률은 15–29세, 30대 참고 고용률은 30–49세로 순이동 연령과 일치하지 않습니다. '
    '|r| 최대 지표와 우선 검토 항목은 탐색 결과이며 인과관계나 정책 효과를 의미하지 않습니다.</div>',
    unsafe_allow_html=True,
)
