from threading import Thread

CLOSE_WINDOW = False


def thread_func():
    import tkinter as tk
    import random
    import time

    def on_close():
        global CLOSE_WINDOW
        CLOSE_WINDOW = True

    root = tk.Tk()
    canvas = tk.Canvas(root, height=500, width=500)
    canvas.pack()

    centers = {
        'T3': [100, 250],
        'T4': [400, 250],
        'O1': [200, 350],
        'O2': [300, 350],
        'EDA': [250, 150]
    }
    sizes = {
        'T3': random.random(),
        'T4': random.random(),
        'O1': random.random(),
        'O2': random.random(),
        'EDA': random.random(),
    }
    items = {}
    for ch in centers:
        items_xys = {}
        items_xys[ch] = [centers[ch][0]-100*sizes[ch],
                         centers[ch][1]-100*sizes[ch],
                         centers[ch][0]+100*sizes[ch],
                         centers[ch][1]+100*sizes[ch]]
        items[ch] = canvas.create_oval(*items_xys[ch], fill="#ff3300", outline="#ff3300")

    for ch in centers:
        canvas.create_text(centers[ch], text=ch, font=('Helvetica','15','bold'))

    def callback():
        sizes = {
            'T3': random.random(),
            'T4': random.random(),
            'O1': random.random(),
            'O2': random.random(),
            'EDA': random.random(),
        }
        for ch in centers:
            items_xys = {}
            items_xys[ch] = [centers[ch][0]-100*sizes[ch],
                             centers[ch][1]-100*sizes[ch],
                             centers[ch][0]+100*sizes[ch],
                             centers[ch][1]+100*sizes[ch]]
            canvas.coords(items[ch], *items_xys[ch])
            canvas.itemconfig(items[ch], fill='#ff3300', outline='#ff3300')

    root.protocol("WM_DELETE_WINDOW", on_close)

    while True:
        root.update_idletasks()
        root.update()
        if CLOSE_WINDOW is True:
            break
        callback()
        time.sleep(0.1)


t1 = Thread(target=thread_func)

t1.start()
