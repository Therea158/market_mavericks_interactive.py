import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns

# Set color palette for teams
colors = {
    "Tim 1": "#FF6347",  # Tomato
    "Tim 2": "#1E90FF",  # DodgerBlue
    "Tim 3": "#32CD32",  # LimeGreen
    "Tim 4": "#FFD700",  # Gold
    "Tim 5": "#FF1493",  # DeepPink
}

commodities = ["Emas", "Minyak", "Gandum", "Timah", "Kopi"]
teams = [f"Tim {i+1}" for i in range(5)]
initial_price = 200_000
initial_capital = 1_000_000
total_periods = 3

# Initialize session state
if "periode" not in st.session_state:
    st.session_state.periode = 1

if "prices" not in st.session_state:
    st.session_state.prices = {kom: initial_price for kom in commodities}

if "wealth_history" not in st.session_state:
    st.session_state.wealth_history = {team: [initial_capital] for team in teams}

if "price_history" not in st.session_state:
    st.session_state.price_history = [{kom: initial_price for kom in commodities}]

# Title and subtitle
st.title("💹 Market Mavericks Simulator")
st.markdown("<style>h1 {text-align: center;}</style>", unsafe_allow_html=True)
st.caption("Simulasi Perdagangan 5 Komoditas untuk 5 Tim - 3 Periode")
st.image("https://via.placeholder.com/800x400?text=Market+Mavericks+Simulator", use_column_width=True)

# Display current period and prices
st.subheader(f"🕐 Periode {st.session_state.periode} / {total_periods}")
st.write("💰 Harga Komoditas Saat Ini:")
st.json(st.session_state.prices)

# Input price changes for each commodity
st.subheader("📈 Perubahan Harga Komoditas (%)")
price_changes = {}
cols = st.columns(len(commodities))
for i, kom in enumerate(commodities):
    with cols[i]:
        change = st.slider(f"{kom} (% change)", -50.0, 50.0, 0.0, step=1.0, key=f"change_{kom}_{st.session_state.periode}")
        price_changes[kom] = change

# Input allocations per team
st.subheader("🧾 Alokasi Dana per Tim ($)")
allocations = pd.DataFrame(index=teams, columns=commodities)

for team in teams:
    with st.expander(team):
        cols = st.columns(len(commodities))
        for i, kom in enumerate(commodities):
            with cols[i]:
                val = st.number_input(f"{kom}", min_value=0, value=0, step=10_000, key=f"{team}_{kom}_{st.session_state.periode}")
                allocations.loc[team, kom] = val
        total_alloc = allocations.loc[team].sum()
        if total_alloc > initial_capital:
            st.error(f"🚫 Total alokasi {team} melebihi $1.000.000")

# Run scenario button
if st.button("🚀 Jalankan Skenario"):
    # Update prices based on input change percentages
    updated_prices = {kom: round(st.session_state.prices[kom] * (1 + price_changes[kom] / 100), 2) for kom in commodities}
    st.session_state.price_history.append(updated_prices)
    st.session_state.prices = updated_prices

    # Calculate new wealth for each team
    results = []
    for team in teams:
        total_value = 0
        for kom in commodities:
            try:
                alloc = float(allocations.loc[team][kom])
            except:
                alloc = 0
            unit = alloc / st.session_state.price_history[-2][kom]
            new_value = unit * updated_prices[kom]
            total_value += new_value
        st.session_state.wealth_history[team].append(round(total_value, 2))
        results.append((team, round(total_value, 2)))

    # Display leaderboard
    leaderboard = sorted(results, key=lambda x: x[1], reverse=True)
    df_result = pd.DataFrame(leaderboard, columns=["Tim", "Total Kekayaan ($)"])
    st.subheader("📊 Leaderboard")
    st.dataframe(df_result, use_container_width=True)

    # Move to next period or finish the game
    if st.session_state.periode < total_periods:
        st.session_state.periode += 1
    else:
        st.success("🎉 Permainan Selesai!")

# Visualize wealth history with Plotly (Interactive)
if st.session_state.periode > 1:
    st.subheader("📊 Grafik Kekayaan Tiap Tim (Interaktif)")
    
    fig = go.Figure()

    # Add traces for each team
    for team in teams:
        fig.add_trace(go.Scatter(
            x=list(range(1, len(st.session_state.wealth_history[team]) + 1)),
            y=st.session_state.wealth_history[team],
            mode='lines+markers',
            name=team,
            line=dict(color=colors[team], width=4),
            marker=dict(size=10)
        ))

    # Update layout
    fig.update_layout(
        title="Grafik Perkembangan Kekayaan Tim",
        xaxis_title="Periode",
        yaxis_title="Total Kekayaan ($)",
        template="plotly_dark",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig)

# Reset button
if st.button("🔄 Reset Game"):
    st.session_state.clear()
    st.rerun()
