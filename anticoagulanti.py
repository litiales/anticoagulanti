import streamlit as st

st.set_page_config(
    page_title="Calcolatore Sospensione Anticoagulanti", layout="centered"
)

st.title("💊 Calcolatore Tempi di Sospensione Anticoagulanti")
st.write(
    "Inserisci i dati del paziente per stimare la clearance della creatinina e"
    " i tempi di sospensione basati sulle linee guida e sulle specifiche"
    " cliniche."
)

# 1. Sezione Input Utente
st.header("1. Dati del Paziente e Procedura")

col1, col2 = st.columns(2)

with col1:
  farmaco = st.selectbox(
      "Seleziona il Farmaco / Classe",
      [
          "Dabigatran (Pradaxa)",
          "Apixaban (Eliquis) / Rivaroxaban (Xarelto) / Edoxaban (Lixiana)",
          "Eparina a Basso Peso Molecolare (EBPM / Enoxaparina)",
          "Warfarin / Acenocumarol (Sintrom)",
      ],
  )
  eta = st.number_input("Età (anni)", min_value=18, max_value=120, value=65)
  peso = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=70.0)

with col2:
  sesso = st.radio("Sesso", ["Maschio", "Femmina"])
  creatinina = st.number_input(
      "Creatininemia sierica (mg/dL)",
      min_value=0.1,
      max_value=10.0,
      value=1.0,
      step=0.1,
  )

  if "Eparina" in farmaco:
    dosaggio_ebpm = st.selectbox(
        "Dosaggio EBPM", ["Basso dosaggio (50UI/kg/die)", "Alto dosaggio (100UI/kg/die)"]
    )
  else:
    regime_altri = st.selectbox(
        "Regime", ["Standard"]
    )


# 2. Funzione per il calcolo della Clearance della Creatinina (Cockcroft-Gault)
def calcola_crcl(eta, peso, creatinina, sesso):
  if creatinina == 0:
    return 0.0
  crcl = ((140 - eta) * peso) / (72 * creatinina)
  if sesso == "Femmina":
    crcl *= 0.85
  return round(crcl, 1)


crcl_stimata = calcola_crcl(eta, peso, creatinina, sesso)


# 3. Logica basata sulle regole aggiornate
def determina_sospensione_avanzata(
    farmaco, eta, peso, creatinina, crcl, **kwargs
):
  # Warfarin / Sintrom
  if "Warfarin" in farmaco:
    return (
        "Sospendere 3-5 giorni prima (verificando che l'INR sia < 1.5 prima"
        " dell'intervento/blocco)."
    )

  # EBPM (Eparine)
  if "Eparina" in farmaco:
    dosaggio = kwargs.get("dosaggio_ebpm")
    if crcl_stimata>=30:
       base = (
       "12 ore prima" if dosaggio == "Basso dosaggio (50UI/kg/die)" else "24 ore prima"
       )  #[span_0](start_span)[span_0](end_span)
    else:
       base = (
       "24 ore prima" if dosaggio == "Basso dosaggio (50UI/kg/die)" else "48 ore prima"
       )  #[span_1](start_span)[span_1](end_span)
    return base

  # Dabigatran
  if "Dabigatran" in farmaco:
      if crcl_stimata >= 80:
        return "48 ore prima"
      elif 50 <= crcl_stimata < 79:
        return "72 ore prima"
      elif 30 <= crcl_stimata < 49:
        return "96 ore prima"
      else:
        return "Controindicato eseguire procedure invasive per filtrato glomerulare troppo basso"

  # Rivaroxaban / Edoxaban
  if "Apixaban (Eliquis) / Rivaroxaban (Xarelto) / Edoxaban (Lixiana)" in farmaco:
    if crcl_stimata >= 15:
        return "48 ore prima"
    else:
        return "Controindicato eseguire procedure invasive per filtrato glomerulare troppo basso"


# 4. Sezione Risultati
st.markdown("---")
st.header("2. Risultati dell'Analisi")

if st.button("Calcola Tempi di Sospensione", type="primary"):
  st.info(
      f"📊 **Clearance della Creatinina stimata (Cockcroft-Gault):**"
      f" **{crcl_stimata} mL/min**"
  )

  # Raccolta argomenti dinamici in base al farmaco scelto
  kwargs_pass = {}
  if "Eparina" in farmaco:
    kwargs_pass["dosaggio_ebpm"] = dosaggio_ebpm

  risultato_sospensione = determina_sospensione_avanzata(
      farmaco, eta, peso, creatinina, crcl_stimata, **kwargs_pass
  )

  st.success(
      f"⏱️ **Intervallo di sospensione raccomandato prima della procedura /"
      f" blocco:**\n\n {risultato_sospensione}"
  )

  st.warning(
      "⚠️ **Nota di responsabilità:** Questo strumento integra criteri"
      " avanzati, ma non sostituisce il giudizio clinico specialistico e le"
      " linee guida ufficiali vigenti."
  )
