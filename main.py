
#Binômes : BARRY Mamadou Bailo et DIAMANKA Mamadou

from tkinter import *  # type: ignore # Importation de toutes les classes et fonctions de tkinter
from tkinter.filedialog import askopenfilename  # Importation de la fonction askopenfilename pour ouvrir une boîte de dialogue de sélection de fichier
import csv  # Importation du module csv pour lire les données du fichier CSV
import pert  # Importation du module pert contenant la fonction main pour l'analyse PERT

# Fonction appelée lorsque le bouton "Importer des données" est cliqué
def on_import():
    global lbl 
    nom_fichier = askopenfilename() 
    
    # Appel de la fonction main du module pert pour analyser les données du fichier sélectionné
    status = pert.main(nom_fichier)
    
    # Affichage du statut de l'importation (succès ou erreur) dans l'étiquette lbl
    if status == -1:
        lbl['text'] = 'ERREUR'
        lbl.config(foreground='red') 
    else:  # Sinon, l'importation des données a réussi
        lbl['text'] = 'Succès'
        lbl.config(foreground='green')  # Changement de la couleur du texte en vert pour indiquer un succès

# Fonction appelée lorsque la fenêtre est fermée
def on_close():
    root.destroy()
# Création de la fenêtre principale de l'application tkinter
root = Tk()
root.title('DIAGRAMME DE PERT') 

# Création d'un cadre dans la fenêtre pour placer les éléments
frame = Frame(root, height=200, width=250)
frame.pack()

# Création d'un bouton pour importer des données
btn = Button(frame, text="Importer des données", command=on_import)
btn.place(relx=0.5, rely=0.4, anchor=CENTER) 

# Création d'une étiquette pour afficher le statut de l'importation
lbl = Label(frame, text=' ')
lbl.place(relx=0.5, rely=0.6, anchor=CENTER)  # Positionnement de l'étiquette au centre du cadre

# Définition de l'action à effectuer lorsque la fenêtre est fermée
root.protocol('WM_DELETE_WINDOW', on_close)

# Lancement de la boucle principale de l'application tkinter
root.mainloop()
