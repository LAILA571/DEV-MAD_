import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.arima.model import ARIMA
import numpy as np

st.set_page_config(page_title="FX Dashboard BAM – Ajustement ARMA", layout="wide")
st.title("📊 Marché de Change Marocain – Ajustement ARMA & Prévision")

# ===============================
# Upload fichier Excel
# ===============================
uploaded_file = st.file_uploader("Importer le fichier Excel", type=["xlsx"])

if uploaded_file:

    # ===============================
    # Charger les données
    # ===============================
    df_usd = pd.read_excel(uploaded_file, sheet_name="Feuil1")
    df_eur = pd.read_excel(uploaded_file, sheet_name="Feuil3")
    df_fx  = pd.read_excel(uploaded_file, sheet_name="EURUSD_2024-01-01_to_2026-02-18")

    df_usd["quote_date"] = pd.to_datetime(df_usd["quote_date"])
    df_eur["quote_date"] = pd.to_datetime(df_eur["quote_date"])
    df_fx["Date"] = pd.to_datetime(df_fx["Date"])

    # Calcul des écarts
    df_usd["error"] = df_usd["mid_rate_USD"] - df_usd["USD_MAD_central"]
    df_eur["error"] = df_eur["Mid_EUR"] - df_eur["EUR_MAD_central"]

    # ===============================
    # Bande de fluctuation
    # ===============================
    bande_pct = st.slider("Bande de fluctuation (%)", 0, 20, 5)
    bande = bande_pct / 100

    # ===============================
    # USD/MAD – Ajustement ARMA
    # ===============================
    st.header("📈 USD/MAD – Ajustement ARMA")

    model_usd = ARIMA(df_usd["error"], order=(1,0,1))
    result_usd = model_usd.fit()
    df_usd["error_ARMA"] = result_usd.fittedvalues
    df_usd["USD_MAD_adjusted"] = df_usd["USD_MAD_central"] + df_usd["error_ARMA"]

    df_usd["Upper"] = df_usd["USD_MAD_central"] * (1 + bande)
    df_usd["Lower"] = df_usd["USD_MAD_central"] * (1 - bande)
    df_usd["error_adjusted"] = df_usd["mid_rate_USD"] - df_usd["USD_MAD_adjusted"]

    fig_usd = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                            row_heights=[0.7, 0.3],
                            subplot_titles=("USD/MAD – Calculé / BAM / Ajusté", "Écart BAM - Ajusté ARMA"))

    fig_usd.add_trace(go.Scatter(x=df_usd["quote_date"], y=df_usd["Upper"], line=dict(width=0), showlegend=False), row=1, col=1)
    fig_usd.add_trace(go.Scatter(x=df_usd["quote_date"], y=df_usd["Lower"], fill="tonexty",
                                 fillcolor="rgba(0,100,255,0.25)", line=dict(width=0), name=f"Bande ±{bande_pct}%"), row=1, col=1)
    fig_usd.add_trace(go.Scatter(x=df_usd["quote_date"], y=df_usd["USD_MAD_central"], name="USD/MAD Calculé"), row=1, col=1)
    fig_usd.add_trace(go.Scatter(x=df_usd["quote_date"], y=df_usd["mid_rate_USD"], name="USD/MAD BAM"), row=1, col=1)
    fig_usd.add_trace(go.Scatter(x=df_usd["quote_date"], y=df_usd["USD_MAD_adjusted"], name="USD/MAD Ajusté ARMA"), row=1, col=1)
    fig_usd.add_trace(go.Scatter(x=df_usd["quote_date"], y=df_usd["error_adjusted"], name="Erreur Ajustée"), row=2, col=1)

    fig_usd.update_layout(template="plotly_white", height=600)
    st.plotly_chart(fig_usd, use_container_width=True)

    # Tableau USD/MAD
    st.subheader("📋 Table USD/MAD – Cours Calculé / BAM / Ajusté")
    st.dataframe(df_usd[["quote_date","USD_MAD_central","mid_rate_USD","USD_MAD_adjusted","error_adjusted"]].rename(
        columns={
            "quote_date":"Date",
            "USD_MAD_central":"Calculé",
            "mid_rate_USD":"BAM",
            "USD_MAD_adjusted":"Ajusté ARMA",
            "error_adjusted":"Erreur Ajustée"
        }
    ), height=300)

    # ===============================
    # EUR/MAD – Ajustement ARMA
    # ===============================
    st.header("📈 EUR/MAD – Ajustement ARMA")

    model_eur = ARIMA(df_eur["error"], order=(1,0,1))
    result_eur = model_eur.fit()
    df_eur["error_ARMA"] = result_eur.fittedvalues
    df_eur["EUR_MAD_adjusted"] = df_eur["EUR_MAD_central"] + df_eur["error_ARMA"]

    df_eur["Upper"] = df_eur["EUR_MAD_central"] * (1 + bande)
    df_eur["Lower"] = df_eur["EUR_MAD_central"] * (1 - bande)
    df_eur["error_adjusted"] = df_eur["Mid_EUR"] - df_eur["EUR_MAD_adjusted"]

    fig_eur = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                            row_heights=[0.7, 0.3],
                            subplot_titles=("EUR/MAD – Calculé / BAM / Ajusté", "Écart BAM - Ajusté ARMA"))

    fig_eur.add_trace(go.Scatter(x=df_eur["quote_date"], y=df_eur["Upper"], line=dict(width=0), showlegend=False), row=1, col=1)
    fig_eur.add_trace(go.Scatter(x=df_eur["quote_date"], y=df_eur["Lower"], fill="tonexty",
                                 fillcolor="rgba(0,180,120,0.25)", line=dict(width=0), name=f"Bande ±{bande_pct}%"), row=1, col=1)
    fig_eur.add_trace(go.Scatter(x=df_eur["quote_date"], y=df_eur["EUR_MAD_central"], name="EUR/MAD Calculé"), row=1, col=1)
    fig_eur.add_trace(go.Scatter(x=df_eur["quote_date"], y=df_eur["Mid_EUR"], name="EUR/MAD BAM"), row=1, col=1)
    fig_eur.add_trace(go.Scatter(x=df_eur["quote_date"], y=df_eur["EUR_MAD_adjusted"], name="EUR/MAD Ajusté ARMA"), row=1, col=1)
    fig_eur.add_trace(go.Scatter(x=df_eur["quote_date"], y=df_eur["error_adjusted"], name="Erreur Ajustée"), row=2, col=1)

    fig_eur.update_layout(template="plotly_white", height=600)
    st.plotly_chart(fig_eur, use_container_width=True)

    # Tableau EUR/MAD
    st.subheader("📋 Table EUR/MAD – Cours Calculé / BAM / Ajusté")
    st.dataframe(df_eur[["quote_date","EUR_MAD_central","Mid_EUR","EUR_MAD_adjusted","error_adjusted"]].rename(
        columns={
            "quote_date":"Date",
            "EUR_MAD_central":"Calculé",
            "Mid_EUR":"BAM",
            "EUR_MAD_adjusted":"Ajusté ARMA",
            "error_adjusted":"Erreur Ajustée"
        }
    ), height=300)

    # ===============================
    # Simulation impact sur le panier MAD
    # ===============================
    st.header("🔮 Simulation impact sur le panier MAD")
    col1, col2, col3 = st.columns(3)
    with col1:
        usd_variation = st.slider("Variation USD (%)", -10, 10, 0)
    with col2:
        eur_variation = st.slider("Variation EUR (%)", -10, 10, 0)
    with col3:
        w_usd = st.slider("Poids USD dans le panier", 0.0, 1.0, 0.4, 0.01)

    w_eur = 1.0 - w_usd
    st.info(f"Pondérations panier : {w_usd*100:.0f}% USD / {w_eur*100:.0f}% EUR")

    df_sim = df_fx.copy()
    df_sim["USD_MAD_sim"] = df_usd["USD_MAD_adjusted"] * (1 + usd_variation/100)
    df_sim["EUR_MAD_sim"] = df_eur["EUR_MAD_adjusted"] * (1 + eur_variation/100)
    df_sim["MAD_panier"] = w_usd*df_sim["USD_MAD_sim"] + w_eur*df_sim["EUR_MAD_sim"]

    fig_sim = go.Figure()
    fig_sim.add_trace(go.Scatter(x=df_sim["Date"], y=df_sim["USD_MAD_sim"], name="USD/MAD simulé"))
    fig_sim.add_trace(go.Scatter(x=df_sim["Date"], y=df_sim["EUR_MAD_sim"], name="EUR/MAD simulé"))
    fig_sim.add_trace(go.Scatter(x=df_sim["Date"], y=df_sim["MAD_panier"], name="MAD Panier simulé",
                                 line=dict(color="black", dash="dash")))
    fig_sim.update_layout(template="plotly_white", title="Impact hypothétique USD & EUR sur le MAD")
    st.plotly_chart(fig_sim, use_container_width=True)

    # Tableau Panier MAD
    st.subheader("📋 Table Simulation Panier MAD")
    st.dataframe(df_sim[["Date","USD_MAD_sim","EUR_MAD_sim","MAD_panier"]].rename(
        columns={
            "USD_MAD_sim":"USD/MAD simulé",
            "EUR_MAD_sim":"EUR/MAD simulé",
            "MAD_panier":"MAD Panier"
        }
    ), height=300)

    # ===============================
    # Prévision 1 mois après le dernier cours
    # ===============================
    st.header("📅 Prévision BAM pour 1 mois après le dernier cours")
    n_days = 20  # approximativement 1 mois

    last_date_usd = df_usd["quote_date"].max()
    last_date_eur = df_eur["quote_date"].max()

    future_dates_usd = pd.date_range(start=last_date_usd + pd.Timedelta(days=1), periods=n_days, freq='B')
    future_dates_eur = pd.date_range(start=last_date_eur + pd.Timedelta(days=1), periods=n_days, freq='B')

   

    # EUR/MAD prévision
    forecast_eur = result_eur.get_forecast(steps=n_days)
    pred_error_eur = forecast_eur.predicted_mean
    pred_ci_eur = forecast_eur.conf_int()
    last_calc_eur = df_eur["EUR_MAD_central"].iloc[-1]
    eur_predicted = last_calc_eur + pred_error_eur.values
    df_forecast_eur = pd.DataFrame({
        "Date": future_dates_eur,
        "EUR/MAD Prévu": eur_predicted,
        "Borne basse": last_calc_eur + pred_ci_eur.iloc[:,0].values,
        "Borne haute": last_calc_eur + pred_ci_eur.iloc[:,1].values
    })

    fig_fore_eur = go.Figure()
    fig_fore_eur.add_trace(go.Scatter(x=df_forecast_eur["Date"], y=df_forecast_eur["EUR/MAD Prévu"],
                                      name="EUR/MAD Prévu", line=dict(color="green")))
    fig_fore_eur.add_trace(go.Scatter(x=df_forecast_eur["Date"], y=df_forecast_eur["Borne haute"],
                                      name="Borne haute", line=dict(dash="dash", color="red")))
    fig_fore_eur.add_trace(go.Scatter(x=df_forecast_eur["Date"], y=df_forecast_eur["Borne basse"],
                                      name="Borne basse", line=dict(dash="dash", color="red")))
    fig_fore_eur.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig_fore_eur, use_container_width=True)

    # Tableau EUR/MAD prévision
    st.subheader("📋 Table Prévision EUR/MAD – 1 mois")
    st.dataframe(df_forecast_eur, height=300)