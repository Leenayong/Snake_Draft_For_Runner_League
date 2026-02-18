import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="러너리그 시즌4 드래프트 시뮬레이터", layout="wide")
st.title("🎮 러너리그 2026 시즌 4: 드래프트 시뮬레이터")
st.write("탱커 팀장들이 스네이크 방식으로 팀원을 선발합니다.")

# 1. 고정 데이터 설정
TIER_SCORES = {'S': 10, 'A': 7, 'B': 4, 'C': 2}
LEADER_ORDER = ["인섹", "이선생", "소우릎", "댕균", "둥그레"]

# 이미지에서 추출한 선수 명단
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
        {"name": "담유미", "role": "Supporter", "tier": "S"},
        {"name": "멋사", "role": "Supporter", "tier": "A"},
        {"name": "새담", "role": "Supporter", "tier": "B"},
        {"name": "서넹", "role": "Supporter", "tier": "B"},
        {"name": "아마츠노 유니", "role": "Supporter", "tier": "S"},
        {"name": "엘리", "role": "Supporter", "tier": "C"},
        {"name": "엘시", "role": "Supporter", "tier": "A"},
        {"name": "인간젤리", "role": "Supporter", "tier": "S"}
    ]

# 2. 사이드바: 티어 수정 기능
st.sidebar.header("📋 선수 티어 조정")
for i, m in enumerate(st.session_state.members):
    st.session_state.members[i]['tier'] = st.sidebar.selectbox(
        f"{m['name']} ({m['role']})", ['S', 'A', 'B', 'C'], 
        index=['S', 'A', 'B', 'C'].index(m['tier']), key=f"tier_{i}"
    )

# 3. 드래프트 로직
if st.button("🚀 드래프트 시뮬레이션 시작!"):
    pool = [m.copy() for m in st.session_state.members]
    for m in pool: m['score'] = TIER_SCORES[m['tier']]
    
    teams = {name: [] for name in LEADER_ORDER}
    slots = {name: {'Dealer': 2, 'Supporter': 2} for name in LEADER_ORDER}
    history = []

    for r in range(1, 5):
        # 스네이크 방식: 홀수 라운드 정순, 짝수 라운드 역순
        current_order = LEADER_ORDER if r % 2 != 0 else list(reversed(LEADER_ORDER))
        
        for l_name in current_order:
            # 희소성 계산 (남은 S, A급 인원)
            scarcity = {role: len([m for m in pool if m['role'] == role and m['score'] >= 7]) for role in ['Dealer', 'Supporter']}
            
            # 봇의 선택 알고리즘
            best_idx = -1
            max_val = -100
            for i, m in enumerate(pool):
                if slots[l_name][m['role']] > 0:
                    bonus = 5 if scarcity[m['role']] <= 2 else 0
                    if m['score'] + bonus > max_val:
                        max_val = m['score'] + bonus
                        best_idx = i
            
            if best_idx != -1:
                picked = pool.pop(best_idx)
                teams[l_name].append(picked)
                slots[l_name][picked['role']] -= 1
                history.append({"라운드": r, "팀장": l_name, "선택 선수": picked['name'], "포지션": picked['role'], "티어": picked['tier']})

    # 결과 전시
    st.subheader("📊 드래프트 히스토리")
    st.table(pd.DataFrame(history))

    st.subheader("🏆 최종 팀 라인업")
    cols = st.columns(5)
    for i, l_name in enumerate(LEADER_ORDER):
        with cols[i]:
            st.info(f"**{l_name} 팀**")
            st.write(f"🛡️ {l_name} (Tank)")
            for m in teams[l_name]:
                role_icon = "⚔️" if m['role'] == 'Dealer' else "🧪"
                st.write(f"{role_icon} {m['name']} ({m['tier']})")