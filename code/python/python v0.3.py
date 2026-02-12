import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import csv

# --- DONNEES GLOBALES ---
all_data = {} 
headers = []

# --- 1. CHARGEMENT DU FICHIER ---
def load_csv():
    global all_data, headers
    
    filename = filedialog.askopenfilename(
        title="Ouvrir un fichier CSV (MESURES.CSV)",
        filetypes=[("Fichiers CSV", "*.csv"), ("Tous", "*.*")]
    )
    if not filename: return

    # Réinitialisation
    all_data = {}
    headers = []

    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Détection automatique du séparateur (; ou ,)
            sep = ';' if ';' in content.splitlines()[0] else ','
            
            # Lecture
            lines = content.splitlines()
            
            # 1. Les Titres (Headers)
            headers = lines[0].split(sep)
            headers = [h.strip() for h in headers if h.strip()] # Nettoyage des espaces
            
            # Création des listes vides pour chaque colonne
            all_data = {h: [] for h in headers}

            # 2. Les Données
            count = 0
            for line in lines[1:]:
                if not line.strip(): continue
                
                # Gestion des virgules (Excel français) -> on remplace par des points
                if sep == ';':
                    line = line.replace(',', '.')
                
                parts = line.split(sep)
                
                # On vérifie qu'on a bien le bon nombre de colonnes
                if len(parts) < len(headers): continue

                try:
                    for i, h in enumerate(headers):
                        # On convertit tout en chiffres (float)
                        val = float(parts[i])
                        all_data[h].append(val)
                    count += 1
                except ValueError:
                    continue # On ignore les lignes qui ne sont pas des chiffres

            if count == 0:
                messagebox.showwarning("Vide", "Aucune donnée valide trouvée dans ce fichier.")
                return

            # --- MISE A JOUR DE L'INTERFACE ---
            
            # Remplir les menus déroulants avec les titres trouvés
            combo_x['values'] = headers
            combo_y['values'] = headers
            
            # Sélection par défaut intelligente
            # Axe X : On cherche "Temps" ou la 1ère colonne
            default_x = 0
            for i, h in enumerate(headers):
                if "Temps" in h or "Time" in h: 
                    default_x = i
                    break
            combo_x.current(default_x)
            
            # Axe Y : On cherche "NDVI" ou la 2ème colonne
            default_y = 1 if len(headers) > 1 else 0
            for i, h in enumerate(headers):
                if "NDVI" in h: 
                    default_y = i
                    break
            combo_y.current(default_y)

            lbl_status.config(text=f"✅ Fichier chargé : {count} points", fg="green")
            
            # On trace direct !
            update_graph()

    except Exception as e:
        messagebox.showerror("Erreur", f"Problème de lecture :\n{e}")

# --- 2. TRACER LE GRAPHIQUE ---
def update_graph():
    if not all_data: return

    # Récupérer les choix de l'utilisateur
    x_name = combo_x.get()
    y_name = combo_y.get()

    if not x_name or not y_name: return

    # Récupérer les listes de données correspondantes
    x_data = all_data[x_name]
    y_data = all_data[y_name]

    # Nettoyage
    ax.clear()

    # --- LOGIQUE DE DESSIN ---
    # Si l'axe X est le "Temps", on fait une courbe (Ligne)
    if "Temps" in x_name or "Time" in x_name:
        ax.plot(x_data, y_data, '-', linewidth=2, color='#2196F3', label=y_name)
    
    # Sinon (ex: Température vs Humidité), on fait un Nuage de points (Scatter)
    else:
        ax.scatter(x_data, y_data, alpha=0.6, edgecolors='b', c='cyan', label='Mesures')

    # Titres et Grille
    ax.set_xlabel(x_name, fontsize=10, fontweight='bold')
    ax.set_ylabel(y_name, fontsize=10, fontweight='bold')
    ax.set_title(f"Analyse : {y_name} en fonction de {x_name}")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()

    canvas.draw()

# --- 3. INTERFACE GRAPHIQUE ---
root = tk.Tk()
root.title("VigneLab - Visualiseur de Données")
root.geometry("1000x700")

# --- CADRE DU HAUT : Fichier & Infos ---
frame_top = tk.Frame(root, bg="#eee", bd=1, relief="raised", pady=10)
frame_top.pack(fill="x")

btn_load = tk.Button(frame_top, text="📂 1. CHARGER UN FICHIER CSV", command=load_csv, 
                     bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))
btn_load.pack(side="left", padx=20)

lbl_status = tk.Label(frame_top, text="En attente de fichier...", bg="#eee", fg="gray", font=("Arial", 10))
lbl_status.pack(side="left", padx=10)

# --- CADRE DU MILIEU : Choix des Axes ---
frame_axes = tk.Frame(root, bg="#ddd", pady=10)
frame_axes.pack(fill="x")

tk.Label(frame_axes, text="Axe X (Bas) :", bg="#ddd", font=("Arial", 10, "bold")).pack(side="left", padx=10)
combo_x = ttk.Combobox(frame_axes, state="readonly", width=20)
combo_x.pack(side="left", padx=5)

tk.Label(frame_axes, text="Axe Y (Côté) :", bg="#ddd", font=("Arial", 10, "bold")).pack(side="left", padx=20)
combo_y = ttk.Combobox(frame_axes, state="readonly", width=20)
combo_y.pack(side="left", padx=5)

btn_plot = tk.Button(frame_axes, text="🔄 2. TRACER / ACTUALISER", command=update_graph, 
                     bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
btn_plot.pack(side="left", padx=30)

# --- ZONE GRAPHIQUE ---
fig, ax = plt.subplots(figsize=(8, 5))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)

# BARRE D'OUTILS (Zoom, Pan, Save...) - Très utile !
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(fill="both", expand=True)

# Lancement
root.mainloop()