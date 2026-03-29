import plotly
import streamlit as st
st.write(plotly.__version__)
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Seriado", layout="wide")

st.markdown("""
<style>
.main {
  background-color: #0e1117;
}

.card {
  background-color: #1c1f26;
  padding: 20px;
  border-radius: 15px;
  text-align: center;
  box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
}

.card h1 {
  margin: 0;
  font-size: 32px;
}

.card p {
  margin: 0;
  color: #aaa;
}

.title {
  font-size: 40px;
  font-weight: bold;
}

@media (max-width: 768px) {

  .title {
    font-size: 28px;
    text-align: center;
  }

  .card {
    padding: 15px;
  }

  .card h1 {
    font-size: 22px;
  }

  .card p {
    font-size: 14px;
  }

  body {
    overflow-x: hidden;
  }
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def carregar():
  df = pd.read_csv("ranking_seriado.csv")
  df = df[df["nota"] > 0]
  df = df.sort_values(by="nota", ascending=False).reset_index(drop=True)
  return df

df = carregar()

st.markdown('<p class="title">📊 Fase 01 do Seriado UFMG Dashboard</p>', unsafe_allow_html=True)

nomes = sorted(df["nome"].unique())

nome_input = st.selectbox(
   "Digite ou procure o seu nome completo",
   nomes,
   index=None,
   )
st.caption("⚠️ Resultados consideram apenas candidatos com nota maior que zero")
if nome_input:
  linha = df[df["nome"] == nome_input].iloc[0]
  idx = linha.name
  nota = linha["nota"]
  
  posicao = idx + 1
  total = len(df)
  top_percent = (posicao/total) * 100

  col1, col2, col3 = st.columns([1,1,1])

  col1.markdown(f"""
  <div class="card">
      <p>🏆 Posição</p>
      <h1>{posicao}</h1>
  </div>
  """, unsafe_allow_html=True)

  col2.markdown(f"""
  <div class="card">
      <p>📊 Nota</p>
      <h1>{nota:.2f}</h1>
  </div>
  """, unsafe_allow_html=True)

  col3.markdown(f"""
  <div class="card">
      <p>🔥 Top</p>
      <h1>{top_percent:.2f}%</h1>
  </div>
  """, unsafe_allow_html=True)

  st.markdown("---")
  
  notas = np.sort(df["nota"])
  percentis = np.linspace(0, 100, len(notas))
  percentil_usuario = (df["nota"] <= nota).sum() / len(df) * 100

  fig = go.Figure()

  fig.add_trace(go.Scatter(
    x=notas,
    y=percentis,
    mode='lines',
    line=dict(color="#4f8cff", width=3),
    name="Distribuição"
  ))

  fig.add_trace(go.Scatter(
    x=[nota],
    y=[percentil_usuario],
    mode='markers',
    marker=dict(size=12, color="#ff4b4b"),
    name="Você"
  ))

  fig.update_layout(
    title="Sua posição na distribuição",
    xaxis_title="Nota",
    yaxis_title="% de candidatos que você superou",
    yaxis=dict(
      range=[0, 100],
      ticksuffix="%",
      showgrid=False
    ),
    plot_bgcolor="#0e1117",
    paper_bgcolor="#0e1117",
    font_color="white"
  )

  fig.update_traces(line_shape='spline')

  st.plotly_chart(fig, use_container_width=True)

  st.markdown("---")

  acima = df[df["nota"] < nota].sort_values(by="nota", ascending=False).head(5)
  igual = df[df["nota"] == nota].head(5)
  abaixo = abaixo = df[df["nota"] > nota].sort_values(by="nota", ascending=True).head(5)

  def tabela(df_slice):
    return df_slice[["nome", "nota"]].reset_index(drop=True)
  
  col1, col2, col3 = st.columns([1,1,1])

  with col1:
    st.markdown("##### ⬆️ Acima")
    st.dataframe(tabela(acima))

  with col2:
    st.markdown("##### 🎯 Mesma nota")
    st.dataframe(tabela(igual).head(5))

  with col3:
    st.markdown("##### ⬇️ Abaixo")
    st.dataframe(tabela(abaixo))

  media = df["nota"].mean()
  mediana = df["nota"].median()

  acima_media = nota > media
  acima_mediana = nota > mediana

  st.markdown("#### 📊 Insights sobre seu desempenho")

  if top_percent <= 5.5:
    st.success("Você está entre os 5% melhores candidatos")
  elif top_percent <= 10:
    st.info("Você está entre os 10% melhores")
  elif top_percent <= 25:
    st.info("Você está entre os 25% melhores")
  else:
    st.warning("Você está acima da média geral, mas ainda pode subir mais")

  if acima_media:
    st.write("Sua nota está acima da média geral")
  else:
    st.write("Sua nota está abaixo da média geral")

  if acima_mediana:
    st.write("Você está acima da mediana (metade dos candidatos)")

  melhor_que = len(df[df["nota"] < nota])

  st.markdown(f"""
  #### 📊 Impacto

  - Você superou **{melhor_que:,} pessoas**
  """)

  st.markdown(f"""
  <div style="background-color:#1c1f26;padding:20px;border-radius:15px">
  <h3>🚀 Seu desempenho</h3>
  <p>Você está melhor que <b>{(melhor_que/len(df))*100:.2f}%</b> dos candidatos</p>
  </div>
  """, unsafe_allow_html=True)

  st.subheader("Top 10")
  st.dataframe(df.head(10))