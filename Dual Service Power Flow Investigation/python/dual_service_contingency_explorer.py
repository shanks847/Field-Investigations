import streamlit as st
import pandapower as pp
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import io
import math

# ----------------------------
# Fix: Set Base Values and PF Parameters
# ----------------------------
PBASE = 10.0       # Base power (MVA)
VBASE = 12.0       # Base voltage (kV)
pf = 0.95
TAN_PHI = math.tan(math.acos(pf))  # ≈ 0.3287

# Nominal load MVA values
NOMINAL_SS1_FD = 15.0
NOMINAL_SS2_FD = 15.0
NOMINAL_LOAD1 = 2.0
NOMINAL_LOAD2 = 2.5

# ----------------------------
# Fix: Initialize Breaker States in Session State
# ----------------------------
if "breaker_states" not in st.session_state:
    st.session_state.breaker_states = {
        'BRK-SS1-FD': True,
        'BRK-SS2-FD': True,
        'BRK-F1': True,
        'BRK-F2': True,
        'BRK-T1': True,
        'BRK-T2': True,
        'BRK-L1': True,
        'BRK-L2': True,
    }

# ----------------------------
# Sidebar Controls: Breaker States (Dropdowns)
# ----------------------------
st.sidebar.title("Breaker Controls")
for brk in st.session_state.breaker_states:
    option = st.sidebar.selectbox(brk, ["Closed", "Open"],
                                  index=0 if st.session_state.breaker_states[brk] else 1,
                                  key="dropdown_" + brk)
    st.session_state.breaker_states[brk] = True if option == "Closed" else False

# ----------------------------
# Sidebar Controls: Loads & Generation Settings (pu multipliers)
# ----------------------------
st.sidebar.title("Load Controls (pu multipliers)")
ss1_fd_scale = st.sidebar.slider("SS1-FD LOAD (×15 MVA)", 0.0, 2.0, 1.0)
ss2_fd_scale = st.sidebar.slider("SS2-FD LOAD (×15 MVA)", 0.0, 2.0, 1.0)
load1_scale    = st.sidebar.slider("LOAD 01 (×2 MVA)", 0.0, 2.0, 1.0)
load2_scale    = st.sidebar.slider("LOAD 02 (×2.5 MVA)", 0.0, 2.0, 1.0)

st.sidebar.title("Generation/Slack Settings (pu)")
gen_output_pu = st.sidebar.slider("SS2 Generator Output (pu, base=10 MVA)", 0.0, 5.0, 2.0)
slack_vm      = st.sidebar.slider("Slack Voltage (pu)", 0.95, 1.05, 1.00)

# ----------------------------
# No buttons: power flow re-runs automatically on any change.
# ----------------------------

# ----------------------------
# Build the pandapower Network Model
# ----------------------------
net = pp.create_empty_network()

# Create four buses (BBS1: Utility side, BBS2: Generator side, BBS3: Downstream of Utility, BBS4: Downstream of Gen)
b1 = pp.create_bus(net, vn_kv=VBASE, name="BBS1")
b2 = pp.create_bus(net, vn_kv=VBASE, name="BBS2")
b3 = pp.create_bus(net, vn_kv=VBASE, name="BBS3")
b4 = pp.create_bus(net, vn_kv=VBASE, name="BBS4")

# Sources
pp.create_ext_grid(net, bus=b1, vm_pu=slack_vm, name="SS1")  # Utility as slack bus
pp.create_gen(net, bus=b2, p_mw=gen_output_pu * PBASE, vm_pu=1.0, name="SS2")  # Generator (sgen)

# Loads (absolute values in MW/MVAr):
pp.create_load(net, bus=b1, p_mw=NOMINAL_SS1_FD * ss1_fd_scale, 
               q_mvar=NOMINAL_SS1_FD * ss1_fd_scale * TAN_PHI, name="SS1-FD LOAD")
pp.create_load(net, bus=b2, p_mw=NOMINAL_SS2_FD * ss2_fd_scale, 
               q_mvar=NOMINAL_SS2_FD * ss2_fd_scale * TAN_PHI, name="SS2-FD LOAD")
pp.create_load(net, bus=b3, p_mw=NOMINAL_LOAD1 * load1_scale, 
               q_mvar=NOMINAL_LOAD1 * load1_scale * TAN_PHI, name="LOAD 01")
pp.create_load(net, bus=b4, p_mw=NOMINAL_LOAD2 * load2_scale, 
               q_mvar=NOMINAL_LOAD2 * load2_scale * TAN_PHI, name="LOAD 02")

# ----------------------------
# Define Lines and Switches
# ----------------------------
# Fix: Use a known high-ampacity standard line type, 20 m (0.02 km) long.
std_type = "NAYY 4x120 SE"  # Ensure this exists in your pandapower std_types library
length_km = 0.02
l1 = pp.create_line(net, from_bus=b1, to_bus=b3, length_km=length_km, std_type=std_type, name="L1")
l2 = pp.create_line(net, from_bus=b2, to_bus=b4, length_km=length_km, std_type=std_type, name="L2")
l3 = pp.create_line(net, from_bus=b3, to_bus=b4, length_km=length_km, std_type=std_type, name="L3")

# Create switches (element-level) representing breakers
pp.create_switch(net, bus=b3, element=l1, et="l", closed=st.session_state.breaker_states['BRK-F1'], name="BRK-F1")
pp.create_switch(net, bus=b4, element=l2, et="l", closed=st.session_state.breaker_states['BRK-F2'], name="BRK-F2")
pp.create_switch(net, bus=b3, element=l3, et="l", closed=st.session_state.breaker_states['BRK-T1'], name="BRK-T1")
pp.create_switch(net, bus=b4, element=l3, et="l", closed=st.session_state.breaker_states['BRK-T2'], name="BRK-T2")

# ----------------------------
# Run Power Flow (Automatically on change)
# ----------------------------
try:
    pp.runpp(net)
except pp.LoadflowNotConverged:
    st.error("Power flow did not converge. Check breaker states, gen limits, or load levels.")

# ----------------------------
# Display pandapower Results in Graphs and Table
# ----------------------------
# Create a table for line loadings in Amps (converting from kA)
if "i_ka" in net.res_line.columns:
    from_bus_names = [net.bus.at[net.line.at[i, 'from_bus'], 'name'] for i in net.line.index]
    to_bus_names   = [net.bus.at[net.line.at[i, 'to_bus'], 'name'] for i in net.line.index]
    amps = net.res_line['i_ka'] * 1000  # convert kA to A
    loading_df = pd.DataFrame({
        "FROM BUS": from_bus_names,
        "TO BUS": to_bus_names,
        "Amps": amps.round(2)
    })
else:
    loading_df = pd.DataFrame({"FROM BUS": [], "TO BUS": [], "Amps": []})
    
# Graphs: Minimal bar charts for Slack (BBS1) and Generator (SS2) outputs
# Get slack voltage from bus b1, and generator active power from net.res_gen:
slack_voltage = net.res_bus.vm_pu.loc[b1]
gen_active = net.res_gen.p_mw.loc[net.gen.index[0]]

# Prepare data as DataFrames:
slack_df = pd.DataFrame({"Slack Voltage (pu)": [slack_voltage]}, index=["BBS1"])
gen_df = pd.DataFrame({"SS2 Gen Output (MW)": [gen_active]}, index=["SS2"])

# ----------------------------
# Render the Results (Diagram on Top, then Graphs, then Table)
# ----------------------------
st.title("Substation Control Interface")

# Draw and display the Single-Line Diagram at the top
def draw_diagram():
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    size = 0.08

    # Diagram layout positions
    y_top = 5
    y_bus_top = 4.0
    y_intermediate = 3.2
    y_bus_bottom = 2.5
    y_load_hinge = 2.0
    y_load_tip = 1.75
    y_fd_hinge = 3.7
    y_fd_tip = 3.5
    y_tie_bottom = y_bus_bottom - 0.5

    # X positions (for busbar sections)
    x_bbs1 = 3       # BBS1 (Utility side)
    x_bbs2 = 9       # BBS2 (Generator side)
    x_bbs3 = 3       # BBS3 (Load side, downstream of BBS1)
    x_bbs4 = 9       # BBS4 (Load side, downstream of BBS2)

    def draw_breaker(x, y, label, state):
        color = 'green' if state else 'red'
        ax.plot([x - size, x + size], [y - size, y + size], color=color, linewidth=2)
        ax.plot([x - size, x + size], [y + size, y - size], color=color, linewidth=2)
        ax.text(x + 0.15, y + 0.02, label, fontsize=7, ha='left')

    def draw_load(x, y_hinge, y_tip, label):
        ax.plot([x, x], [y_hinge, y_tip + 0.05], color='black', linewidth=2)
        ax.add_patch(patches.RegularPolygon((x, y_tip), numVertices=3, radius=0.1,
                                             orientation=3.1416, edgecolor='black',
                                             facecolor='white', linewidth=1.5))
        ax.text(x, y_tip - 0.15, label, ha='center', va='top', fontsize=8)

    # --- Draw Sources ---
    ax.add_patch(plt.Rectangle((x_bbs1 - 0.2, y_top - 0.25), 0.4, 0.4, 
                               edgecolor='black', facecolor='white', hatch='xx'))
    ax.text(x_bbs1 + 0.5, y_top - 0.05, "SS1", ha='left', va='center', fontsize=9)
    ax.plot([x_bbs1, x_bbs1], [y_top - 0.25, y_bus_top], color='black', linewidth=2.5)

    ax.add_patch(patches.Circle((x_bbs2, y_top - 0.05), radius=0.15, 
                                edgecolor='black', facecolor='white'))
    ax.text(x_bbs2 + 0.4, y_top - 0.05, "SS2", ha='left', va='center', fontsize=9)
    ax.text(x_bbs2, y_top - 0.05, "G", ha='center', va='center', fontsize=10)
    ax.plot([x_bbs2, x_bbs2], [y_top - 0.2, y_bus_top], color='black', linewidth=2.5)

    # --- Upper Busbars (BBS1 and BBS2) ---
    ax.plot([x_bbs1 - 1, x_bbs1 + 1], [y_bus_top, y_bus_top], color='black', linewidth=3)
    ax.text(x_bbs1 - 1.05, y_bus_top, "BBS1", ha='right', va='bottom', fontsize=9)

    ax.plot([x_bbs2 - 1, x_bbs2 + 1], [y_bus_top, y_bus_top], color='black', linewidth=3)
    ax.text(x_bbs2 + 1.05, y_bus_top, "BBS2", ha='left', va='bottom', fontsize=9)

    # --- Feeder Loads from BBS1 and BBS2 (SS1-FD and SS2-FD) ---
    x_ss1_fd = x_bbs1 - 0.8
    ax.plot([x_ss1_fd, x_ss1_fd], [y_bus_top, y_fd_hinge], color='black', linewidth=2.5)
    draw_breaker(x_ss1_fd, y_fd_hinge, "BRK-SS1-FD", st.session_state.breaker_states['BRK-SS1-FD'])
    draw_load(x_ss1_fd, y_fd_hinge, y_fd_tip, "SS1-FD LOAD")

    x_ss2_fd = x_bbs2 + 0.8
    ax.plot([x_ss2_fd, x_ss2_fd], [y_bus_top, y_fd_hinge], color='black', linewidth=2.5)
    draw_breaker(x_ss2_fd, y_fd_hinge, "BRK-SS2-FD", st.session_state.breaker_states['BRK-SS2-FD'])
    draw_load(x_ss2_fd, y_fd_hinge, y_fd_tip, "SS2-FD LOAD")

    # --- Feed from Upper Busbars to Lower Busbars (BBS1 -> BBS3, BBS2 -> BBS4) ---
    ax.plot([x_bbs1, x_bbs1], [y_bus_top, y_intermediate], color='black', linewidth=2.5)
    draw_breaker(x_bbs1, y_intermediate, "BRK-F1", st.session_state.breaker_states['BRK-F1'])
    ax.plot([x_bbs1, x_bbs1], [y_intermediate, y_bus_bottom], color='black', linewidth=2.5)

    ax.plot([x_bbs2, x_bbs2], [y_bus_top, y_intermediate], color='black', linewidth=2.5)
    draw_breaker(x_bbs2, y_intermediate, "BRK-F2", st.session_state.breaker_states['BRK-F2'])
    ax.plot([x_bbs2, x_bbs2], [y_intermediate, y_bus_bottom], color='black', linewidth=2.5)

    # --- Lower Busbars (BBS3 and BBS4) ---
    ax.plot([x_bbs3 - 1, x_bbs3 + 1], [y_bus_bottom, y_bus_bottom], color='black', linewidth=3)
    ax.text(x_bbs3 - 1.05, y_bus_bottom, "BBS3", ha='right', va='bottom', fontsize=9)

    ax.plot([x_bbs4 - 1, x_bbs4 + 1], [y_bus_bottom, y_bus_bottom], color='black', linewidth=3)
    ax.text(x_bbs4 + 1.05, y_bus_bottom, "BBS4", ha='left', va='bottom', fontsize=9)

    # --- Tie-line (Regular U-shape with downward spurs)
    # Tie-line spurs now extend downward from the lower busbars.
    x_bbs3_tie = x_bbs3 + 0.6   # for BBS3, spur shifted right
    x_bbs4_tie = x_bbs4 - 0.6   # for BBS4, spur shifted left
    y_tie_top = y_bus_bottom - 0.5   # Top of the tie spur below the busbar level
    mid_tie = (y_bus_bottom + y_tie_top) / 2

    ax.plot([x_bbs3_tie, x_bbs3_tie], [y_bus_bottom, y_tie_top], color='black', linewidth=2.5)
    draw_breaker(x_bbs3_tie, mid_tie, "BRK-T1", st.session_state.breaker_states['BRK-T1'])
    ax.plot([x_bbs4_tie, x_bbs4_tie], [y_bus_bottom, y_tie_top], color='black', linewidth=2.5)
    draw_breaker(x_bbs4_tie, mid_tie, "BRK-T2", st.session_state.breaker_states['BRK-T2'])
    ax.plot([x_bbs3_tie, x_bbs4_tie], [y_tie_top, y_tie_top], color='black', linewidth=2.5)

    # --- Loads on Lower Busbars ---
    # For BBS3, load shifted left (LOAD 01)
    x_bbs3_load = x_bbs3 - 0.8
    ax.plot([x_bbs3_load, x_bbs3_load], [y_bus_bottom, y_load_hinge], color='black', linewidth=2.5)
    draw_breaker(x_bbs3_load, y_load_hinge, "BRK-L1", st.session_state.breaker_states['BRK-L1'])
    draw_load(x_bbs3_load, y_load_hinge, y_load_tip, "LOAD 01")
    # For BBS4, load shifted right (LOAD 02)
    x_bbs4_load = x_bbs4 + 0.8
    ax.plot([x_bbs4_load, x_bbs4_load], [y_bus_bottom, y_load_hinge], color='black', linewidth=2.5)
    draw_breaker(x_bbs4_load, y_load_hinge, "BRK-L2", st.session_state.breaker_states['BRK-L2'])
    draw_load(x_bbs4_load, y_load_hinge, y_load_tip, "LOAD 02")

    ax.set_xlim(1.5, 10.5)
    ax.set_ylim(1.0, 5.2)
    ax.axis('off')
    ax.set_aspect('equal')
    return fig

# st.title("Substation SLD Control Interface")
fig = draw_diagram()

# Convert figure to PNG and display it using st.image so it spans the full width
import io
buf = io.BytesIO()
fig.savefig(buf, format='png', bbox_inches='tight')
st.image(buf.getvalue(), use_column_width=True)

# --- Display Line Loading Table Below Diagram ---
if "i_ka" in net.res_line.columns:
    from_bus_names = [net.bus.at[net.line.at[i, 'from_bus'], 'name'] for i in net.line.index]
    to_bus_names   = [net.bus.at[net.line.at[i, 'to_bus'], 'name'] for i in net.line.index]
    amps = net.res_line['i_ka'] * 1000  # convert kA to A
    loading_df = pd.DataFrame({
        "FROM BUS": from_bus_names,
        "TO BUS": to_bus_names,
        "Amps": amps.round(2)
    })
else:
    loading_df = pd.DataFrame({"FROM BUS": [], "TO BUS": [], "Amps": []})
st.markdown("## Line Loadings (Amps)")
st.dataframe(loading_df)

# --- Display Power Flow Graphs on a New Page (via st.tabs) ---
tab1, tab2 = st.tabs(["Slack/Gen Graphs", "Other Results"])

with tab1:
    col1, col2 = st.columns(2)
    # Slack Voltage from bus b1:
    slack_voltage = net.res_bus.vm_pu.loc[b1]
    slack_df = pd.DataFrame({"Slack Voltage (pu)": [slack_voltage]}, index=["BBS1"])
    with col1:
        st.markdown("### Slack Voltage")
        st.bar_chart(slack_df)
    # Generator Output from gen at bus b2:
    gen_output = net.res_gen.p_mw.loc[net.gen.index[0]]
    gen_df = pd.DataFrame({"Gen Output (MW)": [gen_output]}, index=["SS2"])
    with col2:
        st.markdown("### Generator Output")
        st.bar_chart(gen_df)

with tab2:
    st.markdown("### Bus Voltages (pu)")
    bus_voltage_df = net.res_bus[['vm_pu']]
    bus_voltage_df.index = net.bus.name
    st.bar_chart(bus_voltage_df)
