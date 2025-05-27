# fraction_visualizer_streamlit.py
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from math import gcd
from functools import reduce

# Set page config for better layout
st.set_page_config(page_title="Fraction Visualizer", layout="wide")

def prime_factors(n):
    """Return prime factors of n as a list of strings with exponents"""
    factors = {}
    while n % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n = n // 2
    i = 3
    while i * i <= n:
        while n % i == 0:
            factors[i] = factors.get(i, 0) + 1
            n = n // i
        i += 2
    if n > 1:
        factors[n] = 1
    return [f"{p}{'^'+str(e) if e>1 else ''}" for p, e in factors.items()]

def lcm(a, b):
    """Calculate the Least Common Multiple of two numbers."""
    return a * b // gcd(a, b)

def compute_lcd(denominators):
    """Calculate the Least Common Denominator for a list of denominators."""
    return reduce(lcm, denominators)

def parse_expression(expr):
    """Parse fraction expression into components with validation"""
    expr = expr.replace(" ", "")
    parts = []
    i = 0
    
    while i < len(expr):
        if expr[i] in '+-':
            if parts and isinstance(parts[-1], tuple):
                parts.append(expr[i])
            i += 1
        else:
            j = i
            while j < len(expr) and expr[j] not in '+-':
                j += 1
            fraction = expr[i:j]
            
            if fraction:
                if '/' in fraction:
                    try:
                        num, denom = map(int, fraction.split('/'))
                        if denom == 0:
                            raise ValueError("Denominator cannot be zero")
                    except ValueError as e:
                        raise ValueError(f"Invalid fraction '{fraction}': {str(e)}")
                else:
                    try:
                        num = int(fraction)
                        denom = 1
                    except ValueError:
                        raise ValueError(f"Invalid number '{fraction}'")
                
                parts.append((num, denom))
            i = j
    
    # Validate we have exactly 3 fractions with 2 operators
    fractions = [p for p in parts if isinstance(p, tuple)]
    operators = [p for p in parts if isinstance(p, str)]
    
    if len(fractions) != 3 or len(operators) != 2:
        raise ValueError("Need exactly 3 fractions with 2 operators (+ or -) between them")
    
    return parts

def draw_fraction_circle(ax, numerator, denominator, colors, title):
    """Draw fraction visualization with proper scaling and colors"""
    circle_radius = 0.4
    circle = plt.Circle((0, 0), circle_radius, fill=False, color='black', linewidth=0.8)
    ax.add_patch(circle)
    
    for i in range(denominator):
        angle = 2 * np.pi * i / denominator
        x = [0, circle_radius * np.cos(angle)]
        y = [0, circle_radius * np.sin(angle)]
        ax.plot(x, y, color=colors[0], alpha=0.8, linewidth=0.8)
        
        if i < numerator:
            wedge = np.linspace(angle, angle + 2*np.pi/denominator, 50)
            x_wedge = np.concatenate([[0], circle_radius * np.cos(wedge)])
            y_wedge = np.concatenate([[0], circle_radius * np.sin(wedge)])
            ax.fill(x_wedge, y_wedge, color=colors[1], alpha=0.6)
    
    ax.set_title(title, pad=3, fontsize=9)
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_aspect('equal')
    ax.axis('off')

def main():
    st.title("🍕 Fraction Visualizer")
    st.markdown("""
    Enter fractions with + or - between them (e.g., `1/6-2/3+4/9`)
    """)
    
    # Input section
    col1, col2 = st.columns([3, 1])
    with col1:
        expression = st.text_input("Expression:", "1/6-2/3+4/9")
    with col2:
        st.write("")  # Spacer
        if st.button("Random Example"):
            examples = ["1/2+1/4+1/8", "2/3-1/6+3/4", "5/6+1/3-1/2", "3/4-1/2+5/8"]
            expression = np.random.choice(examples)
            st.experimental_rerun()
    
    if st.button("Solve"):
        try:
            parts = parse_expression(expression)
            fractions = [part for part in parts if isinstance(part, tuple)]
            operators = [part for part in parts if isinstance(part, str)]
            denominators = [f[1] for f in fractions]
            lcd = compute_lcd(denominators)
            converted_nums = [num * (lcd // den) for num, den in fractions]
            
            # Visualization
            st.subheader("Visualization")
            fig, axes = plt.subplots(2, 3, figsize=(12, 6))
            plt.subplots_adjust(wspace=0.4, hspace=0.4)
            
            # Original fractions
            for i, (num, den) in enumerate(fractions):
                draw_fraction_circle(axes[0,i], num, den, ('blue', 'lightblue'), f"Original: {num}/{den}")
            
            # Converted fractions
            for i, (num, den) in enumerate(fractions):
                new_num = num * (lcd // den)
                draw_fraction_circle(axes[1,i], new_num, lcd, ('red', 'lightcoral'), f"Converted: {new_num}/{lcd}")
            
            st.pyplot(fig)
            
            # Calculation steps
            st.subheader("Calculation Steps")
            
            # LCD Explanation
            with st.expander("1. Find Least Common Denominator (LCD)"):
                st.write(f"**Denominators:** {', '.join(str(d) for d in denominators)}")
                st.write("**Prime Factorization:**")
                for d in denominators:
                    st.write(f"- {d} = {' × '.join(prime_factors(d))}")
                
                all_factors = {}
                for d in denominators:
                    factors = {}
                    n = d
                    i = 2
                    while i * i <= n:
                        while n % i == 0:
                            factors[i] = factors.get(i, 0) + 1
                            n = n // i
                        i += 2
                    if n > 1:
                        factors[n] = 1
                    for p, cnt in factors.items():
                        if p in all_factors:
                            if cnt > all_factors[p]:
                                all_factors[p] = cnt
                        else:
                            all_factors[p] = cnt
                
                lcd_factors = [f"{p}^{cnt}" if cnt>1 else str(p) for p,cnt in sorted(all_factors.items())]
                st.write(f"**LCD Calculation:** Take highest power of each prime:")
                st.write(f"**{' × '.join(lcd_factors)} = {lcd}**")
            
            # Conversion
            with st.expander("2. Convert each fraction"):
                for i, (num, den) in enumerate(fractions):
                    multiplier = lcd // den
                    st.write(f"{num}/{den} = ({num}×{multiplier})/({den}×{multiplier}) = {num*multiplier}/{lcd}")
            
            # Calculation
            result = converted_nums[0]
            calculation = [f"{converted_nums[0]}/{lcd}"]
            for i, op in enumerate(operators):
                calculation.append(f" {op} {converted_nums[i+1]}/{lcd}")
                if op == '+':
                    result += converted_nums[i+1]
                else:
                    result -= converted_nums[i+1]
            
            with st.expander("3. Perform calculation"):
                st.write(f"{''.join(calculation)} = {result}/{lcd}")
                
                # Simplification
                common_divisor = gcd(result, lcd)
                if common_divisor > 1:
                    st.success(f"**Simplified:** {result}/{lcd} = {result//common_divisor}/{lcd//common_divisor}")
                else:
                    st.info("Cannot be simplified further")
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("""
            **Valid format examples:**
            - 1/6-2/3+4/9
            - 5/5+6/10-1/20
            - 1/2+1/3-1/4
            """)

if __name__ == "__main__":
    main()
