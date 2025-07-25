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
            # Main colors - Light blue theme
            'primary': '#3b82f6',      # Light blue
            'primary_dark': '#2563eb', # Medium blue
            'primary_light': '#93c5fd', # Very light blue
            
            # Background colors
            'bg_primary': '#ffffff',    # Pure white
            'bg_secondary': '#f0f9ff',  # Very light blue
            'bg_tertiary': '#e0f2fe',   # Light blue
            'bg_accent': '#bfdbfe',     # Soft blue
            
            # Text colors
            'text_primary': '#1e3a8a',  # Dark blue
            'text_secondary': '#1e40af', # Medium blue
            'text_light': '#64748b',    # Gray
            'text_white': '#ffffff',    # White
            
            # Accent colors - Friendly palette
            'success': '#22c55e',       # Friendly green
            'warning': '#f59e0b',       # Warm orange
            'error': '#ef4444',         # Soft red
            'info': '#06b6d4',          # Cyan
            
            # Confidence level colors
            'confidence_high': '#22c55e',    # Green
            'confidence_medium': '#f59e0b',  # Orange
            'confidence_low': '#ef4444',     # Red
            'confidence_selected': '#93c5fd' # Light blue
        }
        
        self.fonts = {
            'default': ('Segoe UI', 10),      # Slightly larger for friendliness
            'heading': ('Segoe UI', 14, 'bold'),
            'subheading': ('Segoe UI', 12, 'bold'),
            'small': ('Segoe UI', 9),
            'monospace': ('Consolas', 10),
            'button': ('Segoe UI', 10)
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
        # Primary button style - Light blue
        style.configure(
            'Modern.TButton',
            background=self.colors['primary'],
            foreground=self.colors['text_white'],
            borderwidth=1,
            focuscolor=self.colors['primary_dark'],
            relief='solid',
            font=self.fonts['button'],
            padding=(12, 8)
        )
        
        style.map(
            'Modern.TButton',
            background=[
                ('active', self.colors['primary_light']),
                ('pressed', self.colors['primary_dark']),
                ('disabled', self.colors['bg_accent'])
            ],
            foreground=[
                ('disabled', self.colors['text_light'])
            ]
        )
        
        # Accent button style - for special actions
        style.configure(
            'Accent.TButton',
            background=self.colors['bg_tertiary'],
            foreground=self.colors['text_primary'],
            borderwidth=1,
            relief='solid',
            font=self.fonts['button'],
            padding=(12, 8)
        )
        
        style.map(
            'Accent.TButton',
            background=[
                ('active', self.colors['bg_accent']),
                ('pressed', self.colors['primary_light'])
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
        
        # Card style frames with light blue theme
        style.configure(
            'Card.TLabelframe',
            background=self.colors['bg_secondary'],
            relief='solid',
            borderwidth=1,
            bordercolor=self.colors['bg_accent'],
            labelmargins=(15, 8)
        )
        
        style.configure(
            'Card.TLabelframe.Label',
            background=self.colors['bg_secondary'],
            foreground=self.colors['text_primary'],
            font=self.fonts['subheading'],
            padding=(5, 5)
        )
        
        # Panel style for main sections
        style.configure(
            'Panel.TLabelframe',
            background=self.colors['bg_tertiary'],
            relief='solid',
            borderwidth=2,
            bordercolor=self.colors['primary_light'],
            labelmargins=(20, 10)
        )
        
        style.configure(
            'Panel.TLabelframe.Label',
            background=self.colors['bg_tertiary'],
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
