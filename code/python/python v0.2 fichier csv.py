import tkinter as tk
from tkinter import filedialog # Pour ouvrir la fenêtre de choix de fichier
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Variables Globales ---
# On enlève la limite MAX_POINTS pour voir tout l'historique du fichier
temps = []         # Liste des temps
history = {        # Historique des données
    "T": [], "H": [], "NDVI": [], 
    "ax": [], "ay": [], "az": [] 
}

# Dernières valeurs (pour l'affichage en haut - prendra la fin du fichier)
current_val = { 
    "T": 0.0, "H": 0.0, "NDVI": 0.0, 
    "ax": 0.0, "ay": 0.0, "az": 0.0, 
    "etat": "Aucun fichier"
}
current_graph = "NDVI" # Graphique par défaut

# --- Fonction pour charger le fichier CSV ---
def load_csv_file():
    global temps, history, current_val
    
    # 1. Ouvrir la fenêtre de sélection
    filename = filedialog.askopenfilename(
        title="Sélectionnez le fichier donnees.csv de la carte SD",
        filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
    )
    
    if not filename:
        return # Si l'utilisateur annule

    # 2. Réinitialiser les données
    temps.clear()
    for key in history:
        history[key].clear()
        
    print(f"📂 Chargement du fichier : {filename}")

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            
            # On saute la première ligne (les titres)
            # Format attendu: Temps(ms);Temp;Hum;Pres;NDVI;ax;ay;az
            for line in lines[1:]:
                parts = line.strip().split(';')
                
                # Vérification simple que la ligne est complète
                if len(parts) >= 8:
                    try:
                        # Conversion des données
                        t_sec = float(parts[0]) / 1000.0 # Convertir ms en secondes
                        t = float(parts[1])
                        h = float(parts[2])
                        ndvi = float(parts[4])
                        ax = float(parts[5])
                        ay = float(parts[6])
                        az = float(parts[7])
                        
                        # Ajout aux listes
                        temps.append(t_sec)
                        history["T"].append(t)
                        history["H"].append(h)
                        history["NDVI"].append(ndvi)
                        history["ax"].append(ax)
                        history["ay"].append(ay)
                        history["az"].append(az)
                        
                    except ValueError:
                        continue # Ignore les lignes mal écrites
            
            # 3. Mettre à jour le tableau de bord avec la DERNIÈRE valeur du fichier
            if len(temps) > 0:
                current_val["T"] = history["T"][-1]
                current_val["H"] = history["H"][-1]
                current_val["NDVI"] = history["NDVI"][-1]
                current_val["ax"] = history["ax"][-1]
                current_val["ay"] = history["ay"][-1]
                current_val["az"] = history["az"][-1]
                
                # Recalcul de l'état (comme l'Arduino le faisait)
                n = current_val["NDVI"]
                if n > 0.5: current_val["etat"] = "[ SAINE ]"
                elif n > 0.2: current_val["etat"] = "[ STRESSÉE ]"
                else: current_val["etat"] = "[ ALERTE ]"
            
            # 4. Mettre à jour l'affichage
            update_dashboard_labels()
            draw_graph()
            print("✅ Fichier chargé avec succès !")

    except Exception as e:
        print(f"❌ Erreur lors de la lecture : {e}")

# --- Affichage (Tkinter) ---

def update_dashboard_labels():
    # Met à jour les gros chiffres en haut
    lbl_temp.config(text=f"{current_val['T']:.1f} °C")
    lbl_hum.config(text=f"{current_val['H']:.1f} %")
    
    ndvi = current_val['NDVI']
    color = "green" if ndvi > 0.5 else "orange" if ndvi > 0.2 else "red"
    lbl_ndvi.config(text=f"{ndvi:.3f}", fg=color)
    lbl_etat.config(text=current_val["etat"], fg=color)

def set_graph_mode(mode):
    global current_graph
    current_graph = mode
    draw_graph() # Redessine tout de suite

def draw_graph():
    ax.clear()
    
    if len(temps) > 0:
        if current_graph == "NDVI":
            ax.plot(temps, history["NDVI"], '-', color='green', linewidth=2, label="NDVI") # 'o-' enlevé pour fluidité si bcp de points
            ax.set_title("Santé de la Vigne (Historique complet)")
            ax.set_ylabel("Indice NDVI")
            ax.set_ylim(-0.1, 1.0)
            
        elif current_graph == "TEMP":
            ax.plot(temps, history["T"], '-', color='blue', linewidth=2, label="Température")
            ax.set_title("Historique Température (°C)")
            ax.set_ylabel("°C")
            
        elif current_graph == "HUM":
            ax.plot(temps, history["H"], '-', color='teal', linewidth=2, label="Humidité")
            ax.set_title("Historique Humidité Relative (%)")
            ax.set_ylabel("%")
            ax.set_ylim(0, 100)
            
        elif current_graph == "ACCEL":
            ax.plot(temps, history["ax"], label="X", color="purple", alpha=0.7)
            ax.plot(temps, history["ay"], label="Y", color="orange", alpha=0.7)
            ax.plot(temps, history["az"], label="Z", color="brown", alpha=0.7)
            ax.set_title("Historique Mouvements (Accéléromètre)")
            ax.set_ylabel("m/s²")
            ax.legend()

    ax.set_xlabel("Temps (secondes)")
    ax.grid(True, linestyle='--', alpha=0.5)
    canvas.draw()

def on_closing():
    window.destroy()

# --- CONSTRUCTION DE LA FENÊTRE ---
window = tk.Tk()
window.title("Lecteur de Sauvegarde - Vigne Connectée") # Petit changement de titre
window.geometry("900x750")
window.config(bg="#f0f0f0")

# --- BOUTON DE CHARGEMENT FICHIER ---
frame_load = tk.Frame(window, bg="#ddd", bd=1, relief="raised")
frame_load.pack(fill="x", padx=0, pady=0)
tk.Button(frame_load, text="📂 OUVRIR UN FICHIER CSV (Carte SD)", command=load_csv_file, 
          bg="white", font=("Arial", 11, "bold"), pady=5).pack(pady=5)

# 1. HEADER (Les chiffres - montreront la fin de l'enregistrement)
frame_top = tk.Frame(window, bg="white", bd=2, relief="groove")
frame_top.pack(fill="x", padx=10, pady=10)

def make_stat(parent, title):
    f = tk.Frame(parent, bg="white")
    f.pack(side="left", expand=True, fill="both")
    tk.Label(f, text=title, font=("Arial", 9, "bold"), fg="gray", bg="white").pack()
    l = tk.Label(f, text="--", font=("Arial", 18, "bold"), bg="white")
    l.pack()
    return l

lbl_temp = make_stat(frame_top, "TEMPÉRATURE (Fin)")
lbl_hum = make_stat(frame_top, "HUMIDITÉ (Fin)")
lbl_ndvi = make_stat(frame_top, "NDVI (Fin)")
lbl_etat = make_stat(frame_top, "ÉTAT (Fin)")

# 2. LES BOUTONS (Pour changer de courbe)
frame_btn = tk.Frame(window, bg="#f0f0f0")
frame_btn.pack(fill="x", pady=5)

btn_style = {"font":("Arial", 10, "bold"), "width":15, "pady":5, "relief":"raised"}

tk.Button(frame_btn, text="🌿 NDVI", bg="#c8e6c9", command=lambda: set_graph_mode("NDVI"), **btn_style).pack(side="left", padx=10, expand=True)
tk.Button(frame_btn, text="🌡️ Température", bg="#bbdefb", command=lambda: set_graph_mode("TEMP"), **btn_style).pack(side="left", padx=10, expand=True)
tk.Button(frame_btn, text="💧 Humidité", bg="#b2ebf2", command=lambda: set_graph_mode("HUM"), **btn_style).pack(side="left", padx=10, expand=True)
tk.Button(frame_btn, text="📉 Accéléromètre", bg="#ffe0b2", command=lambda: set_graph_mode("ACCEL"), **btn_style).pack(side="left", padx=10, expand=True)

# 3. LE GRAPHIQUE
fig, ax = plt.subplots(figsize=(8, 5))
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)

# Lancement
window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()