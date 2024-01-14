import os
import tkinter as tk
import threading
import time
import matplotlib.pyplot as plt
import matplotlib
import winsound
from brainaccess.utils import acquisition
from brainaccess.core.eeg_manager import EEGManager

matplotlib.use("TKAgg", force=True)

def create_gui():
    gui = tk.Tk()
    gui.title("Duomenų rinkimo programa")

    canvas = tk.Canvas(gui, width=200, height=200, bg="white")
    canvas.pack()

    def change_dot_color(color):
        canvas.itemconfig(dot, fill=color)
        
    folder_label = tk.Label(gui, text="Aplanko pavadinimas:")
    folder_label.pack()
    folder_entry = tk.Entry(gui)
    folder_entry.pack()

    file_label = tk.Label(gui, text="Failo pavadinimas:")
    file_label.pack()
    file_entry = tk.Entry(gui)
    file_entry.pack()

    def play_beep():
        winsound.Beep(500, 250)

    dot = canvas.create_oval(90, 90, 110, 110, fill="white")

    connection_label = tk.Label(gui, text="Neprisijungta", fg="black")
    connection_label.pack()

    beep_var = tk.BooleanVar()
    beep_var.set(True)
    beep_checkbox = tk.Checkbutton(gui, text="Įjungti garsinio signalo funkciją", variable=beep_var)
    beep_checkbox.pack()

    plot_var = tk.BooleanVar()
    plot_var.set(False)
    plot_checkbox = tk.Checkbutton(gui, text="Rodyti grafiką", variable=plot_var)
    plot_checkbox.pack()

    sleep_label = tk.Label(gui, text="Įrašo laiko intervalas:")
    sleep_label.pack()
    sleep_entry = tk.Entry(gui)
    sleep_entry.pack()

    loop_label = tk.Label(gui, text="Įrašų kiekis:")
    loop_label.pack()
    loop_entry = tk.Entry(gui)
    loop_entry.pack()

    def start_eeg_manager():
        change_dot_color("white")
        connection_label.config(text="Jungiamasi prie įrenginio", fg="blue")
        gui.update()  
        time.sleep(2)

        try:
            sleep_duration = float(sleep_entry.get())
            loop_count = int(loop_entry.get())
                
            with EEGManager() as mgr:
                for x in range(loop_count):
                    eeg.setup(mgr, port='COM3', cap=cap)
                    change_dot_color("yellow")
                    connection_label.config(text="Renkami duomenys", fg="blue")
                    gui.update() 
                    eeg.start_acquisition()
                    play_beep() if beep_var.get() else None
                    time.sleep(sleep_duration)
                    eeg.annotate('1')
                    eeg.get_mne()
                    eeg.stop_acquisition()
                    if plot_var.get():
                        eeg.data.mne_raw.drop_channels(["Accel_x","Accel_y","Accel_z","Digital","Sample"])
                        eeg.data.mne_raw.filter(1, 40).plot(scalings='auto', verbose=False)
                        plt.ion() 
                        plt.pause(0.001) 
                        plt.show()
                        plt.ioff() 
                    change_dot_color("light green")
                    connection_label.config(text="Duomenys surinkti", fg="green")
                    gui.update()
                    mgr.disconnect()
                    save_folder = folder_entry.get()
                    save_file = file_entry.get()
                    if not os.path.exists(save_folder):
                        os.makedirs(save_folder)
                    full_file_name = f'{save_file}_{x+1}'
                    eeg.data.mne_raw.save(f'{save_folder}/{full_file_name}-raw.fif', overwrite=True)
        except Exception as e:
            connection_label.config(text=f"Error: {str(e)}", fg="red")
            change_dot_color("white")
            gui.update()


    
    start_button = tk.Button(gui, text="Pradėti duomenų rinkimą", command=start_eeg_manager)
    start_button.pack()

    gui.mainloop()

eeg = acquisition.EEG()
cap = {
    0: "F3",
    1: "F4",
    2: "C3",
    3: "C4",
    4: "P3",
    5: "P4",
    6: "O1",
    7: "O2"
}

gui_thread = threading.Thread(target=create_gui)
gui_thread.start()
