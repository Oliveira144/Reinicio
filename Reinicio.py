import streamlit as st

# --- Histórico com limite até 9 resultados ---
def update_history(new_value):
    if len(st.session_state.history) >= 9:
        st.session_state.history.pop()  # remove o resultado mais antigo
    st.session_state.history.insert(0, new_value)  # insere o novo resultado no início

# --- Função para limpar histórico ---
def clear_history():
    st.session_state.history = []

# --- Contagens e análise - melhorias na lógica ---
def count_alternations(history):
    count = 0
    for i in range(len(history) - 1):
        if history[i] != history[i + 1] and history[i] != '🟡' and history[i + 1] != '🟡':
            count += 1
    return count

def count_consecutive_repetitions(history):
    count = max_count = 1
    for i in range(1, len(history)):
        if history[i] == history[i - 1] and history[i] != '🟡':
            count += 1
            max_count = max(max_count, count)
        else:
            count = 1
    return max_count

def find_doubles_blocks(history):
    blocks, i = 0, 0
    while i < len(history) - 1:
        if history[i] == history[i + 1] and history[i] != '🟡':
            blocks += 1
            i += 2
        else:
            i += 1
    return blocks

def find_triples_blocks(history):
    blocks, i = 0, 0
    while i < len(history) - 2:
        if history[i] == history[i + 1] == history[i + 2] and history[i] != '🟡':
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
    for i in range(mid):
        left = history[i]
        right = history[n - 1 - i]
        if left == '🟡' or right == '🟡':  # ignora empates
            continue
        if left != right:
            return False
    return True

def contains_draw_in_last_n(history, n):
    return '🟡' in history[:n]

def detect_zigzag_break(history):
    # Detecta um padrão tipo zigzag com pequenas quebras ou trocas
    for i in range(len(history) - 3):
        segment = history[i:i + 4]
        if segment[0] == segment[2] and segment[1] == segment[3] and segment[0] != segment[1] and '🟡' not in segment:
            return True
    return False

# --- Detecção dos padrões com melhorias ---
def detect_pattern(history):
    if len(history) < 4:
        return 'Insuficientes dados', None

    alternations = count_alternations(history)
    max_reps = count_consecutive_repetitions(history)
    doubles = find_doubles_blocks(history)
    triples = find_triples_blocks(history)
    mirror = is_mirror_pattern(history)
    draws = history.count('🟡')
    zigzag_break = detect_zigzag_break(history)

    # Melhores padrões com base em análise prática do Football Studio
    # Padrão Surf com pico de repetição e alternância forte
    if alternations >= 4 and max_reps <= 2 and not contains_draw_in_last_n(history, 3):
        if len(history) >= 6 and history[4] == history[5]:
            return 'Surf 🌊', 'Após 4 alternâncias, apostar na repetição da última cor; após empate inverter'
        return 'Surf 🌊', 'Apostar na repetição da última cor após 4 alternâncias'

    # Padrão Ping-Pong: alternância limpa e regular
    if 3 <= alternations <= 6 and max_reps == 1:
        if contains_draw_in_last_n(history, 3):
            return 'Ping-Pong 🏓', 'Após empate, indica inversão. Apostar repetição antes do empate.'
        return 'Ping-Pong 🏓', 'Alternância consistente; preparar para quebra'

    # Alternância suja com duplas e pequenas quebras
    if doubles >= 1 and max_reps == 2:
        return 'Alternância Suja 🔁', 'Após duplas, tendência a retornar à alternância; após 2 duplas seguidas, inversão provável'

    # Detecta padrão Zig-Zag aprimorado (com pequenas quebras)
    if zigzag_break and doubles >= 1 and max_reps >= 2 and draws <= 1 and len(history) >= 6:
        return 'Zig-Zag ⚡', 'Após dupla inversa apostar na inversão; após empate, voltar ao lado anterior'

    # Detecta duplas em sequência (2x2)
    if doubles >= 2:
        if doubles >= 3:
            return '2x2 (Duplas) 🟦', 'Após 2ª dupla preparar inversão; após 3 blocos apostar lado oposto'
        return '2x2 (Duplas) 🟦', 'Ciclo de duplas em andamento'

    # Detecta triplas em sequência (3x3)
    if triples >= 2:
        return '3x3 (Triplas) 🔺', 'Após 2 triplas apostar na inversão; após empate inverter e reduzir aposta'

    # Padrão espelhado (mirror)
    if mirror:
        return 'Espelhado 🪞', 'Identifique centro e aposte na repetição da metade anterior'

    # Colapso / Reverso Quântico (complexidade alta)
    if draws >= 1 and doubles >= 2 and alternations >= 1:
        return 'Colapso / Reverso Quântico 🌀', 'Não apostar até reinício limpo; empate indica reinício do ciclo'

    # Âncora (empate)
    if contains_draw_in_last_n(history, 1):
        return 'Âncora (Empate) ⚓', 'Após empate apostar no oposto; se repetir empate, apostar na mesma cor do primeiro'

    # Camuflado - mistura complexa
    if draws >= 2 and doubles >=1 and triples >= 1:
        return 'Camuflado 🕵️‍♂️', 'Apostar somente após confirmação de blocos limpos'

    return 'Padrão Desconhecido', 'Sem sugestão clara'

# --- Nível de manipulação refinado ---
def calculate_manipulation_level(history):
    alternations = count_alternations(history)
    draws = history.count('🟡')
    max_reps = count_consecutive_repetitions(history)
    doubles = find_doubles_blocks(history)
    triples = find_triples_blocks(history)

    # Considera mais fatores e distribui níveis com base em estudos de padrões
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
    return 4  # Default estimado intermediário

# --- Previsão de próxima jogada com distribuição refinada ---
def predict_next(history, manipulation_level, pattern):
    if not history:
        return {'🔴': 33, '🔵': 33, '🟡': 34}

    last = history[0]

    # Definir inverso
    inverse = '🔴' if last == '🔵' else '🔵'

    # Estratégias baseadas em padrão detectado
    if pattern.startswith('Surf'):
        if contains_draw_in_last_n(history, 1) and len(history) > 1:
            return {history[1]: 70, '🟡': 10, last: 20}
        return {last: 75, '🟡': 5, inverse: 20}

    if pattern.startswith('Ping-Pong'):
        if contains_draw_in_last_n(history, 1) and len(history) > 1:
            return {history[1]: 80, '🟡': 10, last: 10}
        return {last: 70, '🟡': 10, inverse: 20}

    if pattern.startswith('Alternância Suja'):
        return {inverse: 70, last: 25, '🟡': 5}

    if pattern.startswith('Zig-Zag'):
        return {inverse: 75, last: 20, '🟡': 5}

    if pattern.startswith('2x2'):
        return {inverse: 80, last: 15, '🟡': 5}

    if pattern.startswith('3x3'):
        return {inverse: 80, last: 15, '🟡': 5}

    if pattern.startswith('Espelhado'):
        return {last: 70, '🟡': 10, inverse: 20}

    if pattern.startswith('Colapso'):
        return {'🔴': 33, '🔵': 33, '🟡': 34}

    if pattern.startswith('Âncora'):
        return {inverse: 75, last: 20, '🟡': 5}

    if pattern.startswith('Camuflado'):
        return {'🔴': 33, '🔵': 33, '🟡': 34}

    return {'🔴': 33, '🔵': 33, '🟡': 34}

# --- Geração de sinal visual de alerta ---
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

    last = history[0]

    if pattern == 'Surf 🌊':
        if '🟡' in history[:3]:
            opposite = '🔴' if last == '🔵' else '🔵'
            return f'Apostar na inversão após empate: {opposite}'
        return f'Apostar na repetição da última cor: {last}'

    if pattern == 'Ping-Pong 🏓':
        if '🟡' in history[:3]:
            opposite = '🔴' if last == '🔵' else '🔵'
            return f'Após empate, apostar na inversão: {opposite}'
        return f'Apostar na repetição da última cor: {last}'

    if pattern == 'Alternância Suja 🔁':
        opposite = '🔴' if last == '🔵' else '🔵'
        return f'Apostar na alternância: {opposite}'

    if pattern == 'Zig-Zag ⚡':
        opposite = '🔴' if last == '🔵' else '🔵'
        return f'Apostar na inversão após dupla: {opposite}'

    if pattern.startswith('2x2'):
        opposite = '🔴' if last == '🔵' else '🔵'
        return f'Apostar no lado oposto após segunda dupla: {opposite}'

    if pattern.startswith('3x3'):
        opposite = '🔴' if last == '🔵' else '🔵'
        if '🟡' in history[:3]:
            return f'Após empate, inverter e reduzir aposta: {opposite}'
        return f'Apostar na inversão após 2 triplas: {opposite}'

    if pattern == 'Espelhado 🪞':
        return f'Repetir metade anterior; aposta provável: {last}'

    if pattern == 'Colapso / Reverso Quântico 🌀':
        return 'Não apostar; aguardar retomada de padrão limpo.'

    if pattern == 'Âncora (Empate) ⚓':
        if '🟡' in history[:2]:
            if len(history) > 2 and history[2] == history[0]:
                return f'Apostar no mesmo lado do primeiro após empate: {last}'
            opposite = '🔴' if last == '🔵' else '🔵'
            return f'Após empate, apostar no oposto: {opposite}'
        opposite = '🔴' if last == '🔵' else '🔵'
        return f'Após empate, apostar no oposto: {opposite}'

    if pattern == 'Camuflado 🕵️‍♂️':
        return 'Apostar somente após confirmação de blocos limpos.'

    return 'Sem sugestão clara para aposta.'

# --- Inicialização do estado ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- Interface Streamlit ---
st.title('Football Studio - Leitura Avançada de Padrões')

st.sidebar.header('Registrar novo resultado (mais recente à esquerda)')
cols = st.sidebar.columns(4)
if cols[0].button('🔴'):
    update_history('🔴')
if cols[1].button('🔵'):
    update_history('🔵')
if cols[2].button('🟡'):
    update_history('🟡')
if cols[3].button('Limpar Histórico'):
    clear_history()

st.subheader('Histórico (mais recente → mais antigo):')
st.write(' '.join(st.session_state.history))

# Detecção de padrão e manipulação
pattern, strategy = detect_pattern(st.session_state.history)
level = calculate_manipulation_level(st.session_state.history)
prediction_raw = predict_next(st.session_state.history, level, pattern)

# Normalizar predição
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
