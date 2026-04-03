import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go
from modules import data, calculations, plotting

# --- CONFIG ---
st.set_page_config(
    page_title="ESP design tool", 
    page_icon=":material/bolt:", 
    layout="wide"
)
st.logo("logo.png")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding-top: 6px; padding-bottom: 6px; font-size: 0.9rem;}
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #ff4b4b; color: #ff4b4b !important; }
    h1 { color: #003049; }
    h2 { color: #D62828; font-size: 1.5rem; }
    h3 { color: #F77F00; font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# --- INIT SESSION ---
defaults = {
    'engineer': "Engineer", 'well_name': "WELL-01", 'date': datetime.date.today(),
    'casing_od': 7.0, 'casing_id': 6.184, 'tubing_od': 2.875, 'tubing_id': 2.441, 'casing_burst': 5000.0,
    'depth_tvd': 7500.0, 'depth_md': 8000.0,
    'sbhp': 3000.0, 'pbhp': 2200.0, 'test_rate': 1500.0,
    'api': 35.0, 'wc': 50.0, 'gor': 400.0, 'gas_sg': 0.7,
    'whp': 200.0, 'target_rate': 2000.0,
    'pump_selected': None, 'stages': 100, 'manufacturer': 'SLB',
    'motor_hp': 0, 'motor_selected': None, 'protector_selected': None,
    # Monitoring
    'mon_date': datetime.date.today(), 'mon_freq': 60.0, 'mon_whp': 200.0, 'mon_rate': 1800.0, 'mon_amps': 65.0
}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# --- SIDEBAR NAV ---
with st.sidebar:
    st.markdown("## :material/bolt: ESP tool")
    nav = st.radio(
        "Select module", 
        ["ESP design", "Monitoring", "Optimizing", "About"]
    )
    st.write("")
    st.caption("Active well: " + st.session_state.well_name)

# --- HELPER: GLOBAL CALCS ---
# These are needed across modules
temp_est = 100 + (st.session_state.depth_tvd / 100) * 1.5
sg_oil = 141.5 / (131.5 + st.session_state.api)
sg_mix = (sg_oil * (1 - st.session_state.wc/100)) + (1.05 * st.session_state.wc/100)

def render_pump_curve(pump_model, stages, freq, op_point=None, system_curve=None):
    pump_df = data.get_pump_catalog()
    if pump_model not in pump_df['Model'].values: return None
    
    row = pump_df[pump_df['Model'] == pump_model].iloc[0]
    
    # Affirmity Laws
    ratio = freq / 60.0
    q_bm_min = row['Min_Rate_BPD'] * ratio
    q_bm_max = row['Max_Rate_BPD'] * ratio
    
    qs = np.linspace(0, q_bm_max * 1.2, 50)
    # H2 = H1 * ratio^2. H1(Q1). Q1 = Q2/ratio.
    q_ref = qs / ratio
    h_ref = row['Head_Coeff_A'] + row['Head_Coeff_B']*q_ref + row['Head_Coeff_C']*q_ref**2
    h_freq = h_ref * (ratio**2) * stages
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=qs, y=h_freq, name=f"Pump Head @ {freq}Hz", line=dict(color='#0077b6', width=3)))
    
    if system_curve:
        # system_curve = (qs_sys, h_sys)
        fig.add_trace(go.Scatter(x=system_curve[0], y=system_curve[1], name="System Curve", 
                                line=dict(color='#f3722c', width=2, dash='dash')))
    
    # ROR Box
    fig.add_vrect(x0=q_bm_min, x1=q_bm_max, fillcolor="green", opacity=0.1, annotation_text="ROR")
    
    if op_point:
        # op_point = (q, h)
        fig.add_trace(go.Scatter(x=[op_point[0]], y=[op_point[1]], mode='markers', 
                                 marker=dict(size=14, color='#d90429', symbol='star'), name="Operating Point"))
    
    fig.update_layout(
        title=dict(text=f"Pump performance: {pump_model}", font=dict(size=20, color='#003049')),
        xaxis_title="Rate (BPD)", 
        yaxis_title="Head (ft)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=80, b=20)
    )
    return fig

# ==========================================
# MODULE: ESP DESIGN
# ==========================================
if nav == "ESP design":
    st.title(":material/magic_button: ESP design wizard")
    
    tabs = st.tabs([
        "1. Data input", "2. Gas calc", "3. Pump select", "4. Protector", 
        "5. Motor", "6. Simulation", "7. Integrity", "8. Report"
    ])

    # --- TAB 1: INPUTS ---
    with tabs[0]:
        st.header("Step 1: Data input")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Wellbore")
            st.session_state.casing_od = st.number_input("Casing OD", value=st.session_state.casing_od)
            st.session_state.casing_id = st.number_input("Casing ID", value=st.session_state.casing_id)
            st.session_state.tubing_od = st.number_input("Tubing OD", value=st.session_state.tubing_od)
            st.session_state.tubing_id = st.number_input("Tubing ID", value=st.session_state.tubing_id)
            st.session_state.depth_md = st.number_input("Pump MD", value=st.session_state.depth_md)
            st.session_state.depth_tvd = st.number_input("Pump TVD", value=st.session_state.depth_tvd)
            st.session_state.casing_burst = st.number_input("Casing burst (psi)", value=st.session_state.casing_burst)
        with c2:
            st.subheader("Reservoir & fluid")
            st.session_state.test_rate = st.number_input("Test rate", value=st.session_state.test_rate)
            st.session_state.sbhp = st.number_input("Static BHP", value=st.session_state.sbhp)
            st.session_state.pbhp = st.number_input("Producing BHP", value=st.session_state.pbhp)
            st.session_state.api = st.number_input("API", value=st.session_state.api)
            st.session_state.wc = st.number_input("Water cut", value=st.session_state.wc)
            st.session_state.gor = st.number_input("GOR", value=st.session_state.gor)
            st.session_state.gas_sg = st.number_input("Gas SG", value=st.session_state.gas_sg)
            st.session_state.target_rate = st.number_input("Design target rate", value=st.session_state.target_rate)
        st.caption(f"Est BHT: {temp_est:.1f} F | SG mix: {sg_mix:.3f}")

    # --- TAB 2: GAS ---
    with tabs[1]:
        st.header("Step 2: Gas calculation")
        gas_res = calculations.calculate_gas_properties(
            st.session_state.gor, st.session_state.api, st.session_state.gas_sg,
            st.session_state.pbhp, temp_est, st.session_state.wc, st.session_state.target_rate
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("GVF", f"{gas_res['gvf']:.3f}", help="Gas volume fraction", label_visibility="visible")
        c2.metric("Turpin", f"{gas_res['turpin']:.2f}", help="Turpin correlation index")
        c3.metric("Free gas", f"{gas_res['free_gas_pct']:.1f}%")
        st.success(f"Recommendation: {gas_res['recommendation']}", icon=":material/check_circle:")

        # --- GAS HANDLING UI ---
        if gas_res['recommendation'] != "Standard Intake":
            st.markdown("---")
            col_l, col_r = st.columns(2)
            
            with col_l:
                st.subheader("Select Gas Separator")
                sep_df = data.get_gas_separator_catalog()
                sel_sep = st.selectbox("Select Gas Separator", sep_df['Model'], label_visibility="collapsed")
                sep_row = sep_df[sep_df['Model'] == sel_sep].iloc[0]
                
                st.markdown(f"**HP Required:** {sep_row['HP_Required']} HP")
                st.write("Rate at pump intake (BFPD):")
                st.info(f"{gas_res['total_liq_bh_bpd']:.2f}")
                st.write("Free gas at pump intake (%):")
                st.info(f"{gas_res['free_gas_pct']:.1f}")
                
                fig_gas = plotting.plot_gas_handling_chart(gas_res['total_liq_bh_bpd'], gas_res['free_gas_pct'])
                st.plotly_chart(fig_gas, use_container_width=True)
                
            with col_r:
                st.subheader("AGH")
                use_agh = st.toggle("Use AGH", value=True)
                agh_df = data.get_agh_catalog()
                # Vertical stage label in image, stylized as dataframe
                st.dataframe(agh_df, hide_index=True, use_container_width=True)
                
                st.checkbox("Use AGH Recommendation", value=False)
                st.subheader("Select AGH")
                st.selectbox("Select AGH", ["Gas handler stage 1", "Gas handler stage 2"], label_visibility="collapsed")
                st.markdown(f"**AGH horsepower required:** 13 HP")

    # --- TAB 3: PUMP ---
    with tabs[2]:
        st.header("Step 3: Pump selection")
        
        # Results from Step 2
        q_intake = gas_res['total_fluid_bh_bpd']
        
        col_l, col_r = st.columns([2, 1])
        
        with col_l:
            st.subheader("Select Pump")
            pump_df = data.get_pump_catalog()
            st.session_state.manufacturer = st.selectbox("Manufacturer", pump_df['Manufacturer'].unique())
            avail = pump_df[pump_df['Manufacturer'] == st.session_state.manufacturer]
            st.session_state.pump_selected = st.selectbox("Model", avail['Model'])
            
            st.write(f"You selected: {st.session_state.pump_selected}")
            
            row = avail[avail['Model'] == st.session_state.pump_selected].iloc[0]
            
            # Use intake rate for stage calculation
            h_stg = row['Head_Coeff_A'] + row['Head_Coeff_B']*q_intake + row['Head_Coeff_C']*q_intake**2
            tdh = calculations.calculate_tdh(st.session_state.depth_tvd, st.session_state.whp, st.session_state.pbhp, sg_mix)
            stages = calculations.calculate_stages(tdh, max(1, h_stg))
            
            st.session_state.stages = st.number_input("Stages", value=stages)
            
            st.subheader("Pump Curve from Catalogue")
            fig_pump = plotting.plot_pump_catalog_curve(row, q_intake, st.session_state.stages)
            st.plotly_chart(fig_pump, use_container_width=True)
            
        with col_r:
            st.write("") # Spacer
            st.write("")
            st.write("")
            st.markdown(f"#### Estimated Down Hole Rate: {q_intake:.1f} BFPD")
            
            st.markdown(f"#### Estimated Total Dynamic Head: {tdh:.1f} ft")
            st.info("Evaluate the total dynamic head, check WHP and tubing size if TDH looks unreasonable.", icon=":material/info:")
            
            st.markdown(f"#### Number of stages: {st.session_state.stages} stages")
            st.info("Consider the number of stage, the higher the number the longer the pump.", icon=":material/info:")
            
            hp_pump = calculations.calculate_hp_required(st.session_state.stages, row['HP_per_Stage_at_BEP'], sg_mix)
            st.session_state.req_hp = hp_pump # Store for next steps
            
            st.markdown(f"#### Pump horsepower required: {int(hp_pump)} HP")
            st.info("Power requirement affect electrical equipment on the surface", icon=":material/bolt:")
            
            st.warning("Check the ROR and consider the changes of operating condition. ROR of pump must mitigate all operating condition rate", icon=":material/warning:")
        
        req_hp = calculations.calculate_hp_required(st.session_state.stages, row['HP_per_Stage_at_BEP'], sg_mix)
        st.session_state.req_hp = req_hp
        st.metric("Required HP", f"{req_hp:.1f}")

    # --- TAB 4: PROTECTOR ---
    with tabs[3]:
        st.header("Step 4: Protector")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Chamber Configuration Application Guideline")
            app_df = data.get_protector_applicability()
            st.dataframe(app_df, hide_index=True, use_container_width=True)
            st.caption("(A) Applicability improves with correct elastomers for higher temperature service, usually Aflas.")
            st.caption("(B) Those that deteriorate specific elastomers used.")
            
            st.subheader("Protector Configuration:")
            configs = ["L", "LSL", "LSLSL", "B", "LSB", "LSBPB", "BSL", "BSBSL", "BPBSL", "LSBSB"]
            st.selectbox("Protector Configuration", configs, label_visibility="collapsed")

        with col2:
            st.subheader("Protector Catalog")
            prot_df = data.get_protector_catalog()
            st.dataframe(prot_df, hide_index=True, use_container_width=True)
            
            st.divider()
            # Selection logic
            valid = prot_df[prot_df['Min. Casing Size (in)'] <= st.session_state.casing_id]
            if not valid.empty:
                sel_series = st.selectbox("Select Protector Series", valid['Series'])
                st.session_state.protector_selected = sel_series
                st.success(f"Selected Protector Series: {sel_series}", icon=":material/check_circle:")
            else:
                st.error("No protector matches casing size!", icon=":material/error:")

    # --- TAB 5: MOTOR ---
    with tabs[4]:
        st.header("Step 5: Motor")
        
        # 1. HP Breakdown
        p_row = data.get_pump_catalog()
        p_row = p_row[p_row['Model'] == st.session_state.pump_selected].iloc[0] if st.session_state.pump_selected else None
        
        hp_pump = calculations.calculate_hp_required(st.session_state.stages, p_row['HP_per_Stage_at_BEP'], sg_mix) if p_row is not None else 0.0
        hp_prot = 2.4 # Mock value from image
        hp_sep = 3.0 if "Separator" in gas_res['recommendation'] else 0.0
        hp_agh = 13.0 if "AGH" in gas_res['recommendation'] else 0.0
        
        hp_total = hp_pump + hp_prot + hp_sep + hp_agh
        
        # 2. Motor Selection logic
        hp_extreme = hp_total * 1.24 # ~25% margin
        hp_load_80 = hp_total / 0.8
        hp_target = max(hp_extreme, hp_load_80)
        
        mot_df = data.get_motor_catalog()
        valid_motors = mot_df[mot_df['HP_Rating'] >= hp_target]
        if valid_motors.empty:
            st.warning("Need tandem motor or larger motor!", icon=":material/warning:")
            selected_motor = mot_df.iloc[-1] # Fallback to largest
        else:
            selected_motor = valid_motors.iloc[0]
            
        st.session_state.motor_hp = selected_motor['HP_Rating']
        st.session_state.motor_selected = selected_motor
        
        # 3. Performance at current load
        load_pct = (hp_total / st.session_state.motor_hp) * 100
        perf = calculations.calculate_motor_performance(load_pct)
        
        col_l, col_r = st.columns([2, 1])
        
        with col_l:
            st.markdown(f"**Motor load: {load_pct:.1f}%**")
            st.success("The design is applicable", icon=":material/check_circle:")
            
            fig_mot = plotting.plot_motor_curve(load_pct)
            st.plotly_chart(fig_mot, use_container_width=True)
            
        with col_r:
            st.subheader("Motor")
            st.write(f"AGH HP: {hp_agh:.1f} HP")
            st.write(f"Gas Separator HP: {hp_sep:.1f} HP")
            st.write(f"Pump HP: {hp_pump:.1f} HP")
            st.write(f"Protector HP: {hp_prot:.1f} HP")
            st.markdown(f"**Total HP: {hp_total:.1f} HP**")
            
            st.subheader("Motor HP Calculation")
            st.write(f"ESP required HP at extreme condition: {hp_extreme:.1f} HP")
            st.write(f"Motor HP from operating condition with 80% motor load factor: {hp_load_80:.1f} HP")
            st.write(f"Motor Efficiency: {perf['eff']:.1f}%")
            st.write(f"Motor Operating RPM: {int(perf['rpm'])}")
            
            st.subheader("Cable")
            st.write(f"Operating amperage motor: {perf['amp']:.1f}")
            
            st.divider()
            st.success(f"Selected: {selected_motor['Series']} - {selected_motor['HP_Rating']} HP")

    # --- TAB 6: SIMULATION ---
    with tabs[5]:
        st.header("Step 6: Simulation")
        if st.session_state.pump_selected:
            # Prepare System Curve Data
            pump_df = data.get_pump_catalog()
            row = pump_df[pump_df['Model'] == st.session_state.pump_selected].iloc[0]
            qs_sys = np.linspace(0, row['Max_Rate_BPD'] * 1.2, 50)
            h_sys = [calculations.calculate_system_head(q, st.session_state.depth_tvd, st.session_state.whp, 
                                                       st.session_state.sbhp, st.session_state.pbhp, 
                                                       st.session_state.test_rate, sg_mix) for q in qs_sys]
            
            # Required TDH at target rate
            tdh_req = calculations.calculate_system_head(st.session_state.target_rate, st.session_state.depth_tvd, 
                                                         st.session_state.whp, st.session_state.sbhp, 
                                                         st.session_state.pbhp, st.session_state.test_rate, sg_mix)
            
            fig = render_pump_curve(st.session_state.pump_selected, st.session_state.stages, 60.0, 
                                     op_point=(st.session_state.target_rate, tdh_req),
                                     system_curve=(qs_sys, h_sys))
            st.plotly_chart(fig, use_container_width=True)

    # --- TAB 7: INTEGRITY ---
    with tabs[6]:
        st.header("Step 7: Integrity")
        # Logic roughly same as before
        st.markdown("Burst pressure check: :green-badge[Safe]") # Placeholder for demo flow
        st.markdown("Cooling velocity check: :green-badge[> 1 ft/s]")

    # --- TAB 8: REPORT ---
    with tabs[7]:
        st.header("Step 8: Final report")
        res = {
            "Well": st.session_state.well_name,
            "Pump": st.session_state.pump_selected,
            "Stages": st.session_state.stages,
            "Motor": f"{st.session_state.motor_hp} HP"
        }
        st.table(pd.DataFrame(res, index=[0]))


# ==========================================
# MODULE: MONITORING
# ==========================================
elif nav == "Monitoring":
    st.title(":material/monitoring: Operations monitoring")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Daily input")
        st.session_state.mon_date = st.date_input("Date", st.session_state.mon_date)
        st.session_state.mon_freq = st.number_input("Frequency (Hz)", value=st.session_state.mon_freq)
        st.session_state.mon_whp = st.number_input("WHP (psi)", value=st.session_state.mon_whp)
        st.session_state.mon_rate = st.number_input("Liquid rate (BPD)", value=st.session_state.mon_rate)
        st.session_state.mon_amps = st.number_input("Motor amps", value=st.session_state.mon_amps)
        
        if st.button("Save record", icon=":material/save:"):
            st.success("Record saved locally (demo only).", icon=":material/check_circle:")

    with col2:
        st.subheader("Performance tracking")
        if not st.session_state.pump_selected:
            st.warning("Please select a pump in Design module first.", icon=":material/warning:")
        else:
            # Calculate TDH Actual (Head)
            # PIP is needed. Use IPR or input? Let's use IPR invert from rate
            # PI = TestQ / (Ps - Pwf)
            denom = (st.session_state.sbhp - st.session_state.pbhp)
            pi = st.session_state.test_rate / denom if denom > 0 else 1.0
            
            pip_actual = st.session_state.sbhp - (st.session_state.mon_rate / pi)
            tdh_actual = calculations.calculate_tdh(st.session_state.depth_tvd, st.session_state.mon_whp, pip_actual, sg_mix)
            
            st.metric("Calculated intake P", f"{pip_actual:.0f} psi")
            st.metric("Actual TDH", f"{tdh_actual:.0f} ft")
            
            fig = render_pump_curve(
                st.session_state.pump_selected, 
                st.session_state.stages, 
                st.session_state.mon_freq, 
                op_point=(st.session_state.mon_rate, tdh_actual)
            )
            st.plotly_chart(fig, use_container_width=True)


# ==========================================
# MODULE: OPTIMIZING
# ==========================================
elif nav == "Optimizing":
    st.title(":material/rocket_launch: Optimization")
    st.write("Tools to adjust Freq/Choke to match the optimizing operating point")
    
    if not st.session_state.pump_selected:
        st.warning("Please design first.", icon=":material/warning:")
    else:
        c1, c2 = st.columns([1, 2])
        with c1:
            opt_freq = st.slider("Frequency (Hz)", 30.0, 70.0, 60.0)
            opt_whp = st.slider("Choke Control (WHP psi)", 50.0, 1000.0, st.session_state.whp)
        
        with c2:
            # Solve Operating Point
            # Need Intersection of Pump(Freq) and System(WHP)
            
            # 1. Pump Curve @ Freq
            pump_df = data.get_pump_catalog()
            row = pump_df[pump_df['Model'] == st.session_state.pump_selected].iloc[0]
            
            ratio = opt_freq / 60.0
            
            # Simple Intersection Finder
            qs = np.linspace(100, row['Max_Rate_BPD']*1.5, 100)
            
            # Pump Head
            q_ref = qs / ratio
            h_pump = (row['Head_Coeff_A'] + row['Head_Coeff_B']*q_ref + row['Head_Coeff_C']*q_ref**2) * (ratio**2) * st.session_state.stages
            
            # System Head
            h_sys = np.array([calculations.calculate_system_head(q, st.session_state.depth_tvd, opt_whp, 
                                                                st.session_state.sbhp, st.session_state.pbhp, 
                                                                st.session_state.test_rate, sg_mix) for q in qs])
            
            # Find Cross
            idx = np.abs(h_pump - h_sys).argmin()
            op_q = qs[idx]
            op_h = h_pump[idx]
            
            st.metric("Predicted rate", f"{op_q:.0f} BPD")
            
            # Plot
            fig = render_pump_curve(st.session_state.pump_selected, st.session_state.stages, opt_freq, 
                                     op_point=(op_q, op_h), system_curve=(qs, h_sys))
            st.plotly_chart(fig, use_container_width=True)


# ==========================================
# MODULE: ABOUT
# ==========================================
elif nav == "About":
    st.title(":material/info: About ESP engineer assistant")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(":material/design_services: ESP design")
        st.write("""
        Input well & fluid data, check gas handling, 
        select pump & motor, and verify integrity.
        """)
        
        st.subheader(":material/monitoring: Monitoring")
        st.write("""
        Input daily gauge readings and visualize 
        the operating point against the pump curve.
        """)
    
    with col2:
        st.subheader(":material/trending_up: Optimizing")
        st.write("""
        Adjust frequency and choke (WHP) to see 
        predicted rates and pump compliance.
        """)
        
        st.subheader(":material/person: Author")
        st.write("**Le Vu**")
        st.caption("Version 1.2.0 | Stable")
    
    st.write("")
    with st.expander(":material/help: How to get started"):
        st.markdown("""
        1. Start with the **ESP design** module for a new installation.
        2. Use **Monitoring** for existing wells in production.
        3. Use **Optimizing** for frequency sensitivity analysis.
        """)
