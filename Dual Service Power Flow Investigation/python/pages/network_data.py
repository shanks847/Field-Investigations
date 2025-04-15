import streamlit as st
import pandapower as pp
import pandas as pd
import math

# ----------------------------
# Equipment Data Page: Display all equipment data
# ----------------------------

st.set_page_config(page_title="Equipment Data", layout="wide")

# Base values and parameters (should match main.py)
PBASE = 10.0
VBASE = 12.0
pf = 0.95
TAN_PHI = math.tan(math.acos(pf))

NOMINAL_SS1_FD = 15.0
NOMINAL_SS2_FD = 15.0
NOMINAL_LOAD1   = 2.0
NOMINAL_LOAD2   = 2.5

# Create a new pandapower network model (or load from a saved file if desired)
net = pp.create_empty_network()

# Create buses
b1 = pp.create_bus(net, vn_kv=VBASE, name="BBS1")
b2 = pp.create_bus(net, vn_kv=VBASE, name="BBS2")
b3 = pp.create_bus(net, vn_kv=VBASE, name="BBS3")
b4 = pp.create_bus(net, vn_kv=VBASE, name="BBS4")

# Sources
pp.create_ext_grid(net, bus=b1, vm_pu=1.0, name="SS1")
pp.create_gen(net, bus=b2, p_mw=2.0 * PBASE, vm_pu=1.0, name="SS2")

# Loads
pp.create_load(net, bus=b1, p_mw=NOMINAL_SS1_FD, 
               q_mvar=NOMINAL_SS1_FD * TAN_PHI, name="SS1-FD LOAD")
pp.create_load(net, bus=b2, p_mw=NOMINAL_SS2_FD, 
               q_mvar=NOMINAL_SS2_FD * TAN_PHI, name="SS2-FD LOAD")
pp.create_load(net, bus=b3, p_mw=NOMINAL_LOAD1, 
               q_mvar=NOMINAL_LOAD1 * TAN_PHI, name="LOAD 01")
pp.create_load(net, bus=b4, p_mw=NOMINAL_LOAD2, 
               q_mvar=NOMINAL_LOAD2 * TAN_PHI, name="LOAD 02")

# Define lines
std_type = "NAYY 4x120 SE"
length_km = 0.02
l1 = pp.create_line(net, from_bus=b1, to_bus=b3, length_km=length_km, std_type=std_type, name="L1")
l2 = pp.create_line(net, from_bus=b2, to_bus=b4, length_km=length_km, std_type=std_type, name="L2")
l3 = pp.create_line(net, from_bus=b3, to_bus=b4, length_km=length_km, std_type=std_type, name="L3")

# Create switches (assume all closed for equipment overview)
pp.create_switch(net, bus=b3, element=l1, et="l", closed=True, name="BRK-F1")
pp.create_switch(net, bus=b4, element=l2, et="l", closed=True, name="BRK-F2")
pp.create_switch(net, bus=b3, element=l3, et="l", closed=True, name="BRK-T1")
pp.create_switch(net, bus=b4, element=l3, et="l", closed=True, name="BRK-T2")

try:
    pp.runpp(net)
except pp.LoadflowNotConverged:
    st.error("Power flow did not converge for the equipment data page.")

st.markdown("## Equipment Data Tables")

# Display data using tabs for clear separation
tabs = st.tabs(["Buses", "Loads", "Generators", "Ext Grid", "Lines", "Switches", "Power Flow Results"])

with tabs[0]:
    st.subheader("Bus Data")
    st.dataframe(net.bus)

with tabs[1]:
    st.subheader("Load Data")
    st.dataframe(net.load)

with tabs[2]:
    st.subheader("Generator Data")
    st.dataframe(net.gen)

with tabs[3]:
    st.subheader("External Grid Data")
    st.dataframe(net.ext_grid)

with tabs[4]:
    st.subheader("Line Data")
    st.dataframe(net.line)

with tabs[5]:
    st.subheader("Switch Data")
    st.dataframe(net.switch)

with tabs[6]:
    st.subheader("Power Flow Results")
    st.markdown("**Bus Voltage Results:**")
    st.dataframe(net.res_bus)
    st.markdown("**Line Loading Results:**")
    st.dataframe(net.res_line)
