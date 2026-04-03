import plotly.graph_objects as go
import numpy as np

def plot_combined_curves(pump_name, q_min, q_max, head_coeffs, stages, design_rate, tdh, design_hp):
    """
    Plot Pump Head Curve vs System Head Curve (Reference).
    """
    # Flow rates
    q = np.linspace(q_min * 0.5, q_max * 1.2, 100)
    
    # Pump Head (Head/stg * stages)
    h_stg = head_coeffs['A'] + head_coeffs['B']*q + head_coeffs['C']*q**2
    h_total = h_stg * stages
    
    fig = go.Figure()
    
    # Pump Curve
    fig.add_trace(go.Scatter(x=q, y=h_total, mode='lines', name=f'{pump_name} Performance', line=dict(color='blue')))
    
    # Operating Point
    fig.add_trace(go.Scatter(x=[design_rate], y=[tdh], mode='markers', name='Operating Point', 
                             marker=dict(color='red', size=12, symbol='star')))
    
    fig.update_layout(
        title=f"Pump Performance Curve: {pump_name} ({stages} stg)",
        xaxis_title="Flow Rate (BPD)",
        yaxis_title="Head (ft)",
        hovermode="x unified"
    )
    

def plot_ipr_curve(sbhp, pbhp, test_rate, mode='linear'):
    """
    Generate IPR Curve (Pwf vs Rate).
    mode: 'linear' or 'vogel'
    """
    fig = go.Figure()
    
    # Calculate AOFP
    # Linear: J = q / (Ps - Pwf) => q = J(Ps - Pwf) => At Pwf=0, q_max = J*Ps
    # Vogel: q/q_max = 1 - 0.2(Pwf/Ps) - 0.8(Pwf/Ps)^2
    
    if sbhp <= pbhp: # Invalid data check
        return fig
        
    if mode == 'linear':
        denom = (sbhp - pbhp)
        if denom == 0: denom = 0.001
        pi = test_rate / denom
        aofp = pi * sbhp
        
        # Points
        p_vals = np.linspace(0, sbhp, 50)
        q_vals = pi * (sbhp - p_vals)
        
    else: # Vogel
        # Calc q_max (AOFP) first
        # q_test / q_max = 1 - 0.2(p/p_s) - 0.8(p/p_s)^2
        ratio_p = pbhp / sbhp
        vogel_factor = 1.0 - 0.2*(ratio_p) - 0.8*(ratio_p**2)
        if vogel_factor == 0: vogel_factor = 0.001
        aofp = test_rate / vogel_factor
        
        p_vals = np.linspace(0, sbhp, 50)
        q_vals = aofp * (1.0 - 0.2*(p_vals/sbhp) - 0.8*((p_vals/sbhp)**2))
        pi = aofp / sbhp * 1.8 # Rough proxy for PI at Ps (derivative)
    
    fig.add_trace(go.Scatter(x=q_vals, y=p_vals, mode='lines', name='IPR', line=dict(color='blue')))
    
    # Test Point
    fig.add_trace(go.Scatter(x=[test_rate], y=[pbhp], mode='markers', name='Test Point', 
                             marker=dict(color='red', size=10)))
                             
    fig.update_layout(
        title="IPR Plot",
        xaxis_title="Rate (STB/d)",
        yaxis_title="Pwf (psia)",
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    
    return fig, pi

def plot_gas_handling_chart(intake_rate, intake_free_gas):
    """
    Plot BFPD vs Free Gas Scatter Plot with lines for 3%, 5%, 10%, 20% free gas.
    """
    qs = np.linspace(0, 4500, 100)
    
    # Simple lines for gas handling limits (mock)
    fig = go.Figure()
    
    # 3% limit line
    fig.add_trace(go.Scatter(x=qs, y=100*np.exp(-0.0006 * qs), name='3% free gas', line=dict(color='#0077b6')))
    # 5%
    fig.add_trace(go.Scatter(x=qs, y=100*np.exp(-0.0004 * qs), name='5% free gas', line=dict(color='#f3722c')))
    # 10%
    fig.add_trace(go.Scatter(x=qs, y=100*np.exp(-0.00025 * qs), name='10% free gas', line=dict(color='#43aa8b')))
    # 20%
    fig.add_trace(go.Scatter(x=qs, y=100*np.exp(-0.00018 * qs), name='20% free gas', line=dict(color='#d90429')))
    
    # Operating Point
    fig.add_trace(go.Scatter(x=[intake_rate], y=[intake_free_gas], mode='markers', name='Actual Intake',
                             marker=dict(color='black', size=14, symbol='star')))
    
    # Intersection lines
    fig.add_shape(type="line", x0=intake_rate, y0=0, x1=intake_rate, y1=intake_free_gas,
                  line=dict(color="grey", width=1, dash="dash"))
    fig.add_shape(type="line", x0=0, y0=intake_free_gas, x1=intake_rate, y1=intake_free_gas,
                  line=dict(color="grey", width=1, dash="dash"))

    fig.update_layout(
        title=dict(text="BFPD vs Free Gas Scatter Plot", font=dict(size=18, color='#003049')),
        xaxis_title="BFPD (at intake)",
        yaxis_title="Free Gas (%)",
        xaxis=dict(range=[0, 4500], gridcolor='#e5e5e5'),
        yaxis=dict(range=[0, 105], gridcolor='#e5e5e5'),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_motor_curve(current_load_pct):
    """
    Plot triple-axis motor curve: RPM, Amperage, and Efficiency vs Load %.
    """
    loads = np.linspace(50, 100, 50)
    # Mock data consistent with calculations.py
    rpms = 3565 - (loads * 1.0)
    amps = 20 + (loads * 0.8)
    effs = 85 + 4 * (1 - ((loads - 80)/40)**2)
    
    fig = go.Figure()
    
    # RPM (Primary Y)
    fig.add_trace(go.Scatter(x=loads, y=rpms, name='RPM', line=dict(color='#0077b6', width=2), yaxis='y'))
    
    # Amperage (Secondary Y)
    fig.add_trace(go.Scatter(x=loads, y=amps, name='Amperage', line=dict(color='#d90429', width=2), yaxis='y2'))
    
    # Efficiency (Tertiary Y)
    fig.add_trace(go.Scatter(x=loads, y=effs, name='Efficiency', line=dict(color='#43aa8b', width=2), yaxis='y3'))
    
    # Vertical indicator at current load
    fig.add_vline(x=current_load_pct, line_width=3, line_dash="dash", line_color="#7209b7")
    fig.add_annotation(x=current_load_pct, y=3560, text=f"{current_load_pct:.1f}%", showarrow=False, yshift=10)
    
    fig.update_layout(
        title=dict(text="Motor Curve from Catalogue", font=dict(size=20, color='#003049')),
        xaxis=dict(title=dict(text="Motor load (%)"), range=[50, 100], gridcolor='#e5e5e5'),
        yaxis=dict(
            title=dict(text="RPM", font=dict(color="#0077b6")), 
            tickfont=dict(color="#0077b6"), 
            gridcolor='#e5e5e5'
        ),
        yaxis2=dict(
            title=dict(text="Amperage (A)", font=dict(color="#d90429")), 
            tickfont=dict(color="#d90429"), 
            overlaying='y', 
            side='right', 
            showgrid=False
        ),
        yaxis3=dict(
            title=dict(text="Efficiency (%)", font=dict(color="#43aa8b")), 
            tickfont=dict(color="#43aa8b"), 
            overlaying='y', 
            side='right', 
            anchor='free', 
            position=1.0, # Shifted to 1.0 to see if 1.1 was the issue
            showgrid=False
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=50, r=50, t=60, b=80),
        plot_bgcolor='white',
        hovermode="x unified"
    )
    return fig

def plot_pump_catalog_curve(row, design_rate, stages):
    """
    Detailed Pump Catalog Curve: Head, Power, Efficiency vs Rate.
    Incl. BEP, Target Rate, Min ROR, Max ROR markers.
    """
    q_max = row['Max_Rate_BPD']
    q_min = row['Min_Rate_BPD']
    bep = row['BEP_Rate_BPD']
    
    q_vals = np.linspace(0, q_max * 1.3, 100)
    
    # Head (ft)
    h_stg = row['Head_Coeff_A'] + row['Head_Coeff_B']*q_vals + row['Head_Coeff_C']*q_vals**2
    h_total = h_stg * stages
    
    # Efficiency (fraction) - Mock bell curve
    eff_vals = 0.75 * np.exp(-0.5 * ((q_vals - bep) / (0.5 * bep))**2)
    
    # Power (HP) - Mock increasing curve anchored at BEP HP
    pwr_vals = (row['HP_per_Stage_at_BEP'] * stages) * (0.6 + 0.4 * (q_vals / bep))
    
    fig = go.Figure()
    
    # Head (Primary Y)
    fig.add_trace(go.Scatter(x=q_vals, y=h_total, name='Head', line=dict(color='#0077b6', width=3), yaxis='y'))
    
    # Power (Secondary Y)
    fig.add_trace(go.Scatter(x=q_vals, y=pwr_vals, name='Power', line=dict(color='#d90429', width=2), yaxis='y2'))
    
    # Efficiency (Tertiary Y)
    fig.add_trace(go.Scatter(x=q_vals, y=eff_vals, name='Efficiency', line=dict(color='#43aa8b', width=2), yaxis='y3'))
    
    # Markers
    markers = [
        {'q': bep, 'name': 'BEP', 'color': 'magenta'},
        {'q': design_rate, 'name': 'Target Rate', 'color': 'cyan'},
        {'q': q_min, 'name': 'Min ROR', 'color': '#fb8b24'},
        {'q': q_max, 'name': 'Max ROR', 'color': '#fb8b24'}
    ]
    
    for m in markers:
        fig.add_vline(x=m['q'], line_width=2, line_dash="dash", line_color=m['color'])
        fig.add_annotation(x=m['q'], y=max(h_total)*0.9, text=m['name'], textangle=-90, 
                           showarrow=False, font=dict(color=m['color']))

    fig.update_layout(
        title=dict(text=f"{row['Model']} Pump Curve @ 60 Hz 3500 RPM", font=dict(size=20, color='#003049')),
        xaxis=dict(title=dict(text="Rate (BPD)"), gridcolor='#e5e5e5'),
        yaxis=dict(
            title=dict(text="Head (ft)", font=dict(color="#0077b6")), 
            tickfont=dict(color="#0077b6"), 
            gridcolor='#e5e5e5'
        ),
        yaxis2=dict(
            title=dict(text="Power (HP)", font=dict(color="#d90429")), 
            tickfont=dict(color="#d90429"), 
            overlaying='y', 
            side='right', 
            showgrid=False
        ),
        yaxis3=dict(
            title=dict(text="Efficiency", font=dict(color="#43aa8b")), 
            tickfont=dict(color="#43aa8b"), 
            overlaying='y', 
            side='right', 
            anchor='free', 
            position=1.0, 
            showgrid=False
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=50, r=50, t=60, b=80),
        plot_bgcolor='white',
        hovermode="x unified"
    )
    return fig
