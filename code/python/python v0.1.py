import tkinter as tk
import serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import re  # Module pour lire le texte complexe de l'Arduino

# --- CONFIGURATION (A VÉRIFIER) ---
PORT = "COM3"      # <--- Mets ton port ici (ex: COM3, COM5, /dev/ttyUSB0)
BAUD = 115200      # Doit être pareil que dans l'Arduino

# --- Variables Globales ---
MAX_POINTS = 50    # On garde les 50 derniers points en mémoire
temps = []         # Liste des temps
history = {        # Historique des données
    "T": [], "H": [], "NDVI": [], 
    "ax": [], "ay": [], "az": [] 
}
# Dernières valeurs reçues (pour l'affichage en haut)
current_val = { 
    "T": 0.0, "H": 0.0, "NDVI": 0.0, 
    "ax": 0.0, "ay": 0.0, "az": 0.0, 
    "etat": "En attente..."
}
current_graph = "NDVI" # Graphique par défaut

# --- Connexion Série ---
ser = None
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"✅ Connecté à l'Arduino sur {PORT}")
    ser.reset_input_buffer()
except serial.SerialException:
    print(f"❌ ERREUR : Impossible d'ouvrir le port {PORT}.")
    print("Vérifie que l'Arduino est branché et que le port est le bon.") 
    # On continue quand même pour afficher l'interface (vide)
    
# --- Fonction qui récupère les VRAIES données ---
def read_serial_data():
    if ser and ser.in_waiting > 0:
        try:
            # 1. Lire la ligne brute envoyée par le câble USB
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            
            # 2. Si la ligne n'est pas vide, on l'analyse
            if line:
                parse_arduino_text(line)
                
        except Exception as e:
            print(f"Erreur de lecture : {e}")

    # On revérifie s'il y a des données toutes les 100ms
    window.after(100, read_serial_data)

# --- Fonction qui "comprend" le texte de ton Arduino ---
def parse_arduino_text(line):
    # C'est ici qu'on extrait les vrais chiffres du texte
    
    # Cas 1 : NDVI (Ex: "SANTÉ FEUILLE (NDVI) : 0.55")
    if "NDVI" in line and ":" in line:
        match = re.search(r":\s*([-+]?\d*\.\d+|\d+)", line)
        if match:
            current_val["NDVI"] = float(match.group(1))
            if "->" in line:
                current_val["etat"] = line.split("->")[1].strip()

    # Cas 2 : Accéléromètre (Ex: "... X: 0.12 | Y: 0.2 ...")
    elif "ACCÉLÉRATION" in line and "X:" in line:
        match_x = re.search(r"X:\s*([-+]?\d*\.\d+)", line)
        match_y = re.search(r"Y:\s*([-+]?\d*\.\d+)", line)
        match_z = re.search(r"Z:\s*([-+]?\d*\.\d+)", line)
        if match_x and match_y and match_z:
            current_val["ax"] = float(match_x.group(1))
            current_val["ay"] = float(match_y.group(1))
            current_val["az"] = float(match_z.group(1))

    # Cas 3 : Météo (Ex: "MÉTÉO | 24.0°C | ...")
    elif "MÉTÉO" in line:
        parts = line.split("|")
        if len(parts) >= 3:
            try:
                t_str = parts[1].replace("°C", "").strip()
                h_str = parts[2].replace("% Hum", "").strip()
                current_val["T"] = float(t_str)
                current_val["H"] = float(h_str)
                
                # Une fois la météo reçue, on considère que le bloc est fini : on enregistre !
                save_and_update()
            except: pass

# --- Sauvegarde et Mise à jour Graphique ---
def save_and_update():
    # Gestion du temps (0, 10s, 20s...)
    if len(temps) == 0:
        temps.append(0)
    else:
        temps.append(temps[-1] + 10) # On ajoute 10 secondes
        
    # Ajout des valeurs dans l'historique
    history["T"].append(current_val["T"])
    history["H"].append(current_val["H"])
    history["NDVI"].append(current_val["NDVI"])
    history["ax"].append(current_val["ax"])
    history["ay"].append(current_val["ay"])
    history["az"].append(current_val["az"])
    
    # On supprime les vieux points si on dépasse MAX_POINTS
    if len(temps) > MAX_POINTS:
        temps.pop(0)
        for k in history: history[k].pop(0)

    # Mise à jour de l'affichage
    update_dashboard_labels()
    draw_graph()

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
            ax.plot(temps, history["NDVI"], 'o-', color='green', linewidth=2, label="NDVI")
            ax.set_title("Santé de la Vigne (NDVI)")
            ax.set_ylabel("Indice")
            ax.set_ylim(-0.1, 1.0)
            
        elif current_graph == "TEMP":
            ax.plot(temps, history["T"], 'o-', color='blue', linewidth=2, label="Température")
            ax.set_title("Température (°C)")
            ax.set_ylabel("°C")
            
        elif current_graph == "HUM":
            ax.plot(temps, history["H"], 'o-', color='teal', linewidth=2, label="Humidité")
            ax.set_title("Humidité Relative (%)")
            ax.set_ylabel("%")
            ax.set_ylim(0, 100)
            
        elif current_graph == "ACCEL":
            ax.plot(temps, history["ax"], label="X", color="purple")
            ax.plot(temps, history["ay"], label="Y", color="orange")
            ax.plot(temps, history["az"], label="Z", color="brown")
            ax.set_title("Mouvements (Accéléromètre)")
            ax.set_ylabel("m/s²")
            ax.legend()

    ax.set_xlabel("Temps écoulé (secondes)")
    ax.grid(True, linestyle='--', alpha=0.5)
    canvas.draw()

def on_closing():
    if ser and ser.is_open: ser.close()
    window.destroy()

# --- CONSTRUCTION DE LA FENÊTRE ---
window = tk.Tk()
window.title("Moniteur Vigne - Données Réelles")
window.geometry("900x700")
window.config(bg="#f0f0f0")

# 1. HEADER (Les chiffres)
frame_top = tk.Frame(window, bg="white", bd=2, relief="groove")
frame_top.pack(fill="x", padx=10, pady=10)

def make_stat(parent, title):
    f = tk.Frame(parent, bg="white")
    f.pack(side="left", expand=True, fill="both")
    tk.Label(f, text=title, font=("Arial", 9, "bold"), fg="gray", bg="white").pack()
    l = tk.Label(f, text="--", font=("Arial", 18, "bold"), bg="white")
    l.pack()
    return l

lbl_temp = make_stat(frame_top, "TEMPÉRATURE")
lbl_hum = make_stat(frame_top, "HUMIDITÉ")
lbl_ndvi = make_stat(frame_top, "NDVI")
lbl_etat = make_stat(frame_top, "ÉTAT")

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
read_serial_data()
window.mainloop()