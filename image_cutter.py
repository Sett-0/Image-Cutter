from tkinter import *
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from PIL import Image, ImageTk, ImageDraw

tk = Tk()
icon = Image.open('brush_icon.png')
icon.resize((50, 50), resample=Image.Resampling.LANCZOS)
photo_icon = ImageTk.PhotoImage(icon)
tk.wm_iconphoto(True, photo_icon)
tk.title('Poster Cutter')
w = 700
h = 550
posx = tk.winfo_screenwidth()  // 2 - w // 2
posy = tk.winfo_screenheight() // 2 - h // 2
tk.geometry(f'{w}x{h}+{posx}+{posy}')
tk.resizable(False, False)

# ---> Настройки кнопки <---
main_f1 = Frame(master=tk)
main_f1.pack(fill=X, anchor=N)

image_path = ''
image_file = ''
image_dir  = ''
image_name = ''
image_extension = ''
image_selected  = False
img = None
photo_img = None
a4_w_px_600dpi = 4960
a4_h_px_600dpi = 7016

def select_file():
    global image_path
    global image_file
    global image_dir
    global image_name
    global image_extension
    global image_selected
    global img
    
    image_path = fd.askopenfilename()
    image_file = image_path.split('/')[-1]
    image_dir  = image_path.removesuffix(image_file)
    image_name = image_file[:image_file.rfind('.')]
    image_extension = image_file[image_file.rfind('.')+1:]
    image_selected  = True
    update_image_preview()
    
def update_image_preview(_img=None, nrows=1, ncols=1):
    global image_path
    global photo_img
    global a4_w_px_600dpi
    global a4_h_px_600dpi
    img_preview = None
    
    if _img == None: img_preview = Image.open(image_path)
    else           : img_preview = _img
    
    width = 280
    wpercent = width / float(img_preview.size[0])
    height   = int(float(img_preview.size[1]) * wpercent)
    
    row_px = int(a4_h_px_600dpi * (height / img_preview.size[1]))
    col_px = int(a4_w_px_600dpi * (width  / img_preview.size[0]))
    
    img_preview = img_preview.resize((width, height), resample=Image.Resampling.LANCZOS)
    
    draw = ImageDraw.Draw(img_preview)
    for i in range(1, nrows):
        draw.line((0, i*row_px, width, i*row_px),  fill='blue', width=2)
    for j in range(1, ncols):
        draw.line((j*col_px, 0, j*col_px, height), fill='blue', width=2)
    del draw
    
    photo_img = ImageTk.PhotoImage(img_preview)
    f2_image.config(image=photo_img)
  
def reshape_image(w_sm, h_sm):
    global image_path
    global image_dir
    global image_name
    global image_extension
    global img
    
    if not image_selected:
        mb.showerror(title='Изображение не выбрано', message='Сначала выберите изображение.')
        return
    
    if w_sm == '': 
        w_sm = 50.0
        row1_width_text.set(w_sm)
    else: 
        w_sm = float(w_sm.replace(',', '.'))
        
    if h_sm == '': 
        h_sm = 7/5 * w_sm
        row2_height_text.set(h_sm)
    else: 
        h_sm = float(h_sm.replace(',', '.'))
    
    # Из-за полей при печати ~2.5 см постера обрезается
    w_sm += 2.5
    h_sm += 2.5
    
    pix_per_sm_600dpi = 236
    width  = int(pix_per_sm_600dpi * w_sm)
    height = int(pix_per_sm_600dpi * h_sm)
        
    img = Image.open(image_path)
    img = img.resize((width, height), resample=Image.Resampling.LANCZOS)
    
    nrows = int(h_sm // 29.7 + 1)
    ncols = int(w_sm // 21   + 1)
    
    # img.save(fp=(image_dir + f'{image_name} {w_sm}см x {h_sm}см.{image_extension}'))
    update_image_preview(img, nrows, ncols)
    
def cut_image():
    global image_path
    global image_selected
    global img
    global a4_w_px_600dpi
    global a4_h_px_600dpi
    
    if not image_selected:
        mb.showerror(title='Изображение не выбрано', message='Сначала выберите изображение.')
        return
    
    ncols = img.size[0] // a4_w_px_600dpi + 1
    nrows = img.size[1] // a4_h_px_600dpi + 1
    
    count = 1
    for i in range(nrows):
        for j in range(ncols):
            if j == ncols - 1 and i == nrows - 1:
                img1 = img.crop((j*a4_w_px_600dpi, i*a4_h_px_600dpi, img.size[0], img.size[1]))
                bg = Image.new(mode='RGB', size=(a4_w_px_600dpi, a4_h_px_600dpi), color='white')
                bg.paste(img1, (0, 0))
                img1 = bg
            elif j == ncols - 1:
                img1 = img.crop((j*a4_w_px_600dpi, i*a4_h_px_600dpi, img.size[0], (i+1)*a4_h_px_600dpi))
                bg = Image.new(mode='RGB', size=(a4_w_px_600dpi, a4_h_px_600dpi), color='white')
                bg.paste(img1, (0, 0))
                img1 = bg
            elif i == nrows - 1:
                img1 = img.crop((j*a4_w_px_600dpi, i*a4_h_px_600dpi, (j+1)*a4_w_px_600dpi, img.size[1]))
                bg = Image.new(mode='RGB', size=(a4_w_px_600dpi, a4_h_px_600dpi), color='white')
                bg.paste(img1, (0, 0))
                img1 = bg
            else:
                img1 = img.crop((j*a4_w_px_600dpi, i*a4_h_px_600dpi, (j+1)*a4_w_px_600dpi, (i+1)*a4_h_px_600dpi))
            
            img1.save(fp=(f'{image_dir}{image_name}_{count}{image_extension}'))
            count += 1
            
    mb.showinfo(title='Готово', message=(f'Изображение успешно разрезано на {count - 1} частей.\n' + 
                                         f'Все части помещены в директорию с исходным изображением.'))
            
open_file_btn = Button(master=main_f1, height=2, text='Выбрать изображение', fg='red', bg='#e6e6e6',
                       font=('TkDefaultFont', 12, 'normal'), command=select_file)
open_file_btn.pack(padx=10, pady=10, fill=X)

main_f2 = Frame(master=tk)
main_f2.pack(expand=1, fill=BOTH, anchor=N)


# ---> Настройки размера <---
f1 = LabelFrame(master=main_f2, text='Настройки размера', font=('TkDefaultFont', 12, 'normal'), fg='green')
f1.pack(expand=1, side=LEFT, fill=X, anchor=N, padx=10)

row1 = Frame(master=f1, padx=10)
row1_label       = Label(master=row1, text='Ширина (см): ', font=('TkDefaultFont', 12, 'normal'), fg='black')
row1_width_text  = StringVar(value=50)
row1_width_entry = Entry(master=row1, textvariable=row1_width_text, justify='center')

row1.pack(expand=1, anchor=W, pady=5)
row1_label.pack(side=LEFT)
row1_width_entry.pack(side=LEFT, anchor=W)

row2 = Frame(master=f1, padx=10)
row2_label        = Label(master=row2, text='Высота (см): ', font=('TkDefaultFont', 12, 'normal'), fg='black')
row2_height_text  = StringVar(value=70)
row2_height_entry = Entry(master=row2, textvariable=row2_height_text, justify='center')

row2.pack(expand=1, anchor=W, pady=5)
row2_label.pack(side=LEFT)
row2_height_entry.pack(side=LEFT, anchor=W)

row3 = Frame(master=f1, padx=10)
row3_reshape_image_btn = Button(master=row3, height=2, text='Применить размеры', fg='red', bg='#e6e6e6', font=('TkDefaultFont', 12, 'normal'), 
                                command=lambda: reshape_image(row1_width_text.get(), row2_height_text.get()))

row3.pack(expand=1, fill=X, anchor=W, pady=5)
row3_reshape_image_btn.pack(padx=10, pady=10, fill=X)



# ---> Предпросмотр <---
f2 = LabelFrame(master=main_f2, text='Предпросмотр', font=('TkDefaultFont', 12, 'normal'), fg='green')
f2.pack(expand=1, side=LEFT, fill=X, anchor=N, padx=10)

img = Image.new(mode='RGB', size=(280, int(1.5*280)), color='black')
photo_img = ImageTk.PhotoImage(img)
f2_image = Label(master=f2, image=photo_img)
f2_image.pack(expand=1, side=TOP, fill=BOTH)


# ---> Разбить изображение <---
row4 = Frame(master=f1, padx=10)
row4_cut_image_button = Button(master=row4, height=10, text='Разбить\nизображение', fg='red', bg='#e6e6e6',
                          font=('TkDefaultFont', 14, 'normal'), command=cut_image)

row4.pack(expand=1, fill=BOTH, anchor=W, pady=5)
row4_cut_image_button.pack(expand=1, padx=10, pady=10, fill=BOTH)


if __name__ == '__main__':
    tk.mainloop()