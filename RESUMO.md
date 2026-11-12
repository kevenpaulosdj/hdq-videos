# "Hoje é dia de quê?" – resumo do projeto (até 12/11/2026, 20h)

Use este arquivo para começar uma conversa nova sem perder contexto: cole-o (ou anexe) na primeira mensagem.

## 1. O canal
- Curiosidades sobre datas comemorativas do dia, em português do Brasil, com linguagem natural e descontraída.
- Contas: Instagram **@datastododia**, TikTok **Datas Comemorativas** e um canal no YouTube (Shorts). O Facebook é opcional e não está conectado.
- Fonte das datas: `https://pt.wikipedia.org/wiki/<D>_de_<mês>`. Todo dia escolho as **3 datas com mais potencial de engajamento**.
- **Plano B:** se faltar data boa, entra o aniversário de uma pessoa famosa no Brasil, com uma curiosidade marcante confirmada em mais de uma fonte.
  - O selo vira "ANIVERSÁRIO DE <NOME>".
  - Sem fotos e sem desenhar o rosto da pessoa: só o mascote e ícones da área dela.
  - Evitar figuras ligadas a crimes, tragédias recentes ou polêmica política.

## 2. Estilo dos vídeos
- Formato 9:16 (1080x1920, 30 fps), um vídeo por data, aprofundado e com **mais de 1 minuto**.
- Visual em blocos/pixel, "parecido com Minecraft", mas **sem nada do Minecraft** (nem personagens, nem logo, nem texturas).
- Mascote: um cubo com rosto que faz ações ligadas ao tema. Exemplos:
  - Fluminense: embaixadinhas e comemoração de gol.
  - Hip hop: boné, microfone, caixa de som e breakdance.
  - Inventor: óculos de proteção, martelo e um mini 14-Bis.
- Boa distância entre o mascote e os elementos animados.
- No topo: o selo "DIA DO..." e o texto "HOJE É DIA DE QUÊ?". Sem barra de progresso.
- Sons do tema (torcida, scratch, martelo etc.) e trilha chiptune gerada pelo motor.
- Ordinais sempre por extenso (nada de º, ª ou nº).
- Fontes pixel: Jersey 10 (texto) e Press Start 2P (títulos).
- **Gancho (desde 12/11):**
  - A 1ª tela abre com `["hook", "frase com *destaque*"]`, inteira no quadro 0.
  - A 1ª fala começa pela surpresa (até 10 palavras), nunca pela data, e promete um bônus no final.
  - A voz começa no segundo 0. A data vem depois, num kicker.

## 3. Narração (ElevenLabs)
- Voz clonada do usuário: "Homem brasileiro jovem", voice_id `1GUkxQUjtQUnYfNagjql`.
- Modelo **eleven_v4**, `generations_count` 1, um áudio por tela, o mesmo flow no dia todo.
- Processamento (`motor/prep.sh`):
  - tira os silêncios;
  - acelera com `atempo=1.25`;
  - normaliza o volume (`loudnorm`);
  - define cada tela como áudio + 0,55 s.
- Mixagem: `motor/mixvoice.py`, que abaixa a música quando a voz entra (ducking).
- Consumo: cerca de 2.000 caracteres por vídeo, uns 5.700 por dia e uns 170 mil por mês. O plano atual não cobre isso.
  - **Decisão:** manter o v4 até o plano acabar e depois trocar para o **Flash v2.5** (0,5 crédito por caractere, uns 86 mil por mês).
  - Basta dizer "troca pro Flash".
- O domínio `elevenlabsusercontent.com` precisa estar liberado no ambiente para baixar os áudios.

## 4. Motor e arquivos
- Repositório: **github.com/kevenpaulosdj/hdq-videos**.
  - `motor/`: engine.py, themes.py, mascot2.py, sound.py, run.py, prep.sh, mixvoice.py e exemplos .json.
  - Vídeos publicados: `videos/AAAA-MM-DD/<tema>.mp4`.
  - Link público (GitHub Pages): `https://kevenpaulosdj.github.io/hdq-videos/videos/AAAA-MM-DD/<tema>.mp4`
- Uso: `python run.py spec.json [--stills 0,5,20]`, com as variáveis `HDQ_WORK` e `HDQ_FONTS`.
- Os vídeos precisam ter no máximo uns 18 MB, senão o Metricool não consegue baixar. Para reduzir:
  `ffmpeg -i in.mp4 -c:v libx264 -preset veryfast -b:v 850k -maxrate 1000k -bufsize 2000k -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out.mp4`
- Cópia de reserva do motor: artefato "Hoje é dia de quê? – motor dos vídeos" (slug `7f7ec5b9-2ed7-45c1-81c7-7ae7eb33eb1f`).
- Skill proposta: "hoje-e-dia-de-que". Confirme que foi salva no cartão de proposta.
- Documento do dia 12/11 (roteiros, legendas, títulos e fontes): https://claude.ai/artifact/Rcv3UryJMHRGvDUNER7vGR
- Ícone da página: canvas de design `7ef78bd5-48da-45b8-87cc-799dd73bd540`, com 3 opções.

## 5. Publicação
- **Horários padrão:** 8h, 14h e 20h (Brasília), um vídeo por horário. No dia 12/11 foi exceção: 16h, 19h e 22h.
- **Metricool** (marca `blogId 8066887`, com Instagram, TikTok e YouTube ligados) agenda e publica nas 3 redes. Para cada vídeo, 2 posts:
  1. **TikTok + YouTube:** legenda do TikTok.
     - TikTok: `title` obrigatório.
     - YouTube: `type short`, público, `madeForKids false`.
  2. **Instagram:** Reel com o arquivo `static.metricool.com` devolvido pelo post 1 e o comentário para fixar em `firstCommentText`.
  - Fazer as chamadas uma por vez, nunca em paralelo.
- **Windsor.ai:** plano reserva só para o Instagram (conta `17841414231186823`, `create_video_post` e `create_comment`).
  - O Windsor não publica no TikTok nem no YouTube; lá, ele só lê métricas.
- **Selo de IA:** o usuário escolheu **não** marcar os vídeos como IA.
- **Aprovação:** nada é publicado sem o "sim" do usuário. O padrão é um único "sim" por dia para agendar os 3 vídeos.

## 6. Legendas e tags
- **Instagram** (limite de 5 hashtags): `#fyp #foryou #viral #historia #curiosidades`
- **TikTok e YouTube Shorts:** `#fy #foryou #fyp #viral #historia #curiosidades`
- **Título do Shorts:** chamativo, até 70 caracteres, em forma de curiosidade ou pergunta, com no máximo 1 emoji. Exemplo: "21 segundos de voo que viraram feriado ✈️ Santos Dumont e o 14-Bis".
- Toda legenda termina com uma pergunta. O comentário fixado também é uma pergunta.

## 7. Automação ativa
- **Tarefa diária "Hoje é dia de quê? – vídeos do dia"** (`trig_01ACxj9KRC5HJct13c9PoutK`).
  - Roda às 3h23 (America/Bahia), na nuvem, então funciona com o PC desligado.
  - Pesquisa, gera narração, renderiza, publica no GitHub, cria o documento e pede o "sim".
  - Depois agenda no Metricool e confere se tudo saiu. Envia notificação no celular.
- O usuário só precisa responder "sim" pelo app, de preferência até 7h45.

## 8. Resultados até agora (12/11)
- **Inventor:** Instagram (Windsor), TikTok e YouTube (Metricool), tudo publicado.
- **Fluminense:** TikTok e YouTube publicados às 19h. O Instagram falhou no Metricool porque ainda não estava conectado lá; publiquei pelo Windsor às 19h20.
- **Hip Hop:** agendado para as 22h nas 3 redes. Haverá uma conferência às 22h10.
- O YouTube Shorts trouxe bem mais alcance que o TikTok e o Instagram no primeiro dia. É normal para contas novas; vale comparar depois de uma semana.

## 9. Ideias pendentes
- Encurtar os vídeos em uns 20 a 30 s (hoje vão de 1:40 a 2:05) para melhorar a retenção. O usuário ainda não decidiu.
- Trocar para o ElevenLabs Flash quando o plano acabar.
- Conectar o Facebook (opcional).

## 10. Quando trocar de modelo e de esforço
| Situação | Modelo | Esforço |
|---|---|---|
| Responder "sim", conferir se os posts saíram, ajustar uma legenda ou um horário | Sonnet (ou Haiku) | baixo |
| Tarefa diária de rotina (pesquisa, roteiro, render, agendamento) | Sonnet | médio |
| Dia com tema difícil, plano B de aniversariantes ou checagem de fatos polêmicos | Opus | médio a alto |
| Mudar o motor (novo tema, novo mascote, nova animação), depurar erro de render ou de publicação | Opus | alto |
| Estratégia (analisar métricas da semana, repensar formato e ganchos) | Opus | alto |

Notas:
- A tarefa diária está hoje no **Opus 5.5**. Depois de 3 a 5 dias rodando sem erro, dá para trocar para o **Sonnet 5.5** e economizar. Se a qualidade dos roteiros cair ou aparecerem erros, volte para o Opus.
- Abra uma **conversa nova** para cada assunto grande (ex.: "mudar o motor", "análise da semana") e cole este arquivo no começo. Conversas longas ficam lentas e caras.
