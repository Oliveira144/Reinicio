import streamlit as st

# --- Histórico de até 9 resultados (mais recente no índice 0) ---
def update_history(new_value):
    if len(st.session_state.history) >= 9:
        st.session_state.history.pop()  # remove o mais antigo (final da lista)
    st.session_state.history.insert(0, new_value)  # insere o novo no início

# --- Auxiliares para análise ---
def count_alternations(history):
    count = 0
    for i in range(len(history)-1):
        if history[i] != history[i+1] and history[i] != '🟡' and history[i+1] != '🟡':
            count += 1
    return count

def count_consecutive_repetitions(history):
    count = 1
    max_count = 1
    for i in range(1, len(history)):
        if history[i] == history[i-1] and history[i] != '🟡':
            count += 1
            max_count = max(max_count, count)
        else:
            count = 1
    return max_count

def find_doubles_blocks(history):
    blocks = 0
    i = 0
    while i < len(history) - 1:
        if history[i] == history[i+1] and history[i] != '🟡':
            blocks += 1
            i += 2
        else:
            i += 1
    return blocks

def find_triples_blocks(history):
    blocks = 0
    i = 0
    while i < len(history) - 2:
        if history[i] == history[i+1] == history[i+2] and history[i] != '🟡':
            blocks += 1
            i += 3
        else:
            i += 1
    return blocks

def is_mirror_pattern(history):
    n = len(history)
    if n < 6:
        return False
    mid = n // 2
    # Tolerância a empates no meio
    for i in range(mid):
        left = history[i]
        right = history[n - 1 - i]
        if left == '🟡' or right == '🟡':
            continue
        if left != right:
            return False
    return True

def contains_draw_in_last_n(history, n):
    return '🟡' in history[:n]

# --- Detecção principal de padrões e descrição estratégica ---
def detect_pattern(history):
    if len(history) < 4:
        return 'Insuficientes dados', None

    alternations = count_alternations(history)
    max_reps = count_consecutive_repetitions(history)
    doubles = find_doubles_blocks(history)
    triples = find_triples_blocks(history)
    mirror = is_mirror_pattern(history)
    draws = history.count('🟡')

    # Padrão Surf 🌊: 4+ alternâncias suaves e repetição no pico
    if alternations >= 4 and max_reps <= 2 and not contains_draw_in_last_n(history, 3):
        # Checa se há repetição na 5ª-6ª alternância para caracterizar pico
        if len(history) >= 6 and history[4] == history[5]:
            return 'Surf 🌊', 'Após 4 alternâncias, apostar na repetição da última cor; após empate inverter'
        return 'Surf 🌊', 'Apostar na repetição da última cor após 4 alternâncias'

    # Ping-Pong 🏓: alternância limpa 4-6 jogadas
    if alternations >= 3 and alternations <= 6 and max_reps == 1:
        if contains_draw_in_last_n(history, 3):
            return 'Ping-Pong 🏓', 'Após empate, indica inversão. Apostar na repetição da última cor antes do empate.'
        else:
            return 'Ping-Pong 🏓', 'Após 3 alternâncias, preparar para quebra; apostar repetição na 5ª ou 6ª.'

    # Alternância 🔁 - suja / micro quebras com duplas curtas
    if doubles >= 1 and max_reps == 2:
        return 'Alternância Suja 🔁', 'Após dupla, sistema tende a voltar à alternância; após 2 duplas seguidas, inversão.'

    # Zig-Zag ⚡ - reversões camufladas (duplas falsas inseridas)
    if doubles >= 1 and max_reps >= 2 and draws <= 1 and len(history) >= 6:
        return 'Zig-Zag ⚡', 'Após dupla inversa apostar na inversão; após empate, voltar lado anterior do empate.'

    # 2x2 (Duplas alternadas)
    if doubles >= 2:
        if doubles >= 3:
            return '2x2 (Duplas) 🟦', 'Após 2ª dupla preparar inversão; após 3 blocos apostar no lado oposto.'
        else:
            return '2x2 (Duplas) 🟦', 'Ciclo de duplas em andamento.'

    # 3x3 (Triplas alternadas)
    if triples >= 2:
        return '3x3 (Triplas) 🔺', 'Após 2 triplas apostar na inversão; após empate inverter e reduzir aposta.'

    # Espelhado (Mirror)
    if mirror:
        return 'Espelhado 🪞', 'Identifique centro e aposte na repetição da metade anterior.'

    # Colapso / Reverso Quântico
    if draws >= 1 and doubles >= 2 and alternations >= 1:
        return 'Colapso / Reverso Quântico 🌀', 'Não apostar até reinício limpo; empate indica reinício do ciclo.'

    # Âncora (Empate)
    if contains_draw_in_last_n(history, 1):
        return 'Âncora (Empate) ⚓', 'Após empate apostar no oposto da última cor; se ocorrer novo empate, apostar mesmo lado anterior.'

    # Camuflado - mistura complexa
    if draws >= 2 and doubles >= 1 and triples >= 1:
        return 'Camuflado 🕵️‍♂️', 'Apostar somente após confirmação de blocos limpos.'

    return 'Padrão Desconhecido', 'Sem sugestão clara'

# --- Nível de manipulação ---
def calculate_manipulation_level(history):
    alternations = count_alternations(history)
    draws = history.count('🟡')
    max_reps = count_consecutive_repetitions(history)
    doubles = find_doubles_blocks(history)
    triples = find_triples_blocks(history)

    # Regras baseadas em pulsos e complexidade
    if alternations <= 2 and draws == 0 and max_reps <= 2:
        return 1  # Natural / aleatório
    elif draws <= 2 and max_reps <= 2 and doubles <= 1:
        return 3  # Controle leve
    elif alternations >= 4 and draws >= 1:
        return 5  # Manipulação média
    elif max_reps >= 3 or doubles >= 3:
        return 7  # Manipulação profunda
    elif triples >= 2 or draws >= 3 or doubles >= 4:
        return 9  # Manipulação quântica
    return 4  # Default intermediário

# --- Previsão de próxima jogada ---
def predict_next(history, manipulation_level, pattern):
    if not history:
        return {'🔴': 33, '🔵': 33, '🟡': 34}

    last = history[0]

    # Estratégia baseada no padrão detectado
    if pattern.startswith('Surf'):
        # Após 4 alternâncias, repetir última cor, após empate inverter
        if contains_draw_in_last_n(history, 1) and len(history) > 1:
            return {history[1]: 70, '🟡': 10, last: 20}
        else:
            return {last: 75, '🟡': 5, **{c:10 for c in ['🔴', '🔵', '🟡'] if c != last}}

    if pattern.startswith('Ping-Pong'):
        if contains_draw_in_last_n(history, 1) and len(history) > 1:
            return {history[1]: 80, '🟡': 10, last: 10}
        else:
            return {last: 70, '🟡': 10, **{c:10 for c in ['🔴', '🔵', '🟡'] if c != last}}

    if pattern.startswith('Alternância'):
        # Apostar na alternância
        alt_color = '🔴' if last == '🔵' else '🔵'
        return {alt_color: 70, last: 25, '🟡': 5}

    if pattern.startswith('Zig-Zag'):
        # Apostar na inversão após duplas
        invert_color = '🔴' if last == '🔵' else '🔵'
        return {invert_color: 75, last: 20, '🟡': 5}

    if pattern.startswith('2x2'):
        invert_color = '🔴' if last == '🔵' else '🔵'
        return {invert_color: 80, last:15, '🟡':5}

    if pattern.startswith('3x3'):
        invert_color = '🔴' if last == '🔵' else '🔵'
        return {invert_color: 80, last:15, '🟡':5}

    if pattern.startswith('Espelhado'):
        # Repetir metade anterior (simplificado)
        return {last: 70, '🟡': 10, **{c:10 for c in ['🔴', '🔵', '🟡'] if c != last}}

    if pattern.startswith('Colapso'):
        return {'🔴': 33, '🔵': 33, '🟡': 34}

    if pattern.startswith('Âncora'):
        invert_color = '🔴' if last == '🔵' else '🔵'
        return {invert_color: 75, last: 20, '🟡':5}

    # Pattern Camuflado e demais
    return {'🔴': 33, '🔵': 33, '🟡': 34}

# --- Gerar sinal visual de alerta ---
def alert_signal(level):
    if 4 <= level <= 6:
        return '🟢 Brecha Detectada'
    elif 7 <= level <= 8:
        return '🟡 Risco Médio'
    elif level == 9:
        return '🔴 Manipulação Alta'
    else:
        return '🟢 Normal'

# --- Sugestão de aposta detalhada ---
def suggest_bet(pattern, history):
    if not history or len(history) < 2:
        return 'Aguardando mais dados para recomendação'

    if pattern == 'Insuficientes dados':
        return 'Insuficientes dados para análise'

    # A partir da descrição da detecção, pode-se aprimorar aqui conforme necessidade
    # Para simplicidade, aproveita as estratégias descritas nos padrões
    return pattern

# --- Inicializar estado ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- Interface Streamlit ---
st.title('Football Studio - Leitura Avançada de Padrões')

st.sidebar.header('Registrar novo resultado (mais recente à esquerda)')

cols = st.sidebar.columns(3)
if cols[0].button('🔴'):
    update_history('🔴')
if cols[1].button('🔵'):
    update_history('🔵')
if cols[2].button('🟡'):
    update_history('🟡')

st.subheader('Histórico (mais recente → mais antigo):')
st.write(' '.join(st.session_state.history))

# Detectar padrão e nível de manipulação
pattern, strategy = detect_pattern(st.session_state.history)
level = calculate_manipulation_level(st.session_state.history)
prediction_raw = predict_next(st.session_state.history, level, pattern)

# Normalizar previsão para 100%
total_pred = sum(prediction_raw.values())
prediction = {k: round(v / total_pred * 100) for k, v in prediction_raw.items()}

alert_msg = alert_signal(level)
bet_recommendation = suggest_bet(pattern, st.session_state.history)

st.subheader('Resumo da Análise')
st.markdown(f"- **Padrão Detectado:** {pattern}")
st.markdown(f"- **Descrição / Estratégia:** {strategy}")
st.markdown(f"- **Nível de Manipulação:** {level}")
st.markdown(f"- **Sinal de Alerta:** {alert_msg}")

st.subheader('Previsão Próxima Jogada')
st.write(f"🔴 {prediction['🔴']}% | 🔵 {prediction['🔵']}% | 🟡 {prediction['🟡']}%")

st.subheader('Sugestão de Aposta')
st.write(bet_recommendation)
