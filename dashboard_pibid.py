import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# Set page config
st.set_page_config(
    page_title="PIBID - Portal Interativo de Ações",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Corporate Blue Theme)
st.markdown("""
<style>
    .main-title {
        color: #1F497D;
        font-family: 'Calibri', sans-serif;
        font-weight: bold;
        font-size: 2.5rem;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #595959;
        font-family: 'Calibri', sans-serif;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background-color: #F2F4F8;
        border-radius: 8px;
        padding: 1.5rem;
        border-left: 5px solid #1F497D;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1F497D;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #595959;
        font-weight: bold;
        text-transform: uppercase;
    }
    .project-card {
        background-color: #FFFFFF;
        border: 1px solid #DCE6F1;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-top: 4px solid #1F497D;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.02);
    }
    .badge-escola {
        background-color: #DCE6F1;
        color: #1F497D;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .badge-supervisor {
        background-color: #E2EFDA;
        color: #375623;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .badge-periodo {
        background-color: #FFF2CC;
        color: #7F6000;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_html=True)

# -------------------------------------------------------------
# EMBEDDED BACKUP DATA (Used if no file or Google Sheet is linked)
# -------------------------------------------------------------
EMBEDDED_ESCOLAS = [
    {"ID_Escola": 1, "Nome_Escola": "EEM Almirante Lamego", "Sigla": "EEMAL", "Supervisor": "Adriano da Silva Oriano Junior", "Email_Supervisor": "a.juninhoo@hotmail.com", "Telefone_Supervisor": "(48) 99844-7589", "Subprojetos": "Educação Física, Letras, Pedagogia", "Bolsistas_Ativos": 8},
    {"ID_Escola": 2, "Nome_Escola": "EEB João Teixeira Nunes", "Sigla": "EEBJTN", "Supervisor": "Elisa Vieira da Silva Soares", "Email_Supervisor": "elisaartel@gmail.com", "Telefone_Supervisor": "(48) 99606-9837", "Subprojetos": "Pedagogia, Letras, Matemática", "Bolsistas_Ativos": 5},
    {"ID_Escola": 3, "Nome_Escola": "CEJA de Tubarão", "Sigla": "CEJA", "Supervisor": "Fabíola Medeiros Savi", "Email_Supervisor": "fabirevert@gmail.com", "Telefone_Supervisor": "(48) 99637-2913", "Subprojetos": "Leitura Literária (EJA)", "Bolsistas_Ativos": 9},
    {"ID_Escola": 4, "Nome_Escola": "EEB Henrique Fontes", "Sigla": "EEBHF", "Supervisor": "Lucas Zamparetti Oliveira", "Email_Supervisor": "lucaszampa@hotmail.com", "Telefone_Supervisor": "(48) 98405-7412", "Subprojetos": "NEPRE, Xadrez na Escola", "Bolsistas_Ativos": 7},
    {"ID_Escola": 5, "Nome_Escola": "EEB Senador Francisco Francisco Gallotti", "Sigla": "EEB Gallotti", "Supervisor": "Luciana Fernandes", "Email_Supervisor": "345429@profe.sed.sc.gov.br", "Telefone_Supervisor": "(48) 99901-8159", "Subprojetos": "Projeto de Leitura (Mundo dos Sonhos)", "Bolsistas_Ativos": 7}
]

EMBEDDED_ACOES = [
    {
        "ID_Acao": 1, "Escola": "EEM Almirante Lamego", "Supervisor": "Adriano da Silva Oriano Junior", "Ano": 2025, "Bimestre": "Abr-Mai",
        "Nome_da_Acao": "Projeto Recreio Interativo",
        "Descricao": "Planejamento de intervalo dinâmico com queimada, pula-corda, música e futebol.",
        "Resultados_Alcancados": "Alunos do Ensino Fundamental I participaram de jogos guiados pelos bolsistas (IDs).",
        "Impactos_na_Escola": "A assessora de direção relatou uma redução notável de ruídos e correrias nos dias de ação.",
        "Dificuldades_Enfrentadas": "O tempo do recreio é muito curto (15 minutos) e alguns alunos chegam no final."
    },
    {
        "ID_Acao": 2, "Escola": "EEM Almirante Lamego", "Supervisor": "Adriano da Silva Oriano Junior", "Ano": 2025, "Bimestre": "Ago-Set",
        "Nome_da_Acao": "Projeto Pontes do Saber",
        "Descricao": "Aulas semanais de reforço em Matemática e Português para alunos de 4º e 5º anos.",
        "Resultados_Alcancados": "IDs lecionaram noções lúdicas e problemas matemáticos práticos.",
        "Impactos_na_Escola": "Fortalecimento do vínculo dos alunos e adesão total com aulas dinâmicas.",
        "Dificuldades_Enfrentadas": "Falta de dados estatísticos de longo prazo, pois o projeto iniciou há pouco tempo."
    },
    {
        "ID_Acao": 3, "Escola": "EEB João Teixeira Nunes", "Supervisor": "Elisa Vieira da Silva Soares", "Ano": 2025, "Bimestre": "Fev-Mar",
        "Nome_da_Acao": "Revitalização da Biblioteca",
        "Descricao": "Catalogação e digitalização do acervo da biblioteca escolar por meio de um aplicativo online.",
        "Resultados_Alcancados": "Cada livro cadastrado com resumo, imagem da capa e páginas no aplicativo virtual.",
        "Impactos_na_Escola": "Facilitou de forma expressiva o acesso e o interesse pela leitura com acervo visível.",
        "Dificuldades_Enfrentadas": "Acervo de literatura muito escasso, com predomínio de livros didáticos."
    },
    {
        "ID_Acao": 4, "Escola": "EEB João Teixeira Nunes", "Supervisor": "Elisa Vieira da Silva Soares", "Ano": 2026, "Bimestre": "Abr-Mai",
        "Nome_da_Acao": "Sociedade Secreta Literária",
        "Descricao": "Encontros do Clube do Livro JTN com dinâmicas de 'leitura às cegas' e chá literário.",
        "Resultados_Alcancados": "Alunos escolheram livros baseados apenas em uma frase secreta. Assinaram termo de adesão.",
        "Impactos_na_Escola": "Estímulo ao protagonismo dos participantes e valorização da biblioteca escolar.",
        "Dificuldades_Enfrentadas": "Conciliação de horários de alunos e bolsistas que necessitou de readequação de rotina."
    },
    {
        "ID_Acao": 5, "Escola": "CEJA de Tubarão", "Supervisor": "Fabíola Medeiros Savi", "Ano": 2025, "Bimestre": "Abr-Mai",
        "Nome_da_Acao": "Despertar Literário (Freire)",
        "Descricao": "Encontros formativos presenciais e leituras teóricas com foco na pedagogia de Paulo Freire.",
        "Resultados_Alcancados": "Construção do diagnóstico escolar a partir da escuta atenta dos estudantes de nivelamento.",
        "Impactos_na_Escola": "Consolidação de uma proposta pedagógica crítica e transformadora para a EJA.",
        "Dificuldades_Enfrentadas": "Cansaço extremo dos estudantes no período noturno após longas jornadas de trabalho."
    },
    {
        "ID_Acao": 6, "Escola": "CEJA de Tubarão", "Supervisor": "Fabíola Medeiros Savi", "Ano": 2026, "Bimestre": "Fev-Mar",
        "Nome_da_Acao": "Oficina de Literatura e Cordel",
        "Descricao": "Oficina com o poema 'Brincadeiras' de Manoel de Barros para produção de sextilhas e xilogravura.",
        "Resultados_Alcancados": "Estudantes da turma de nivelamento criaram folhetos de cordel e técnicas de desenho.",
        "Impactos_na_Escola": "Impulso no desenvolvimento da escrita, leitura crítica e expressão artística de adultos.",
        "Dificuldades_Enfrentadas": "Elevado índice de faltas dos alunos da EJA devido a imprevistos de saúde e trabalho."
    },
    {
        "ID_Acao": 7, "Escola": "EEB Henrique Fontes", "Supervisor": "Lucas Zamparetti Oliveira", "Ano": 2025, "Bimestre": "Abr-Mai",
        "Nome_da_Acao": "Xadrez na Escola (AEE)",
        "Descricao": "Aulas de xadrez semanais no contraturno realizadas no espaço do AEE.",
        "Resultados_Alcancados": "Alunos de todas as séries aprenderam regras teóricas e práticas do jogo de tabuleiro.",
        "Impactos_na_Escola": "Aprimoramento notável do raciocínio lógico, foco e competências socioemocionais.",
        "Dificuldades_Enfrentadas": "Mudanças de horários no AEE tornaram inviável o projeto no segundo semestre de 2025."
    },
    {
        "ID_Acao": 8, "Escola": "EEB Henrique Fontes", "Supervisor": "Lucas Zamparetti Oliveira", "Ano": 2025, "Bimestre": "Ago-Set",
        "Nome_da_Acao": "Correio de Denúncias contra Bullying",
        "Descricao": "Palestra educativa sobre o bullying escolar acompanhada do 'Correio de Denúncias'.",
        "Resultados_Alcancados": "Construção física de uma caixa coletora para que os alunos deixassem relatos anônimos.",
        "Impactos_na_Escola": "Alunos puderam se expressar de forma segura sobre abusos sofridos e buscar apoio.",
        "Dificuldades_Enfrentadas": "Escassez de infraestrutura adequada na escola para reuniões e empenho de material."
    },
    {
        "ID_Acao": 9, "Escola": "EEB Henrique Fontes", "Supervisor": "Lucas Zamparetti Oliveira", "Ano": 2026, "Bimestre": "Abr-Mai",
        "Nome_da_Acao": "Maio Laranja: Combate ao Abuso",
        "Descricao": "Coreografia e ensaio da dança 'Baião da Proteção' voltada ao combate da exploração infantil.",
        "Resultados_Alcancados": "Minipalestras nas salas acompanhadas de questionários por celular via QR Code.",
        "Impactos_na_Escola": "Profunda sensibilização dos estudantes, professores e engajamento da comunidade escolar.",
        "Dificuldades_Enfrentadas": "Temática altamente sensível requer cuidado pedagógico e abordagem acolhedora."
    },
    {
        "ID_Acao": 10, "Escola": "EEB Senador Francisco Francisco Gallotti", "Supervisor": "Luciana Fernandes", "Ano": 2025, "Bimestre": "Jun-Jul",
        "Nome_da_Acao": "Mundo dos Sonhos: Coraline",
        "Descricao": "Uso do livro Coraline e produção de maquete e cenários com biscuit no laboratório maker.",
        "Resultados_Alcancados": "Alunos recriaram personagens e cenários em biscuit a partir de leituras em grupos.",
        "Impactos_na_Escola": "Integração perfeita entre literatura, arte manual e recursos makers de forma ativa.",
        "Dificuldades_Enfrentadas": "Quantidade muito limitada de exemplares físicos do livro Coraline na biblioteca."
    },
    {
        "ID_Acao": 11, "Escola": "EEB Senador Francisco Francisco Gallotti", "Supervisor": "Luciana Fernandes", "Ano": 2026, "Bimestre": "Abr-Mai",
        "Nome_da_Acao": "Sarau Marina Colasanti",
        "Descricao": "Sarau literário sobre contos 'A Moça Tecelã' e 'Entre a Espada e a Rosa' da escritora Marina Colasanti.",
        "Resultados_Alcancados": "Alunos produziram scrapbooks, realizaram encenações teatrais e gravaram podcasts opinativos.",
        "Impactos_na_Escola": "Estímulo exemplar à oralidade, argumentação, senso crítico e trabalho cooperativo.",
        "Dificuldades_Enfrentadas": "Grade curricular compacta dificultou o agendamento de todas as apresentações previstas."
    }
]

# -------------------------------------------------------------
# DATA LOADING FUNCTION
# -------------------------------------------------------------
@st.cache_data
def load_data(gsheets_url=None):
    df_escolas = pd.DataFrame(EMBEDDED_ESCOLAS)
    df_acoes = pd.DataFrame(EMBEDDED_ACOES)
    data_source_info = "Dados Internos de Exemplo (PIBID 2024-2026)"
    
    if gsheets_url:
        try:
            # Extract Spreadsheet ID
            match = re.search(r"/d/([a-zA-Z0-9-_]+)", gsheets_url)
            if match:
                sheet_id = match.group(1)
                export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
                
                # Try reading sheets
                df_escolas_temp = pd.read_excel(export_url, sheet_name="Escolas_e_Equipes")
                df_acoes_temp = pd.read_excel(export_url, sheet_name="Registro_de_Acoes")
                
                # Make sure the read worked and sheets are not empty
                if not df_escolas_temp.empty and not df_acoes_temp.empty:
                    df_escolas = df_escolas_temp
                    df_acoes = df_acoes_temp
                    data_source_info = "Conectado à Planilha do Google Sheets Online 🟢"
                    st.sidebar.success("Sincronização com o Google Sheets concluída!")
                else:
                    st.sidebar.warning("A planilha online foi lida, mas os dados parecem vazios. Usando dados internos.")
            else:
                st.sidebar.error("URL do Google Sheets inválida! Certifique-se de copiar o link completo.")
        except Exception as e:
            st.sidebar.error(f"Erro ao conectar com Google Sheets. Verifique o compartilhamento. Detalhes: {e}")
            
    return df_escolas, df_acoes, data_source_info

# -------------------------------------------------------------
# SIDEBAR - CONFIGURATIONS & FILTERS
# -------------------------------------------------------------
st.sidebar.image("https://contribution.usercontent.google.com/download?c=Cgpub3RlYm9va2xtEkASCWFydGlmYWN0cxozCiRhZmI3N2NhZC01MWFhLTQzZTMtOGYzNS04YTI3ZDBmZDAyMzQSCxIHEMvXv_XnDBgB&filename=pibid_dados_modelo.xlsx&opi=96797242", width=150) # Fallback indicator or generic text
st.sidebar.title("🔗 Conexão de Dados")

# Input for Google Sheet
gs_url = st.sidebar.text_input(
    "Insira o Link da Planilha Google (Compartilhada como Qualquer Pessoa com o Link pode ler):",
    placeholder="https://docs.google.com/spreadsheets/d/..."
)

# Load the data
df_escolas, df_acoes, data_source_info = load_data(gs_url if gs_url else None)

st.sidebar.markdown(f"**Fonte Atual:** `{data_source_info}`")

st.sidebar.divider()
st.sidebar.title("🎯 Filtros do Portal")

# Sidebar School Filter
escolas_list = ["Todas"] + sorted(df_escolas["Nome_Escola"].unique().tolist())
selected_escola = st.sidebar.selectbox("Filtrar por Escola:", escolas_list)

# Sidebar Supervisor Filter
supervisors_list = ["Todos"] + sorted(df_escolas["Supervisor"].unique().tolist())
selected_supervisor = st.sidebar.selectbox("Filtrar por Supervisor:", supervisors_list)

# Apply filters
df_filtered_escolas = df_escolas.copy()
df_filtered_acoes = df_acoes.copy()

if selected_escola != "Todas":
    # Filter Escolas
    df_filtered_escolas = df_filtered_escolas[df_filtered_escolas["Nome_Escola"] == selected_escola]
    # Filter Acoes (map full name or sigla)
    sigla = df_escolas[df_escolas["Nome_Escola"] == selected_escola]["Sigla"].values[0]
    df_filtered_acoes = df_filtered_acoes[(df_filtered_acoes["Escola"] == selected_escola) | (df_filtered_acoes["Escola"] == sigla)]

if selected_supervisor != "Todos":
    df_filtered_escolas = df_filtered_escolas[df_filtered_escolas["Supervisor"] == selected_supervisor]
    df_filtered_acoes = df_filtered_acoes[df_filtered_acoes["Supervisor"] == selected_supervisor]

# -------------------------------------------------------------
# HEADER SECTION
# -------------------------------------------------------------
col_logo, col_title = st.columns([1, 8])
with col_title:
    st.markdown('<p class="main-title">PORTAL INTERATIVO PIBID UNISUL</p>', unsafe_html=True)
    st.markdown('<p class="subtitle">Análise Consolidada de Relatórios Bimestrais de Atividades (EEM Almirante Lamego e Escolas Parceiras) • 2024 - 2026</p>', unsafe_html=True)

# -------------------------------------------------------------
# TABBED INTERFACE
# -------------------------------------------------------------
tab_overview, tab_actions, tab_nucleos, tab_search = st.tabs([
    "📊 Painel Geral (Visão Geral)", 
    "🔍 Explorar Atividades", 
    "🏫 Núcleos & Equipes", 
    "📚 Projetos Especiais & Busca"
])

# -------------------------------------------------------------
# TAB 1: PAINEL GERAL (OVERVIEW)
# -------------------------------------------------------------
with tab_overview:
    # KPI cards row
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Escolas Parceiras</div>
            <div class="kpi-value">{len(df_filtered_escolas)}</div>
        </div>
        """, unsafe_html=True)
    with col_kpi2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Supervisores Ativos</div>
            <div class="kpi-value">{len(df_filtered_escolas["Supervisor"].unique())}</div>
        </div>
        """, unsafe_html=True)
    with col_kpi3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Bolsistas (IDs) Ativos</div>
            <div class="kpi-value">{df_filtered_escolas["Bolsistas_Ativos"].sum()}</div>
        </div>
        """, unsafe_html=True)
    with col_kpi4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Ações Registradas</div>
            <div class="kpi-value">{len(df_filtered_acoes)}</div>
        </div>
        """, unsafe_html=True)

    st.markdown("### 📈 Estatísticas & Evolução Temporal")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Action counts per school
        actions_by_school = df_filtered_acoes["Escola"].value_counts().reset_index()
        actions_by_school.columns = ["Escola/Sigla", "Quantidade de Ações"]
        fig_school = px.bar(
            actions_by_school,
            x="Quantidade de Ações",
            y="Escola/Sigla",
            orientation="h",
            title="Distribuição de Ações Desenvolvidas por Escola",
            color="Quantidade de Ações",
            color_continuous_scale="Blues",
            labels={"Escola/Sigla": "Escola"}
        )
        fig_school.update_layout(showlegend=False, height=350, margin=dict(t=50, b=20, l=20, r=20))
        st.plotly_chart(fig_school, use_container_width=True)
        
    with col_chart2:
        # Time distribution (Ano e Bimestre)
        df_time = df_filtered_acoes.copy()
        df_time["Periodo"] = df_time["Ano"].astype(str) + " - " + df_time["Bimestre"]
        actions_by_time = df_time["Periodo"].value_counts().reset_index()
        actions_by_time.columns = ["Período", "Quantidade de Ações"]
        actions_by_time = actions_by_time.sort_values(by="Período")
        
        fig_time = px.line(
            actions_by_time,
            x="Período",
            y="Quantidade de Ações",
            title="Evolução Temporal das Atividades (Bimestral)",
            markers=True
        )
        fig_time.update_traces(line_color="#1F497D", line_width=3, marker=dict(size=8, color="#1F497D"))
        fig_time.update_layout(height=350, margin=dict(t=50, b=20, l=20, r=20))
        st.plotly_chart(fig_time, use_container_width=True)

# -------------------------------------------------------------
# TAB 2: EXPLORAR ATIVIDADES
# -------------------------------------------------------------
with tab_actions:
    st.markdown("### 📋 Registro Histórico Detalhado")
    st.write("Clique nas linhas ou use os expanders para ver o relatório completo de cada ação pedagógica desenvolvida na comunidade escolar.")
    
    for idx, row in df_filtered_acoes.iterrows():
        with st.expander(f"📌 {row['Nome_da_Acao']} — {row['Escola']} ({row['Ano']} | {row['Bimestre']})"):
            col_info1, col_info2 = st.columns([2, 1])
            with col_info1:
                st.markdown(f"**Escola:** `{row['Escola']}`")
                st.markdown(f"**Supervisor Responsável:** `{row['Supervisor']}`")
            with col_info2:
                st.markdown(f"**Ano Letivo:** `{row['Ano']}`")
                st.markdown(f"**Bimestre:** `{row['Bimestre']}`")
            
            st.divider()
            
            st.markdown(f"#### 📖 Descrição da Ação:")
            st.write(row["Descricao"])
            
            st.markdown(f"#### 🎯 Resultados Alcançados:")
            st.write(row["Resultados_Alcancados"])
            
            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                st.markdown(f"#### 🌱 Impactos na Escola:")
                st.write(row["Impactos_na_Escola"])
            with col_sub2:
                st.markdown(f"#### ⚠️ Dificuldades & Desafios Enfrentados:")
                st.write(row["Dificuldades_Enfrentadas"])

# -------------------------------------------------------------
# TAB 3: NÚCLEOS & EQUIPES
# -------------------------------------------------------------
with tab_nucleos:
    st.markdown("### 🏫 Núcleos de Atuação e Corpo Docente")
    
    for idx, row in df_filtered_escolas.iterrows():
        st.markdown(f"""
        <div class="project-card">
            <h3>🏢 {row['Nome_Escola']} ({row['Sigla']})</h3>
            <p>👨‍🏫 <b>Supervisor(a):</b> {row['Supervisor']}</p>
            <p>📧 <b>Email:</b> {row['Email_Supervisor']} | 📞 <b>Contato:</b> {row['Telefone_Supervisor']}</p>
            <p>📚 <b>Subprojetos Integrados:</b> {row['Subprojetos']}</p>
            <span class="badge-escola">Ativo</span>
            <span class="badge-supervisor">Bolsistas de Iniciação: {row['Bolsistas_Ativos']}</span>
        </div>
        """, unsafe_html=True)

# -------------------------------------------------------------
# TAB 4: PROJETOS ESPECIAIS & BUSCA
# -------------------------------------------------------------
with tab_search:
    st.markdown("### 📚 Explorador Temático Inteligente")
    st.write("Digite termos específicos ou palavras-chave (ex: *Bullying*, *Xadrez*, *Feminicídio*, *Leitura*, *Festa*) para encontrar em quais relatórios e núcleos as ações correspondentes foram documentadas.")
    
    search_query = st.text_input("🔍 Campo de Busca por Palavra-Chave:", "")
    
    if search_query:
        # Full text search across several columns
        query = search_query.lower()
        df_results = df_filtered_acoes[
            df_filtered_acoes["Nome_da_Acao"].str.lower().str.contains(query) |
            df_filtered_acoes["Descricao"].str.lower().str.contains(query) |
            df_filtered_acoes["Resultados_Alcancados"].str.lower().str.contains(query) |
            df_filtered_acoes["Impactos_na_Escola"].str.lower().str.contains(query) |
            df_filtered_acoes["Dificuldades_Enfrentadas"].str.lower().str.contains(query)
        ]
        
        st.markdown(f"**Resultados Encontrados ({len(df_results)}):**")
        
        if not df_results.empty:
            for idx, row in df_results.iterrows():
                st.markdown(f"""
                <div class="project-card">
                    <h4>🔥 {row['Nome_da_Acao']}</h4>
                    <p><span class="badge-escola">{row['Escola']}</span> 
                       <span class="badge-supervisor">{row['Supervisor']}</span>
                       <span class="badge-periodo">{row['Ano']} | {row['Bimestre']}</span></p>
                    <p><b>Descrição:</b> {row['Descricao']}</p>
                    <p><b>Resultados:</b> {row['Resultados_Alcancados']}</p>
                    <p><b>Impactos:</b> {row['Impactos_na_Escola']}</p>
                    <p><b>Dificuldades:</b> {row['Dificuldades_Enfrentadas']}</p>
                </div>
                """, unsafe_html=True)
        else:
            st.info("Nenhuma atividade encontrada com o termo buscado. Tente outra palavra-chave!")
    else:
        st.info("Digite uma palavra-chave acima para filtrar as ações de forma inteligente e dinâmica.")
