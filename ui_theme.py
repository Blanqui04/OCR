#!/usr/bin/env python3
"""
Modern UI Theme for OCR Viewer Application
Provides a professional, modern look and feel
"""

import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger(__name__)

class ModernTheme:
    """Modern theme configuration for the OCR Viewer application"""
    
    def __init__(self):
        self.colors = {
            # Main colors
            'primary': '#2563eb',      # Blue
            'primary_dark': '#1e40af',
            'primary_light': '#3b82f6',
            
            # Background colors
            'bg_primary': '#ffffff',    # White
            'bg_secondary': '#f8fafc',  # Light gray
            'bg_dark': '#1e293b',      # Dark gray
            
            # Text colors
            'text_primary': '#1e293b',  # Dark gray
            'text_secondary': '#64748b', # Medium gray
            'text_light': '#94a3b8',   # Light gray
            
            # Accent colors
            'success': '#10b981',      # Green
            'warning': '#f59e0b',      # Orange
            'error': '#ef4444',        # Red
            'info': '#06b6d4',         # Cyan
            
            # Confidence level colors
            'confidence_high': '#10b981',    # Green
            'confidence_medium': '#f59e0b',  # Orange
            'confidence_low': '#ef4444',     # Red
            'confidence_selected': '#3b82f6' # Blue
        }
        
        self.fonts = {
            'default': ('Segoe UI', 9),
            'heading': ('Segoe UI', 12, 'bold'),
            'small': ('Segoe UI', 8),
            'monospace': ('Consolas', 9)
        }
        
    def apply_theme(self, root):
        """Apply the modern theme to the application"""
        try:
            # Configure the style
            style = ttk.Style()
            
            # Use a modern theme as base
            available_themes = style.theme_names()
            if 'winnative' in available_themes:
                style.theme_use('winnative')
            elif 'clam' in available_themes:
                style.theme_use('clam')
            
            # Configure root window
            root.configure(bg=self.colors['bg_primary'])
            
            # Configure ttk styles
            self.configure_button_style(style)
            self.configure_frame_style(style)
            self.configure_label_style(style)
            self.configure_entry_style(style)
            self.configure_treeview_style(style)
            self.configure_notebook_style(style)
            self.configure_progressbar_style(style)
            
            logger.info("Modern theme applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying theme: {str(e)}")
            
    def configure_button_style(self, style):
        """Configure button styles"""
        style.configure(
            'Modern.TButton',
            background=self.colors['primary'],
            foreground='white',
            borderwidth=0,
            focuscolor=self.colors['primary_dark'],
            relief='flat',
            font=self.fonts['default']
        )
        
        style.map(
            'Modern.TButton',
            background=[
                ('active', self.colors['primary_light']),
                ('pressed', self.colors['primary_dark'])
            ]
        )
        
    def configure_frame_style(self, style):
        """Configure frame styles"""
        style.configure(
            'Modern.TFrame',
            background=self.colors['bg_primary'],
            relief='flat',
            borderwidth=0
        )
        
        style.configure(
            'Card.TLabelframe',
            background=self.colors['bg_secondary'],
            relief='solid',
            borderwidth=1,
            labelmargins=(10, 5)
        )
        
        style.configure(
            'Card.TLabelframe.Label',
            background=self.colors['bg_secondary'],
            foreground=self.colors['text_primary'],
            font=self.fonts['heading']
        )
        
    def configure_label_style(self, style):
        """Configure label styles"""
        style.configure(
            'Modern.TLabel',
            background=self.colors['bg_primary'],
            foreground=self.colors['text_primary'],
            font=self.fonts['default']
        )
        
        style.configure(
            'Heading.TLabel',
            background=self.colors['bg_primary'],
            foreground=self.colors['text_primary'],
            font=self.fonts['heading']
        )
        
        style.configure(
            'Small.TLabel',
            background=self.colors['bg_primary'],
            foreground=self.colors['text_secondary'],
            font=self.fonts['small']
        )
        
    def configure_entry_style(self, style):
        """Configure entry styles"""
        style.configure(
            'Modern.TEntry',
            fieldbackground='white',
            borderwidth=1,
            relief='solid',
            insertcolor=self.colors['primary'],
            font=self.fonts['default']
        )
        
        style.map(
            'Modern.TEntry',
            focuscolor=[('focus', self.colors['primary'])]
        )
        
    def configure_treeview_style(self, style):
        """Configure treeview styles"""
        style.configure(
            'Modern.Treeview',
            background='white',
            foreground=self.colors['text_primary'],
            fieldbackground='white',
            borderwidth=1,
            relief='solid',
            font=self.fonts['default']
        )
        
        style.configure(
            'Modern.Treeview.Heading',
            background=self.colors['bg_secondary'],
            foreground=self.colors['text_primary'],
            relief='flat',
            font=self.fonts['default']
        )
        
        style.map(
            'Modern.Treeview',
            background=[('selected', self.colors['primary_light'])],
            foreground=[('selected', 'white')]
        )
        
    def configure_notebook_style(self, style):
        """Configure notebook (tabs) styles"""
        style.configure(
            'Modern.TNotebook',
            background=self.colors['bg_primary'],
            borderwidth=0
        )
        
        style.configure(
            'Modern.TNotebook.Tab',
            background=self.colors['bg_secondary'],
            foreground=self.colors['text_primary'],
            padding=(12, 8),
            font=self.fonts['default']
        )
        
        style.map(
            'Modern.TNotebook.Tab',
            background=[
                ('selected', self.colors['primary']),
                ('active', self.colors['primary_light'])
            ],
            foreground=[
                ('selected', 'white'),
                ('active', 'white')
            ]
        )
        
    def configure_progressbar_style(self, style):
        """Configure progressbar styles"""
        style.configure(
            'Modern.Horizontal.TProgressbar',
            background=self.colors['primary'],
            troughcolor=self.colors['bg_secondary'],
            borderwidth=0,
            lightcolor=self.colors['primary'],
            darkcolor=self.colors['primary']
        )
        
    def get_confidence_color(self, confidence: float) -> str:
        """Get color based on confidence level"""
        if confidence >= 0.9:
            return self.colors['confidence_high']
        elif confidence >= 0.7:
            return self.colors['confidence_medium']
        else:
            return self.colors['confidence_low']
            
    def get_rgba_color(self, color: str, alpha: float = 1.0) -> str:
        """Convert hex color to RGBA with alpha transparency"""
        # Remove # if present
        color = color.lstrip('#')
        
        # Convert hex to RGB
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        return f"rgba({r}, {g}, {b}, {alpha})"
