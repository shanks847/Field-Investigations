import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Initialize breaker states
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
    st.session_state.breaker_states[brk] = st.sidebar.checkbox(brk, value=st.session_state.breaker_states[brk])

def draw_diagram():
    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    size = 0.08

    y_top = 5
    y_bus_top = 4.0
    y_intermediate = 3.2
    y_bus_bottom = 2.5
    y_load_hinge = 2.0
    y_load_tip = 1.75
    y_fd_hinge = 3.7
    y_fd_tip = 3.5
    y_tie_bottom = y_bus_bottom - 0.5

    x_bbs1 = 3
    x_bbs2 = 9
    x_bbs3 = 3
    x_bbs4 = 9

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

    # Sources
    ax.add_patch(plt.Rectangle((x_bbs1 - 0.2, y_top - 0.25), 0.4, 0.4, edgecolor='black', facecolor='white', hatch='xx'))
    ax.text(x_bbs1 + 0.5, y_top - 0.05, "SS1", ha='left', va='center', fontsize=9)
    ax.plot([x_bbs1, x_bbs1], [y_top - 0.25, y_bus_top], color='black', linewidth=2.5)

    ax.add_patch(patches.Circle((x_bbs2, y_top - 0.05), radius=0.15, edgecolor='black', facecolor='white'))
    ax.text(x_bbs2 + 0.4, y_top - 0.05, "SS2", ha='left', va='center', fontsize=9)
    ax.text(x_bbs2, y_top - 0.05, "G", ha='center', va='center', fontsize=10)
    ax.plot([x_bbs2, x_bbs2], [y_top - 0.2, y_bus_top], color='black', linewidth=2.5)

    # Busbars
    ax.plot([x_bbs1 - 1, x_bbs1 + 1], [y_bus_top, y_bus_top], color='black', linewidth=3)
    ax.text(x_bbs1 - 1.05, y_bus_top, "BBS1", ha='right', va='bottom', fontsize=9)

    ax.plot([x_bbs2 - 1, x_bbs2 + 1], [y_bus_top, y_bus_top], color='black', linewidth=3)
    ax.text(x_bbs2 + 1.05, y_bus_top, "BBS2", ha='left', va='bottom', fontsize=9)

    # Loads from BBS1 and BBS2
    x_ss1_fd = x_bbs1 - 0.8
    ax.plot([x_ss1_fd, x_ss1_fd], [y_bus_top, y_fd_hinge], color='black', linewidth=2.5)
    draw_breaker(x_ss1_fd, y_fd_hinge, "BRK-SS1-FD", st.session_state.breaker_states['BRK-SS1-FD'])
    draw_load(x_ss1_fd, y_fd_hinge, y_fd_tip, "SS1-FD LOAD")

    x_ss2_fd = x_bbs2 + 0.8
    ax.plot([x_ss2_fd, x_ss2_fd], [y_bus_top, y_fd_hinge], color='black', linewidth=2.5)
    draw_breaker(x_ss2_fd, y_fd_hinge, "BRK-SS2-FD", st.session_state.breaker_states['BRK-SS2-FD'])
    draw_load(x_ss2_fd, y_fd_hinge, y_fd_tip, "SS2-FD LOAD")

    # BBS1 and BBS2 to BBS3 and BBS4
    ax.plot([x_bbs1, x_bbs1], [y_bus_top, y_intermediate], color='black', linewidth=2.5)
    draw_breaker(x_bbs1, y_intermediate, "BRK-F1", st.session_state.breaker_states['BRK-F1'])
    ax.plot([x_bbs1, x_bbs1], [y_intermediate, y_bus_bottom], color='black', linewidth=2.5)

    ax.plot([x_bbs2, x_bbs2], [y_bus_top, y_intermediate], color='black', linewidth=2.5)
    draw_breaker(x_bbs2, y_intermediate, "BRK-F2", st.session_state.breaker_states['BRK-F2'])
    ax.plot([x_bbs2, x_bbs2], [y_intermediate, y_bus_bottom], color='black', linewidth=2.5)

    # Bottom Busbars
    ax.plot([x_bbs3 - 1, x_bbs3 + 1], [y_bus_bottom, y_bus_bottom], color='black', linewidth=3)
    ax.text(x_bbs3 - 1.05, y_bus_bottom, "BBS3", ha='right', va='bottom', fontsize=9)

    ax.plot([x_bbs4 - 1, x_bbs4 + 1], [y_bus_bottom, y_bus_bottom], color='black', linewidth=3)
    ax.text(x_bbs4 + 1.05, y_bus_bottom, "BBS4", ha='left', va='bottom', fontsize=9)

    # Tie-line (U style)
    x_bbs3_tie = x_bbs3 + 0.6
    x_bbs4_tie = x_bbs4 - 0.6
    mid_tie = (y_bus_bottom + y_tie_bottom) / 2

    ax.plot([x_bbs3_tie, x_bbs3_tie], [y_bus_bottom, y_tie_bottom], color='black', linewidth=2.5)
    draw_breaker(x_bbs3_tie, mid_tie, "BRK-T1", st.session_state.breaker_states['BRK-T1'])
    ax.plot([x_bbs4_tie, x_bbs4_tie], [y_bus_bottom, y_tie_bottom], color='black', linewidth=2.5)
    draw_breaker(x_bbs4_tie, mid_tie, "BRK-T2", st.session_state.breaker_states['BRK-T2'])
    ax.plot([x_bbs3_tie, x_bbs4_tie], [y_tie_bottom, y_tie_bottom], color='black', linewidth=2.5)

    # Loads on BBS3 and BBS4
    x_bbs3_load = x_bbs3 - 0.8
    ax.plot([x_bbs3_load, x_bbs3_load], [y_bus_bottom, y_load_hinge], color='black', linewidth=2.5)
    draw_breaker(x_bbs3_load, y_load_hinge, "BRK-L1", st.session_state.breaker_states['BRK-L1'])
    draw_load(x_bbs3_load, y_load_hinge, y_load_tip, "LOAD 01")

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
st.pyplot(fig)
