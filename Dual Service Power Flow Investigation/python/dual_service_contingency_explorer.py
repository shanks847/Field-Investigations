# import streamlit as st  # Streamlit for interactive web UI
# import pandapower as pp  # Power system modeling and analysis
# import pandapower.networks as pn  # Predefined networks (not used here)
# import pandapower.plotting as plot  # Optional plotting tools
# import matplotlib.pyplot as plt  # Optional plotting (used for diagram)
# import matplotlib.patches as patches  # For drawing symbols like breakers and loads

# # --- Constants ---
# PBASE = 10  # Power base in MVA for per-unit scaling
# VBASE = 12  # Voltage base in kV for buses
# pf = 0.95
# TAN_PHI = 0.3287  # tan(acos(0.95)) ≈ 0.3287

# # --- Initialize Breaker States in session memory ---
# if "breaker_states" not in st.session_state:
#     st.session_state.breaker_states = {
#         'BRK-SS1-FD': True,
#         'BRK-SS2-FD': True,
#         'BRK-F1': True,
#         'BRK-F2': True,
#         'BRK-T1': True,
#         'BRK-T2': True,
#         'BRK-L1': True,
#         'BRK-L2': True,
#     }

# # --- UI Controls ---
# st.sidebar.title("Breaker Controls")
# for brk in st.session_state.breaker_states:
#     st.session_state.breaker_states[brk] = st.sidebar.checkbox(brk, value=st.session_state.breaker_states[brk])

# st.sidebar.title("Load Controls (pu multipliers)")
# ss1_fd_scale = st.sidebar.slider("SS1-FD LOAD (×15 MVA)", 0.0, 2.0, 1.0)
# ss2_fd_scale = st.sidebar.slider("SS2-FD LOAD (×15 MVA)", 0.0, 2.0, 1.0)
# load1_scale = st.sidebar.slider("LOAD 01 (×2 MVA)", 0.0, 2.0, 1.0)
# load2_scale = st.sidebar.slider("LOAD 02 (×2.5 MVA)", 0.0, 2.0, 1.0)

# st.sidebar.title("Generation Limits (in pu)")
# gen_p_mw = st.sidebar.slider("SS2 Generator Output (MW)", 0.0, 5.0, 2.0)
# slack_vm = st.sidebar.slider("Slack Voltage (pu)", 0.95, 1.05, 1.00)

# # --- Create pandapower network ---
# net = pp.create_empty_network()
# b1 = pp.create_bus(net, vn_kv=VBASE, name="BBS1")
# b2 = pp.create_bus(net, vn_kv=VBASE, name="BBS2")
# b3 = pp.create_bus(net, vn_kv=VBASE, name="BBS3")
# b4 = pp.create_bus(net, vn_kv=VBASE, name="BBS4")

# pp.create_ext_grid(net, bus=b1, vm_pu=slack_vm, name="SS1")
# pp.create_gen(net, bus=b2, p_mw=gen_p_mw * PBASE, vm_pu=1.0, name="SS2")

# pp.create_load(net, bus=b1, p_mw=15.0 * ss1_fd_scale, q_mvar=15.0 * ss1_fd_scale * TAN_PHI, name="SS1-FD LOAD")
# pp.create_load(net, bus=b2, p_mw=15.0 * ss2_fd_scale, q_mvar=15.0 * ss2_fd_scale * TAN_PHI, name="SS2-FD LOAD")
# pp.create_load(net, bus=b3, p_mw=2.0 * load1_scale, q_mvar=2.0 * load1_scale * TAN_PHI, name="LOAD 01")
# pp.create_load(net, bus=b4, p_mw=2.5 * load2_scale, q_mvar=2.5 * load2_scale * TAN_PHI, name="LOAD 02")

# line_type = "NAYY 4x120 SE"
# length_km = 0.02
# l1 = pp.create_line(net, from_bus=b1, to_bus=b3, length_km=length_km, std_type=line_type)
# l2 = pp.create_line(net, from_bus=b2, to_bus=b4, length_km=length_km, std_type=line_type)
# l3 = pp.create_line(net, from_bus=b3, to_bus=b4, length_km=length_km, std_type=line_type)

# pp.create_switch(net, bus=b3, element=l1, et="l", closed=st.session_state.breaker_states['BRK-F1'], name="BRK-F1")
# pp.create_switch(net, bus=b4, element=l2, et="l", closed=st.session_state.breaker_states['BRK-F2'], name="BRK-F2")
# pp.create_switch(net, bus=b3, element=l3, et="l", closed=st.session_state.breaker_states['BRK-T1'], name="BRK-T1")
# pp.create_switch(net, bus=b4, element=l3, et="l", closed=st.session_state.breaker_states['BRK-T2'], name="BRK-T2")

# # --- Power Flow ---
# try:
#     pp.runpp(net)
# except pp.LoadflowNotConverged:
#     st.error("Power flow did not converge. Check breaker states or generator limits.")

# # --- Plotting SLD Diagram ---
# def draw_sld():
#     fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
#     size = 0.08
    
#     def draw_breaker(x, y, closed):
#         color = 'green' if closed else 'red'
#         if closed:
#             ax.plot([x - size, x + size], [y - size, y + size], color=color, linewidth=2)
#             ax.plot([x - size, x + size], [y + size, y - size], color=color, linewidth=2)
#         else:
#             ax.plot([x, x + 0.25], [y + 0.25, y - 0.25], color=color, linewidth=2)

#     # Minimal schematic (can be extended)
#     ax.text(2, 5, "SS1", fontsize=9)
#     ax.text(8, 5, "SS2", fontsize=9)
#     draw_breaker(2, 4.5, st.session_state.breaker_states['BRK-F1'])
#     draw_breaker(8, 4.5, st.session_state.breaker_states['BRK-F2'])
#     draw_breaker(3, 2.5, st.session_state.breaker_states['BRK-T1'])
#     draw_breaker(7, 2.5, st.session_state.breaker_states['BRK-T2'])

#     ax.set_xlim(0, 10)
#     ax.set_ylim(1, 6)
#     ax.axis('off')
#     return fig

# st.subheader("Substation Single-Line Diagram")
# st.pyplot(draw_sld(), use_container_width=True)

# # --- Results Output ---
# st.subheader("Bus Voltages (pu)")
# st.dataframe(net.res_bus[['vm_pu']])

# st.subheader("Line Loadings (%)")
# st.dataframe(net.res_line[['loading_percent']])

# st.subheader("Load Powers (MW)")
# st.dataframe(net.res_load[['p_mw', 'q_mvar']])

# st.subheader("Generator Output")
# st.dataframe(net.res_gen[['p_mw', 'q_mvar']])

#------------STABLE ABOVE-----------------------

import streamlit as st
import pandapower as pp
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io



# -------------------------------
# Constants and Base Values
# -------------------------------
PBASE = 10.0     # Base power in MVA
VBASE = 12.0     # Base voltage in kV
pf = 0.95
TAN_PHI = 0.3287  # tan(acos(0.95)) ≈ 0.3287

# -------------------------------
# Initialize Breaker States
# -------------------------------
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

st.sidebar.title("Breaker Controls")
for brk in st.session_state.breaker_states:
    st.session_state.breaker_states[brk] = st.sidebar.checkbox(brk, 
                                        value=st.session_state.breaker_states[brk],
                                        key=brk)

# -------------------------------
# Streamlit UI: Load and Generation Controls
# -------------------------------
st.sidebar.title("Load Controls (per-unit multipliers)")
ss1_fd_scale = st.sidebar.slider("SS1-FD LOAD (×10 MVA)", 0.0, 2.0, 1.0)
ss2_fd_scale = st.sidebar.slider("SS2-FD LOAD (×10 MVA)", 0.0, 2.0, 1.0)
load1_scale = st.sidebar.slider("LOAD 01 (×2 MVA)", 0.0, 2.0, 1.0)
load2_scale = st.sidebar.slider("LOAD 02 (×2.5 MVA)", 0.0, 2.0, 1.0)

st.sidebar.title("Generation/Slack Settings")
gen_output_pu = st.sidebar.slider("SS2 Generator Output (pu, base=10 MVA)", 0.0, 5.0, 2.0)
slack_vm = st.sidebar.slider("Slack Voltage (pu)", 0.95, 1.05, 1.00)

# -------------------------------
# Create pandapower Network Model
# -------------------------------
net = pp.create_empty_network()

# Create buses (BBS1: Utility, BBS2: Gen, BBS3: Downstream of Utility, BBS4: Downstream of Gen)
b1 = pp.create_bus(net, vn_kv=VBASE, name="BBS1")
b2 = pp.create_bus(net, vn_kv=VBASE, name="BBS2")
b3 = pp.create_bus(net, vn_kv=VBASE, name="BBS3")
b4 = pp.create_bus(net, vn_kv=VBASE, name="BBS4")

# Sources
pp.create_ext_grid(net, bus=b1, vm_pu=slack_vm, name="SS1")
pp.create_gen(net, bus=b2, p_mw=gen_output_pu * PBASE, vm_pu=1.0, name="SS2")

# Loads (actual load values; all in MW, scaled by multipliers)
pp.create_load(net, bus=b1, p_mw=15.0 * ss1_fd_scale, q_mvar=15.0 * ss1_fd_scale * TAN_PHI, name="SS1-FD LOAD")
pp.create_load(net, bus=b2, p_mw=15.0 * ss2_fd_scale, q_mvar=15.0 * ss2_fd_scale * TAN_PHI, name="SS2-FD LOAD")
pp.create_load(net, bus=b3, p_mw=2.0 * load1_scale, q_mvar=2.0 * load1_scale * TAN_PHI, name="LOAD 01")
pp.create_load(net, bus=b4, p_mw=2.5 * load2_scale, q_mvar=2.5 * load2_scale * TAN_PHI, name="LOAD 02")

# Define Lines: All lines are 20 m (0.02 km); use a high-ampacity standard type
std_type = "NAYY 4x120 SE"  # Make sure this type exists in your pandapower std_types
length_km = 0.02
l1 = pp.create_line(net, from_bus=b1, to_bus=b3, length_km=length_km, std_type=std_type, name="L1")
l2 = pp.create_line(net, from_bus=b2, to_bus=b4, length_km=length_km, std_type=std_type, name="L2")
l3 = pp.create_line(net, from_bus=b3, to_bus=b4, length_km=length_km, std_type=std_type, name="L3")

# Create element-level switches (breakers) on lines (using the Streamlit states)
pp.create_switch(net, bus=b3, element=l1, et="l", closed=st.session_state.breaker_states['BRK-F1'], name="BRK-F1")
pp.create_switch(net, bus=b4, element=l2, et="l", closed=st.session_state.breaker_states['BRK-F2'], name="BRK-F2")
pp.create_switch(net, bus=b3, element=l3, et="l", closed=st.session_state.breaker_states['BRK-T1'], name="BRK-T1")
pp.create_switch(net, bus=b4, element=l3, et="l", closed=st.session_state.breaker_states['BRK-T2'], name="BRK-T2")

# Run the Power Flow
try:
    pp.runpp(net)
except pp.LoadflowNotConverged:
    st.error("Power flow did not converge. Check breaker states, generator limits, or load levels.")

# Display pandapower results in Streamlit
st.subheader("Bus Voltages (pu)")
st.dataframe(net.res_bus[['vm_pu']])

st.subheader("Line Loadings (%)")
st.dataframe(net.res_line[['loading_percent']])

st.subheader("Load Powers (MW/MVAr)")
st.dataframe(net.res_load[['p_mw', 'q_mvar']])

st.subheader("Generator Output (MW/MVAr)")
st.dataframe(net.res_gen[['p_mw', 'q_mvar']])

# -------------------------------
# Draw the SLD Diagram using matplotlib
# -------------------------------
def draw_diagram():
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    size = 0.08

    # Diagram Y positions
    y_top = 5
    y_bus_top = 4.0
    y_intermediate = 3.2
    y_bus_bottom = 2.5
    y_load_hinge = 2.0
    y_load_tip = 1.75
    y_fd_hinge = 3.7
    y_fd_tip = 3.5
    y_tie_bottom = y_bus_bottom - 0.5

    # Diagram X positions (representing busbar sections)
    x_bbs1 = 3       # BBS1 (Source side for Utility)
    x_bbs2 = 9       # BBS2 (Source side for Generator)
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

    # --- Sources ---
    # SS1: Utility (hatched box)
    ax.add_patch(plt.Rectangle((x_bbs1 - 0.2, y_top - 0.25), 0.4, 0.4,
                               edgecolor='black', facecolor='white', hatch='xx'))
    ax.text(x_bbs1 + 0.5, y_top - 0.05, "SS1", ha='left', va='center', fontsize=9)
    ax.plot([x_bbs1, x_bbs1], [y_top - 0.25, y_bus_top], color='black', linewidth=2.5)

    # SS2: Generator (circle with G)
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

    # --- Feeder Loads (SS1-FD and SS2-FD) ---
    x_ss1_fd = x_bbs1 - 0.8
    ax.plot([x_ss1_fd, x_ss1_fd], [y_bus_top, y_fd_hinge], color='black', linewidth=2.5)
    draw_breaker(x_ss1_fd, y_fd_hinge, "BRK-SS1-FD", st.session_state.breaker_states['BRK-SS1-FD'])
    draw_load(x_ss1_fd, y_fd_hinge, y_fd_tip, "SS1-FD LOAD")

    x_ss2_fd = x_bbs2 + 0.8
    ax.plot([x_ss2_fd, x_ss2_fd], [y_bus_top, y_fd_hinge], color='black', linewidth=2.5)
    draw_breaker(x_ss2_fd, y_fd_hinge, "BRK-SS2-FD", st.session_state.breaker_states['BRK-SS2-FD'])
    draw_load(x_ss2_fd, y_fd_hinge, y_fd_tip, "SS2-FD LOAD")

    # --- Feeds from Upper Busbars to Lower Busbars (BBS1 -> BBS3, BBS2 -> BBS4) ---
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

    # --- Tie-line (U-style, but now the tie-line spur extends DOWNWARD)
    # Invert tie-line: now the vertical spur from the busbar goes downward (instead of upward)
    # and the tie-line horizontal segment is below the busbars.
    x_bbs3_tie = x_bbs3 + 0.6  # BBS3 spur shifted right
    x_bbs4_tie = x_bbs4 - 0.6  # BBS4 spur shifted left
    y_tie_top = y_bus_bottom - 0.5  # Tie-line top now below busbar
    mid_tie = (y_bus_bottom + y_tie_top) / 2

    ax.plot([x_bbs3_tie, x_bbs3_tie], [y_bus_bottom, y_tie_top], color='black', linewidth=2.5)
    draw_breaker(x_bbs3_tie, mid_tie, "BRK-T1", st.session_state.breaker_states['BRK-T1'])
    ax.plot([x_bbs4_tie, x_bbs4_tie], [y_bus_bottom, y_tie_top], color='black', linewidth=2.5)
    draw_breaker(x_bbs4_tie, mid_tie, "BRK-T2", st.session_state.breaker_states['BRK-T2'])
    ax.plot([x_bbs3_tie, x_bbs4_tie], [y_tie_top, y_tie_top], color='black', linewidth=2.5)

    # --- Loads on Lower Busbars ---
    # LOAD 01: For BBS3, now shift left (off-center)
    x_bbs3_load = x_bbs3 - 0.8
    ax.plot([x_bbs3_load, x_bbs3_load], [y_bus_bottom, y_load_hinge], color='black', linewidth=2.5)
    draw_breaker(x_bbs3_load, y_load_hinge, "BRK-L1", st.session_state.breaker_states['BRK-L1'])
    draw_load(x_bbs3_load, y_load_hinge, y_load_tip, "LOAD 01")

    # LOAD 02: For BBS4, shift right
    x_bbs4_load = x_bbs4 + 0.8
    ax.plot([x_bbs4_load, x_bbs4_load], [y_bus_bottom, y_load_hinge], color='black', linewidth=2.5)
    draw_breaker(x_bbs4_load, y_load_hinge, "BRK-L2", st.session_state.breaker_states['BRK-L2'])
    draw_load(x_bbs4_load, y_load_hinge, y_load_tip, "LOAD 02")

    ax.set_xlim(1.5, 10.5)
    ax.set_ylim(1.0, 5.2)
    ax.axis('off')
    ax.set_aspect('equal')
    return fig

st.title("Substation SLD Control Interface")
fig = draw_diagram()
# Convert figure to PNG using BytesIO and display it with st.image
buf = io.BytesIO()
fig.savefig(buf, format='png', dpi=450, bbox_inches='tight')
st.image(buf.getvalue(), use_column_width=True)
