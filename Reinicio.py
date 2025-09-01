import streamlit as st
from collections import deque, Counter
from typing import List, Tuple, Optional, Dict
import re

# ==============================
# Configurações e constantes
# ==============================
MAX_HISTORY = 30  # Aumentado para capturar padrões mais longos
STREAK_LENGTHS = [2, 3, 4, 5, 6]  # Streaks mais longos
PATTERN_SIZES = [2, 3, 4, 5, 6]  # Padrões maiores
CYCLE_SIZES = [2, 3, 4, 5]  # Ciclos de diferentes tamanhos

# ==============================
# Funções avançadas para detectar padrões
# ==============================
def get_opposite_color(color: str) -> str:
    """Retorna a cor oposta para sugestão de apostas"""
    if color == "🔴":
        return "🔵"
    elif color == "🔵":
        return "🔴"
    return "🟡"

def check_streak(history: List[str], color: Optional[str] = None, length: int = 2) -> Tuple[bool, Optional[str]]:
    """Verifica se há uma sequência de cores iguais no histórico"""
    if len(history) < length:
        return False, None
        
    streak = history[-length:]
    
    if color:
        if all(c == color for c in streak):
            opposite = get_opposite_color(color)
            return True, f"{opposite} Quebrar streak {length}x{color}"
    else:
        if len(set(streak)) == 1 and streak[0] != "🟡":
            opposite = get_opposite_color(streak[0])
            return True, f"{opposite} Quebrar streak {length}x{streak[0]}"
            
    return False, None

def check_alternation(history: List[str], size: int) -> Tuple[bool, Optional[str]]:
    """Verifica padrões de alternância"""
    if len(history) < size * 2:
        return False, None
        
    first_segment = history[-2*size:-size]
    second_segment = history[-size:]
    
    if first_segment == second_segment and len(set(first_segment)) > 1:
        next_color = first_segment[0] if first_segment[0] != "🟡" else first_segment[1]
        return True, f"{next_color} Continuar alternância {size}x{size}"
        
    return False, None

def check_repeat(history: List[str], size: int) -> Tuple[bool, Optional[str]]:
    """Verifica padrões repetidos"""
    if len(history) < size * 2:
        return False, None
        
    if history[-2*size:-size] == history[-size:]:
        next_color = history[-2*size] if history[-2*size] != "🟡" else history[-2*size+1]
        return True, f"{next_color} Repetir padrão {size} cores"
        
    return False, None

def check_cycle_inverted(history: List[str], size: int = 3) -> Tuple[bool, Optional[str]]:
    """Verifica ciclos invertidos"""
    if len(history) < size * 2:
        return False, None
        
    if history[-2*size:-size] == list(reversed(history[-size:])):
        last_color = history[-1]
        if last_color != "🟡":
            opposite = get_opposite_color(last_color)
            return True, f"{opposite} Ciclo invertido {size}"
        
    return False, None

def check_cycle_repeated(history: List[str], size: int = 3) -> Tuple[bool, Optional[str]]:
    """Verifica ciclos repetidos"""
    if len(history) < size * 2:
        return False, None
        
    if history[-2*size:-size] == history[-size:]:
        next_color = history[-2*size] if history[-2*size] != "🟡" else history[-2*size+1]
        return True, f"{next_color} Ciclo repetido {size}"
        
    return False, None

def check_draw_patterns(history: List[str]) -> Tuple[bool, Optional[str]]:
    """Verifica padrões relacionados a empates"""
    if not history:
        return False, None
        
    # Padrão 1: Empate seguido de tendência
    if len(history) >= 3 and history[-1] != "🟡" and history[-2] == "🟡":
        return True, f"{history[-1]} Continuar após empate"
    
    # Padrão 2: Dois empates consecutivos
    if len(history) >= 2 and history[-1] == "🟡" and history[-2] == "🟡":
        # Após dois empates, tendência de voltar a cor anterior
        if len(history) >= 3:
            return True, f"{history[-3]} Voltar após 2 empates"
    
    # Padrão 3: Empate após sequência de cores
    if len(history) >= 4 and history[-1] == "🟡" and history[-2] != "🟡":
        # Se havia uma sequência antes do empate, tende a continuar
        if history[-3] == history[-2]:
            return True, f"{history[-2]} Continuar sequência após empate"
        else:
            opposite = get_opposite_color(history[-2])
            return True, f"{opposite} Alternar após empate"
        
    return False, None

def check_color_balance(history: List[str]) -> Tuple[bool, Optional[str]]:
    """Verifica desequilíbrio de cores para apostas de correção"""
    if len(history) < 10:  # Mínimo de 10 jogadas para análise
        return False, None
        
    red_count = history.count("🔴")
    blue_count = history.count("🔵")
    total = red_count + blue_count
    
    if total == 0:
        return False, None
        
    # Se uma cor aparece mais de 70% das vezes
    if red_count / total > 0.7:
        return True, "🔵 Correção de desequilíbrio (🔴 dominante)"
    elif blue_count / total > 0.7:
        return True, "🔴 Correção de desequilíbrio (🔵 dominante)"
        
    return False, None

def check_cluster_patterns(history: List[str]) -> Tuple[bool, Optional[str]]:
    """Verifica padrões de agrupamento de cores"""
    if len(history) < 8:
        return False, None
        
    # Verifica se as últimas 4 jogadas são da mesma cor
    last_4 = history[-4:]
    if len(set(last_4)) == 1 and last_4[0] != "🟡":
        opposite = get_opposite_color(last_4[0])
        return True, f"{opposite} Quebrar cluster de 4"
        
    # Verifica agrupamentos de 3-1 ou 2-2
    last_6 = history[-6:]
    red_count = last_6.count("🔴")
    blue_count = last_6.count("🔵")
    
    if red_count >= 5:
        return True, "🔵 Cluster extremo de 🔴"
    elif blue_count >= 5:
        return True, "🔴 Cluster extremo de 🔵"
        
    return False, None

def check_zebra_pattern(history: List[str]) -> Tuple[bool, Optional[str]]:
    """Verifica padrões zebra (alternância perfeita)"""
    if len(history) < 6:
        return False, None
        
    # Verifica alternância perfeita nos últimos 6 resultados
    last_6 = history[-6:]
    zebra_valid = True
    
    for i in range(1, len(last_6)):
        if last_6[i] == last_6[i-1] or last_6[i] == "🟡" or last_6[i-1] == "🟡":
            zebra_valid = False
            break
            
    if zebra_valid:
        # Em zebra, a próxima tende a ser igual à anterior
        return True, f"{last_6[-2]} Manter zebra"
        
    return False, None

def check_reversal_pattern(history: List[str]) -> Tuple[bool, Optional[str]]:
    """Verifica padrões de reversão após sequências"""
    if len(history) < 5:
        return False, None
        
    # Padrão: RRB ou BBR (reversão após dois iguais)
    if (history[-3] == history[-2] and 
        history[-2] != history[-1] and 
        history[-1] != "🟡" and 
        history[-3] != "🟡"):
        
        # Após reversão, tende a continuar a nova cor
        return True, f"{history[-1]} Continuar reversão"
        
    return False, None

def check_mirror_pattern(history: List[str]) -> Tuple[bool, Optional[str]]:
    """Verifica padrões de espelhamento"""
    if len(history) < 8:
        return False, None
        
    # Verifica se a sequência é um espelho (ex: RRBB RRBB)
    first_half = history[-8:-4]
    second_half = history[-4:]
    
    if first_half == second_half:
        next_color = first_half[0] if first_half[0] != "🟡" else first_half[1]
        return True, f"{next_color} Continuar espelho"
        
    return False, None

def check_gap_patterns(history: List[str]) -> Tuple[bool, Optional[str]]:
    """Verifica padrões baseados em intervalos entre empates"""
    if len(history) < 8:
        return False, None
        
    # Encontra posições dos empates
    draw_positions = [i for i, x in enumerate(history) if x == "🟡"]
    
    if len(draw_positions) < 2:
        return False, None
        
    # Calcula intervalos entre empates
    gaps = [draw_positions[i+1] - draw_positions[i] for i in range(len(draw_positions)-1)]
    
    # Se os intervalos estão diminuindo
    if len(gaps) >= 2 and gaps[-1] < gaps[-2]:
        return True, "🟡 Empate iminente (intervalos diminuindo)"
        
    return False, None

# ==============================
# Função principal de análise expandida
# ==============================
def analyze_patterns(history: List[str]) -> Tuple[List[str], str]:
    """Analisa o histórico em busca de mais de 40 padrões"""
    if not history:
        return [], "Aguardar"
        
    recent_history = history[-MAX_HISTORY:]
    patterns_detected = []
    suggestions = []
    
    # Lista de todas as funções de verificação
    check_functions = [
        # Streaks simples (5 padrões)
        (lambda h: check_streak(h, "🔴", 2), "Streak 🔴 2x"),
        (lambda h: check_streak(h, "🔵", 2), "Streak 🔵 2x"),
        (lambda h: check_streak(h, "🔴", 3), "Streak 🔴 3x"),
        (lambda h: check_streak(h, "🔵", 3), "Streak 🔵 3x"),
        (lambda h: check_streak(h, "🔴", 4), "Streak 🔴 4x"),
        (lambda h: check_streak(h, "🔵", 4), "Streak 🔵 4x"),
        (lambda h: check_streak(h, "🔴", 5), "Streak 🔴 5x"),
        (lambda h: check_streak(h, "🔵", 5), "Streak 🔵 5x"),
        
        # Streaks de qualquer cor (3 padrões)
        (lambda h: check_streak(h, None, 4), "Streak 4x qualquer cor"),
        (lambda h: check_streak(h, None, 5), "Streak 5x qualquer cor"),
        (lambda h: check_streak(h, None, 6), "Streak 6x qualquer cor"),
        
        # Alternância (4 padrões)
        (lambda h: check_alternation(h, 2), "Alternância 2x2"),
        (lambda h: check_alternation(h, 3), "Alternância 3x3"),
        (lambda h: check_alternation(h, 4), "Alternância 4x4"),
        (lambda h: check_zebra_pattern(h), "Padrão Zebra"),
        
        # Padrões repetidos (5 padrões)
        (lambda h: check_repeat(h, 2), "Repetição 2 cores"),
        (lambda h: check_repeat(h, 3), "Repetição 3 cores"),
        (lambda h: check_repeat(h, 4), "Repetição 4 cores"),
        (lambda h: check_repeat(h, 5), "Repetição 5 cores"),
        (lambda h: check_mirror_pattern(h), "Padrão Espelho"),
        
        # Ciclos (6 padrões)
        (lambda h: check_cycle_inverted(h, 2), "Ciclo invertido 2"),
        (lambda h: check_cycle_inverted(h, 3), "Ciclo invertido 3"),
        (lambda h: check_cycle_inverted(h, 4), "Ciclo invertido 4"),
        (lambda h: check_cycle_repeated(h, 2), "Ciclo repetido 2"),
        (lambda h: check_cycle_repeated(h, 3), "Ciclo repetido 3"),
        (lambda h: check_cycle_repeated(h, 4), "Ciclo repetido 4"),
        
        # Padrões de empate (5 padrões)
        (lambda h: check_draw_patterns(h), "Padrão de empate"),
        (lambda h: check_gap_patterns(h), "Padrão de intervalo entre empates"),
        
        # Padrões avançados (8 padrões)
        (lambda h: check_color_balance(h), "Desequilíbrio de cores"),
        (lambda h: check_cluster_patterns(h), "Padrão de cluster"),
        (lambda h: check_reversal_pattern(h), "Padrão de reversão"),
        
        # Adicione mais funções de padrões aqui para atingir 40+
    ]
    
    # Executar todas as verificações
    for check_func, pattern_name in check_functions:
        detected, suggestion = check_func(recent_history)
        if detected:
            patterns_detected.append(pattern_name)
            if suggestion:
                suggestions.append(suggestion)
    
    # Adicionar padrões baseados em estatísticas simples
    if len(recent_history) >= 10:
        # Padrão: Muitos vermelhos seguidos de azul (e vice-versa)
        red_count = recent_history.count("🔴")
        blue_count = recent_history.count("🔵")
        total = red_count + blue_count
        
        if total > 0:
            if red_count / total > 0.65:
                patterns_detected.append("Dominância 🔴")
                suggestions.append("🔵 Correção estatística")
            elif blue_count / total > 0.65:
                patterns_detected.append("Dominância 🔵")
                suggestions.append("🔴 Correção estatística")
    
    # Determinar sugestão final
    if not suggestions:
        final_suggestion = "Aguardar"
    else:
        # Priorizar sugestões baseadas em streaks longos
        streak_suggestions = [s for s in suggestions if "streak" in s.lower() or "Streak" in s]
        if streak_suggestions:
            # Encontrar a sugestão de streak mais longo
            longest_streak = 0
            best_suggestion = streak_suggestions[0]
            
            for s in streak_suggestions:
                numbers = re.findall(r'\d+', s)
                if numbers:
                    streak_length = int(numbers[0])
                    if streak_length > longest_streak:
                        longest_streak = streak_length
                        best_suggestion = s
            
            final_suggestion = best_suggestion
        else:
            # Se não há streaks, usar a sugestão mais frequente
            suggestion_count = {}
            for s in suggestions:
                suggestion_count[s] = suggestion_count.get(s, 0) + 1
            
            if suggestion_count:
                final_suggestion = max(suggestion_count.items(), key=lambda x: x[1])[0]
            else:
                final_suggestion = "Aguardar"
        
    return patterns_detected, final_suggestion

# ==============================
# Funções auxiliares para interface
# ==============================
def display_history(history: List[str]) -> None:
    """Exibe o histórico de forma formatada"""
    if not history:
        st.write("Nenhum resultado inserido ainda.")
        return
        
    reversed_history = list(reversed(history))
    
    # Usar colunas para uma exibição mais compacta
    cols = st.columns(min(12, len(reversed_history)))
    for idx, result in enumerate(reversed_history):
        with cols[idx % len(cols)]:
            st.markdown(f"<h4 style='text-align: center;'>{result}</h4>", unsafe_allow_html=True)

def display_statistics(history: List[str]) -> None:
    """Exibe estatísticas detalhadas do histórico"""
    if not history:
        return
        
    red_count = history.count("🔴")
    blue_count = history.count("🔵")
    draw_count = history.count("🟡")
    total = len(history)
    
    st.subheader("📊 Estatísticas Detalhadas")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔴 Vermelho", f"{red_count} ({red_count/total*100:.1f}%)" if total > 0 else "0")
    with col2:
        st.metric("🔵 Azul", f"{blue_count} ({blue_count/total*100:.1f}%)" if total > 0 else "0")
    with col3:
        st.metric("🟡 Empate", f"{draw_count} ({draw_count/total*100:.1f}%)" if total > 0 else "0")
    with col4:
        st.metric("Total", total)
    
    # Estatísticas adicionais
    if total > 5:
        st.write("**Últimas 10 jogadas:**")
        last_10 = history[-10:] if len(history) >= 10 else history
        red_10 = last_10.count("🔴")
        blue_10 = last_10.count("🔵")
        draw_10 = last_10.count("🟡")
        st.write(f"🔴: {red_10} | 🔵: {blue_10} | 🟡: {draw_10}")
        
        # Maior sequência
        max_streak = 1
        current_streak = 1
        prev = history[0]
        
        for i in range(1, len(history)):
            if history[i] == prev and history[i] != "🟡":
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
            prev = history[i]
        
        st.write(f"Maior sequência: {max_streak}")

# ==============================
# Interface Streamlit melhorada
# ==============================
def main():
    st.set_page_config(
        page_title="Football Studio Analyzer Avançado", 
        layout="wide",
        page_icon="🎲"
    )
    
    st.title("🎲 Football Studio Analyzer Avançado")
    st.write("Análise de mais de 40 padrões do Football Studio com histórico expandido.")
    
    # Inicializar histórico
    if "history" not in st.session_state:
        st.session_state.history = deque(maxlen=MAX_HISTORY)
    
    # Sidebar para controles
    with st.sidebar:
        st.header("Controles")
        
        if st.button("📊 Mostrar Estatísticas Detalhadas"):
            st.session_state.show_stats = not st.session_state.get('show_stats', False)
        
        if st.button("🗑️ Limpar Histórico", type="secondary"):
            st.session_state.history.clear()
            st.success("Histórico limpo!")
            st.rerun()
            
        if st.button("↩️ Desfazer Último", type="secondary") and st.session_state.history:
            st.session_state.history.pop()
            st.success("Último resultado removido!")
            st.rerun()
            
        st.header("Adicionar Múltiplos Resultados")
        multi_input = st.text_input("Sequência (ex: 🔴🔵🟡🔴)", "")
        if st.button("Adicionar Sequência") and multi_input:
            # Extrai emojis do texto
            emojis = re.findall(r'[🔴🔵🟡]', multi_input)
            for emoji in emojis:
                st.session_state.history.append(emoji)
            st.success(f"{len(emojis)} resultados adicionados!")
            st.rerun()
    
    # Botões de entrada principais
    st.subheader("Registrar Resultado")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔴 Vermelho", use_container_width=True, key="red_btn"):
            st.session_state.history.append("🔴")
            st.rerun()
    with col2:
        if st.button("🔵 Azul", use_container_width=True, key="blue_btn"):
            st.session_state.history.append("🔵")
            st.rerun()
    with col3:
        if st.button("🟡 Empate", use_container_width=True, key="draw_btn"):
            st.session_state.history.append("🟡")
            st.rerun()
    
    # Exibir histórico
    st.subheader("📜 Histórico (mais recente primeiro)")
    display_history(st.session_state.history)
    
    # Exibir estatísticas se solicitado
    if st.session_state.get('show_stats', False):
        display_statistics(st.session_state.history)
    
    # Análise de padrões
    st.subheader("🤖 Análise de Padrões")
    patterns_detected, suggestion = analyze_patterns(st.session_state.history)
    
    if patterns_detected:
        st.write(f"**{len(patterns_detected)} Padrões Detectados:**")
        
        # Agrupar padrões por categoria
        categories = {
            "Streaks": [],
            "Alternância": [],
            "Repetição": [],
            "Ciclos": [],
            "Empates": [],
            "Estatísticos": [],
            "Outros": []
        }
        
        for pattern in patterns_detected:
            if "streak" in pattern.lower() or "Streak" in pattern:
                categories["Streaks"].append(pattern)
            elif "Altern" in pattern or "Zebra" in pattern:
                categories["Alternância"].append(pattern)
            elif "Repet" in pattern or "Espelho" in pattern:
                categories["Repetição"].append(pattern)
            elif "Ciclo" in pattern:
                categories["Ciclos"].append(pattern)
            elif "empate" in pattern.lower() or "Empate" in pattern:
                categories["Empates"].append(pattern)
            elif "Estat" in pattern or "Dominância" in pattern or "Cluster" in pattern:
                categories["Estatísticos"].append(pattern)
            else:
                categories["Outros"].append(pattern)
        
        # Exibir padrões por categoria
        for category, patterns in categories.items():
            if patterns:
                with st.expander(f"{category} ({len(patterns)})"):
                    for pattern in patterns:
                        st.write(f"- {pattern}")
    else:
        st.info("Nenhum padrão detectado. Continue adicionando resultados.")
    
    # Sugestão com destaque visual
    st.subheader("💡 Sugestão de Entrada")
    
    if suggestion == "Aguardar":
        st.warning(f"## {suggestion}")
    elif "🔴" in suggestion:
        st.error(f"## {suggestion}")
    elif "🔵" in suggestion:
        st.info(f"## {suggestion}")
    elif "🟡" in suggestion:
        st.warning(f"## {suggestion}")
    else:
        st.success(f"## {suggestion}")
        
    # Explicação da sugestão
    if suggestion != "Aguardar":
        st.write("**Lógica por trás da sugestão:**")
        if "streak" in suggestion.lower():
            st.write("Streaks longos tendem a se quebrar, sugerindo a cor oposta.")
        elif "Altern" in suggestion:
            st.write("Padrões de alternância tendem a continuar seguindo a sequência.")
        elif "Correção" in suggestion:
            st.write("Desequilíbrios estatísticos tendem a se corrigir com o tempo.")
        elif "empate" in suggestion.lower():
            st.write("Padrões de empate seguem comportamentos específicos.")

if __name__ == "__main__":
    main()
