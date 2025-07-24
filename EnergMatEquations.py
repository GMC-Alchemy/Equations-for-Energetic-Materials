"""
Energy Materials Calculator

by Gabriel Monteiro de Castro.

Description:
This script provides a graphical calculator for estimating key properties of energetic materials, such as detonation velocity, detonation pressure, impact sensitivity, density, and heat of sublimation. It uses empirical equations sourced from scientific literature and allows users to solve for any variable given the others.

Purpose:
Developed as a personal project to support research, teaching, and experimentation in the field of energetic materials chemistry and physics.

Features:
- Interactive GUI built with Tkinter.
- Dynamic rendering of chemical equations using LaTeX and Matplotlib.
- Symbolic computation and equation solving via SymPy.
- Support for multiple empirical models including Kamlet-Jacobs, Pepekin-Lebedev, and Smirnov-Smirnov equations.
"""

import os
import sympy as sp
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Define colors used consistently across the GUI.
BG_COLOR = '#4B5320'     # army/olive green.
FG_COLOR = '#FFD700'     # gold.

# Define fonts for various UI elements.
title_font = ("Courier New", 18, "bold")
entry_font = ("Courier New", 14)
button_font = ("Courier New", 14, "bold")
output_font = ("Courier New", 18, "bold")

# Define equations and associated metadata.
equations = {
    "Friction Sensitivity (FS)": {
        "latex": r"FS = 600.8 - 2428.6 \frac{n_H}{M_w} - 6481.4 \frac{n_N}{M_w} - 9560.9 \frac{n_O}{M_w} + 54.5 P^{+} - 77.8 P^{-}",
        "expr": "600.8 - 2428.6 * (nH/Mw) - 6481.4 * (nN/Mw) - 9560.9 * (nO/Mw) + 54.5 * Pp - 77.8 * Pn",
        "variables": ['FS', 'nH', 'nN', 'nO', 'Mw', 'Pp', 'Pn'],
        "units": {'FS': 'N',
            'nH': '',
            'nN': '',
            'nO': '',
            'Mw': 'g/mol',
            'Pp': '',
            'Pn': ''}
    },
    "Density (ρ)": {
        "latex": r"\rho = 0.9183[\frac{M}{V(0.001)}] + 0.0028 \nu\sigma_{tot}^{2} + 0.0443",
        "expr": "0.9183 * M / V001 + 0.0028 * νσtot2 + 0.0443",
        "variables": ['ρ', 'M', 'V001', 'νσtot2'],
        "units": {'ρ': 'g/cm³',
            'M': 'g/mol',
            'V001': 'cm³/mol',
            'νσtot2': 'kcal²/mol²'}
    },
    "Detonation Pressure at Chapman-Jouguet point (PCJ) - Kamlet Jacobs (KJ) equation": {
        "latex": r"P_{CJ}^{KJ} = 1.558 \rho^{2} N \sqrt{M} \sqrt{Q_{max}}",
        "expr": "1.558 * ρ**2 * N * sqrt(M) * sqrt(Qmax)",
        "variables": ['P', 'ρ', 'N', 'M', 'Qmax'],
        "units": {'P': 'GPa',
            'ρ': 'g/cm³',
            'N': 'mol/g',
            'M': 'g/mol',
            'Qmax': 'kcal/kg'}
    },
    "Detonation Pressure at Chapman-Jouguet point (PCJ) - Pepekin-Lebedev (PL) equation": {
        "latex": r"P_{CJ}^{PL} = 4.0 + 7.5 n_{eff} Q_{cal}^{0.5} ρ^{2}",
        "expr": "4.0 + 7.5 * neff * sqrt(Qcal) * ρ**2",
        "variables": ['P', 'neff', 'Qcal', 'ρ'],
        "units": {'P': 'GPa',
            'neff': '',
            'Qcal': 'kcal/kg',
            'ρ': 'g/cm³'}
    },
    "Detonation Pressure at Chapman-Jouguet point (PCJ) - Smirnov-Smirnov (SS) equation": {
        "latex": r"P_{CJ}^{SS} = 0.034 ρ^{2.022} a^{-0.0111} b^{0.00536} c^{0.149} Q_{max}^{0.589} N_{g}^{0.26}",
        "expr": "0.034 * ρ**2.022 * a**(-0.0111) * b**0.00536 * c**0.149 * Qmax**0.589 * Ng**0.26",
        "variables": ['P', 'ρ', 'a', 'b', 'c', 'Qmax', 'Ng'],
        "units": {'P': 'GPa',
            'ρ': 'g/cm³',
            'a': '',
            'b': '',
            'c': '',
            'Qmax': 'kcal/kg',
            'Ng': 'mol/kg'}
    },
    "Impact sensitivity (h50) - CHNO compounds": {
        "latex": r"h_{50} = -234.83 [V_{eff} - V(0.002)]^{\frac{1}{3}} - 3.197 \nu\sigma_{tot}^{2} + 962",
        "expr": "-234.83 * (Veff-V002)**(1./3.) - 3.197 * νσtot2 + 962",
        "variables": ['h50', 'Veff', 'V002', 'νσtot2'],
        "units": {'h50': 'cm',
            'Veff': 'cm³/mol',
            'V002': 'cm³/mol',
            'νσtot2': 'kcal²/mol²'}
    },
    "Impact sensitivity (h50) - Nitramines": {
        "latex": r"h_{50} = -0.0064 \sigma_{+}^{2} + 241.42 \nu - 3.43",
        "expr": "-0.0064 * σ_p2 + 241.42 * ν - 3.43",
        "variables": ['h50', 'σ_p2', 'ν'],
        "units": {'h50': 'cm',
            'σ_p2': 'kcal²/mol²',
            'ν': ''}
    },
    "Detonation velocity (D) - Kamlet Jacobs (KJ) equation": {
        "latex": r"D^{KJ} = 1.01 N^{0.5} M^{0.25} Q_{max}^{0.25} (1 + 1.3 \rho)",
        "expr": "1.01 * sqrt(N) * M**0.25 * Qmax**0.25 * (1+1.3*ρ)",
        "variables": ['D', 'N', 'M', 'Qmax', 'ρ'],
        "units": {'D': 'km/s',
            'N': 'mol/g',
            'M': 'g/mol',
            'Qmax': 'kcal/kg',
            'ρ': 'g/cm³'}
    },
    "Detonation velocity (D) - Pepekin-Lebedev (PL) equation": {
        "latex": r"D^{PL} = 4.2 + 2.0 n_{eff} Q_{cal}^{0.5} \rho",
        "expr": "4.2 + 2.0 * neff * sqrt(Qcal) * ρ",
        "variables": ['D', 'neff', 'Qcal', 'ρ'],
        "units": {'D': 'km/s',
            'neff': '',
            'Qcal': 'kcal/kg',
            'ρ': 'g/cm³'}
    },
    "Detonation velocity (D) - Smirnov-Smirnov (SS) equation": {
        "latex": r"D^{SS} = 0.481 \rho^{0.607} c^{0.089} d^{0.066} Q_{cal}^{0.221} N_{g}^{0.19}",
        "expr": "0.481 * ρ**0.607 * c**0.089 * d**0.066 * Qcal**0.221 * Ng**0.19",
        "variables": ['D', 'ρ', 'c', 'd', 'Qcal', 'Ng'],
        "units": {'D': 'km/s',
            'ρ': 'g/cm³',
            'c': '',
            'd': '',
            'Qcal': 'kcal/kg',
            'Ng': 'mol/kg'}
    },
    "Heat of sublimation (∆Hsub)": {
        "latex": r"\Delta H_{sub} = 0.000267 A^{2} + 1.650087 \sqrt{\nu\sigma_{tot}^{2}} + 2.966078",
        "expr": "0.000267 * A**2 + 1.650087 * sqrt(νσtot2) + 2.966078",
        "variables": ['ΔHsub', 'A', 'νσtot2'],
        "units": {'ΔHsub': 'kcal/mol',
            'A': 'Å²',
            'νσtot2': 'kcal²/mol²'}
    }
}

# Map variable names to prettier Unicode display names for better GUI readability.
var_display = {'νσtot2': 'νσₜₒₜ²',
    'Veff': 'Veff',
    'V001': 'V(0.001)',
    'V002': 'V(0.002)',
    'σ_p2': 'σ₊²',
    'ρ': 'ρ',
    'Qmax': 'Qmax',
    'Qcal': 'Qcal',
    'ΔHsub': 'ΔHsub',
    'h50': 'h₅₀',
    'neff': 'neff',
    'Ng': 'Ng',
    'M': 'M',
    'N': 'N',
    'A': 'A',
    'c': 'c',
    'd': 'd',
    'P': 'P',
    'D': 'D',
    'Pp': 'P⁺',
    'Pn': 'P⁻',
    'nH': 'nH',
    'nN': 'nN',
    'nO': 'nO'}

# Reverse mapping to go back from pretty name to variable name.
pretty_to_var = {v: k for k, v in var_display.items()}

# Render equation as LaTeX image using matplotlib.
def render_equation(latex_str):
    
    # Create figure sized to show equation clearly.
    plt.figure(figsize=(10, 1.5))   # Wider figure. Adjust height to avoid squeeze.
    plt.text(0.5,
        0.5,
        f"${latex_str}$",
        fontsize=24,
        ha='center',
        va='center',
        fontname='Courier New',     # Ensure this is installed.
        color=FG_COLOR)
    plt.axis('off')                 # Hide axes to display only the equation.
    plt.tight_layout(pad=0.5)       # Reduce padding for compactness.
    
    # Create temp folder if it doesn't exist to store the image.
    if not os.path.exists('temp'):
        os.makedirs('temp')
    filepath = os.path.join('temp', 'equation.png')
    plt.savefig(filepath,
        dpi=300,
        transparent=True,
        bbox_inches='tight')
    plt.close()
    
    return filepath

# Callback when an equation is selected from the combobox.
def on_equation_selected(event=None):
    
    # Get selected equation name.
    eq_name = eq_choice.get()
    eq_info = equations[eq_name]
    latex_str = eq_info['latex']
    vars_list = eq_info['variables']
    
    # Create list of prettier variable names for display.
    pretty_vars_list = [var_display.get(v, v) for v in vars_list]
    var_choice['values'] = pretty_vars_list
    var_choice.set('')

    # Render and display the equation image.
    img_path = render_equation(latex_str)
    img = Image.open(img_path)
    max_width = 600                             # Resize to fit GUI.
    aspect_ratio = img.height / img.width
    new_height = int(max_width * aspect_ratio)
    img = img.resize((max_width, new_height), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    eq_label.config(image=img_tk)
    eq_label.image = img_tk                     # Keep reference to avoid garbage collection.
    
    # Clear any previous input fields and output.
    for widget in input_frame.winfo_children():
        widget.destroy()
        
    output_label.config(text="")

# Callback when a target variable is selected.
def on_variable_selected(event=None):
    
    eq_name = eq_choice.get()
    
    selected_pretty = var_choice.get()
    target_var = pretty_to_var.get(selected_pretty, selected_pretty)
    
    eq_info = equations[eq_name]
    vars_list = eq_info['variables']
    units_dict = eq_info.get('units', {})

    # Clear previous input fields.
    for widget in input_frame.winfo_children():
        widget.destroy()

    global input_entries
    input_entries = {}

    # Create entry fields for all variables except the one we want to calculate.
    for var in vars_list:
        if var != target_var:
            var_frame = tk.Frame(input_frame, bg=BG_COLOR)
            var_frame.pack(pady=2, fill='x')

            pretty_var = var_display.get(var, var)
            lbl = tk.Label(var_frame,
                text=f"{pretty_var}:",
                bg=BG_COLOR,
                fg=FG_COLOR,
                font=entry_font,
                anchor='e',
                width=10)
            lbl.pack(side=tk.LEFT, padx=5)

            ent = tk.Entry(var_frame,
                font=entry_font,
                width=15)
            ent.pack(side=tk.LEFT, padx=5)

            unit_lbl = tk.Label(var_frame,
                text=units_dict.get(var, ''),
                bg=BG_COLOR,
                fg=FG_COLOR,
                font=entry_font)
            unit_lbl.pack(side=tk.LEFT, padx=5)

            input_entries[var] = ent

# Perform calculation based on user inputs.
def calculate():
    
    eq_name = eq_choice.get()
    
    selected_pretty = var_choice.get()
    target_var = pretty_to_var.get(selected_pretty, selected_pretty)
    
    eq_str = equations[eq_name]['expr']
    vars_list = equations[eq_name]['variables']
    eq_info = equations[eq_name]
    units_dict = eq_info.get('units', {})
    unit = units_dict.get(target_var, '')

    # Define symbols for sympy to parse.
    symbols = {v: sp.Symbol(v) for v in vars_list}
    expr = sp.sympify(eq_str, locals=symbols)
    
    # Solve for the target variable.
    sol = sp.solve(sp.Eq(symbols[vars_list[0]], expr), symbols[target_var])
    if not sol:
        messagebox.showerror("Error", "Cannot solve for selected variable.")
        return
    solution = sol[0]
    
    # Collect user inputs and substitute into the solution.
    subs = {}
    for var, ent in input_entries.items():
        val = ent.get()
        try:
            subs[var] = float(val)
        except:
            messagebox.showerror("Input Error", f"Invalid number for {var}")
            return
            
    # Evaluate the expression and display the result.
    try:
        result = solution.evalf(subs=subs)
        pretty_target = var_display.get(target_var, target_var)
        output_label.config(text=f"{pretty_target} = {result:.4f} {unit}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI initialization.
root = tk.Tk()
root.title("GMC - Energetic Materials Calculator")
root.geometry("1500x600")
root.configure(bg=BG_COLOR)

# Software title.
title = tk.Label(root,
    text="Energetic Materials Calculator",
    font=title_font,
    bg=BG_COLOR,
    fg=FG_COLOR)
title.pack(pady=10)

# Frame containing dropdowns for equation and variable selection.
choice_frame = tk.Frame(root, bg=BG_COLOR)
choice_frame.pack(pady=5)

# Equation selection label and combobox.
eq_label_text = tk.Label(choice_frame,
    text="Equation:",
    bg=BG_COLOR,
    fg=FG_COLOR,
    font=entry_font)
eq_label_text.grid(row=0, column=0, padx=5)

# Dynamically size based on longest text.
longest_eq = max(equations.keys(), key=len)
eq_choice = ttk.Combobox(choice_frame,
    values=list(equations.keys()),
    font=entry_font,
    width=len(longest_eq)+5)
eq_choice.grid(row=0, column=1, padx=5)
eq_choice.bind("<<ComboboxSelected>>", on_equation_selected)

# Variable selection label and combobox.
var_label_text = tk.Label(choice_frame,
    text="Variable:",
    bg=BG_COLOR,
    fg=FG_COLOR,
    font=entry_font)
var_label_text.grid(row=0, column=2, padx=5)

var_choice = ttk.Combobox(choice_frame,
    font=entry_font,
    width=15)
var_choice.grid(row=0, column=3, padx=5)
var_choice.bind("<<ComboboxSelected>>", on_variable_selected)

# Label for displaying rendered equation image.
eq_label = tk.Label(root, bg=BG_COLOR)
eq_label.pack(pady=10)

# Frame for dynamic input fields.
input_frame = tk.Frame(root, bg=BG_COLOR)
input_frame.pack(pady=10)

# Calculate button.
calc_btn = tk.Button(root,
    text="Calculate",
    command=calculate,
    bg=BG_COLOR,
    fg=FG_COLOR,
    font=button_font)
calc_btn.pack(pady=5)

# Label to show output/result.
output_label = tk.Label(root,
    text="",
    font=output_font,
    bg=BG_COLOR,
    fg=FG_COLOR)
output_label.pack(pady=10)

# Start the GUI event loop.
root.mainloop()
