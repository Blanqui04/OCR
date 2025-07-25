#!/usr/bin/env python3
"""
Modern UI Theme for OCR Viewer Application
Provides a professional, modern look and feel with light blue and white color scheme
"""

import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger(__name__)


class ModernTheme:
    """
    Modern UI theme with light blue and white color scheme for a friendly appearance
    """
    
    def __init__(self):
        """Initialize theme with light blue and white color palette"""
        self.colors = {
            # Primary colors - light blue and white
            'primary': '#4A90E2',           # Light blue
            'primary_light': '#7FB8E6',     # Lighter blue
            'primary_dark': '#2E6BC0',      # Darker blue
            
            # Background colors - white and very light blue
            'bg_primary': '#FFFFFF',        # Pure white
            'bg_secondary': '#F8FAFB',      # Very light blue-gray
            'bg_tertiary': '#E8F4FD',       # Light blue tint
            'bg_accent': '#E3F2FD',         # Soft blue accent
            
            # Text colors for good contrast
            'text_primary': '#2C3E50',      # Dark blue-gray
            'text_secondary': '#34495E',    # Medium blue-gray
            'text_light': '#7F8C8D',        # Light gray
            'text_white': '#FFFFFF',        # White text
            
            # Status colors
            'success': '#27AE60',           # Green
            'warning': '#F39C12',           # Orange
            'error': '#E74C3C',             # Red
            'info': '#3498DB',              # Blue
            
            # Border and hover colors
            'border': '#BDC3C7',            # Light gray border
            'hover': '#D6E9F7',             # Light blue hover
            'selected': '#B3D9F2',          # Medium blue selection
            
            # Confidence level colors
            'confidence_high': '#27AE60',    # Green
            'confidence_medium': '#F39C12',  # Orange
            'confidence_low': '#E74C3C',     # Red
            'confidence_selected': '#B3D9F2' # Light blue
        }
        
        # Font definitions for friendly appearance
        self.fonts = {
            'heading': ('Segoe UI', 14, 'bold'),
            'subheading': ('Segoe UI', 12, 'bold'),
            'normal': ('Segoe UI', 10, 'normal'),
            'small': ('Segoe UI', 9, 'normal'),
            'large': ('Segoe UI', 16, 'bold')
        }
    
    def apply_theme(self, root):
        """Apply the modern theme to the tkinter application"""
        try:
            style = ttk.Style(root)
            
            # Configure the theme name
            style.theme_use('clam')  # Use clam as base theme for better customization
            
            # Apply all style configurations
            self.configure_button_style(style)
            self.configure_frame_style(style)
            self.configure_label_style(style)
            self.configure_entry_style(style)
            self.configure_treeview_style(style)
            self.configure_progressbar_style(style)
            self.configure_scrollbar_style(style)
            self.configure_notebook_style(style)
            
            # Configure root window
            root.configure(bg=self.colors['bg_primary'])
            
            logger.info("Modern theme applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying theme: {e}")
            raise
    
    def configure_button_style(self, style):
        """Configure button styles with light blue theme"""
        # Primary button style
        style.configure(
            'Modern.TButton',
            font=self.fonts['normal'],
            padding=(16, 8),
            relief='flat',
            borderwidth=0,
            focuscolor='none'
        )
        
        # Map button states for modern look
        style.map(
            'Modern.TButton',
            background=[
                ('active', self.colors['hover']),
                ('pressed', self.colors['primary_dark']),
                ('!disabled', self.colors['primary'])
            ],
            foreground=[
                ('!disabled', self.colors['text_white'])
            ],
            borderwidth=[
                ('pressed', 0),
                ('!pressed', 0)
            ]
        )
        
        # Secondary button style (light blue outline)
        style.configure(
            'Secondary.TButton',
            font=self.fonts['normal'],
            padding=(14, 7),
            relief='solid',
            borderwidth=2,
            focuscolor='none'
        )
        
        style.map(
            'Secondary.TButton',
            background=[
                ('active', self.colors['bg_accent']),
                ('pressed', self.colors['primary_light']),
                ('!disabled', self.colors['bg_primary'])
            ],
            foreground=[
                ('!disabled', self.colors['primary'])
            ],
            bordercolor=[
                ('!disabled', self.colors['primary'])
            ]
        )
        
        # Success button style
        style.configure(
            'Success.TButton',
            font=self.fonts['normal'],
            padding=(16, 8),
            relief='flat',
            borderwidth=0,
            focuscolor='none'
        )
        
        style.map(
            'Success.TButton',
            background=[
                ('active', '#2ECC71'),
                ('pressed', '#229954'),
                ('!disabled', self.colors['success'])
            ],
            foreground=[
                ('!disabled', self.colors['text_white'])
            ]
        )
    
    def configure_frame_style(self, style):
        """Configure frame styles with light blue theme"""
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
        """Configure label styles with consistent formatting"""
        # Primary labels
        style.configure(
            'Modern.TLabel',
            background=self.colors['bg_primary'],
            foreground=self.colors['text_primary'],
            font=self.fonts['normal'],
            padding=(8, 6)
        )
        
        # Heading labels
        style.configure(
            'Heading.TLabel',
            background=self.colors['bg_primary'],
            foreground=self.colors['text_primary'],
            font=self.fonts['heading'],
            padding=(10, 8)
        )
        
        # Subheading labels
        style.configure(
            'Subheading.TLabel',
            background=self.colors['bg_secondary'],
            foreground=self.colors['text_primary'],
            font=self.fonts['subheading'],
            padding=(8, 6)
        )
        
        # Info labels with light blue accent
        style.configure(
            'Info.TLabel',
            background=self.colors['bg_accent'],
            foreground=self.colors['text_secondary'],
            font=self.fonts['small'],
            padding=(10, 6),
            relief='flat',
            borderwidth=1
        )
        
        # Status labels
        style.configure(
            'Status.TLabel',
            background=self.colors['bg_tertiary'],
            foreground=self.colors['text_primary'],
            font=self.fonts['normal'],
            padding=(12, 8),
            relief='solid',
            borderwidth=1,
            bordercolor=self.colors['primary_light']
        )
    
    def configure_entry_style(self, style):
        """Configure entry widget styles"""
        style.configure(
            'Modern.TEntry',
            fieldbackground=self.colors['bg_primary'],
            foreground=self.colors['text_primary'],
            bordercolor=self.colors['border'],
            borderwidth=2,
            relief='solid',
            padding=(10, 8),
            font=self.fonts['normal']
        )
        
        style.map(
            'Modern.TEntry',
            bordercolor=[
                ('focus', self.colors['primary']),
                ('!focus', self.colors['border'])
            ],
            fieldbackground=[
                ('readonly', self.colors['bg_secondary']),
                ('!readonly', self.colors['bg_primary'])
            ]
        )
    
    def configure_treeview_style(self, style):
        """Configure treeview styles with light blue theme"""
        style.configure(
            'Modern.Treeview',
            background=self.colors['bg_primary'],
            foreground=self.colors['text_primary'],
            fieldbackground=self.colors['bg_primary'],
            bordercolor=self.colors['border'],
            borderwidth=1,
            relief='solid',
            font=self.fonts['normal'],
            rowheight=28
        )
        
        # Treeview heading style
        style.configure(
            'Modern.Treeview.Heading',
            background=self.colors['bg_accent'],
            foreground=self.colors['text_primary'],
            font=self.fonts['subheading'],
            relief='flat',
            borderwidth=1,
            bordercolor=self.colors['primary_light']
        )
        
        style.map(
            'Modern.Treeview',
            background=[
                ('selected', self.colors['selected'])
            ],
            foreground=[
                ('selected', self.colors['text_primary'])
            ]
        )
        
        style.map(
            'Modern.Treeview.Heading',
            background=[
                ('active', self.colors['hover']),
                ('pressed', self.colors['primary_light'])
            ]
        )
    
    def configure_progressbar_style(self, style):
        """Configure progressbar styles"""
        style.configure(
            'Modern.TProgressbar',
            troughcolor=self.colors['bg_accent'],
            background=self.colors['primary'],
            bordercolor=self.colors['border'],
            lightcolor=self.colors['primary_light'],
            darkcolor=self.colors['primary_dark'],
            borderwidth=1,
            relief='flat'
        )
    
    def configure_scrollbar_style(self, style):
        """Configure scrollbar styles"""
        style.configure(
            'Modern.TScrollbar',
            troughcolor=self.colors['bg_secondary'],
            background=self.colors['primary_light'],
            bordercolor=self.colors['border'],
            borderwidth=1,
            relief='flat',
            width=12
        )
        
        style.map(
            'Modern.TScrollbar',
            background=[
                ('active', self.colors['primary']),
                ('pressed', self.colors['primary_dark'])
            ]
        )
    
    def configure_notebook_style(self, style):
        """Configure notebook tab styles"""
        style.configure(
            'Modern.TNotebook',
            background=self.colors['bg_primary'],
            bordercolor=self.colors['border'],
            borderwidth=1,
            relief='solid'
        )
        
        style.configure(
            'Modern.TNotebook.Tab',
            background=self.colors['bg_secondary'],
            foreground=self.colors['text_primary'],
            font=self.fonts['normal'],
            padding=(15, 8),
            borderwidth=1,
            relief='solid'
        )
        
        style.map(
            'Modern.TNotebook.Tab',
            background=[
                ('selected', self.colors['bg_primary']),
                ('active', self.colors['hover']),
                ('!selected', self.colors['bg_secondary'])
            ],
            foreground=[
                ('selected', self.colors['primary']),
                ('!selected', self.colors['text_secondary'])
            ]
        )
    
    def get_text_color_for_confidence(self, confidence):
        """Get appropriate text color based on confidence level"""
        if confidence >= 0.8:
            return self.colors['confidence_high']
        elif confidence >= 0.6:
            return self.colors['confidence_medium']
        else:
            return self.colors['confidence_low']
    
    def get_background_color_for_confidence(self, confidence, selected=False):
        """Get appropriate background color based on confidence level"""
        if selected:
            return self.colors['confidence_selected']
        
        if confidence >= 0.8:
            return self.colors['bg_primary']
        elif confidence >= 0.6:
            return self.colors['bg_secondary']
        else:
            return self.colors['bg_tertiary']


# Create a global theme instance
theme = ModernTheme()


def apply_modern_theme(root):
    """Convenience function to apply the modern theme"""
    theme.apply_theme(root)
    return theme


def get_theme():
    """Get the current theme instance"""
    return theme
