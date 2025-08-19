"""
    ENERGY MATERIALS CALCULATOR

by Gabriel Monteiro de Castro, Ph.D.

Description:
This script provides a graphical calculator for estimating key properties of energetic materials, such as detonation velocity, detonation pressure, impact sensitivity, density, and heat of sublimation. It uses empirical equations sourced from scientific literature and allows users to solve for any variable given the others.

Purpose:
Developed as a personal project to support research, teaching, and experimentation in the field of energetic materials chemistry and physics.
"""

import os
import json
import sympy as sp
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# TOOLTIP CLASS.
class ToolTip:
    # Tooltip initialization.
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    # Show tooltip.
    def show_tip(self, _):
        if self.tipwindow or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + cy + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.geometry(f"+{x}+{y}")
        label = tk.Label(tw,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("tahoma", 10, "normal"))
        label.pack(ipadx=5, ipady=5)

    def hide_tip(self, _):
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None

# MAIN CLASS.
class EnergeticMaterialsCalculator:
    # GUI initialization.
    def __init__(self, master, equations):
        self.master = master
        self.equations = equations
        self.bg_color = '#4B5320'
        self.fg_color = '#FFD700'
        self.title_font = ("Courier New", 18, "bold")
        self.entry_font = ("Courier New", 14)
        self.button_font = ("Courier New", 14, "bold")
        self.output_font = ("Courier New", 18, "bold")

        self.eq_choice = None
        self.var_choice = None
        self.input_entries = {}
        self.result_text = ""

        self.master.title("GMC - Energetic Materials Calculator")
        self.master.geometry("1500x900")
        self.master.configure(bg=self.bg_color)

        self.build_gui()

    def build_gui(self):
        # Software title.
        title = tk.Label(self.master,
            text="Energetic Materials Calculator",
            font=self.title_font,
            bg=self.bg_color,
            fg=self.fg_color)
        title.pack(pady=10)

        choice_frame = tk.Frame(self.master, bg=self.bg_color)
        choice_frame.pack(pady=5)

        # Equation selection label and combobox.
        tk.Label(choice_frame,
            text="Equation:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.entry_font).grid(row=0, column=0, padx=5)

        self.eq_choice = ttk.Combobox(choice_frame, values=list(self.equations.keys()), font=self.entry_font, width=80)
        self.eq_choice.grid(row=0, column=1, padx=5)
        self.eq_choice.bind("<<ComboboxSelected>>", self.on_equation_selected)

        # Variable selection label and combobox.
        tk.Label(choice_frame,
            text="Variable:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.entry_font).grid(row=0, column=2, padx=5)

        self.var_choice = ttk.Combobox(choice_frame, font=self.entry_font, width=15)
        self.var_choice.grid(row=0, column=3, padx=5)
        self.var_choice.bind("<<ComboboxSelected>>", self.on_variable_selected)

        # Frame for equations side-by-side.
        eq_frame = tk.Frame(self.master, bg=self.bg_color)
        eq_frame.pack(pady=10)

        self.eq_label = tk.Label(eq_frame, bg=self.bg_color)
        self.eq_label.pack(side=tk.LEFT, padx=20)

        self.solved_label = tk.Label(eq_frame, bg=self.bg_color)
        self.solved_label.pack(side=tk.LEFT, padx=20)

        self.source_label = tk.Label(self.master,
            text="",
            font=("Courier New", 12, "italic"),
            wraplength=1400,
            bg=self.bg_color,
            fg=self.fg_color,
            justify="center")
        self.source_label.pack(pady=5)

        self.input_frame = tk.Frame(self.master, bg=self.bg_color)
        self.input_frame.pack(pady=10)

        # "Calculate" button.
        self.calc_btn = tk.Button(self.master,
            text="Calculate",
            command=self.calculate,
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.button_font)
        self.calc_btn.pack(pady=5)
        self.master.bind("<Return>", lambda e: self.calculate())

        # Label to show output/result.
        self.output_label = tk.Label(self.master,
            text="",
            font=self.output_font,
            bg=self.bg_color,
            fg=self.fg_color)
        self.output_label.pack(pady=10)

        # "Copy Result to Clipboard" button.
        self.copy_btn = tk.Button(self.master,
            text="Copy Result to Clipboard",
            command=self.copy_to_clipboard,
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.button_font)
        self.copy_btn.pack(pady=5)

    # Render equation as LaTeX image using matplotlib.pyplot (plt).
    def render_equation(self, latex_str, filename):
        plt.figure(figsize=(6, 1.5))
        plt.text(0.5,
            0.5,
            f"${latex_str}$",
            fontsize=20,
            ha='center',
            va='center',
            fontname='Courier New',
            color=self.fg_color)
        plt.axis('off')
        plt.tight_layout(pad=0.5)
        
        # Create temp folder if it doesn't exist to store the image.
        if not os.path.exists('temp'):
            os.makedirs('temp')
        filepath = os.path.join('temp', filename)
        plt.savefig(filepath, dpi=300, transparent=True, bbox_inches='tight')
        plt.close()
        return filepath

    # Callback when an equation is selected from the combobox.
    def on_equation_selected(self, event=None):
        # Get selected equation name.
        eq_name = self.eq_choice.get()
        eq_info = self.equations[eq_name]
        self.var_choice['values'] = eq_info['variables']
        self.var_choice.set("")

        img_path = self.render_equation(eq_info['latex'], 'equation.png')
        img = self.load_image(img_path)
        self.eq_label.config(image=img)
        self.eq_label.image = img

        self.solved_label.config(image="")  # Clear solved form until calculated.
        self.source_label.config(text=f"Source: {eq_info.get('source', '')}")

        for widget in self.input_frame.winfo_children():
            widget.destroy()
        self.output_label.config(text="")

    # Render and display the equation image.
    def load_image(self, path):
        img = Image.open(path)
        max_width = 600 # Resize to fit GUI.
        aspect_ratio = img.height / img.width
        new_height = int(max_width * aspect_ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    # Callback when a target variable is selected.
    def on_variable_selected(self, event=None):
        eq_name = self.eq_choice.get()
        eq_info = self.equations[eq_name]
        target_var = self.var_choice.get()

        # Clear previous input fields.
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        self.input_entries.clear()

        # Create entry fields for all variables except the one we want to calculate.
        for var in eq_info['variables']:
            if var != target_var:
                var_frame = tk.Frame(self.input_frame, bg=self.bg_color)
                var_frame.pack(pady=2, fill='x')

                lbl = tk.Label(var_frame,
                    text=f"{var}:",
                    bg=self.bg_color,
                    fg=self.fg_color,
                    font=self.entry_font,
                    anchor='e',
                    width=10)
                lbl.pack(side=tk.LEFT, padx=5)
                if 'tooltip' in eq_info and var in eq_info['tooltip']:
                    ToolTip(lbl, eq_info['tooltip'][var])

                ent = tk.Entry(var_frame, font=self.entry_font, width=15)
                ent.pack(side=tk.LEFT, padx=5)

                unit_lbl = tk.Label(var_frame,
                    text=eq_info['units'].get(var, ''),
                    bg=self.bg_color,
                    fg=self.fg_color,
                    font=self.entry_font)
                unit_lbl.pack(side=tk.LEFT, padx=5)

                self.input_entries[var] = ent

    # Perform calculation based on user inputs.
    def calculate(self):
        eq_name = self.eq_choice.get()
        eq_info = self.equations[eq_name]
        target_var = self.var_choice.get()

        # Define symbols for sympy to parse.
        symbols = {v: sp.Symbol(v) for v in eq_info['variables']}
        expr = sp.sympify(eq_info['expr'], locals=symbols)

        # Solve for the target variable.
        sol = sp.solve(sp.Eq(symbols[eq_info['variables'][0]], expr), symbols[target_var])
        if not sol:
            messagebox.showerror("Error", "Cannot solve for selected variable.")
            return
        solution = sol[0]

        # Collect user inputs and substitute into the solution.
        subs = {}
        for var, ent in self.input_entries.items():
            val = ent.get()
            try:
                val = float(val)
                unit = eq_info['units'].get(var, '')
                subs[var] = val
            except:
                messagebox.showerror("Input Error", f"Invalid number for {var}")
                return

        # Evaluate the expression and display the result.
        try:
            result = solution.evalf(subs=subs)
            unit = eq_info['units'].get(target_var, '')
            display_val = result
            
            self.result_text = f"{target_var} = {display_val:.4f} {unit}"
            self.output_label.config(text=self.result_text)

            # Render solved form.
            solved_latex = sp.latex(sp.Eq(symbols[target_var], solution))
            img_path = self.render_equation(solved_latex, 'solved.png')
            img = self.load_image(img_path)
            self.solved_label.config(image=img)
            self.solved_label.image = img
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def copy_to_clipboard(self):
        if self.result_text:
            self.master.clipboard_clear()
            self.master.clipboard_append(self.result_text)
            self.master.update()
        else:
            messagebox.showinfo("Copy Result", "No result to copy yet.")

if __name__ == "__main__":
    # Get equations from the JSON file.
    with open("equations.json", "r", encoding="utf-8") as f:
        EQUATIONS = json.load(f)
    root = tk.Tk()
    app = EnergeticMaterialsCalculator(root, EQUATIONS)
    
    # Start the GUI event loop.
    root.mainloop()
