"""
Modern UI Theme Manager for OCR Viewer
Creates a beautiful, modern interface with blue colors and rounded elements
Inspired by Apple and Microsoft design languages
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont

class ModernUITheme:
    def __init__(self):
        # Modern Blue Color Palette
        self.colors = {
            # Primary Blues
            'primary_blue': '#007AFF',        # iOS Blue
            'primary_blue_hover': '#0051D5',  # Darker blue for hover
            'primary_blue_pressed': '#004CCC', # Even darker for pressed
            
            # Secondary Blues
            'light_blue': '#E3F2FD',          # Very light blue background
            'medium_blue': '#BBDEFB',         # Medium blue accents
            'accent_blue': '#2196F3',         # Material Design Blue
            
            # Backgrounds
            'bg_primary': '#FFFFFF',          # Pure white
            'bg_secondary': '#F8F9FA',        # Light gray-blue
            'bg_tertiary': '#F0F4F8',         # Slightly blue-tinted white
            'bg_sidebar': '#F5F7FA',          # Sidebar background
            
            # Text Colors
            'text_primary': '#1D1D1F',        # Apple-style dark text
            'text_secondary': '#6E6E73',      # Medium gray text
            'text_tertiary': '#8E8E93',       # Light gray text
            'text_white': '#FFFFFF',          # White text
            
            # Borders and Dividers
            'border_light': '#E5E5E7',        # Light border
            'border_medium': '#D1D1D6',       # Medium border
            'divider': '#F2F2F7',            # Very light divider
            
            # Status Colors
            'success': '#34C759',             # Green
            'warning': '#FF9500',             # Orange
            'error': '#FF3B30',              # Red
            'info': '#5AC8FA',               # Light blue
        }
        
        # Typography
        self.fonts = {
            'heading_large': ('Segoe UI', 20, 'normal'),
            'heading_medium': ('Segoe UI', 16, 'normal'),
            'heading_small': ('Segoe UI', 14, 'normal'),
            'body_large': ('Segoe UI', 12, 'normal'),
            'body_medium': ('Segoe UI', 10, 'normal'),
            'body_small': ('Segoe UI', 9, 'normal'),
            'caption': ('Segoe UI', 8, 'normal'),
            'button_text': ('Segoe UI', 10, 'bold'),  # Changed from 600 to bold
            'code': ('Consolas', 10, 'normal'),
        }
        
        # Spacing and Sizing
        self.spacing = {
            'xs': 4,    # Extra small
            'sm': 8,    # Small
            'md': 12,   # Medium
            'lg': 16,   # Large
            'xl': 24,   # Extra large
            'xxl': 32,  # Double extra large
        }
        
        self.corner_radius = {
            'small': 6,
            'medium': 8,
            'large': 12,
            'extra_large': 16,
        }

    def configure_ttk_styles(self, root):
        """Configure TTK styles with modern design"""
        style = ttk.Style()
        
        # Configure theme
        style.theme_use('clam')
        
        # Configure modern button styles
        self._configure_button_styles(style)
        
        # Configure frame styles
        self._configure_frame_styles(style)
        
        # Configure notebook styles
        self._configure_notebook_styles(style)
        
        # Configure treeview styles
        self._configure_treeview_styles(style)
        
        # Configure other widgets
        self._configure_misc_styles(style)
        
    def _configure_button_styles(self, style):
        """Configure modern button styles"""
        # Primary button (Blue)
        style.configure('Primary.TButton',
                       background=self.colors['primary_blue'],
                       foreground=self.colors['text_white'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(16, 10),
                       font=self.fonts['button_text'],
                       relief='flat')
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['primary_blue_hover']),
                           ('pressed', self.colors['primary_blue_pressed']),
                           ('disabled', self.colors['border_medium'])])
        
        # Secondary button (Light blue)
        style.configure('Secondary.TButton',
                       background=self.colors['light_blue'],
                       foreground=self.colors['primary_blue'],
                       borderwidth=1,
                       focuscolor='none',
                       padding=(16, 10),
                       font=self.fonts['button_text'],
                       relief='flat')
        
        style.map('Secondary.TButton',
                 background=[('active', self.colors['medium_blue']),
                           ('pressed', self.colors['medium_blue'])])
        
        # Icon button (Compact with icon)
        style.configure('Icon.TButton',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(12, 8),
                       font=self.fonts['body_medium'],
                       relief='flat')
        
        style.map('Icon.TButton',
                 background=[('active', self.colors['bg_tertiary']),
                           ('pressed', self.colors['border_light'])])
        
        # Danger button (Red)
        style.configure('Danger.TButton',
                       background=self.colors['error'],
                       foreground=self.colors['text_white'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(16, 10),
                       font=self.fonts['button_text'],
                       relief='flat')
        
        style.map('Danger.TButton',
                 background=[('active', '#E6342A'),
                           ('pressed', '#D12B20')])
        
        # Success button (Green)
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground=self.colors['text_white'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(16, 10),
                       font=self.fonts['button_text'],
                       relief='flat')
        
        style.map('Success.TButton',
                 background=[('active', '#2FB344'),
                           ('pressed', '#2A9F3A')])

    def _configure_frame_styles(self, style):
        """Configure frame styles"""
        # Main frame
        style.configure('Modern.TFrame',
                       background=self.colors['bg_primary'],
                       relief='flat',
                       borderwidth=0)
        
        # Card frame (with subtle shadow effect)
        style.configure('Card.TFrame',
                       background=self.colors['bg_primary'],
                       relief='flat',
                       borderwidth=1)
        
        # Sidebar frame
        style.configure('Sidebar.TFrame',
                       background=self.colors['bg_sidebar'],
                       relief='flat',
                       borderwidth=0)
        
        # Toolbar frame
        style.configure('Toolbar.TFrame',
                       background=self.colors['bg_secondary'],
                       relief='flat',
                       borderwidth=0)

    def _configure_notebook_styles(self, style):
        """Configure notebook (tab) styles"""
        style.configure('Modern.TNotebook',
                       background=self.colors['bg_primary'],
                       borderwidth=0,
                       tabmargins=[0, 0, 0, 0])
        
        style.configure('Modern.TNotebook.Tab',
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_secondary'],
                       padding=[16, 8],
                       font=self.fonts['body_medium'],
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', self.colors['bg_primary']),
                           ('active', self.colors['bg_secondary'])],
                 foreground=[('selected', self.colors['text_primary']),
                           ('active', self.colors['text_primary'])])

    def _configure_treeview_styles(self, style):
        """Configure treeview styles"""
        style.configure('Modern.Treeview',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_primary'],
                       borderwidth=0,
                       font=self.fonts['body_medium'],
                       rowheight=32)
        
        style.configure('Modern.Treeview.Heading',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['body_medium'],
                       borderwidth=0,
                       relief='flat')
        
        style.map('Modern.Treeview',
                 background=[('selected', self.colors['light_blue'])],
                 foreground=[('selected', self.colors['text_primary'])])

    def _configure_misc_styles(self, style):
        """Configure other widget styles"""
        # Labels
        style.configure('Heading.TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['heading_medium'])
        
        style.configure('Subheading.TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_secondary'],
                       font=self.fonts['body_large'])
        
        style.configure('Caption.TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_tertiary'],
                       font=self.fonts['caption'])
        
        # Entry widgets
        style.configure('Modern.TEntry',
                       fieldbackground=self.colors['bg_primary'],
                       borderwidth=1,
                       relief='solid',
                       padding=8,
                       font=self.fonts['body_medium'])
        
        style.map('Modern.TEntry',
                 bordercolor=[('focus', self.colors['primary_blue']),
                           ('!focus', self.colors['border_light'])])
        
        # Progress bar
        style.configure('Modern.Horizontal.TProgressbar',
                       background=self.colors['primary_blue'],
                       troughcolor=self.colors['bg_tertiary'],
                       borderwidth=0,
                       lightcolor=self.colors['primary_blue'],
                       darkcolor=self.colors['primary_blue'])
        
        # Separator
        style.configure('Modern.TSeparator',
                       background=self.colors['divider'])

    def create_rounded_button(self, parent, text, command=None, style='primary', width=None, **kwargs):
        """Create a custom rounded button with modern styling"""
        # For now, use TTK button with appropriate style
        style_map = {
            'primary': 'Primary.TButton',
            'secondary': 'Secondary.TButton',
            'icon': 'Icon.TButton',
            'danger': 'Danger.TButton',
            'success': 'Success.TButton'
        }
        
        button = ttk.Button(parent, text=text, command=command, 
                           style=style_map.get(style, 'Primary.TButton'),
                           **kwargs)
        
        if width:
            button.configure(width=width)
            
        return button
    
    def create_modern_button(self, parent, text, command=None, style='primary', state='normal', **kwargs):
        """Create a modern styled button"""
        # Style mapping for different button types
        style_config = {
            'primary': {
                'bg': self.colors['primary_blue'],
                'fg': self.colors['text_white'],
                'active_bg': self.colors['primary_blue_hover'],
                'font': self.fonts['button_text']
            },
            'secondary': {
                'bg': self.colors['bg_tertiary'],
                'fg': self.colors['text_primary'],
                'active_bg': self.colors['medium_blue'],
                'font': self.fonts['button_text']
            },
            'success': {
                'bg': self.colors['success'],
                'fg': self.colors['text_white'],
                'active_bg': '#2EAD4A',
                'font': self.fonts['button_text']
            },
            'danger': {
                'bg': self.colors['error'],
                'fg': self.colors['text_white'],
                'active_bg': '#E5342B',
                'font': self.fonts['button_text']
            }
        }
        
        config = style_config.get(style, style_config['primary'])
        
        # Create button with modern styling
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=config['bg'],
            fg=config['fg'],
            font=config['font'],
            relief='flat',
            borderwidth=0,
            padx=20,
            pady=10,
            cursor='hand2',
            state=state,
            **kwargs
        )
        
        # Add hover effects
        def on_enter(event):
            if button['state'] != 'disabled':
                button.config(bg=config['active_bg'])
        
        def on_leave(event):
            if button['state'] != 'disabled':
                button.config(bg=config['bg'])
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def create_modern_notebook(self, parent, **kwargs):
        """Create a modern styled notebook widget"""
        notebook = ttk.Notebook(parent, **kwargs)
        return notebook
    
    def create_modern_treeview(self, parent, columns=None, **kwargs):
        """Create a modern styled treeview widget"""
        # Configure columns for structured data
        if columns is None:
            columns = ('element', 'description', 'value', 'tolerance')
        
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=15, **kwargs)
        
        # Configure column headers
        tree.heading('element', text='Nº Element')
        tree.heading('description', text='Descripció')
        tree.heading('value', text='Valor')
        tree.heading('tolerance', text='Tolerància')
        
        # Configure column widths
        tree.column('element', width=100, anchor='center')
        tree.column('description', width=300)
        tree.column('value', width=150, anchor='center')
        tree.column('tolerance', width=150, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the treeview and scrollbar
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return tree

    def create_card_frame(self, parent, title=None, has_shadow=False, padding=None, **kwargs):
        """Create a card-style frame with title"""
        # Remove has_shadow from kwargs since ttk.Frame doesn't support it
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'has_shadow'}
        
        # Main card frame - use appropriate style based on shadow preference
        frame_style = 'Card.TFrame' if has_shadow else 'Modern.TFrame'
        card = ttk.Frame(parent, style=frame_style, **filtered_kwargs)
        
        # Apply default padding if specified
        if padding is not None:
            card.configure(padding=padding)
        
        if title:
            # Title frame
            title_frame = ttk.Frame(card, style='Modern.TFrame')
            title_frame.pack(fill=tk.X, padx=self.spacing['lg'], pady=(self.spacing['lg'], 0))
            
            # Title label
            title_label = ttk.Label(title_frame, text=title, style='Heading.TLabel')
            title_label.pack(side=tk.LEFT)
            
            # Content frame
            content_frame = ttk.Frame(card, style='Modern.TFrame')
            content_frame.pack(fill=tk.BOTH, expand=True, padx=self.spacing['lg'], 
                              pady=(self.spacing['md'], self.spacing['lg']))
            
            return card, content_frame
        else:
            return card

    def create_icon_label(self, parent, icon, text, **kwargs):
        """Create a label with icon and text"""
        frame = ttk.Frame(parent, style='Modern.TFrame')
        
        # Icon (emoji for now, could be replaced with actual icons)
        icon_label = ttk.Label(frame, text=icon, font=self.fonts['heading_medium'])
        icon_label.pack(side=tk.LEFT, padx=(0, self.spacing['sm']))
        
        # Text
        text_label = ttk.Label(frame, text=text, font=self.fonts['body_medium'], **kwargs)
        text_label.pack(side=tk.LEFT)
        
        return frame

    def apply_hover_effect(self, widget, hover_color=None, normal_color=None):
        """Apply hover effect to a widget"""
        if not hover_color:
            hover_color = self.colors['bg_tertiary']
        if not normal_color:
            normal_color = self.colors['bg_primary']
            
        def on_enter(event):
            widget.configure(background=hover_color)
            
        def on_leave(event):
            widget.configure(background=normal_color)
            
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def create_status_bar(self, parent):
        """Create a modern status bar"""
        status_frame = ttk.Frame(parent, style='Toolbar.TFrame')
        
        # Status text
        status_var = tk.StringVar(value="✅ L'aplicació està llesta")
        status_label = ttk.Label(status_frame, textvariable=status_var, 
                                style='Caption.TLabel')
        status_label.pack(side=tk.LEFT, padx=self.spacing['md'])
        
        return status_frame, status_var

    def show_notification(self, parent, message, type='info', duration=3000):
        """Show a modern notification"""
        # Create notification window
        notification = tk.Toplevel(parent)
        notification.withdraw()  # Hide initially
        notification.overrideredirect(True)  # Remove window decorations
        
        # Configure based on type
        color_map = {
            'info': self.colors['info'],
            'success': self.colors['success'],
            'warning': self.colors['warning'],
            'error': self.colors['error']
        }
        
        icon_map = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        
        bg_color = color_map.get(type, self.colors['info'])
        icon = icon_map.get(type, 'ℹ️')
        
        # Create notification content
        notification.configure(bg=bg_color)
        
        frame = tk.Frame(notification, bg=bg_color, padx=16, pady=12)
        frame.pack()
        
        # Icon
        icon_label = tk.Label(frame, text=icon, bg=bg_color, fg='white',
                             font=self.fonts['body_large'])
        icon_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # Message
        msg_label = tk.Label(frame, text=message, bg=bg_color, fg='white',
                            font=self.fonts['body_medium'])
        msg_label.pack(side=tk.LEFT)
        
        # Position notification
        notification.update_idletasks()
        x = parent.winfo_rootx() + parent.winfo_width() - notification.winfo_width() - 20
        y = parent.winfo_rooty() + 20
        notification.geometry(f"+{x}+{y}")
        
        # Show notification
        notification.deiconify()
        
        # Auto-hide after duration
        notification.after(duration, notification.destroy)
        
        return notification
    
    def apply_style(self):
        """Apply the modern theme styles to ttk widgets globally"""
        style = ttk.Style()
        
        # Set the default theme as base
        style.theme_use('clam')
        
        # Configure notebook styles
        style.configure('TNotebook', 
                       background=self.colors['bg_primary'],
                       borderwidth=0)
        
        style.configure('TNotebook.Tab',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       padding=[20, 12],
                       borderwidth=0)
        
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['primary_blue']),
                           ('active', self.colors['accent_blue'])],
                 foreground=[('selected', 'white'),
                           ('active', 'white')])
        
        # Configure basic widget styles
        style.configure('TFrame',
                       background=self.colors['bg_primary'])
        
        style.configure('TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['body_medium'])
        
        # Configure scrollbar
        style.configure('TScrollbar',
                       background=self.colors['bg_secondary'],
                       troughcolor=self.colors['bg_primary'])
