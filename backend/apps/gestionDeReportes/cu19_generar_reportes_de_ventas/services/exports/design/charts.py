import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

class ChartRenderer:
    """
    Motor de diseño gráfico usando matplotlib.
    Dibuja gráficos estilizados, corporativos y limpios.
    """
    
    @classmethod
    def setup_figure(cls, width=8, height=4.5):
        plt.style.use('default')
        fig = plt.figure(figsize=(width, height))
        fig.patch.set_facecolor('white')
        
        # Eliminar bordes (spines) derecho y superior por defecto
        ax = plt.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#bdc3c7')
        ax.spines['bottom'].set_color('#bdc3c7')
        
        return fig, ax

    @classmethod
    def save_to_buffer(cls):
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=200, bbox_inches='tight', transparent=False)
        plt.close()
        buf.seek(0)
        return buf

    @classmethod
    def draw_bar(cls, labels, values):
        fig, ax = cls.setup_figure()
        
        # Dibujar barras azules
        bars = ax.bar(labels, values, color='#3498db', width=0.6, alpha=0.9)
        
        # Rotar etiquetas si son muy largas
        plt.xticks(rotation=45 if len(labels) > 4 else 0, ha='right' if len(labels) > 4 else 'center')
        
        # Agregar etiquetas de valor (útiles) flotantes sobre las barras
        for bar in bars:
            yval = bar.get_height()
            # Formato bonito: si es entero sin decimales, sino con 1 decimal
            label = f"{yval:,.0f}" if yval % 1 == 0 else f"{yval:,.1f}"
            ax.text(bar.get_x() + bar.get_width()/2, yval + (max(values)*0.02), 
                    label, ha='center', va='bottom', fontsize=9, color='#2c3e50', fontweight='bold')
            
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, linestyle='--', alpha=0.3, color='#bdc3c7')
        
        return cls.save_to_buffer()

    @classmethod
    def draw_line(cls, labels, values):
        fig, ax = cls.setup_figure()
        
        # Dibujar línea verde esmeralda con marcadores
        line, = ax.plot(labels, values, marker='o', color='#27ae60', linewidth=3, markersize=8, markerfacecolor='white', markeredgewidth=2)
        
        plt.xticks(rotation=45 if len(labels) > 4 else 0, ha='right' if len(labels) > 4 else 'center')
        
        # Agregar etiquetas sobre los puntos
        for i, val in enumerate(values):
            label = f"{val:,.0f}" if val % 1 == 0 else f"{val:,.1f}"
            ax.annotate(label, 
                        (labels[i], val),
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center', 
                        fontsize=9, 
                        color='#2c3e50', 
                        fontweight='bold')

        ax.set_axisbelow(True)
        ax.grid(True, linestyle='--', alpha=0.3, color='#bdc3c7')
        
        return cls.save_to_buffer()

    @classmethod
    def draw_donut(cls, labels, values):
        # Donut chart requires equal aspect ratio
        fig = plt.figure(figsize=(7, 5))
        ax = plt.gca()
        
        # Paleta de colores corporativa para pasteles
        colors_palette = ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e67e22', '#e74c3c', '#1abc9c']
        
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=labels, 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=colors_palette,
            pctdistance=0.85,
            textprops={'fontsize': 10, 'color': '#2c3e50'}
        )
        
        # Hacer los textos de porcentaje blancos o gruesos
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            
        # Dibujar un círculo blanco en el centro para convertirlo en dona
        centre_circle = plt.Circle((0,0), 0.65, fc='white')
        fig.gca().add_artist(centre_circle)
        
        ax.axis('equal')  # Proporción igual asegura que el donut sea circular
        
        return cls.save_to_buffer()

    @classmethod
    def draw_prediction(cls, all_labels, hist_data, pred_data, lower_bound, upper_bound):
        fig, ax = cls.setup_figure(width=9, height=5)
        
        # Histórico (Azul sólido)
        ax.plot(all_labels, hist_data, marker='o', color='#3498db', linewidth=2, label="Histórico")
        
        # Predicción (Rojo punteado)
        ax.plot(all_labels, pred_data, marker='o', color='#e74c3c', linewidth=2, linestyle='--', label="Predicción")
        
        # Intervalo de confianza (Gris sombreado)
        # Necesitamos limpiar los None/Null para el fill_between
        valid_idx = [i for i, v in enumerate(lower_bound) if v is not None]
        if valid_idx:
            x_valid = [all_labels[i] for i in valid_idx]
            y1 = [lower_bound[i] for i in valid_idx]
            y2 = [upper_bound[i] for i in valid_idx]
            ax.fill_between(x_valid, y1, y2, color='gray', alpha=0.2, label="Intervalo de Confianza")

        plt.xticks(rotation=45 if len(all_labels) > 5 else 0, ha='right' if len(all_labels) > 5 else 'center')
        ax.legend(loc="upper left")
        ax.set_axisbelow(True)
        ax.grid(True, linestyle='--', alpha=0.3, color='#bdc3c7')
        
        return cls.save_to_buffer()

    # --- NUEVOS GRÁFICOS E-COMMERCE ---
    
    @classmethod
    def draw_sparkline(cls, values):
        fig, ax = plt.subplots(figsize=(4, 1.5))
        fig.patch.set_facecolor('white')
        ax.axis('off')
        
        # Determine trend
        color = '#10b981' if values[-1] >= values[0] else '#f43f5e'
        
        ax.plot(values, color=color, linewidth=2)
        ax.fill_between(range(len(values)), min(values) - (max(values)-min(values))*0.1, values, color=color, alpha=0.2)
        
        return cls.save_to_buffer()

    @classmethod
    def draw_waterfall(cls, labels, values):
        fig, ax = cls.setup_figure()
        
        running_total = 0
        bottoms = []
        for val in values[:-1]:
            if val < 0:
                bottoms.append(running_total + val)
            else:
                bottoms.append(running_total)
            running_total += val
        
        # El último suele ser el total (no flotante)
        bottoms.append(0)
        
        colors = ['#10b981' if v > 0 else '#f43f5e' for v in values[:-1]]
        colors.append('#334155') # Color del total final
        
        bars = ax.bar(labels, [abs(v) for v in values], bottom=bottoms, color=colors, width=0.6)
        
        # Conectores punteados
        for i in range(1, len(values)):
            prev_total = bottoms[i-1] + values[i-1] if values[i-1] > 0 else bottoms[i-1]
            ax.plot([i-1, i], [prev_total, prev_total], 'k--', alpha=0.3)
            
        plt.xticks(rotation=45, ha='right')
        return cls.save_to_buffer()

    @classmethod
    def draw_funnel(cls, labels, values):
        fig, ax = cls.setup_figure()
        
        y_pos = np.arange(len(labels))[::-1] # Invertido para que el embudo vaya hacia abajo
        max_val = max(values)
        
        colors = ['#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#1d4ed8']
        
        for i, (label, val) in enumerate(zip(labels, values)):
            width = val
            left = (max_val - val) / 2
            ax.barh(y_pos[i], width, left=left, color=colors[i % len(colors)], height=0.6)
            ax.text(max_val/2, y_pos[i], f"{val:,.0f}", ha='center', va='center', color='white', fontweight='bold')
            ax.text(left - (max_val*0.05), y_pos[i], label, ha='right', va='center', color='#475569', fontsize=10)
            
        ax.axis('off')
        return cls.save_to_buffer()

    @classmethod
    def draw_cohort(cls, cohorts, data_matrix):
        # Utilizando matplotlib imshow para generar heatmap estilo cohort
        fig, ax = cls.setup_figure()
        
        # Normalizar datos (llenar nulos con 0 para matriz cuadrada)
        max_len = max(len(row) for row in data_matrix)
        padded_matrix = [row + [np.nan] * (max_len - len(row)) for row in data_matrix]
        
        im = ax.imshow(padded_matrix, cmap='Blues', aspect='auto', vmin=0, vmax=100)
        
        ax.set_yticks(np.arange(len(cohorts)))
        ax.set_yticklabels(cohorts)
        ax.set_xticks(np.arange(max_len))
        ax.set_xticklabels([f"Mes {i}" for i in range(max_len)])
        
        # Anotar textos
        for i in range(len(cohorts)):
            for j in range(len(data_matrix[i])):
                val = data_matrix[i][j]
                color = 'white' if val > 40 else 'black'
                ax.text(j, i, f"{val}%", ha="center", va="center", color=color, fontsize=8)
                
        # Removiendo spines
        for edge, spine in ax.spines.items():
            spine.set_visible(False)
            
        return cls.save_to_buffer()

    @classmethod
    def draw_heatmap(cls, x_labels, y_labels, matrix):
        fig, ax = cls.setup_figure()
        
        im = ax.imshow(matrix, cmap='Greens', aspect='auto')
        
        ax.set_xticks(np.arange(len(x_labels)))
        ax.set_xticklabels(x_labels)
        ax.set_yticks(np.arange(len(y_labels)))
        ax.set_yticklabels(y_labels)
        
        # Valores
        for i in range(len(y_labels)):
            for j in range(len(x_labels)):
                val = matrix[i][j]
                color = 'white' if val > (np.max(matrix)/2) else 'black'
                ax.text(j, i, str(val), ha="center", va="center", color=color, fontsize=8)
                
        for edge, spine in ax.spines.items():
            spine.set_visible(False)
            
        return cls.save_to_buffer()

    @classmethod
    def draw_radar(cls, labels, values):
        # Gráfico polar para el radar
        fig = plt.figure(figsize=(6, 6))
        fig.patch.set_facecolor('white')
        ax = fig.add_subplot(111, polar=True)
        
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        values = values + [values[0]]
        angles += angles[:1]
        
        ax.plot(angles, values, color='#8b5cf6', linewidth=2)
        ax.fill(angles, values, color='#8b5cf6', alpha=0.25)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, size=10, color='#475569')
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels([]) # Ocultamos los números del radio interior
        ax.spines['polar'].set_color('#e2e8f0')
        
        return cls.save_to_buffer()

    @classmethod
    def draw_horizontal(cls, labels, values):
        fig, ax = cls.setup_figure()
        
        y_pos = np.arange(len(labels))[::-1]
        bars = ax.barh(y_pos, values, color='#3b82f6', height=0.6)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.spines['bottom'].set_visible(False)
        ax.xaxis.set_visible(False) # Esconder eje X
        
        for bar in bars:
            width = bar.get_width()
            ax.text(width + (max(values)*0.01), bar.get_y() + bar.get_height()/2, f"{width:,.0f}", ha='left', va='center', color='#475569', fontweight='bold')
            
        return cls.save_to_buffer()

    @classmethod
    def draw_stacked(cls, labels, segments1, segments2, segments3):
        fig, ax = cls.setup_figure()
        
        ax.bar(labels, segments1, color='#2563eb', label='Seg 1')
        ax.bar(labels, segments2, bottom=segments1, color='#6366f1', label='Seg 2')
        bottom3 = [s1 + s2 for s1, s2 in zip(segments1, segments2)]
        ax.bar(labels, segments3, bottom=bottom3, color='#8b5cf6', label='Seg 3')
        
        plt.xticks(rotation=45, ha='right')
        ax.legend()
        return cls.save_to_buffer()

    @classmethod
    def draw_area(cls, labels, values):
        fig, ax = cls.setup_figure()
        
        ax.plot(labels, values, color='#10b981', linewidth=2)
        ax.fill_between(range(len(labels)), 0, values, color='#10b981', alpha=0.2)
        
        plt.xticks(rotation=45, ha='right')
        ax.set_ylim(bottom=0)
        return cls.save_to_buffer()
