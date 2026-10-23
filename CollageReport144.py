import io
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageOps, ImageGrab, ImageColor

APP_NAME = "CollageReport144"
SUPPORTED = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp", ".gif")

class CollageReport144:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1120x760")
        self.root.minsize(900, 620)
        self.images = []
        self.bg = "#FFFFFF"
        self.dark = False
        self.gap = tk.IntVar(value=16)
        self.columns = tk.IntVar(value=2)
        self.output_width = tk.IntVar(value=1800)
        self.variation_count = tk.IntVar(value=3)
        self.ratio = tk.StringVar(value="Original")
        self.fit_mode = tk.StringVar(value="Conter sem cortar")
        self.align_x = tk.StringVar(value="Centro")
        self.align_y = tk.StringVar(value="Centro")
        self.status = tk.StringVar(value="Adicione imagens ou cole uma imagem com Ctrl+V.")
        self._build_ui()
        self.root.bind("<Control-v>", self.paste_clipboard)
        self.root.bind("<Control-V>", self.paste_clipboard)
        self.root.bind("<Delete>", self.remove_selected)

    def _build_ui(self):
        self.root.configure(bg="#F4F6F8")
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        self.style = style
        self._apply_theme()

        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill="both", expand=True)
        self.outer = outer

        header = ttk.Frame(outer)
        header.pack(fill="x", pady=(0, 12))
        title_row = ttk.Frame(header)
        title_row.pack(fill="x")
        ttk.Label(title_row, text="CollageReport144", style="Title.TLabel").pack(side="left")
        self.dark_button = ttk.Button(title_row, text="☾ Modo dark", command=self.toggle_dark)
        self.dark_button.pack(side="right")
        ttk.Label(header, text="Monte pranchas proporcionais para relatórios Word — local, offline e sem banco de dados.", style="Sub.TLabel").pack(anchor="w", pady=(4, 0))

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=(0, 10))
        ttk.Button(actions, text="＋ Adicionar imagens", command=self.add_files, style="Accent.TButton").pack(side="left")
        ttk.Button(actions, text="Colar imagem  Ctrl+V", command=self.paste_clipboard).pack(side="left", padx=(7, 0))
        ttk.Button(actions, text="Remover", command=self.remove_selected).pack(side="left", padx=(7, 0))
        ttk.Button(actions, text="Limpar", command=self.clear_all).pack(side="left", padx=(7, 0))

        body = ttk.Frame(outer)
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body, width=330)
        left.pack(side="left", fill="y", padx=(0, 14))
        left.pack_propagate(False)
        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="IMAGENS", style="Section.TLabel").pack(anchor="w", pady=(0, 5))
        list_frame = ttk.Frame(left)
        list_frame.pack(fill="x")
        self.listbox = tk.Listbox(list_frame, width=36, height=10, selectmode=tk.SINGLE,
                                  font=("Segoe UI", 9), relief="flat", highlightthickness=1,
                                  activestyle="dotbox")
        self.list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.list_scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.list_scroll.pack(side="right", fill="y")
        reorder = ttk.Frame(left)
        reorder.pack(fill="x", pady=(6, 12))
        ttk.Button(reorder, text="↑ Subir", command=lambda: self.move_selected(-1)).pack(side="left", fill="x", expand=True)
        ttk.Button(reorder, text="↓ Descer", command=lambda: self.move_selected(1)).pack(side="left", fill="x", expand=True, padx=(6, 0))

        ttk.Label(left, text="AJUSTES INDIVIDUAIS", style="Section.TLabel").pack(anchor="w", pady=(0, 5))
        settings = ttk.Frame(left)
        settings.pack(fill="x")
        self._setting_row(settings, 0, "Proporção da célula", self.ratio, ["Original", "1:1", "4:3", "3:2", "16:9", "9:16"])
        self._setting_row(settings, 1, "Ajuste da imagem", self.fit_mode, ["Conter sem cortar", "Preencher cortando"])
        self._setting_row(settings, 2, "Alinhamento horizontal", self.align_x, ["Esquerda", "Centro", "Direita"])
        self._setting_row(settings, 3, "Alinhamento vertical", self.align_y, ["Acima", "Centro", "Abaixo"])
        self._setting_row(settings, 4, "Colunas base", self.columns, ["1", "2", "3", "4", "5", "6"])
        ttk.Label(settings, text="Espaçamento (px)").grid(row=5, column=0, sticky="w", pady=3)
        ttk.Spinbox(settings, from_=0, to=100, increment=2, width=8, textvariable=self.gap, command=self.refresh_preview).grid(row=5, column=1, sticky="ew", pady=3)
        ttk.Label(settings, text="Largura de saída (px)").grid(row=6, column=0, sticky="w", pady=3)
        ttk.Combobox(settings, textvariable=self.output_width, values=(1200, 1600, 1800, 2000, 2400, 3000), width=8, state="readonly").grid(row=6, column=1, sticky="ew", pady=3)
        ttk.Label(settings, text="Variações a gerar (3–10)").grid(row=7, column=0, sticky="w", pady=3)
        ttk.Spinbox(settings, from_=3, to=10, increment=1, width=8, textvariable=self.variation_count).grid(row=7, column=1, sticky="ew", pady=3)
        settings.columnconfigure(1, weight=1)

        ttk.Button(left, text="Cor de fundo", command=self.choose_bg).pack(fill="x", pady=(9, 0))
        ttk.Button(left, text="Atualizar prévia", command=self.refresh_preview).pack(fill="x", pady=(6, 0))

        ttk.Label(right, text="PRÉ-VISUALIZAÇÃO", style="Section.TLabel").pack(anchor="w", pady=(0, 5))
        self.preview_area = tk.Canvas(right, highlightthickness=0)
        self.preview_area.pack(fill="both", expand=True)
        self.preview_area.bind("<Configure>", lambda e: self._draw_preview())

        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(10, 0))
        ttk.Label(footer, textvariable=self.status, style="Sub.TLabel").pack(side="left", fill="x", expand=True)
        ttk.Button(footer, text="Exportar variações", command=self.export_variations, style="Accent.TButton").pack(side="right")
        ttk.Button(footer, text="Exportar PNG", command=self.export_png).pack(side="right", padx=(0, 7))
        ttk.Button(footer, text="Criar Word", command=self.export_docx).pack(side="right", padx=(0, 7))
        self._refresh_list()

    def _setting_row(self, parent, row, label, variable, values):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
        cb = ttk.Combobox(parent, textvariable=variable, values=values, width=15, state="readonly")
        cb.grid(row=row, column=1, sticky="ew", pady=3)
        cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_preview())

    def _apply_theme(self):
        dark = self.dark
        bg = "#17191C" if dark else "#F4F6F8"
        panel = "#22262B" if dark else "#FFFFFF"
        fg = "#F1F3F5" if dark else "#202124"
        muted = "#AAB2BD" if dark else "#667085"
        border = "#3A4149" if dark else "#D0D5DD"
        self.root.configure(bg=bg)
        s = self.style
        s.configure("TFrame", background=bg)
        s.configure("TLabel", background=bg, foreground=fg, font=("Segoe UI", 9))
        s.configure("Title.TLabel", background=bg, foreground=fg, font=("Segoe UI", 17, "bold"))
        s.configure("Sub.TLabel", background=bg, foreground=muted, font=("Segoe UI", 9))
        s.configure("Section.TLabel", background=bg, foreground=muted, font=("Segoe UI", 9, "bold"))
        s.configure("TButton", font=("Segoe UI", 9), padding=(8, 6), background=panel, foreground=fg)
        s.map("TButton", background=[("active", "#3B82F6" if dark else "#E5E7EB")])
        s.configure("Accent.TButton", font=("Segoe UI", 9, "bold"), padding=(10, 7), background="#2563EB", foreground="#FFFFFF")
        s.map("Accent.TButton", background=[("active", "#1D4ED8")])
        s.configure("TCombobox", fieldbackground=panel, background=panel, foreground=fg, arrowcolor=fg)
        s.configure("TSpinbox", fieldbackground=panel, background=panel, foreground=fg, arrowcolor=fg)
        s.configure("Vertical.TScrollbar", background=panel, troughcolor=bg)
        if hasattr(self, "listbox"):
            self.listbox.configure(bg=panel, fg=fg, selectbackground="#2563EB", selectforeground="#FFFFFF",
                                   highlightbackground=border, highlightcolor="#2563EB")
        if hasattr(self, "preview_area"):
            self.preview_area.configure(bg="#30343A" if dark else "#E8EAED")
        if hasattr(self, "dark_button"):
            self.dark_button.configure(text="☀ Modo claro" if dark else "☾ Modo dark")

    def toggle_dark(self):
        self.dark = not self.dark
        self._apply_theme()
        self._draw_preview()

    def add_files(self):
        paths = filedialog.askopenfilenames(title="Selecione imagens", filetypes=[
            ("Imagens", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp *.gif"),
            ("Todos os arquivos", "*.*")])
        added = 0
        for path in paths:
            try:
                with Image.open(path) as source:
                    source.seek(0)
                    im = ImageOps.exif_transpose(source).convert("RGB")
                self.images.append((im.copy(), os.path.basename(path)))
                added += 1
            except Exception as exc:
                messagebox.showwarning(APP_NAME, f"Não foi possível abrir:\n{path}\n\n{exc}")
        self._refresh_list()
        self.status.set(f"{added} imagem(ns) adicionada(s). Total: {len(self.images)}.")

    def paste_clipboard(self, event=None):
        try:
            item = ImageGrab.grabclipboard()
            if isinstance(item, Image.Image):
                im = ImageOps.exif_transpose(item).convert("RGB")
                self.images.append((im.copy(), f"Imagem colada {len(self.images)+1}"))
                self._refresh_list()
                self.status.set(f"Imagem colada. Total: {len(self.images)}.")
            elif isinstance(item, list):
                paths = [p for p in item if isinstance(p, str) and p.lower().endswith(SUPPORTED)]
                for path in paths:
                    try:
                        with Image.open(path) as source:
                            source.seek(0)
                            im = ImageOps.exif_transpose(source).convert("RGB")
                        self.images.append((im.copy(), os.path.basename(path)))
                    except Exception:
                        pass
                self._refresh_list()
                self.status.set(f"Imagens da área de transferência adicionadas. Total: {len(self.images)}.")
                if not paths:
                    messagebox.showinfo(APP_NAME, "A área de transferência não contém uma imagem reconhecida.")
            else:
                messagebox.showinfo(APP_NAME, "Copie uma imagem e tente Ctrl+V novamente.")
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Falha ao colar imagem:\n{exc}")
        return "break"

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for i, (_, label) in enumerate(self.images, 1):
            self.listbox.insert(tk.END, f"{i:02d}  {label}")
        self._draw_preview()

    def remove_selected(self, event=None):
        selection = self.listbox.curselection()
        if not selection:
            return
        del self.images[selection[0]]
        self._refresh_list()
        self.status.set(f"Imagem removida. Total: {len(self.images)}.")

    def clear_all(self):
        if self.images and messagebox.askyesno(APP_NAME, "Remover todas as imagens?"):
            self.images.clear()
            self._refresh_list()
            self.status.set("Lista limpa.")

    def move_selected(self, direction):
        selection = self.listbox.curselection()
        if not selection:
            return
        old = selection[0]
        new = old + direction
        if not 0 <= new < len(self.images):
            return
        self.images[old], self.images[new] = self.images[new], self.images[old]
        self._refresh_list()
        self.listbox.selection_set(new)

    def choose_bg(self):
        color = colorchooser.askcolor(color=self.bg, title="Cor de fundo")[1]
        if color:
            self.bg = color
            self._draw_preview()

    def _ratio_value(self, im):
        value = self.ratio.get()
        if value == "Original":
            return im.width / max(1, im.height)
        w, h = value.split(":")
        return int(w) / int(h)

    def _cell_dimensions(self, width, ratio, cols, rows, gap):
        cell_w = max(1, (width - gap * (cols + 1)) // cols)
        cell_h = max(1, int(cell_w / ratio))
        return cell_w, cell_h

    def _paste_aligned(self, canvas, im, box, mode, align_x, align_y):
        x, y, w, h = box
        if mode == "Preencher cortando":
            # Fit cover then crop based on requested alignment.
            scale = max(w / im.width, h / im.height)
            nw, nh = max(w, int(round(im.width * scale))), max(h, int(round(im.height * scale)))
            resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
            max_x, max_y = nw - w, nh - h
            if align_x == "Esquerda":
                cx = 0
            elif align_x == "Direita":
                cx = max_x
            else:
                cx = max_x // 2
            if align_y == "Acima":
                cy = 0
            elif align_y == "Abaixo":
                cy = max_y
            else:
                cy = max_y // 2
            crop = resized.crop((cx, cy, cx + w, cy + h))
            canvas.paste(crop, (x, y))
        else:
            # Fit contain and place image according to horizontal/vertical alignment.
            scale = min(w / im.width, h / im.height)
            nw, nh = max(1, int(round(im.width * scale))), max(1, int(round(im.height * scale)))
            resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
            if align_x == "Esquerda":
                px = x
            elif align_x == "Direita":
                px = x + w - nw
            else:
                px = x + (w - nw) // 2
            if align_y == "Acima":
                py = y
            elif align_y == "Abaixo":
                py = y + h - nh
            else:
                py = y + (h - nh) // 2
            canvas.paste(resized, (px, py))

    def make_collage(self, cols=None, order=None):
        if not self.images:
            raise ValueError("Adicione pelo menos uma imagem.")
        n = len(self.images)
        cols = max(1, min(6, int(cols if cols is not None else self.columns.get())))
        gap = max(0, min(100, int(self.gap.get())))
        width = max(600, min(5000, int(self.output_width.get())))
        ordered = self.images if order is None else [self.images[i] for i in order]
        rows = (n + cols - 1) // cols

        # Every tile in the collage uses a common aspect ratio. In Original mode,
        # use the first image's ratio for a consistent grid.
        if self.ratio.get() == "Original":
            first = ordered[0][0]
            ratio = first.width / max(1, first.height)
        else:
            ratio = self._ratio_value(ordered[0][0])
        cell_w, cell_h = self._cell_dimensions(width, ratio, cols, rows, gap)
        total_h = gap + rows * cell_h + gap * rows
        canvas = Image.new("RGB", (width, total_h), self.bg)
        for idx, (im, _) in enumerate(ordered):
            r, c = divmod(idx, cols)
            x = gap + c * (cell_w + gap)
            y = gap + r * (cell_h + gap)
            self._paste_aligned(canvas, im, (x, y, cell_w, cell_h),
                                self.fit_mode.get(), self.align_x.get(), self.align_y.get())
        return canvas

    def refresh_preview(self):
        self._draw_preview()
        self.status.set("Pré-visualização atualizada.")

    def _draw_preview(self):
        if not hasattr(self, "preview_area"):
            return
        self.preview_area.delete("all")
        if not self.images:
            self.preview_area.create_text(max(1, self.preview_area.winfo_width())//2,
                                          max(1, self.preview_area.winfo_height())//2,
                                          text="Adicione imagens para visualizar a prancha",
                                          fill="#AAB2BD" if self.dark else "#667085",
                                          font=("Segoe UI", 12))
            return
        try:
            collage = self.make_collage()
            max_w = max(100, self.preview_area.winfo_width() - 30)
            max_h = max(100, self.preview_area.winfo_height() - 30)
            scale = min(max_w / collage.width, max_h / collage.height)
            preview = collage.resize((max(1, int(collage.width * scale)), max(1, int(collage.height * scale))), Image.Resampling.LANCZOS)
            self._preview_photo = ImageTk.PhotoImage(preview)
            self.preview_area.create_image(self.preview_area.winfo_width()//2,
                                           self.preview_area.winfo_height()//2,
                                           image=self._preview_photo, anchor="center")
        except Exception as exc:
            self.preview_area.create_text(12, 12, anchor="nw", text=f"Prévia indisponível:\n{exc}", fill="#B42318")

    def _save_image(self, collage, path):
        ext = PathSuffix(path)
        if ext in (".jpg", ".jpeg"):
            collage.save(path, format="JPEG", quality=95, optimize=True, dpi=(300, 300))
        else:
            collage.save(path, format="PNG", optimize=True, dpi=(300, 300))

    def export_png(self):
        try:
            collage = self.make_collage()
        except Exception as exc:
            messagebox.showinfo(APP_NAME, str(exc))
            return
        path = filedialog.asksaveasfilename(title="Salvar prancha", defaultextension=".png",
                                            initialfile="CollageReport144.png",
                                            filetypes=[("Imagem PNG", "*.png"), ("Imagem JPEG", "*.jpg")])
        if not path:
            return
        try:
            self._save_image(collage, path)
            self.status.set(f"Prancha exportada: {path}")
            messagebox.showinfo(APP_NAME, f"Prancha salva:\n{path}")
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Falha ao salvar:\n{exc}")

    def export_variations(self):
        if not self.images:
            messagebox.showinfo(APP_NAME, "Adicione pelo menos uma imagem.")
            return
        try:
            count = max(3, min(10, int(self.variation_count.get())))
            base_cols = max(1, min(6, int(self.columns.get())))
        except Exception:
            count, base_cols = 3, 2
        folder = filedialog.askdirectory(title="Escolha a pasta para salvar as variações")
        if not folder:
            return
        try:
            # Build up to 10 meaningfully distinct variants: vary column count and image order.
            n = len(self.images)
            saved = []
            for i in range(count):
                cols = max(1, min(6, 1 + ((base_cols - 1 + i) % 6)))
                if i == 0:
                    order = list(range(n))
                elif i % 3 == 1:
                    order = list(reversed(range(n)))
                elif i % 3 == 2:
                    order = list(range(0, n, 2)) + list(range(1, n, 2))
                else:
                    shift = i % n
                    order = list(range(shift, n)) + list(range(shift))
                collage = self.make_collage(cols=cols, order=order)
                path = os.path.join(folder, f"CollageReport144_variacao_{i+1:02d}.png")
                collage.save(path, format="PNG", optimize=True, dpi=(300, 300))
                saved.append(path)
            self.status.set(f"{len(saved)} variações exportadas para {folder}")
            messagebox.showinfo(APP_NAME, f"Foram criadas {len(saved)} variações PNG em:\n{folder}")
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Falha ao gerar variações:\n{exc}")

    def export_docx(self):
        try:
            collage = self.make_collage()
        except Exception as exc:
            messagebox.showinfo(APP_NAME, str(exc))
            return
        path = filedialog.asksaveasfilename(title="Criar documento Word", defaultextension=".docx",
                                            initialfile="CollageReport144.docx",
                                            filetypes=[("Documento Word", "*.docx")])
        if not path:
            return
        try:
            from docx import Document
            from docx.shared import Inches
            bio = io.BytesIO()
            collage.save(bio, format="PNG", dpi=(300, 300))
            bio.seek(0)
            doc = Document()
            section = doc.sections[0]
            usable_width = section.page_width - section.left_margin - section.right_margin
            doc.add_picture(bio, width=usable_width)
            doc.save(path)
            self.status.set(f"Documento Word criado: {path}")
            messagebox.showinfo(APP_NAME, f"Documento Word criado:\n{path}")
        except ImportError:
            messagebox.showerror(APP_NAME, "Instale as dependências com instalar_dependencias.bat e tente novamente.")
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Falha ao criar Word:\n{exc}")

def PathSuffix(path):
    return os.path.splitext(path)[1].lower()

def main():
    root = tk.Tk()
    CollageReport144(root)
    root.mainloop()

if __name__ == "__main__":
    main()
