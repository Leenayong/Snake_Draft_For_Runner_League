import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="러너리그 시즌4 드래프트 시뮬레이터", layout="wide")

# 제목 및 설명
st.title("🎮 러너리그 2026 시즌 4: 전략 드래프트 시뮬레이터")
st.markdown("""
이 시뮬레이터는 **인섹 → 이선생 → 소우릎 → 댕균 → 둥그레** 순서의 스네이크 드래프트를 지원합니다.
사이드바에서 선수들의 티어를 설정하고, 봇의 **선택 전략 가중치**를 조절하여 결과를 확인해보세요!
""")
st.markdown("---")

# 1. 고정 데이터 및 설정
TIER_SCORES = {'S': 10, 'A': 7, 'B': 4, 'C': 2}
LEADER_ORDER = ["인섹", "이선생", "소우릎", "댕균", "둥그레"]

if 'members' not in st.session_state:
    st.session_state.members = [
        {"name": "갱맘", "role": "Dealer", "tier": "S"},
        {"name": "고수달", "role": "Dealer", "tier": "A"},
        {"name": "디디디용", "role": "Dealer", "tier": "B"},
        {"name": "마뫄", "role": "Dealer", "tier": "A"},
        {"name": "뱅", "role": "Dealer", "tier": "S"},
        {"name": "양아지", "role": "Dealer", "tier": "B"},
        {"name": "왈도쿤", "role": "Dealer", "tier": "C"},
        {"name": "콩콩", "role": "Dealer", "tier": "B"},
        {"name": "큐베", "role": "Dealer", "tier": "A"},
        {"name": "핑맨", "role": "Dealer", "tier": "S"},
        {"name": "꽃핀", "role": "Supporter", "tier": "A"},
        {"name": "뀨냥냥", "role": "Supporter", "tier": "B"},
        {"name": "담유이", "role": "Supporter", "tier": "S"},
        {"name": "멋사", "role": "Supporter", "tier": "A"},
        {"name": "새담", "role": "Supporter", "tier": "B"},
        {"name": "서넹", "role": "Supporter", "tier": "B"},
        {"name": "아마츠노 유니", "role": "Supporter", "tier": "S"},
        {"name": "엘리", "role": "Supporter", "tier": "C"},
        {"name": "엘시", "role": "Supporter", "tier": "A"},
        {"name": "인간젤리", "role": "Supporter", "tier": "S"}
    ]

# 2. 사이드바: 봇 전략 가중치 조절 (Slider)
st.sidebar.header("⚙️ 드래프트 전략 설정")
strategy_val = st.sidebar.slider(
    "전략 가중치 (희소성 보너스)",
    min_value=0, max_value=10, value=5,
    help="낮을수록 '티어'를 중시하고, 높을수록 '포지션 밸런스'를 중시합니다."
)

# 가중치 설명 문구
if strategy_val <= 3:
    st.sidebar.success("🔥 **티어 우선**: 포지션 상관없이 고티어 선수를 먼저 선점합니다.")
elif strategy_val >= 7:
    st.sidebar.warning("⚖️ **밸런스 중시**: 특정 직업군 매물이 적으면 티어가 낮아도 먼저 뽑습니다.")
else:
    st.sidebar.info("⭐ **권장(Balanced)**: 실력과 포지션 상황을 적절히 조화합니다.")

st.sidebar.markdown("---")
st.sidebar.header("📋 선수 티어 설정")
for i, m in enumerate(st.session_state.members):
    st.session_state.members[i]['tier'] = st.sidebar.selectbox(
        f"{m['name']} ({m['role']})", ['S', 'A', 'B', 'C'], 
        index=['S', 'A', 'B', 'C'].index(m['tier']), key=f"t_{i}"
    )

# 3. 드래프트 실행 로직
if st.button("🚀 드래프트 시뮬레이션 시작!"):
    pool = [m.copy() for m in st.session_state.members]
    for m in pool: m['score'] = TIER_SCORES[m['tier']]
    
    teams = {name: [] for name in LEADER_ORDER}
    slots = {name: {'Dealer': 2, 'Supporter': 2} for name in LEADER_ORDER}
    history = []

    # 4라운드 스네이크 드래프트
    for r in range(1, 5):
        current_order = LEADER_ORDER if r % 2 != 0 else list(reversed(LEADER_ORDER))
        
        for l_name in current_order:
            # 실시간 희소성 체크 (남은 A티어 이상 인원)
            scarcity = {role: len([m for m in pool if m['role'] == role and m['score'] >= 7]) for role in ['Dealer', 'Supporter']}
            
            best_idx = -1
            max_val = -100
            
            for i, m in enumerate(pool):
                if slots[l_name][m['role']] > 0:
                    # 가치 평가 = 티어 점수 + (전략 가중치 if 매물 부족 else 0)
                    bonus = strategy_val if scarcity[m['role']] <= 2 else 0
                    eval_score = m['score'] + bonus
                    
                    if eval_score > max_val:
                        max_val = eval_score
                        best_idx = i
            
            if best_idx != -1:
                picked = pool.pop(best_idx)
                teams[l_name].append(picked)
                slots[l_name][picked['role']] -= 1
                history.append({
                    "라운드": r, 
                    "팀장": l_name, 
                    "선택": picked['name'], 
                    "포지션": picked['role'], 
                    "티어": picked['tier'],
                    "판단 근거": "희소성 고려 선점" if strategy_val > 0 and scarcity[picked['role']] <= 2 else "티어 우선 선택"
                })

    # 결과 레이아웃
    st.subheader("📊 드래프트 히스토리")
    st.dataframe(pd.DataFrame(history), use_container_width=True)

    st.subheader("🏆 최종 팀 라인업")
    cols = st.columns(5)
    for i, l_name in enumerate(LEADER_ORDER):
        with cols[i]:
            st.success(f"**{l_name} 팀**")
            st.write(f"🛡️ {l_name} (Tank)")
            for m in teams[l_name]:
                icon = "⚔️" if m['role'] == 'Dealer' else "🧪"
                st.write(f"{icon} {m['name']} ({m['tier']})")

