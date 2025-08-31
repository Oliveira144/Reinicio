import streamlit as st

# ==============================
# Funções para detectar cada padrão
# ==============================
def check_streak(h, color=None, length=2):
    if len(h) >= length:
        streak = h[-length:]
        if color:
            if all(c == color for c in streak):
                return True, "Alternar"
        else:
            if len(set(streak)) == 1 and streak[0] != "🟡":
                return True, "Alternar"
    return False, None

def check_alternation(h, size):
    if len(h) >= size*2:
        first = h[-2*size:-size]
        second = h[-size:]
        if first == second and len(set(first)) > 1:
            return True, "Repetir sequência"
    return False, None

def check_repeat(h, size):
    if len(h) >= size*2:
        if h[-2*size:-size] == h[-size:]:
            return True, "Repetir padrão"
    return False, None

def check_cycle_inverted(h, size=3):
    if len(h) >= size*2:
        if h[-2*size:-size] == list(reversed(h[-size:])):
            return True, "Repetir ciclo invertido"
    return False, None

def check_cycle_repeated(h, size=3):
    if len(h) >= size*2:
        if h[-2*size:-size] == h[-size:]:
            return True, "Repetir ciclo"
    return False, None

def check_draw(h):
    if len(h) >= 1 and h[-1] == "🟡":
        return True, "Reiniciar padrão"
    if len(h) >=2 and h[-1]=="🟡" and h[-2]!="🟡":
        return True, "Reiniciar streak"
    if len(h) >=3 and h[-2]=="🟡":
        return True, "Reiniciar alternância"
    return False, None

# ==============================
# Função principal de análise
# ==============================
def analyze_patterns(history):
    if not history:
        return [], "Aguardar"

    h = history[-18:]  # últimos 18 resultados
    patterns_detected = []
    next_entries = []

    # 1. Streak vermelho ≥2
    detected, suggestion = check_streak(h, "🔴", 2)
    if detected:
        patterns_detected.append("Streak 🔴 ≥2")
        next_entries.append(suggestion)

    # 2. Streak azul ≥2
    detected, suggestion = check_streak(h, "🔵", 2)
    if detected:
        patterns_detected.append("Streak 🔵 ≥2")
        next_entries.append(suggestion)

    # 3. Streak vermelho ≥3
    detected, suggestion = check_streak(h, "🔴", 3)
    if detected:
        patterns_detected.append("Streak 🔴 ≥3")
        next_entries.append(suggestion)

    # 4. Streak azul ≥3
    detected, suggestion = check_streak(h, "🔵", 3)
    if detected:
        patterns_detected.append("Streak 🔵 ≥3")
        next_entries.append(suggestion)

    # 5. Streak ≥4 (qualquer cor)
    detected, suggestion = check_streak(h, None, 4)
    if detected:
        patterns_detected.append(f"Streak ≥4 {h[-1]}")
        next_entries.append(suggestion)

    # 6. Alternância simples 2 cores
    detected, suggestion = check_alternation(h, 2)
    if detected:
        patterns_detected.append("Alternância 2 cores")
        next_entries.append(suggestion)

    # 7. Alternância 3 cores
    detected, suggestion = check_alternation(h, 3)
    if detected:
        patterns_detected.append("Alternância 3 cores")
        next_entries.append(suggestion)

    # 8-10. Padrões repetidos 3,4,5 cores
    for size in [3,4,5]:
        detected, suggestion = check_repeat(h, size)
        if detected:
            patterns_detected.append(f"Padrão repetido {size} cores")
            next_entries.append(suggestion)

    # 11. Ciclo invertido 3
    detected, suggestion = check_cycle_inverted(h, 3)
    if detected:
        patterns_detected.append("Ciclo invertido 3")
        next_entries.append(suggestion)

    # 12. Ciclo repetido 3
    detected, suggestion = check_cycle_repeated(h, 3)
    if detected:
        patterns_detected.append("Ciclo repetido 3")
        next_entries.append(suggestion)

    # 13-15. Empates
    detected, suggestion = check_draw(h)
    if detected:
        patterns_detected.append("Empate detectado")
        next_entries.append(suggestion)

    # Determinar sugestão final
    if not next_entries:
        suggestion = "Aguardar"
    else:
        if len(set(next_entries)) == 1:
            suggestion = next_entries[0]
        else:
            suggestion = "Aguardar"

    return patterns_detected, suggestion

# ==============================
# Interface Streamlit
# ==============================
st.set_page_config(page_title="Football Studio Analyzer Profissional", layout="centered")
st.title("🎲 Football Studio Analyzer Profissional")
st.write("Análise dos 15 principais padrões do Football Studio com histórico de 18 resultados. Sugestão baseada em padrões detectados.")

# Inicializar histórico
if "history" not in st.session_state:
    st.session_state.history = []

# Botões de entrada
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔴 Vermelho"):
        st.session_state.history.append("🔴")
with col2:
    if st.button("🔵 Azul"):
        st.session_state.history.append("🔵")
with col3:
    if st.button("🟡 Empate"):
        st.session_state.history.append("🟡")

# Histórico mais recente à esquerda
st.subheader("📜 Histórico (mais recente → mais antigo)")
if st.session_state.history:
    max_per_line = 9
    reversed_history = list(reversed(st.session_state.history))
    lines=[]
    current_line=[]
    for idx,res in enumerate(reversed_history):
        current_line.append(res)
        if (idx+1)%max_per_line==0:
            lines.append(current_line)
            current_line=[]
    if current_line:
        lines.append(current_line)
    for line in lines:
        st.write(" ".join(line))
else:
    st.write("Nenhum resultado inserido ainda.")

# Análise de padrões
st.subheader("🤖 Análise de Padrões")
patterns_detected, suggestion = analyze_patterns(st.session_state.history)

if patterns_detected:
    st.write("**Padrões detectados:**")
    for p in patterns_detected:
        st.write(f"- {p} 🔥")
else:
    st.write("Nenhum padrão detectado.")

# Sugestão baseada no padrão
st.write(f"**Sugestão de entrada:** {suggestion}")

# Reset histórico
if st.button("🔄 Resetar Histórico"):
    st.session_state.history = []
    st.success("Histórico limpo!")
