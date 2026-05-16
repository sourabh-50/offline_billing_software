import customtkinter as ctk
from tkinter import messagebox

class ctkAutocompleteEntry(ctk.CTkEntry):
    def __init__(self, parent, suggestions=None, suggestions_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.suggestions = suggestions if suggestions else []
        self.suggestions_callback = suggestions_callback
        self._lb_open = False
        self._lb = None
        
        self._current_selection = -1
        self._btns = []
        
        self.bind("<KeyRelease>", self._on_keyrelease)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Down>", self._on_arrow_down)
        self.bind("<Up>", self._on_arrow_up)
        self.bind("<Return>", self._on_enter)

    def set_suggestions(self, suggestions):
        self.suggestions = sorted(list(set(suggestions))) if suggestions else []

    def _on_keyrelease(self, event):
        if event.keysym in ("Up", "Down", "Return", "Escape", "Tab"):
            return
            
        value = self.get()
        if not value or len(value) < 1:
            self._close_lb()
            return

        suggestions = self.suggestions
        if self.suggestions_callback:
            suggestions = self.suggestions_callback()

        hits = [item for item in suggestions if value.lower() in item.lower()]
        if hits:
            self._show_lb(hits)
        else:
            self._close_lb()

    def _show_lb(self, hits):
        if not self._lb_open:
            self._lb = ctk.CTkToplevel(self.winfo_toplevel())
            self._lb.overrideredirect(True)
            self._lb.attributes("-topmost", True)
            self._lb.configure(fg_color=("#ffffff", "#2d2d2d"))
            self._lb_open = True
            
        for widget in self._lb.winfo_children():
            widget.destroy()
        self._btns = []
        self._current_selection = -1
            
        inner = ctk.CTkFrame(self._lb, border_width=1, border_color=("gray80", "gray30"), corner_radius=12, fg_color=("#ffffff", "#2d2d2d"))
        inner.pack(fill="both", expand=True)
            
        for i, hit in enumerate(hits[:8]):
            btn = ctk.CTkButton(inner, text=hit, font=("Helvetica", 13), fg_color="transparent", 
                                text_color=("black", "white"), hover_color=("#3b82f6", "#3b82f6"),
                                anchor="w", height=35, corner_radius=8, command=lambda h=hit: self._select_hit(h))
            btn.pack(fill="x", padx=5, pady=2)
            self._btns.append(btn)
            
        self.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 2
        width = max(self.winfo_width(), 220)
        height = len(hits[:8]) * 40 + 15
        
        screen_height = self.winfo_screenheight()
        if y + height > screen_height:
            y = self.winfo_rooty() - height - 2

        self._lb.geometry(f"{width}x{height}+{x}+{y}")
        self._lb.lift()
        self._lb.attributes("-topmost", True)

    def _on_arrow_down(self, event):
        if self._lb_open and self._btns:
            self._update_selection((self._current_selection + 1) % len(self._btns))

    def _on_arrow_up(self, event):
        if self._lb_open and self._btns:
            self._update_selection((self._current_selection - 1) % len(self._btns))

    def _update_selection(self, index):
        if self._current_selection != -1:
            self._btns[self._current_selection].configure(fg_color="transparent")
        self._current_selection = index
        self._btns[self._current_selection].configure(fg_color="#3b82f6", text_color="white")

    def _on_enter(self, event):
        if self._lb_open and self._current_selection != -1:
            self._select_hit(self._btns[self._current_selection].cget("text"))
            return "break"

    def _select_hit(self, hit):
        self.delete(0, 'end')
        self.insert(0, hit)
        self._close_lb()
        # Trigger any bound event
        self.event_generate("<<AutocompleteSelected>>")

    def _close_lb(self, event=None):
        if self._lb:
            self._lb.destroy()
            self._lb = None
        self._lb_open = False

    def _on_focus_out(self, event):
        # Small delay to allow button click
        self.after(200, self._close_lb)

    def _on_focus_in(self, event):
        pass
