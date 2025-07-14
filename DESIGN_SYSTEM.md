# Smart MCQ Platform - Design System & Style Guide

This document defines the design system and UI patterns for the Smart MCQ Platform, ensuring consistency across all pages and components.

## 🎨 Color Palette

### Primary Colors
```css
/* Brand Colors */
--color-primary: #2563eb;        /* Blue - Primary actions, links */
--color-primary-light: #3b82f6;  /* Lighter blue for hover states */
--color-primary-dark: #1d4ed8;   /* Darker blue for active states */

/* Success/Questions */
--color-success: #059669;        /* Green - Success states, Questions section */
--color-success-light: #10b981;  /* Light green for hover */
--color-success-dark: #047857;   /* Dark green for active */

/* Info/Sessions */
--color-info: #0891b2;           /* Cyan - Info states, Sessions section */
--color-info-light: #06b6d4;     /* Light cyan for hover */
--color-info-dark: #0e7490;      /* Dark cyan for active */

/* Warning */
--color-warning: #d97706;        /* Orange - Warning states, upcoming items */
--color-warning-light: #f59e0b;  /* Light orange for hover */
--color-warning-dark: #b45309;   /* Dark orange for active */

/* Danger */
--color-danger: #dc2626;         /* Red - Error states, failed items */
--color-danger-light: #ef4444;   /* Light red for hover */
--color-danger-dark: #b91c1c;    /* Dark red for active */
```

### Neutral Colors
```css
/* Text Colors */
--color-gray-900: #111827;       /* Primary text - headings, important content */
--color-gray-700: #374151;       /* Secondary text - body content */
--color-gray-500: #6b7280;       /* Muted text - captions, placeholders */
--color-gray-400: #9ca3af;       /* Disabled text */

/* Background Colors */
--color-white: #ffffff;          /* Primary background */
--color-gray-50: #f9fafb;        /* Light background - table headers */
--color-gray-100: #f3f4f6;       /* Subtle background - cards, sections */

/* Border Colors */
--color-border: #f1f5f9;         /* Default borders */
--color-border-light: #e5e7eb;   /* Light borders */
--color-border-strong: #d1d5db;  /* Strong borders */
```

### Background Opacity Variants
```css
/* For badges and status indicators */
.bg-opacity-10 { --bs-bg-opacity: 0.1; }
.bg-opacity-20 { --bs-bg-opacity: 0.2; }
```

## 📐 Spacing System

### Margin & Padding Scale
```css
/* Custom spacing utilities */
.mb-6 { margin-bottom: 3rem !important; }    /* 48px - Large section spacing */
.g-4 { gap: 1.5rem !important; }             /* 24px - Grid gaps */
.gap-2 { gap: 0.5rem !important; }           /* 8px - Small gaps (buttons) */
.gap-3 { gap: 1rem !important; }             /* 16px - Medium gaps */

/* Standard Bootstrap spacing should be used for everything else */
/* .p-4 = 1.5rem (24px) - Card padding */
/* .py-3 = 1rem (16px) - Header/footer padding */
/* .px-4 = 1.5rem (24px) - Horizontal padding */
```

## 🔘 Border Radius

### Radius Scale
```css
/* Border radius system */
--radius-sm: 0.375rem;   /* 6px - Small elements, buttons */
--radius-md: 0.5rem;     /* 8px - Default radius */
--radius-lg: 0.75rem;    /* 12px - Cards, larger elements */
--radius-xl: 1rem;       /* 16px - Large containers */

/* Implementation */
.rounded-3 { border-radius: 0.75rem !important; }  /* Cards */
.btn { border-radius: 0.375rem; }                   /* Buttons */
.card { border-radius: 0.75rem; }                   /* Cards */
```

## 🌟 Shadows & Elevation

### Shadow System
```css
/* Shadow hierarchy */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);                    /* Subtle elements */
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);                  /* Cards, dropdowns */
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);                /* Modals, popovers */
--shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); /* Hover states */

/* Implementation */
.shadow-sm { box-shadow: var(--shadow-sm); }
.card { box-shadow: var(--shadow-md); }
.hover-lift:hover { box-shadow: var(--shadow-hover); }
```

## 📝 Typography System

### Font Hierarchy
```css
/* Headings */
.h1, h1 { font-size: 2.25rem; font-weight: 700; color: var(--color-gray-900); }  /* Page titles */
.h2, h2 { font-size: 1.875rem; font-weight: 600; color: var(--color-gray-900); } /* Section titles */
.h3, h3 { font-size: 1.5rem; font-weight: 600; color: var(--color-gray-900); }   /* Card titles */
.h4, h4 { font-size: 1.25rem; font-weight: 600; color: var(--color-gray-900); }  /* Subsection titles */
.h5, h5 { font-size: 1.125rem; font-weight: 500; color: var(--color-gray-900); } /* Component titles */
.h6, h6 { font-size: 1rem; font-weight: 500; color: var(--color-gray-900); }     /* Small titles */

/* Body Text */
.text-body { color: var(--color-gray-700); }      /* Default body text */
.text-muted { color: var(--color-gray-500); }     /* Secondary text */
.text-caption { font-size: 0.875rem; color: var(--color-gray-500); } /* Small text */

/* Special Fonts */
.font-monospace { 
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace !important; 
}
```

## 🃏 Card Design Patterns

### Standard Card Structure
```html
<!-- Basic Card -->
<div class="card border-0 shadow-sm">
  <div class="card-header bg-white py-3">
    <h5 class="mb-0">Card Title</h5>
  </div>
  <div class="card-body p-4">
    <!-- Card content -->
  </div>
</div>

<!-- Interactive Card with Hover -->
<div class="card border-0 shadow-sm h-100 hover-lift">
  <div class="card-body p-4">
    <!-- Card content -->
  </div>
</div>
```

### Card Specifications
```css
.card {
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  box-shadow: var(--shadow-md);
}

.card-header {
  background-color: var(--color-white);
  border-bottom: 1px solid var(--color-border);
  padding: 1rem 1.5rem;
}

.card-body {
  padding: 1.5rem; /* For standard cards */
}

.hover-lift {
  transition: all 0.2s ease-in-out;
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}
```

## 📊 Table Design Standards

### Modern Table Structure
```html
<div class="card border-0 shadow-sm">
  <div class="card-header bg-white py-3">
    <h5 class="mb-0">Table Title</h5>
  </div>
  <div class="card-body p-0">
    <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead class="bg-light">
          <tr>
            <th class="border-0 ps-4">Column 1</th>
            <th class="border-0">Column 2</th>
            <th class="border-0 pe-4">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="ps-4">Data</td>
            <td>Data</td>
            <td class="pe-4">Actions</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>
```

### Table Styling Rules
```css
.table > :not(caption) > * > * {
  padding: 1rem 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.table-hover > tbody > tr:hover > * {
  background-color: #f8fafc;
}

.table thead th {
  background-color: var(--color-gray-50);
  font-weight: 500;
  color: var(--color-gray-700);
  border-bottom: 1px solid var(--color-border);
}

/* First and last column padding */
.ps-4 { padding-left: 1.5rem !important; }
.pe-4 { padding-right: 1.5rem !important; }
```

## 🏷️ Badge & Status Design

### Status Badge System
```html
<!-- Success Status -->
<span class="badge bg-success bg-opacity-10 text-success border border-success">Active</span>

<!-- Warning Status -->
<span class="badge bg-warning bg-opacity-10 text-warning border border-warning">Pending</span>

<!-- Info Status -->
<span class="badge bg-info bg-opacity-10 text-info border border-info">Scheduled</span>

<!-- Danger Status -->
<span class="badge bg-danger bg-opacity-10 text-danger border border-danger">Failed</span>
```

### Badge Styling
```css
.badge {
  font-weight: 500;
  font-size: 0.75rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
}

/* Code badges (access codes, etc.) */
.font-monospace.bg-light {
  background-color: var(--color-gray-100) !important;
  color: var(--color-gray-700);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}
```

## 🔘 Button Design System

### Button Hierarchy
```html
<!-- Primary Actions -->
<button class="btn btn-primary">Primary Action</button>
<button class="btn btn-outline-primary">Secondary Action</button>

<!-- Contextual Actions -->
<button class="btn btn-success">Success Action</button>
<button class="btn btn-outline-success">Success Secondary</button>

<button class="btn btn-info">Info Action</button>
<button class="btn btn-outline-info">Info Secondary</button>

<!-- Sizes -->
<button class="btn btn-sm btn-primary">Small Button</button>
<button class="btn btn-primary">Default Button</button>
<button class="btn btn-lg btn-primary">Large Button</button>
```

### Button Styling Rules
```css
.btn {
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 0.15s ease-in-out;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

/* Remove transform on outline button hover to prevent layout shift */
.btn-outline-primary:hover,
.btn-outline-success:hover,
.btn-outline-info:hover {
  transform: none;
}
```

## 🎯 Icon Usage Guidelines

### Icon System
- **Use SVG icons** for scalability and customization
- **Standard sizes**: 16px (small), 24px (default), 32px (large), 48px (empty states)
- **Consistent stroke width**: 1.5-2px for line icons
- **Color**: Inherit from parent or use semantic colors

### Icon Implementation
```html
<!-- Standard Icon -->
<svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="24" height="24">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="..."></path>
</svg>

<!-- Icon with background -->
<div class="bg-primary bg-opacity-10 p-3 rounded-3">
  <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="..."></path>
  </svg>
</div>
```

### Icon Size Classes
```css
.w-6 { width: 1.5rem; }    /* 24px - Standard icons */
.h-6 { height: 1.5rem; }   /* 24px - Standard icons */
.w-12 { width: 3rem; }     /* 48px - Large icons for empty states */
.h-12 { height: 3rem; }    /* 48px - Large icons for empty states */
```

## 📱 Layout Patterns

### Page Header Pattern
```html
<div class="d-flex justify-content-between align-items-center mb-6">
  <div>
    <h1 class="h3 mb-0 text-gray-900">Page Title</h1>
    <p class="mb-0 text-muted">Page description or breadcrumb</p>
  </div>
  <div class="d-flex align-items-center gap-3">
    <!-- Action buttons or status indicators -->
  </div>
</div>
```

### Grid Layout Pattern
```html
<div class="row g-4 mb-6">
  <div class="col-lg-4 col-md-6">
    <!-- Card content -->
  </div>
  <!-- Repeat for other cards -->
</div>
```

### Empty State Pattern
```html
<div class="card-body text-center py-5">
  <div class="mb-3">
    <svg class="w-12 h-12 text-muted mx-auto"><!-- Icon --></svg>
  </div>
  <h6 class="text-muted mb-2">No items yet</h6>
  <p class="text-muted mb-4">Description of the empty state</p>
  <a href="#" class="btn btn-primary">Primary Action</a>
</div>
```

## 🔄 Animation Guidelines

### Transition Standards
```css
/* Standard transition for interactive elements */
.transition-standard {
  transition: all 0.15s ease-in-out;
}

/* Hover lift effect for cards */
.hover-lift {
  transition: all 0.2s ease-in-out;
}

.hover-lift:hover {
  transform: translateY(-2px);
}
```

## 📋 Form Design Patterns

### Form Layout
```html
<div class="row g-3">
  <div class="col-md-6">
    <label for="input1" class="form-label">Label</label>
    <input type="text" class="form-control" id="input1">
  </div>
  <div class="col-md-6">
    <label for="input2" class="form-label">Label</label>
    <input type="text" class="form-control" id="input2">
  </div>
</div>
```

## 🎨 Implementation Checklist

### For New Pages/Components:
- [ ] Use consistent color palette
- [ ] Apply proper spacing (mb-6 for sections, g-4 for grids)
- [ ] Use shadow-sm for cards
- [ ] Apply hover-lift to interactive cards
- [ ] Use proper typography hierarchy
- [ ] Implement consistent table styling
- [ ] Use status badge system for state indicators
- [ ] Apply border-radius consistently (0.75rem for cards)
- [ ] Use SVG icons with proper sizing
- [ ] Implement empty states with proper messaging

### Code Review Points:
- [ ] Colors match the defined palette
- [ ] Spacing follows the system
- [ ] Cards have proper elevation and hover states
- [ ] Tables follow the borderless design
- [ ] Typography uses proper hierarchy
- [ ] Icons are consistent in size and style
- [ ] Animations are subtle and purposeful
- [ ] Mobile responsiveness is maintained

This design system ensures consistency across the entire Smart MCQ Platform and provides clear guidelines for future development.