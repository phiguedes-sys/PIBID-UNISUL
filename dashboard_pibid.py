import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# Set page config
st.set_page_config(
    page_title="PIBID UNISUL - Portal de Vivências Qualitativas",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Corporate Blue and elegant qualitative theme)
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
    .qualitative-card {
        background-color: #F8F9FA;
        border-left: 5px solid #1F497D;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.05);
    }
    .card-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1F497D;
        margin-bottom: 0.5rem;
    }
    .badge-escola {
        background-color: #DCE6F1;
        color: #1F497D;
        padding: 0.25rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    .badge-supervisor {
        background-color: #E2EFDA;
        color: #375623;
        padding: 0.25rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    .badge-periodo {
        background-color: #FFF2CC;
        color: #7F6000;
        padding: 0.25rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .section-title {
        color: #1F497D;
        border-bottom: 2px solid #DCE6F1;
        padding-bottom: 0.3rem;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .text-content {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #333333;
        text-align: justify;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# IMAGE CONVERSION UTILITIES (API-Driven Thumbnail Renderer)
# -------------------------------------------------------------
def get_direct_img_url(url):
    url = url.strip()
    if not url:
        return "invalid", ""
    # Check if folder link
    if "drive.google.com/drive/folders/" in url or "drive.google.com/drive/u/0/folders/" in url:
        return "folder", url
    # Extract file ID from regular shared links
    match_id = re.search(r"id=([a-zA-Z0-9-_]+)", url)
    if not match_id:
        match_id = re.search(r"/file/d/([a-zA-Z0-9-_]+)", url)
    if match_id:
        file_id = match_id.group(1)
        # Usando a API de renderização de miniaturas (thumbnails) do Google Drive, que ignora telas de aviso e CORS, funcionando perfeitamente no Streamlit
        return "image", f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
    # Standard web link
    if url.startswith("http"):
        return "image", url
    return "invalid", url

def process_links(links_str):
    if not isinstance(links_str, str) or pd.isna(links_str):
        return []
    parts = []
    # Google Sheet lists are usually separated by commas or spaces
    if "," in links_str:
        parts = [p.strip() for p in links_str.split(",") if p.strip()]
    else:
        parts = [p.strip() for p in links_str.split() if p.strip()]
    
    processed = []
    for p in parts:
        ptype, conv = get_direct_img_url(p)
        if ptype != "invalid":
            processed.append({"type": ptype, "url": conv, "orig": p})
    return processed

def render_image_carousel(images_list, interval_ms=4000, height=350):
    """
    Renders an auto-playing pure HTML/CSS/JS image carousel inside Streamlit.
    images_list: List of dicts with {"url": "...", "orig": "..."}
    """
    import json
    urls = [img["url"] for img in images_list]
    js_images = json.dumps(urls)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: 'Calibri', 'Arial', sans-serif;
            background-color: transparent;
        }}
        .carousel-container {{
            width: 100%;
            height: {height}px;
            position: relative;
            overflow: hidden;
            border-radius: 8px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
            border: 1px solid #DCE6F1;
        }}
        .slide {{
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
            opacity: 0;
            transition: opacity 1.0s ease-in-out;
            z-index: 1;
        }}
        .slide.active {{
            opacity: 1;
            z-index: 2;
        }}
        .slide img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .caption-bar {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(31, 73, 125, 0.85); /* Corporate Blue with opacity */
            color: white;
            padding: 10px 15px;
            font-size: 0.9rem;
            text-align: center;
            z-index: 3;
            font-weight: bold;
            letter-spacing: 0.5px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }}
        .dots {{
            position: absolute;
            bottom: 45px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 8px;
            z-index: 4;
        }}
        .dot {{
            width: 10px;
            height: 10px;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 50%;
            cursor: pointer;
            transition: background 0.3s, transform 0.3s;
        }}
        .dot.active {{
            background: #E2EFDA; /* Soft green active indicator */
            transform: scale(1.2);
            box-shadow: 0 0 5px rgba(0,0,0,0.5);
        }}
        .dot:hover {{
            background: white;
        }}
    </style>
    </head>
    <body>
    <div class="carousel-container">
        <div id="slides-wrapper"></div>
        <div class="dots" id="dots-wrapper"></div>
        <div class="caption-bar" id="caption-el"></div>
    </div>

    <script>
        const urls = {js_images};
        const interval = {interval_ms};
        
        const slidesWrapper = document.getElementById('slides-wrapper');
        const dotsWrapper = document.getElementById('dots-wrapper');
        const captionEl = document.getElementById('caption-el');
        
        // Generate Slides and Dots
        urls.forEach((url, index) => {{
            const slide = document.createElement('div');
            slide.className = 'slide' + (index === 0 ? ' active' : '');
            slide.innerHTML = `<img src="${{url}}" alt="Slide ${{index + 1}}">`;
            slidesWrapper.appendChild(slide);
            
            const dot = document.createElement('div');
            dot.className = 'dot' + (index === 0 ? ' active' : '');
            dot.addEventListener('click', () => showSlide(index));
            dotsWrapper.appendChild(dot);
        }});
        
        captionEl.innerText = `Foto ${{1}} de ${{urls.length}}`;
        
        let currentIndex = 0;
        let slideInterval = setInterval(nextSlide, interval);
        
        function showSlide(index) {{
            clearInterval(slideInterval);
            const slides = document.querySelectorAll('.slide');
            const dots = document.querySelectorAll('.dot');
            
            slides[currentIndex].classList.remove('active');
            dots[currentIndex].classList.remove('active');
            
            currentIndex = index;
            
            slides[currentIndex].classList.add('active');
            dots[currentIndex].classList.add('active');
            captionEl.innerText = `Foto ${{currentIndex + 1}} de ${{urls.length}}`;
            
            slideInterval = setInterval(nextSlide, interval);
        }}
        
        function nextSlide() {{
            const nextIndex = (currentIndex + 1) % urls.length;
            showSlide(nextIndex);
        }}
    </script>
    </body>
    </html>
    """
    import streamlit.components.v1 as components
    components.html(html_code, height=height + 10)


# -------------------------------------------------------------
# EMBEDDED BACKUP DATA (PIBID qualitative narratives - Academically Dense & Complete)
# -------------------------------------------------------------
EMBEDDED_NARRATIVAS = [
    {
        "Escola": "EEM Almirante Lamego", 
        "Supervisor": "Adriano da Silva Oriano Junior", 
        "Projeto_Acao": "Recreio Interativo & Gamificação", 
        "Periodo_Bimestre": "Abril/Maio 2025 (Reativado Fev/Mar 2026)",
        "Metodologia": "Intervalos dinamizados no Ensino Fundamental I com planejamento sistemático de jogos motores cooperativos (pula-corda, queimada, circuitos de agilidade, futebol e expressão corporal). Em 2026, o projeto foi reformulado pela equipe acadêmica com a incorporação de técnicas de gamificação. Foram criados critérios objetivos de participação ativa e socialização, culminando na produção física e entrega de certificados personalizados ('Você é Brilhante', 'Super Participante') e brindes simbólicos feitos de EVA para estimular o engajamento continuado.",
        "Impacto_Escola": "A assessoria de direção da escola registrou formalmente uma redução significativa nos ruídos, correria excessiva e desentendimentos no pátio e nos corredores durante o recreio escolar nos dias de ação. O espaço do recreio foi ressignificado, deixando de ser um tempo ocioso e desestruturado para tornar-se um ambiente de inclusão escolar, desenvolvimento motor consciente e convivência lúdica democrática entre diferentes faixas etárias.",
        "Voz_Bolsista": "Os bolsistas (IDs) de Educação Física e Pedagogia relataram uma excelente articulação entre a fundamentação teórica de jogos cooperativos e a transposição prática na regência compartilhada. Essa inserção progressiva no ambiente escolar permitiu aos futuros professores superar o nervosismo inicial de reger grupos heterogêneos, consolidando suas identidades docentes por meio do planejamento sistemático e da mediação pedagógica.",
        "Dificuldades": "A extrema brevidade do recreio (apenas 15 minutos de duração) exigiu agilidade extrema na organização prévia dos materiais e na divisão rápida das turmas. A falta inicial de material diversificado foi suprida pela confecção de recursos alternativos duráveis pelas pibidianas.",
        "Foto": "https://drive.google.com/open?id=1RM3AUkqIsJKyG4KuyxG8-ExAX8KBln1R"
    },
    {
        "Escola": "EEM Almirante Lamego", 
        "Supervisor": "Adriano da Silva Oriano Junior", 
        "Projeto_Acao": "Pontes do Saber: Nivelamento Pedagógico", 
        "Periodo_Bimestre": "Agosto a Novembro 2025",
        "Metodologia": "Programa de reforço escolar e nivelamento estruturado para as turmas de 4º e 5º anos do Ensino Fundamental I, focado em mitigar defasagens críticas nas áreas de Alfabetização, Compreensão Leitora e Raciocínio Lógico-Matemático. O projeto envolveu reuniões de alinhamento diagnóstico com as regentes e reuniões periódicas de planejamento metodológico com a coordenação. As aulas presenciais de 1h30 semanais utilizavam recursos lúdicos, dinâmicas de raciocínio concreto e escrita individualizada para aproximar os estudantes de forma prazerosa das disciplinas escolares fundamentais.",
        "Impacto_Escola": "Observou-se um fortalecimento do vínculo afetivo dos alunos com a escola e uma sensível evolução em suas notas nas avaliações regulares conduzidas pelas professoras das turmas de origem. Houve adesão integral das famílias das crianças participantes, que frequentavam ativamente as oficinas pedagógicas no contraturno escolar, transformando o espaço do reforço em um polo acolhedor de autoconfiança acadêmica.",
        "Voz_Bolsista": "Os bolsistas (IDs) de Letras e Pedagogia vivenciaram de forma profunda as complexidades da diferenciação pedagógica e do planejamento de aulas de apoio no contraturno. Relatam que o projeto ensinou-os a importância do diagnóstico contínuo de defasagens e de exercer a paciência metodológica para adaptar o cronograma de ensino aos ritmos heterogêneos de cada criança.",
        "Dificuldades": "A inflexibilidade do calendário escolar do contraturno exigiu dos bolsistas uma rígida readequação em suas rotinas de estudos na universidade. O desafio de engajar alunos que apresentavam histórico de frustração escolar foi superado pela criação de jogos matemáticos concretos de tabuleiro e o uso de lanches afetivos.",
        "Foto": "https://drive.google.com/open?id=1iRQ9L99AKJmSSwfCutoK0oxPgBmzxv6h"
    },
    {
        "Escola": "EEB João Teixeira Nunes", 
        "Supervisor": "Elisa Vieira da Silva Soares", 
        "Projeto_Acao": "Sociedade Secreta Literária / Clube do Livro JTN", 
        "Periodo_Bimestre": "Fevereiro a Junho de 2026",
        "Metodologia": "Projeto de incentivo à leitura literária voltado a estudantes do Ensino Médio e anos finais do Fundamental. Iniciou-se com a confecção e distribuição de convites enigmáticos nas salas de aula ('Se desejas ingressar nesta respeitável sociedade...'). Para consolidar a pertença, os estudantes preencheram fichas de inscrição e receberam carteirinhas oficiais de membros personalizadas com fotos. As reuniões semanais eram estruturadas como encontros de 'Leitura às Cegas' acompanhados de chá e biscoitos, nos quais os alunos debatiam as obras sem rótulos de autor, trocavam cartas anônimas destinadas aos personagens e montavam lapbooks interativos sobre enredos.",
        "Impacto_Escola": "Resgate e revitalização do papel social da biblioteca escolar, que se tornou um dinâmico polo de convivência cultural ativa, leitura autónoma e debate crítico. O projeto promoveu o protagonismo juvenil, o desenvolvimento da interpretação crítica e do letramento literário estético dos estudantes, aproximando-os voluntariamente e com entusiasmo do espaço da biblioteca.",
        "Voz_Bolsista": "As bolsistas de Letras e Pedagogia planejaram as oficinas com foco na estética da recepção e no incentivo afetivo à leitura. Relatam que mediar rodas de conversas em torno do chá literário ensinou-lhes como o lúdico e a hospitalidade reduzem a resistência dos estudantes à literatura clássica, aproximando os futuros docentes de uma prática acolhedora.",
        "Dificuldades": "Conciliar os horários de presença das bolsistas na escola com o período escolar dos alunos participantes demandou flexibilização e reagendamentos constantes, contornados pela criação de encontros em dias alternados e plantões de leitura na biblioteca.",
        "Foto": "https://drive.google.com/open?id=19dYUF5kAD0950iinqr5rulDvwIIHfRyc"
    },
    {
        "Escola": "EEB João Teixeira Nunes", 
        "Supervisor": "Elisa Vieira da Silva Soares", 
        "Projeto_Acao": "Revitalização e Reestruturação da Biblioteca", 
        "Periodo_Bimestre": "Fevereiro a Maio de 2025",
        "Metodologia": "Desenvolvimento de um plano de ação sistemático para modernizar o acervo ocioso da biblioteca escolar. Os bolsistas atuaram na catalogação física, reorganização por gêneros literários de interesse e faixa etária, identificação magnética e digitalização do acervo utilizando um aplicativo online que exibe capa do livro, número de páginas e resumos detalhados para consulta facilitada. Como fomento estético-visual, desenharam a mão livre um grande mural de incentivo utilizando páginas de livros que seriam descartados, e aplicaram questionários virtuais aos professores sobre livros favoritos para criar murais externos de indicação literária.",
        "Impacto_Escola": "Transformou a biblioteca de um espaço passivo de depósito em um ambiente convidativo, acolhedor e dinâmico na rotina da escola. Facilitou imensamente o fluxo de busca de livros pelos estudantes, aumentando drasticamente o índice bimestral de empréstimos e o interesse voluntário dos discentes por leituras extracurriculares de lazer.",
        "Voz_Bolsista": "O envolvimento dos pibidianos revelou a importância da gestão do espaço físico educativo como ferramenta ativa de incentivo ao conhecimento. Compreenderam as rotinas administrativas, a relevância do planejamento colaborativo com o corpo docente e a estruturação de ambientes dinâmicos que dialoguem afetivamente com os alunos.",
        "Dificuldades": "A grave escassez inicial de obras contemporâneas de literatura infantojuvenil de interesse e o predomínio de livros didáticos antigos. Os bolsistas contornaram esse desafio organizando campanhas de doações na universidade e contatos comunitários para captação de recursos.",
        "Foto": "https://drive.google.com/open?id=1rBVObCfSfHsdN3FnacbgvX1CDgQ6AXu3"
    },
    {
        "Escola": "EEB João Teixeira Nunes", 
        "Supervisor": "Elisa Vieira da Silva Soares", 
        "Projeto_Acao": "A Colcha de Retalhos: Poesia e Identidade", 
        "Periodo_Bimestre": "Outubro a Novembro de 2025",
        "Metodologia": "Oficina de escrita criativa e expressão artística com turmas de 5º ano, baseada na leitura do livro de poemas 'Sobre Importâncias' de Manoel de Barros e a obra infantojuvenil 'Feita de Pano' de Valéria Belém. Os estudantes debateram sobre as coisas que possuem real valor e afeto em suas vidas e redigiram poemas individuais sobre 'suas importâncias'. Das produções, os bolsistas extraíram versos marcantes e criaram um grande poema coletivo. Na aula de artes, cada aluno pintou com tinta acrílica e marcadores permanentes o seu verso autoral sobre um retalho de tecido de algodão cru. Os retalhos foram costurados em uma grande colcha física exposta no corredor.",
        "Impacto_Escola": "Impacto pedagógico e socioemocional profundo, promovendo a autoria, a sensibilidade artística e a reflexão sobre identidade em crianças de anos iniciais. A colcha de retalhos exposta no corredor principal se tornou símbolo físico do trabalho cooperativo e da valorização estética della escrita, elevando a autoestima e o sentimento de reconhecimento coletivo.",
        "Voz_Bolsista": "Os bolsistas puderam experimentar metodologias de letramento literário que uniram escrita, pintura e expressão artesanal. Relatam que ver o entusiasmo dos alunos na pintura de seus próprios poemas evidenciou o poder de desmistificar o ensino de poesia, tornando-o acessível e interligado a memórias afetivas infantis.",
        "Dificuldades": "A heterogeneidade de níveis de escrita e a resistência inicial de some estudantes em redigir poemas autorais. O obstáculo foi superado pelo acompanhamento individualizado e mediação atenta de cada dupla de pibidianos, estimulando a livre expressão oral antes da escrita.",
        "Foto": "https://drive.google.com/open?id=1SgPaUc3WT0jL3AElsuzXzpzffti_saHz"
    },
    {
        "Escola": "CEJA de Tubarão", 
        "Supervisor": "Fabíola Medeiros Savi", 
        "Projeto_Acao": "Despertar Literário: Alfabetização e Cordel", 
        "Periodo_Bimestre": "Fevereiro a Maio de 2026 (Início em Abril 2025)",
        "Metodologia": "Projeto de letramento literário crítico e expressão poética para estudantes de nivelamento (séries iniciais) do CEJA de Tubarão, fundamentado nos aportes teóricos da pedagogia freireana ('Cartas à Guiné-Bissau' e 'O Ato de Ler'). As ações envolveram momentos de escuta e contação de histórias na biblioteca escolar, seguidas de oficinas sequenciais de folhetos de cordel inspiradas no poema 'Brincadeiras' de Manoel de Barros. Os alunos da EJA (incluindo adultos e idosos) debateram sobre suas memórias de infância e produziram sextilhas de cordéis autorais e ilustrações baseadas na técnica da xilogravura (usando bandejas de isopor e tinta preta).",
        "Impacto_Escola": "Fomento exemplar do sentimento de autoconfiança, autoria e emancipation sociocultural de estudantes adultos com histórico de exclusão ou pouca escolaridade escolar. Ao verem suas trajetórias de vida e memórias transformadas em cordéis autorais expostos, os alunos integraram-se como sujeitos críticos no processo de alfabetização de forma prazerosa.",
        "Voz_Bolsista": "Os bolsistas de Pedagogia realizaram uma articulação dialógica profunda, compreendendo que na EJA a alfabetização deve emergir das carências reais e do repertório de vivências do próprio aluno. Relatam que o projeto desenvolveu a escuta sensível, paciência pedagógica e habilidade para ajustar propostas às heterogeneidades dos ritmos cognitivos.",
        "Dificuldades": "O cansaço físico extremo dos estudantes noturnos da EJA após longas jornadas de trabalho e o elevado índice de faltas por imprevistos laborais ou familiares. Os bolsistas contornaram os obstáculos por meio de dinâmicas envolvendo lanches coletivos, café literário com momentos reflexivos e acolhimento sensível das ausências.",
        "Foto": "https://drive.google.com/open?id=13zXCE4b419p9Ol89qUXOBMvbVlBs4t4k"
    },
    {
        "Escola": "EEB Henrique Fontes", 
        "Supervisor": "Lucas Zamparetti Oliveira", 
        "Projeto_Acao": "Xadrez na Escola: Cognição e Inclusão no AEE", 
        "Periodo_Bimestre": "Abril de 2025 a Julho de 2026",
        "Metodologia": "Implementação de oficinas pedagógicas de xadrez em contraturno escolar, realizadas nas manhãs de sexta-feira das 7h30 às 11h30. O projeto foi desenhado em conjunto com os profissionais do Atendimento Educacional Especializado (AEE) e ocorreu de forma contínua na sala do AEE, sendo aberto a estudantes de todas as séries dos períodos vespertino e noturno. A metodologia abordou desde noções e regras básicas de movimentação de peças de xadrez até noções avançadas de táticas e jogos em equipes, com ênfase na gamificação e no uso do lúdico.",
        "Impacto_Escola": "Impacto notável no desenvolvimento do raciocínio lógico-matemático, da concentração, do foco e da capacidade de tomada de decisão estratégica dos alunos regidos. No âmbito social e inclusivo, o projeto consolidou o espaço do AEE como polo acolhedor, integrando de forma harmônica e igualitária alunos com deficiências e transtornos em atividades socioeducativas cooperativas, estimulando a resiliência pedagógica.",
        "Voz_Bolsista": "Os bolsistas de Educação Física e Ciências Biológicas relatam que o ensino do xadrez exigiu planejamento estratégico e didática apurada para explicar regras abstratas de forma simples e inclusiva. Vivenciaram na prática os princípios de uma educação humanizada e adaptada à diversidade de ritmos individuais de aprendizagem na sala de aula do AEE.",
        "Dificuldades": "As alterações na matriz de horários da escola e a incompatibilidade inicial de agendas dos bolsistas com o AEE no final de 2025, o que demandou reuniões de alinhamento com a equipe gestora para a reformulação teórica e reativação plena e bem-sucedida do projeto em 2026.",
        "Foto": "https://drive.google.com/open?id=1ZjFwf2SeADmQ8QW9nGilNe6ylecoQmke"
    },
    {
        "Escola": "EEB Senador Francisco Benjamin Gallotti", 
        "Supervisor": "Luciana Fernandes", 
        "Projeto_Acao": "Mundo dos Sonhos: Coraline Maker", 
        "Periodo_Bimestre": "Junho a Setembro de 2025",
        "Metodologia": "Projeto de leitura interpretativa ativa com turmas do Ensino Médio, utilizando como fomento literário o livro de fantasia 'Coraline', de Neil Gaiman. Os estudantes realizaram leituras orientadas em pequenos grupos, debateram e estabeleceram relações reflexivas entre o enredo da obra e suas próprias transformações pessoais e relações sociofamiliares. Como transposição estética interdisciplinar, os alunos foram levados ao laboratório maker de artes para confeccionar maquetes tridimensionais detalhadas dos cenários e modelar os personagens do livro utilizando biscuit e argila.",
        "Impacto_Escola": "As maquetes e as produções textuais foram reunidas em um 'Varal da Leitura' e expostas no corredor principal da escola. A biblioteca e as salas de leitura ganharam grande dinamismo e os alunos expressaram enorme protagonismo juvenil, aproximando-se voluntariamente do universo literário através da integração inovadora com recursos de arte maker.",
        "Voz_Bolsista": "As bolsistas de Iniciação (IDs) consolidaram suas identidades docentes ao mediar reflexões complexas no Ensino Médio. Relatam que o projeto ensinou-as a importância de transpor conteúdos textuais para formas concretas de produção artística manual, despertando a sensibilidade estética e a criatividade como aliadas do letramento.",
        "Dificuldades": "A falta crítica de exemplares físicos do livro 'Coraline' na biblioteca para todos os alunos participantes. O obstáculo foi superado pelas pibidianas ao baixar e disponibilizar arquivos digitais em PDF licenciados nos tablets da escola, organizando círculos de leitura compartilhados em duplas.",
        "Foto": "https://drive.google.com/open?id=1oJxomWUxnFyoOhUe0dgmQXxn4517bXTu"
    }
]

EMBEDDED_FORM_VISITAS = [
    {
        "Carimbo": "24/02/2025 22:16:50",
        "Email": "orianoadriano@gmail.com",
        "Supervisor": "Adriano da Silva Oriano Junior",
        "Data_Visita": "24/02/2025",
        "Ficha_Avaliacao": "https://drive.google.com/open?id=10Eg8aXaaXIvxqH1dS9LisgiSS4B3CL2b",
        "Fotos": "https://drive.google.com/open?id=1RM3AUkqIsJKyG4KuyxG8-ExAX8KBln1R, https://drive.google.com/open?id=11bNrw28LSgYdz4T5-KLkDIPez2Ex9qv_",
        "Ficha_Frequencia": "https://drive.google.com/open?id=1G-vBPdS3Q2JIyDcZt3yc59UD8maECLvm"
    },
    {
        "Carimbo": "22/04/2025 22:18:08",
        "Email": "orianoadriano@gmail.com",
        "Supervisor": "Adriano da Silva Oriano Junior",
        "Data_Visita": "17/04/2025",
        "Ficha_Avaliacao": "https://drive.google.com/open?id=1ZKZ-HSp_gYkL0SMcrIALEzaK3_Ptu5_U",
        "Fotos": "https://drive.google.com/open?id=1iRQ9L99AKJmSSwfCutoK0oxPgBmzxv6h, https://drive.google.com/open?id=1FOFdEcZYZiGPGZaxJE-J5GSsspoE61h5",
        "Ficha_Frequencia": "https://drive.google.com/open?id=1e2MbDF3-wKb-aT15klV2GnTapZgbIik7"
    },
    {
        "Carimbo": "26/05/2025 08:30:48",
        "Email": "elisavieiradasilvasoares@gmail.com",
        "Supervisor": "Elisa Vieira da Silva Soares",
        "Data_Visita": "23/04/2025",
        "Ficha_Avaliacao": "https://drive.google.com/open?id=1s1LQnJ_OVkiHa_jl8ShQa14VZcooA5Oc",
        "Fotos": "https://drive.google.com/open?id=19dYUF5kAD0950iinqr5rulDvwIIHfRyc, https://drive.google.com/open?id=1C72WpqlmGpYiDslS9wMCKqLtNORM2njb",
        "Ficha_Frequencia": "https://drive.google.com/open?id=1NYXLywuxLzmzt-ffdE939IVi8CgokEbe"
    },
    {
        "Carimbo": "04/08/2025 15:42:00",
        "Email": "fabirevert@gmail.com",
        "Supervisor": "Fabíola Medeiros Savi",
        "Data_Visita": "25/06/2025",
        "Ficha_Avaliacao": "https://drive.google.com/open?id=1eNrNPvVdnzSTeg-GrNsp7wib9OMks6tH",
        "Fotos": "https://drive.google.com/open?id=13zXCE4b419p9Ol89qUXOBMvbVlBs4t4k, https://drive.google.com/open?id=1aq0WuGWaZiGsBqLD5lwl-1Ps1MXDJx8y",
        "Ficha_Frequencia": "https://drive.google.com/open?id=1j0o3BluBrxr-8rtLQCHIJUxVTqhS_Gyk"
    },
    {
        "Carimbo": "22/04/2026 16:11:04",
        "Email": "lucaszampa@hotmail.com",
        "Supervisor": "Lucas Zamparetti Oliveira",
        "Data_Visita": "19/02/2026",
        "Ficha_Avaliacao": "https://drive.google.com/open?id=1X-pgdG3x3PXl964VLku5SPjpdMKjuzMk",
        "Fotos": "https://drive.google.com/open?id=1ZjFwf2SeADmQ8QW9nGilNe6ylecoQmke, https://drive.google.com/open?id=1xsPNKDgAGxGR7AAAlcmlZyX8iYqW3VWB",
        "Ficha_Frequencia": "https://drive.google.com/open?id=1epLQAQRa_dv1S1U75vSM1DuxZmx55FsT"
    }
]

# -------------------------------------------------------------
# DATA LOADING FUNCTION (ROBUST GOOGLE SHEETS SYNC)
# -------------------------------------------------------------

# -------------------------------------------------------------
# SAFE COLUMN MAPPING UTILITIES
# -------------------------------------------------------------
def map_columns_safely(df, rules):
    mapped_cols = {}
    used_original_cols = set()
    mapped_standards = set()
    
    # First pass: try exact matches (case-insensitive)
    for std_name, keywords in rules:
        for col in df.columns:
            if col in used_original_cols:
                continue
            if str(col).strip().lower() == std_name.lower():
                mapped_cols[col] = std_name
                used_original_cols.add(col)
                mapped_standards.add(std_name)
                break
                
    # Second pass: try keyword matches
    for std_name, keywords in rules:
        if std_name in mapped_standards:
            continue
        for col in df.columns:
            if col in used_original_cols:
                continue
            col_str = str(col).lower()
            if any(kw in col_str for kw in keywords):
                mapped_cols[col] = std_name
                used_original_cols.add(col)
                mapped_standards.add(std_name)
                break
                
    return df.rename(columns=mapped_cols)


# -------------------------------------------------------------
# DATA LOADING FUNCTION (ROBUST GOOGLE SHEETS SYNC)
# -------------------------------------------------------------
@st.cache_data
def load_data(gsheets_url=None):
    df_narrativas = pd.DataFrame(EMBEDDED_NARRATIVAS)
    df_visitas = pd.DataFrame(EMBEDDED_FORM_VISITAS)
    data_source_info = "Dados Internos Qualitativos (PIBID 2024-2026)"
    
    if gsheets_url:
        try:
            match = re.search(r"/d/([a-zA-Z0-9-_]+)", gsheets_url)
            if match:
                sheet_id = match.group(1)
                export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
                
                # Dynamic sheet loading
                xls = pd.ExcelFile(export_url)
                sheets = xls.sheet_names
                
                # Load Narrativas sheet
                narr_sheet = None
                for s in sheets:
                    if "Narrativas" in s or "Qualitativas" in s:
                        narr_sheet = s
                        break
                if narr_sheet:
                    df_narr_temp = pd.read_excel(export_url, sheet_name=narr_sheet)
                    if not df_narr_temp.empty:
                        rules_narrativas = [
                            ("Escola", ["escola", "núcleo", "nucleo"]),
                            ("Supervisor", ["supervisor", "nome completo do supervisor"]),
                            ("Projeto_Acao", ["projeto", "ação", "acao", "atividade"]),
                            ("Periodo_Bimestre", ["período", "periodo", "bimestre", "mês", "mes"]),
                            ("Metodologia", ["metodologia", "desenvolvido", "como foi desenvolvido", "descrição", "descricao"]),
                            ("Impacto_Escola", ["impacto", "social", "pedagógico", "pedagogico", "escola"]),
                            ("Voz_Bolsista", ["voz", "bolsista", "reflexiva", "depoimento", "id"]),
                            ("Dificuldades", ["dificuldade", "superação", "superacao", "desafios", "problema"]),
                            ("Foto", ["foto", "link", "imagem", "registro"])
                        ]
                        df_narrativas = map_columns_safely(df_narr_temp, rules_narrativas)
                
                # Load Visitas sheet (Form responses)
                vis_sheet = None
                for s in sheets:
                    if "Respostas" in s or "Visita" in s or "Formulario" in s:
                        vis_sheet = s
                        break
                if vis_sheet:
                    df_vis_temp = pd.read_excel(export_url, sheet_name=vis_sheet)
                    if not df_vis_temp.empty:
                        rules_visitas = [
                            ("Carimbo", ["carimbo", "timestamp", "data/hora"]),
                            ("Email", ["email", "e-mail", "endereço", "endereco"]),
                            ("Supervisor", ["supervisor", "nome completo"]),
                            ("Data_Visita", ["data da visita", "data oficial"]),
                            ("Fotos", ["fotos", "imagens", "anexe as fotos"]),
                            ("Ficha_Avaliacao", ["avaliação", "avaliacao", "ficha de avaliação"]),
                            ("Ficha_Frequencia", ["frequencia", "frequência", "ficha de frequencia"])
                        ]
                        df_visitas = map_columns_safely(df_vis_temp, rules_visitas)
                
                data_source_info = "Conectado à Planilha do Google Sheets Online 🟢"
                st.sidebar.success("Sincronização qualitativa com o Google Sheets concluída!")
        except Exception as e:
            st.sidebar.error(f"Erro de conexão: certifique-se de que a planilha está compartilhada como 'Leitor público'. Detalhes: {e}")
            
    # Ensure all expected columns exist with default values to prevent key errors
    for col in ["Escola", "Supervisor", "Projeto_Acao", "Periodo_Bimestre", "Metodologia", "Impacto_Escola", "Voz_Bolsista", "Dificuldades", "Foto"]:
        if col not in df_narrativas.columns:
            df_narrativas[col] = ""
            
    for col in ["Carimbo", "Email", "Supervisor", "Data_Visita", "Fotos"]:
        if col not in df_visitas.columns:
            df_visitas[col] = ""
            
    return df_narrativas, df_visitas, data_source_info


# -------------------------------------------------------------
# SIDEBAR - BRANDING & CONNECTIONS
# -------------------------------------------------------------
# Branding Logos (UNISUL and Anima Group styling - Elegant Corporate Badge)
st.sidebar.markdown("""
<div style='background-color:#1F497D; color:white; padding:15px; border-radius:8px; text-align:center; font-family:"Calibri",sans-serif; margin-bottom:15px;'>
    <h3 style='margin:0; font-size:1.3rem; font-weight:bold; letter-spacing:1px;'>PIBID UNISUL</h3>
    <div style='border-top:1px solid #DCE6F1; margin:8px 0;'></div>
    <p style='margin:0; font-size:0.8rem; color:#DCE6F1; font-weight:bold; text-transform:uppercase;'>GRUPO ÂNIMA EDUCAÇÃO</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("🔗 Conexão Google Sheets")
gs_url = st.sidebar.text_input(
    "Insira o Link Compartilhado da sua Planilha do Google Sheets:",
    placeholder="https://docs.google.com/spreadsheets/d/..."
)

# Load datasets
df_narrativas, df_visitas, data_source_info = load_data(gs_url if gs_url else None)

st.sidebar.markdown(f"**Fonte de Dados Ativa:**\n`{data_source_info}`")

st.sidebar.divider()
st.sidebar.title("🎯 Filtros Narrativos")

# School and supervisor filters
escolas_list = ["Todas"] + sorted(df_narrativas["Escola"].unique().tolist())
selected_escola = st.sidebar.selectbox("Filtrar por Núcleo / Escola:", escolas_list)

supervisors_list = ["Todos"] + sorted(df_narrativas["Supervisor"].unique().tolist())
selected_supervisor = st.sidebar.selectbox("Filtrar por Supervisor:", supervisors_list)

# Apply filters
df_filtered_narr = df_narrativas.copy()
if selected_escola != "Todas":
    df_filtered_narr = df_filtered_narr[df_filtered_narr["Escola"] == selected_escola]
if selected_supervisor != "Todos":
    df_filtered_narr = df_filtered_narr[df_filtered_narr["Supervisor"] == selected_supervisor]

# -------------------------------------------------------------
# MAIN HEADER
# -------------------------------------------------------------
st.markdown('<p class="main-title">PORTAL DE VIVÊNCIAS QUALITATIVAS PIBID UNISUL</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Portfólio Reflexivo de Práticas Docentes, Projetos de Intervenção e Registros Fotográficos • 2024 - 2026</p>', unsafe_allow_html=True)

# -------------------------------------------------------------
# TABS INTERFACE
# -------------------------------------------------------------
tab_narr, tab_photos, tab_reflections, tab_search = st.tabs([
    "📖 Portfólio de Narrativas & Vivências",
    "📸 Mural de Visitas Mensais (Formulário)",
    "🧠 Dimensões Qualitativas (Teoria e Prática)",
    "🔍 Busca de Práticas"
])

# -------------------------------------------------------------
# TAB 1: PORTFOLIO OF NARRATIVES
# -------------------------------------------------------------
with tab_narr:
    st.markdown("### 📋 Narrativas Pedagógicas por Escola")
    st.write("Abaixo estão detalhados os relatos das experiências reais que moldaram o PIBID. Cada projeto representa o engajamento dos bolsistas na construção de um ambiente escolar mais reflexivo e acolhedor.")
    
    if df_filtered_narr.empty:
        st.info("Nenhuma narrativa encontrada para os filtros selecionados.")
    else:
        for idx, row in df_filtered_narr.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="qualitative-card">
                    <div class="card-header">📌 {row['Projeto_Acao']}</div>
                    <span class="badge-escola">🏢 {row['Escola']}</span>
                    <span class="badge-supervisor">👨‍🏫 Supervisor: {row['Supervisor']}</span>
                    <span class="badge-periodo">📅 {row['Periodo_Bimestre']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Split page into layout columns
                col_text, col_visual = st.columns([3, 2])
                
                with col_text:
                    st.markdown("<p class='section-title'>📖 Como foi desenvolvido (Metodologia)</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='text-content'>{row['Metodologia']}</p>", unsafe_allow_html=True)
                    
                    st.markdown("<p class='section-title'>🌱 Impacto Social e Pedagógico na Escola</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='text-content'>{row['Impacto_Escola']}</p>", unsafe_allow_html=True)
                    
                    st.markdown("<p class='section-title'>👩‍🏫 A Voz do Bolsista (Prática Reflexiva)</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='text-content'><i>\\\"{row['Voz_Bolsista']}\\\"</i></p>", unsafe_allow_html=True)
                    
                    st.markdown("<p class='section-title'>⚠️ Desafios & Como Foram Superados</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='text-content'>{row['Dificuldades']}</p>", unsafe_allow_html=True)
                
                with col_visual:
                    st.markdown("<p class='section-title'>📸 Registro Visual do Núcleo</p>", unsafe_allow_html=True)
                    
                    # 1. Busca dinâmica de fotos reais nas respostas do formulário (df_visitas) baseando-se no Supervisor
                    sup_narrative = row.get("Supervisor", "")
                    
                    # Filtra as visitas registradas por esse supervisor específico
                    visitas_do_nucleo = df_visitas[
                        df_visitas["Supervisor"].str.lower().str.strip() == sup_narrative.lower().strip()
                    ] if not df_visitas.empty else pd.DataFrame()
                    
                    # Se não achar por correspondência exata de nome, tenta uma busca parcial inteligente
                    if visitas_do_nucleo.empty and not df_visitas.empty and sup_narrative:
                        primeiro_nome = sup_narrative.split()[0].lower()
                        visitas_do_nucleo = df_visitas[
                            df_visitas["Supervisor"].str.lower().str.contains(primeiro_nome, na=False)
                        ]
                    
                    fotos_reais = []
                    if not visitas_do_nucleo.empty:
                        # Ordena para colocar os registros mais recentes primeiro usando a coluna Carimbo de envio
                        visitas_do_nucleo = visitas_do_nucleo.copy()
                        if "Carimbo" in visitas_do_nucleo.columns:
                            try:
                                visitas_do_nucleo["Carimbo_dt"] = pd.to_datetime(visitas_do_nucleo["Carimbo"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
                                visitas_do_nucleo = visitas_do_nucleo.sort_values(by="Carimbo_dt", ascending=False)
                            except:
                                pass
                        
                        # Compila as fotos reais enviadas
                        for _, v_row in visitas_do_nucleo.iterrows():
                            v_photos = v_row.get("Fotos", "")
                            processed_v = process_links(v_photos)
                            fotos_reais.extend([p for p in processed_v if p["type"] == "image"])
                    
                    # Exibe as fotos vinculadas dinamicamente via Carrossel ou Imagem Estática
                    if fotos_reais:
                        if len(fotos_reais) == 1:
                            st.markdown(f"✨ *Foto real encontrada no formulário:*")
                            st.image(fotos_reais[0]["url"], use_container_width=True, caption=f"Registro de Visita - Supervisor(a) {sup_narrative}")
                        else:
                            st.markdown(f"✨ *Carrossel de Slides: **{len(fotos_reais)} fotos** reais registradas em visitas (transição automática de 4s):*")
                            render_image_carousel(fotos_reais, interval_ms=4000, height=380)
                    else:
                        # Fallback: Se não houver fotos de visitas, usa os links da planilha Narrativas (podem ser múltiplos!)
                        foto_url = row.get("Foto", "")
                        processed_fallback = process_links(foto_url) if isinstance(foto_url, str) and foto_url.strip() else []
                        
                        fallback_images = [p for p in processed_fallback if p["type"] == "image"]
                        fallback_folders = [p for p in processed_fallback if p["type"] == "folder"]
                        
                        if fallback_images:
                            if len(fallback_images) == 1:
                                st.image(fallback_images[0]["url"], use_container_width=True, caption=f"Foto: {row['Projeto_Acao']}")
                            else:
                                st.markdown(f"✨ *Carrossel de Slides do Portfólio ({len(fallback_images)} fotos - transição automática de 4s):*")
                                render_image_carousel(fallback_images, interval_ms=4000, height=380)
                        elif fallback_folders:
                            st.warning("Este núcleo possui fotos armazenadas em uma pasta do Google Drive.")
                            st.link_button("Abrir Pasta de Fotos 🌐", fallback_folders[0]["url"])
                        else:
                            st.info("Nenhuma foto cadastrada ou enviada por este núcleo ainda.")
                        
                st.divider()

# -------------------------------------------------------------
# TAB 2: VISITS AND FORM PHOTO GALLERY
# -------------------------------------------------------------
with tab_photos:
    st.markdown("### 📸 Registro e Acompanhamento de Visitas do Coordenador de Área")
    st.write("Esta seção é integrada em tempo real à planilha de respostas do formulário que os coordenadores utilizam nas visitas mensais de acompanhamento aos núcleos do PIBID.")
    
    if df_visitas.empty:
        st.info("Nenhum registro de visita encontrado.")
    else:
        for idx, row in df_visitas.iterrows():
            supervisor_name = row.get("Supervisor", "Supervisor não informado")
            data_visita = row.get("Data_Visita", "Data não informada")
            
            with st.expander(f"🏫 Visita de Acompanhamento — Núcleo do(a) Supervisor(a) {supervisor_name} ({data_visita})"):
                col_meta1, col_meta2 = st.columns(2)
                with col_meta1:
                    st.markdown(f"**Carimbo de Envio:** `{row.get('Carimbo', 'N/A')}`")
                    st.markdown(f"**Email de Envio:** `{row.get('Email', 'N/A')}`")
                with col_meta2:
                    st.markdown(f"**Data Oficial da Visita:** `{data_visita}`")
                
                st.divider()
                
                # Check photos column
                photos_col = row.get("Fotos", "")
                processed_photos = process_links(photos_col)
                
                st.markdown("#### 📸 Acervo Fotográfico Anexado nesta Visita:")
                if processed_photos:
                    images_to_show = [p for p in processed_photos if p["type"] == "image"]
                    folders_to_show = [p for p in processed_photos if p["type"] == "folder"]
                    
                    # Display images
                    if images_to_show:
                        img_cols = st.columns(min(len(images_to_show), 3))
                        for col_idx, img_info in enumerate(images_to_show):
                            with img_cols[col_idx % len(img_cols)]:
                                st.image(img_info["url"], use_container_width=True, caption=f"Foto Anexo {col_idx+1}")
                    
                    # Display folders
                    if folders_to_show:
                        for f_info in folders_to_show:
                            st.warning(f"📂 Esta resposta contém um link para uma pasta do Google Drive: \n{f_info['url']}")
                            st.link_button("Abrir Pasta Completa no Google Drive 🌐", f_info["url"])
                else:
                    st.info("Nenhum arquivo de imagem anexado nesta resposta de formulário.")

# -------------------------------------------------------------
# TAB 3: THEORETICAL AND REFLECTIVE DIMENSIONS
# -------------------------------------------------------------
with tab_reflections:
    st.markdown("### 🧠 Dimensões Formativas e Impacto Crítico do PIBID")
    st.write("Análise qualitativa aprofundada baseada nas considerações e aportes teóricos encontrados nos relatórios de atividades oficiais de 2024-2026.")
    
    sub_tab1, sub_tab2, sub_tab3 = st.tabs([
        "📚 Formação de Professores (Prática Reflexiva)",
        "⚖️ Inclusão & Justiça Social na Escola",
        "🎯 Práticas de Superação & Flexibilização"
    ])
    
    with sub_tab1:
        st.markdown("#### 👩‍🏫 A Articulação entre Teoria e Prática e a Formação Docente")
        st.write("""
        Os relatórios mostram que o PIBID é de suma importância para construir confiança na atuação e conforto com o ambiente escolar. 
        Entre as atividades qualitativas reflexivas que geraram esse amadurecimento, destacam-se:
        
        * **Memoriais Descritivos (Livro 'Infância' de Graciliano Ramos)**: Bolsistas escreveram relatos autobiográficos interligando suas próprias memórias escolares à obra do autor. Esse exercício estimulou a sensibilidade e a empatia para lidar com as realidades diversas de seus futuros alunos.
        * **Participação nos Conselhos de Classe como Ouvintes**: IDs dos núcleos como Henrique Fontes acompanharam as dinâmicas de fechamento trimestral dos professores. A observação ativa proporcionou aos bolsistas uma visão realista e crítica sobre avaliação continuada, indisciplina, bullying e o uso do sistema digital de regência 'Professor Online'.
        * **Encontros de Estudo Teórico**: Leituras orientadas sobre o fracasso escolar, interseccionalidade e a pedagogia freireana serviram de base para que as pibidianas planejassem suas ações de intervenção a partir das carências reais de cada instituição.
        """)
        
    with sub_tab2:
        st.markdown("#### ⚖️ Inclusão, Acolhimento e o Combate ao Bullying")
        st.write("""
        A dimensão humana e o acolhimento estão no centro do PIBID UNISUL. As ações foram planejadas e executadas para garantir ambientes seguros de aprendizagem:
        
        * **Xadrez na Escola no Contraturno (Espaço do AEE)**: Ofereceu suporte aos alunos com necessidades educacionais especiais no Atendimento Educacional Especializado (AEE), desenvolvendo o foco, as competências socioemocionais e o raciocínio lógico.
        * **Cuidar de Si e do Outro (NEPRE)**: O 'Correio de Denúncias' contra Bullying permitiu aos alunos expressarem relatos de sofrimento de forma anônima. Os bolsistas, orientadora e supervisor analisavam cada caso de forma confidencial para dar o devido encaminhamento pedagógico protetivo.
        * **Conscientização em Datas Sensíveis**: Oficinas e apresentações sobre o Dia Internacional da Mulher e a gincana educativa contra a exploração infantil 'Maio Laranja' debateram e esclareceram os sinais de relacionamentos abusivos em sala de aula.
        * **Alfabetização e Literatura no CEJA**: No Centro de Educação de Jovens e Adultos (CEJA), os núcleos aplicaram a escuta atenta aos alunos da EJA, muitos em fase de alfabetização, transformando a biblioteca escolar num ambiente afetuoso de pertencimento.
        """)
        
    with sub_tab3:
        st.markdown("#### 🎯 Desafios Pedagógicos de Infraestrutura e Soluções Criativas")
        st.write("""
        Os relatórios registram de forma realista que o ambiente escolar apresenta dificuldades concretas, cuja superação fortalece o perfil profissional dos licenciandos:
        
        * **Limitação de Acervo Físico**: No projeto *Mundo dos Sonhos (Coraline)* no Gallotti, a quantidade muito pequena de livros físicos obrigou os bolsistas a organizarem leituras compartilhadas em duplas e a criarem capítulos digitalizados nos tablets da escola.
        * **Canso Extremo e Evasão na EJA**: Estudantes adultos que chegam à escola após longas jornadas de trabalho enfrentam esgotamento físico e mental. As pibidianas contornaram esse desafio desenvolvendo estratégias afetivas envolvendo lanches coletivos e cafés literários.
        * **Gestão do Tempo e Calendário**: Mudanças de cronograma, feriados e readequações curriculares demandaram dos bolsistas flexibilidade constante para replanejar suas ações em conjunto com a gestão escolar.
        """)

# -------------------------------------------------------------
# TAB 4: PALAVRA-CHAVE SEARCH IN NARRATIVES
# -------------------------------------------------------------
with tab_search:
    st.markdown("### 🔍 Busca de Narrativas por Palavra-Chave")
    st.write("Digite um tema ou termo de interesse (ex: *Bullying*, *Livro*, *Feminicídio*, *Freire*, *EJA*) para filtrar as práticas e relatos de vivência armazenados no banco de dados.")
    
    search_query = st.text_input("Digite o termo para buscar:", "")
    
    if search_query:
        query_clean = search_query.lower()
        search_results = df_narrativas[
            df_narrativas["Metodologia"].str.lower().str.contains(query_clean) |
            df_narrativas["Impacto_Escola"].str.lower().str.contains(query_clean) |
            df_narrativas["Voz_Bolsista"].str.lower().str.contains(query_clean) |
            df_narrativas["Projeto_Acao"].str.lower().str.contains(query_clean) |
            df_narrativas["Dificuldades"].str.lower().str.contains(query_clean)
        ]
        
        if search_results.empty:
            st.warning(f"Nenhum relato encontrado para o termo '{search_query}'.")
        else:
            st.success(f"Encontrado {len(search_results)} relato(s) pedagógico(s) correspondente(s)!")
            for idx, row in search_results.iterrows():
                with st.expander(f"📌 {row['Projeto_Acao']} — {row['Escola']} ({row['Periodo_Bimestre']})"):
                    st.markdown(f"**Supervisor:** `{row['Supervisor']}`")
                    st.markdown(f"**Como foi desenvolvido:** {row['Metodologia']}")
                    st.markdown(f"**Impacto Social:** {row['Impacto_Escola']}")
                    st.markdown(f"**A Voz do Bolsista:** *\"{row['Voz_Bolsista']}\"*\n")
                    st.markdown(f"**Dificuldades Superadas:** {row['Dificuldades']}")
                    
                    foto = row.get("Foto", "")
                    if isinstance(foto, str) and foto.strip():
                        ptype, conv_url = get_direct_img_url(foto)
                        if ptype == "image":
                            st.image(conv_url, width=500, caption=row['Projeto_Acao'])
                        else:
                            st.image(foto, width=500, caption=row['Projeto_Acao'])
    else:
        st.info("Digite uma palavra no campo acima para iniciar a busca.")
