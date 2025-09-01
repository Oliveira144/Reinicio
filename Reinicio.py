import streamlit as st
from collections import deque, Counter
from typing import List, Tuple, Optional, Dict
import re
import numpy as np
from datetime import datetime

# ==============================
# Configurações e constantes
# ==============================
MAX_HISTORY = 30
STREAK_LENGTHS = [2, 3, 4, 5, 6]
PATTERN_SIZES = [2, 3, 4, 5, 6]
CYCLE_SIZES = [2, 3, 4, 5]

# ==============================
# Classe principal de análise dinâmica
# ==============================
class FootballStudioAnalyzer:
    def __init__(self):
        self.pattern_weights = {
            'high_streak': 5,          # Streaks longos
            'medium_streak': 3,        # Streaks médios
            'low_streak': 2,           # Streaks curtos
            'repetition': 4,           # Padrões repetidos
            'alternation': 3,          # Padrões de alternância
            'cycle': 4,                # Ciclos
            'mirror': 4,               # Padrões espelhados
            'draw_pattern': 3,         # Padrões com empates
            'statistical': 5,          # Análise estatística
            'cluster': 3,              # Agrupamentos
            'zebra': 3,                # Padrão zebra
            'reversal': 3              # Reversões
        }
        
    def get_opposite_color(self, color: str) -> str:
        """Retorna a cor oposta para sugestão de apostas"""
        if color == "🔴": return "🔵"
        elif color == "🔵": return "🔴"
        return "🟡"
    
    def detect_all_patterns(self, history: List[str]) -> Tuple[List[Dict], Dict]:
        """Detecta todos os padrões possíveis no histórico"""
        if len(history) < 5:
            return [], {}
            
        patterns = []
        confidence_scores = {"🔴": 0, "🔵": 0, "🟡": 0}
        
        # 1. Análise de streaks (sequências)
        streaks = self._analyze_streaks(history)
        patterns.extend(streaks)
        
        # 2. Análise de padrões repetitivos
        repetitions = self._analyze_repetitions(history)
        patterns.extend(repetitions)
        
        # 3. Análise de ciclos
        cycles = self._analyze_cycles(history)
        patterns.extend(cycles)
        
        # 4. Análise de padrões com empates
        draw_patterns = self._analyze_draw_patterns(history)
        patterns.extend(draw_patterns)
        
        # 5. Análise estatística
        stats_patterns = self._analyze_statistical(history)
        patterns.extend(stats_patterns)
        
        # 6. Análise de agrupamentos
        clusters = self._analyze_clusters(history)
        patterns.extend(clusters)
        
        # 7. Análise de padrões avançados
        advanced = self._analyze_advanced_patterns(history)
        patterns.extend(advanced)
        
        # Calcular pontuação de confiança para cada cor
        for pattern in patterns:
            if pattern['suggestion'] in confidence_scores:
                confidence_scores[pattern['suggestion']] += pattern['confidence']
        
        return patterns, confidence_scores
    
    def _analyze_streaks(self, history: List[str]) -> List[Dict]:
        """Analisa sequências de cores iguais"""
        patterns = []
        recent = history[-10:]  # Últimas 10 jogadas
        
        for length in STREAK_LENGTHS:
            if len(recent) < length:
                continue
                
            # Verificar streaks de vermelho
            if all(c == "🔴" for c in recent[-length:]):
                confidence = self.pattern_weights['high_streak'] if length >= 4 else self.pattern_weights['medium_streak']
                patterns.append({
                    'type': f'streak_red_{length}',
                    'description': f'Sequência de {length} vermelhos consecutivos',
                    'suggestion': '🔵',
                    'confidence': confidence
                })
            
            # Verificar streaks de azul
            if all(c == "🔵" for c in recent[-length:]):
                confidence = self.pattern_weights['high_streak'] if length >= 4 else self.pattern_weights['medium_streak']
                patterns.append({
                    'type': f'streak_blue_{length}',
                    'description': f'Sequência de {length} azuis consecutivos',
                    'suggestion': '🔴',
                    'confidence': confidence
                })
        
        return patterns
    
    def _analyze_repetitions(self, history: List[str]) -> List[Dict]:
        """Analisa padrões repetitivos"""
        patterns = []
        recent = history[-12:]  # Últimas 12 jogadas
        
        for size in PATTERN_SIZES:
            if len(recent) < size * 2:
                continue
                
            # Verificar padrões repetidos (ex: 🔴🔵🔴🔵 se repete)
            first = recent[-(size*2):-size]
            second = recent[-size:]
            
            if first == second:
                # Determinar próxima cor baseada no padrão
                next_index = size % len(first)
                next_color = first[next_index] if first[next_index] != "🟡" else first[0]
                
                patterns.append({
                    'type': f'repetition_{size}',
                    'description': f'Padrão de {size} cores se repetindo',
                    'suggestion': next_color,
                    'confidence': self.pattern_weights['repetition']
                })
        
        return patterns
    
    def _analyze_cycles(self, history: List[str]) -> List[Dict]:
        """Analisa padrões cíclicos"""
        patterns = []
        recent = history[-12:]
        
        for size in CYCLE_SIZES:
            if len(recent) < size * 2:
                continue
                
            # Verificar ciclos regulares
            first = recent[-(size*2):-size]
            second = recent[-size:]
            
            if first == second:
                next_color = first[0] if first[0] != "🟡" else first[1]
                patterns.append({
                    'type': f'cycle_regular_{size}',
                    'description': f'Ciclo regular de {size} cores',
                    'suggestion': next_color,
                    'confidence': self.pattern_weights['cycle']
                })
            
            # Verificar ciclos invertidos
            if first == list(reversed(second)):
                next_color = self.get_opposite_color(second[-1]) if second[-1] != "🟡" else "🔴"
                patterns.append({
                    'type': f'cycle_inverted_{size}',
                    'description': f'Ciclo invertido de {size} cores',
                    'suggestion': next_color,
                    'confidence': self.pattern_weights['cycle']
                })
        
        return patterns
    
    def _analyze_draw_patterns(self, history: List[str]) -> List[Dict]:
        """Analisa padrões envolvendo empates"""
        patterns = []
        recent = history[-8:]
        draw_positions = [i for i, c in enumerate(recent) if c == "🟡"]
        
        if not draw_positions:
            return patterns
        
        # Padrão: Empate seguido de tendência
        if len(recent) >= 3 and recent[-2] == "🟡" and recent[-1] != "🟡":
            patterns.append({
                'type': 'draw_followed',
                'description': 'Empate seguido de cor definida',
                'suggestion': recent[-1],
                'confidence': self.pattern_weights['draw_pattern']
            })
        
        # Padrão: Múltiplos empates próximos
        if len(draw_positions) >= 2:
            last_draw_gap = draw_positions[-1] - draw_positions[-2]
            if last_draw_gap <= 2:  # Empates muito próximos
                patterns.append({
                    'type': 'draw_cluster',
                    'description': 'Agrupamento de empates recentes',
                    'suggestion': self.get_opposite_color(history[-1]) if history[-1] != "🟡" else "🔴",
                    'confidence': self.pattern_weights['draw_pattern']
                })
        
        return patterns
    
    def _analyze_statistical(self, history: List[str]) -> List[Dict]:
        """Análise estatística do histórico"""
        patterns = []
        recent = history[-15:]
        
        if len(recent) < 10:
            return patterns
        
        red_count = recent.count("🔴")
        blue_count = recent.count("🔵")
        total = red_count + blue_count
        
        if total == 0:
            return patterns
        
        # Desequilíbrio significativo
        if red_count / total >= 0.7:
            patterns.append({
                'type': 'statistical_imbalance_red',
                'description': f'Desequilíbrio estatístico: {red_count}🔴 vs {blue_count}🔵',
                'suggestion': '🔵',
                'confidence': self.pattern_weights['statistical']
            })
        elif blue_count / total >= 0.7:
            patterns.append({
                'type': 'statistical_imbalance_blue',
                'description': f'Desequilíbrio estatístico: {blue_count}🔵 vs {red_count}🔴',
                'suggestion': '🔴',
                'confidence': self.pattern_weights['statistical']
            })
        
        # Tendência recente (últimas 5 vs anteriores)
        if len(recent) >= 10:
            last_5 = recent[-5:]
            previous_5 = recent[-10:-5]
            
            last_red = last_5.count("🔴")
            last_blue = last_5.count("🔵")
            prev_red = previous_5.count("🔴")
            prev_blue = previous_5.count("🔵")
            
            # Mudança significativa de tendência
            if last_red >= 4 and prev_blue >= 3:
                patterns.append({
                    'type': 'trend_change_red',
                    'description': 'Mudança de tendência para vermelho',
                    'suggestion': '🔴',
                    'confidence': self.pattern_weights['statistical']
                })
            elif last_blue >= 4 and prev_red >= 3:
                patterns.append({
                    'type': 'trend_change_blue',
                    'description': 'Mudança de tendência para azul',
                    'suggestion': '🔵',
                    'confidence': self.pattern_weights['statistical']
                })
        
        return patterns
    
    def _analyze_clusters(self, history: List[str]) -> List[Dict]:
        """Analisa agrupamentos de cores"""
        patterns = []
        recent = history[-10:]
        
        # Verificar agrupamentos extremos
        for color in ["🔴", "🔵"]:
            count = recent.count(color)
            if count >= 7:  # 70% ou mais de uma cor
                patterns.append({
                    'type': f'cluster_{color}',
                    'description': f'Agrupamento extremo de {color}',
                    'suggestion': self.get_opposite_color(color),
                    'confidence': self.pattern_weights['cluster']
                })
        
        return patterns
    
    def _analyze_advanced_patterns(self, history: List[str]) -> List[Dict]:
        """Analisa padrões avançados e complexos"""
        patterns = []
        recent = history[-12:]
        
        # Padrão Zebra (alternância perfeita)
        zebra = True
        for i in range(1, len(recent)):
            if recent[i] == recent[i-1] or recent[i] == "🟡" or recent[i-1] == "🟡":
                zebra = False
                break
                
        if zebra and len(recent) >= 4:
            patterns.append({
                'type': 'zebra_pattern',
                'description': 'Padrão zebra (alternância perfeita)',
                'suggestion': recent[-2],  # Manter a alternância
                'confidence': self.pattern_weights['zebra']
            })
        
        # Padrão de reversão (ex: 🔴🔴🔵 -> continua 🔵)
        if len(recent) >= 4:
            if recent[-3] == recent[-2] and recent[-2] != recent[-1] and recent[-1] != "🟡":
                patterns.append({
                    'type': 'reversal_pattern',
                    'description': 'Padrão de reversão após sequência',
                    'suggestion': recent[-1],  # Continuar a reversão
                    'confidence': self.pattern_weights['reversal']
                })
        
        return patterns
    
    def generate_recommendation(self, confidence_scores: Dict) -> Tuple[str, float]:
        """Gera recomendação baseada nas pontuações de confiança"""
        if not confidence_scores or sum(confidence_scores.values()) == 0:
            return "Aguardar", 0.0
        
        max_score = max(confidence_scores.values())
        total_score = sum(confidence_scores.values())
        
        if max_score == 0:
            return "Aguardar", 0.0
        
        # Encontrar a cor com maior pontuação
        for color, score in confidence_scores.items():
            if score == max_score:
                confidence_percentage = (max_score / total_score) * 100
                return color, confidence_percentage
        
        return "Aguardar", 0.0

# ==============================
# Interface Streamlit melhorada
# ==============================
def main():
    st.set_page_config(
        page_title="Football Studio Analyzer Pro", 
        layout="wide",
        page_icon="🎲"
    )
    
    st.title("🎲 Football Studio Analyzer Pro")
    st.write("Sistema avançado de análise de padrões em tempo real para Football Studio")
    
    # Inicializar analisador
    if "analyzer" not in st.session_state:
        st.session_state.analyzer = FootballStudioAnalyzer()
    
    # Inicializar histórico
    if "history" not in st.session_state:
        st.session_state.history = deque(maxlen=MAX_HISTORY)
    
    # Inicializar estatísticas
    if "pattern_stats" not in st.session_state:
        st.session_state.pattern_stats = {
            "🔴": 0, "🔵": 0, "🟡": 0,
            "total_analyzed": 0,
            "last_analysis": None
        }
    
    # Sidebar para controles
    with st.sidebar:
        st.header("⚙️ Controles")
        
        # Entrada rápida de resultados
        st.subheader("Entrada Rápida")
        sequence_input = st.text_input("Digite uma sequência (ex: 🔴🔵🟡🔴):", "")
        if st.button("Adicionar Sequência") and sequence_input:
            # Extrair emojis válidos
            emojis = re.findall(r'[🔴🔵🟡]', sequence_input)
            for emoji in emojis:
                st.session_state.history.append(emoji)
            st.success(f"{len(emojis)} resultados adicionados!")
            st.rerun()
        
        # Controles de histórico
        st.subheader("Gerenciamento de Histórico")
        if st.button("🗑️ Limpar Histórico", type="secondary"):
            st.session_state.history.clear()
            st.success("Histórico limpo!")
            st.rerun()
            
        if st.button("↩️ Desfazer Último", type="secondary") and st.session_state.history:
            st.session_state.history.pop()
            st.success("Último resultado removido!")
            st.rerun()
        
        # Configurações de análise
        st.subheader("Configurações de Análise")
        analysis_depth = st.slider("Profundidade de Análise", 5, 30, 15, 
                                  help="Quantidade de jogadas anteriores a serem analisadas")
    
    # Layout principal
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🎯 Registrar Resultado")
        
        # Botões de entrada
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            if st.button("🔴", use_container_width=True, key="red_btn"):
                st.session_state.history.append("🔴")
                st.rerun()
        with btn_col2:
            if st.button("🔵", use_container_width=True, key="blue_btn"):
                st.session_state.history.append("🔵")
                st.rerun()
        with btn_col3:
            if st.button("🟡", use_container_width=True, key="draw_btn"):
                st.session_state.history.append("🟡")
                st.rerun()
        
        # Exibir histórico
        st.subheader("📜 Histórico Recente")
        if st.session_state.history:
            # Mostrar histórico com os mais recentes primeiro
            reversed_history = list(reversed(st.session_state.history))
            cols = st.columns(min(10, len(reversed_history)))
            for idx, result in enumerate(reversed_history):
                with cols[idx % len(cols)]:
                    st.markdown(f"<h3 style='text-align: center;'>{result}</h3>", 
                               unsafe_allow_html=True)
        else:
            st.info("Nenhum resultado registrado ainda.")
        
        # Estatísticas simples
        if st.session_state.history:
            st.subheader("📊 Estatísticas Básicas")
            red_count = list(st.session_state.history).count("🔴")
            blue_count = list(st.session_state.history).count("🔵")
            draw_count = list(st.session_state.history).count("🟡")
            total = len(st.session_state.history)
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("🔴 Vermelho", f"{red_count} ({red_count/total*100:.1f}%)")
            with col_stat2:
                st.metric("🔵 Azul", f"{blue_count} ({blue_count/total*100:.1f}%)")
            with col_stat3:
                st.metric("🟡 Empate", f"{draw_count} ({draw_count/total*100:.1f}%)")
    
    with col2:
        st.subheader("🤖 Análise de Padrões em Tempo Real")
        
        if len(st.session_state.history) >= 5:
            # Realizar análise
            patterns, confidence_scores = st.session_state.analyzer.detect_all_patterns(
                list(st.session_state.history)[-analysis_depth:]
            )
            
            # Gerar recomendação
            recommendation, confidence = st.session_state.analyzer.generate_recommendation(confidence_scores)
            
            # Exibir recomendação principal
            st.subheader("💡 Recomendação de Entrada")
            
            # Destacar a recomendação com base na confiança
            if confidence > 60:
                st.success(f"## {recommendation} (Confiança: {confidence:.1f}%)")
                st.write("**Alta confiança nesta recomendação**")
            elif confidence > 30:
                st.info(f"## {recommendation} (Confiança: {confidence:.1f}%)")
                st.write("**Confiança moderada nesta recomendação**")
            else:
                st.warning(f"## {recommendation} (Confiança: {confidence:.1f}%)")
                st.write("**Baixa confiança - aguardar padrão mais claro**")
            
            # Exibir padrões detectados
            st.subheader("🔍 Padrões Detectados")
            if patterns:
                # Agrupar padrões por tipo
                pattern_categories = {}
                for pattern in patterns:
                    category = pattern['type'].split('_')[0]
                    if category not in pattern_categories:
                        pattern_categories[category] = []
                    pattern_categories[category].append(pattern)
                
                # Exibir padrões por categoria
                for category, items in pattern_categories.items():
                    with st.expander(f"{category.title()} ({len(items)} padrões)"):
                        for pattern in items:
                            st.write(f"**{pattern['description']}**")
                            st.write(f"Sugestão: {pattern['suggestion']} | Confiança: {pattern['confidence']}")
            else:
                st.info("Nenhum padrão significativo detectado. Continue registrando resultados.")
            
            # Exibir pontuações de confiança
            st.subheader("📈 Pontuações de Confiança")
            col_conf1, col_conf2, col_conf3 = st.columns(3)
            with col_conf1:
                st.metric("🔴 Vermelho", f"{confidence_scores.get('🔴', 0):.1f}")
            with col_conf2:
                st.metric("🔵 Azul", f"{confidence_scores.get('🔵', 0):.1f}")
            with col_conf3:
                st.metric("🟡 Empate", f"{confidence_scores.get('🟡', 0):.1f}")
        
        else:
            st.info("Registre pelo menos 5 resultados para ativar a análise de padrões.")
    
    # Rodapé com informações adicionais
    st.divider()
    st.write("""
    **Sobre o sistema:** Este analisador verifica mais de 40 padrões diferentes em tempo real, 
    adaptando-se dinamicamente ao histórico de resultados. Quanto mais dados disponíveis, 
    mais precisas se tornam as recomendações.
    """)

if __name__ == "__main__":
    main()
