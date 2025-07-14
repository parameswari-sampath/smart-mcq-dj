# Smart MCQ Platform - Design System & Style Guide

This document defines the design system and UI patterns for the Smart MCQ Platform, ensuring consistency across all pages and components.

## 🎨 Foundation Framework

### **shadcn/ui Integration**
The Smart MCQ Platform uses **shadcn/ui** as the foundational component library, providing:
- Pre-built, accessible components
- Tailwind CSS-based styling
- Consistent design tokens
- TypeScript support
- Customizable themes

### **Component Hierarchy**
1. **shadcn/ui Base Components** - Foundation layer
2. **Smart MCQ Custom Components** - Platform-specific extensions
3. **Page-Level Compositions** - Feature-specific layouts

### **Setup Requirements**
- Tailwind CSS configuration
- shadcn/ui component installation
- Custom theme configuration
- Component registry setup

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

### **shadcn/ui Radius System**
```css
/* Border radius system - following shadcn/ui tokens */
--radius: 0.5rem;        /* Default radius (8px) */

/* Implementation classes */
.rounded-sm { border-radius: calc(var(--radius) - 2px); }    /* 6px */
.rounded-md { border-radius: var(--radius); }                /* 8px */
.rounded-lg { border-radius: calc(var(--radius) + 2px); }    /* 10px */
.rounded-xl { border-radius: calc(var(--radius) + 4px); }    /* 12px */

/* Component-specific radius */
.btn { border-radius: var(--radius); }
.card { border-radius: calc(var(--radius) + 2px); }
.input { border-radius: calc(var(--radius) - 2px); }
```

## 🌟 Shadows & Elevation

### **shadcn/ui Shadow System**
```css
/* Shadow hierarchy - based on Tailwind CSS shadows */
--shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);    /* Default shadow */
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);                                  /* Subtle elements */
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1); /* Cards, dropdowns */
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1); /* Modals, popovers */
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1); /* Large modals */

/* Implementation with shadcn/ui classes */
.shadow { box-shadow: var(--shadow); }
.shadow-sm { box-shadow: var(--shadow-sm); }
.shadow-md { box-shadow: var(--shadow-md); }
.shadow-lg { box-shadow: var(--shadow-lg); }
```

## 📝 Typography System

### **shadcn/ui Typography Scale**
```css
/* Typography scale - following shadcn/ui conventions */

/* Headings */
.text-4xl { font-size: 2.25rem; line-height: 2.5rem; }     /* 36px - Page titles */
.text-3xl { font-size: 1.875rem; line-height: 2.25rem; }   /* 30px - Section titles */
.text-2xl { font-size: 1.5rem; line-height: 2rem; }        /* 24px - Card titles */
.text-xl { font-size: 1.25rem; line-height: 1.75rem; }     /* 20px - Subsection titles */
.text-lg { font-size: 1.125rem; line-height: 1.75rem; }    /* 18px - Component titles */
.text-base { font-size: 1rem; line-height: 1.5rem; }       /* 16px - Body text */
.text-sm { font-size: 0.875rem; line-height: 1.25rem; }    /* 14px - Small text */
.text-xs { font-size: 0.75rem; line-height: 1rem; }        /* 12px - Caption text */

/* Font weights */
.font-light { font-weight: 300; }
.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }

/* Text colors - using CSS custom properties */
.text-foreground { color: hsl(var(--foreground)); }
.text-muted-foreground { color: hsl(var(--muted-foreground)); }
.text-primary { color: hsl(var(--primary)); }
.text-destructive { color: hsl(var(--destructive)); }

/* Monospace font */
.font-mono { font-family: ui-monospace, 'SF Mono', 'Monaco', 'Cascadia Code', monospace; }
```

## 🃏 Card Design Patterns

### **shadcn/ui Card Component**
```html
<!-- Basic Card using shadcn/ui tokens -->
<div class="rounded-lg border bg-card text-card-foreground shadow-sm">
  <div class="flex flex-col space-y-1.5 p-6">
    <h3 class="text-2xl font-semibold leading-none tracking-tight">Card Title</h3>
  </div>
  <div class="p-6 pt-0">
    <!-- Card content -->
  </div>
</div>

<!-- Interactive Card with Hover -->
<div class="rounded-lg border bg-card text-card-foreground shadow-sm transition-all hover:shadow-md hover:-translate-y-1">
  <div class="p-6">
    <!-- Card content -->
  </div>
</div>
```

### **Bootstrap Integration with shadcn/ui Tokens**
```css
/* Card using shadcn/ui design tokens */
.card {
  border: 1px solid hsl(var(--border));
  border-radius: var(--radius);
  background-color: hsl(var(--card));
  color: hsl(var(--card-foreground));
  box-shadow: var(--shadow);
}

.card-header {
  background-color: hsl(var(--card));
  border-bottom: 1px solid hsl(var(--border));
  padding: 1.5rem;
}

.card-body {
  padding: 1.5rem;
}

.hover-lift {
  transition: all 0.2s ease-in-out;
}

.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
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

### **shadcn/ui Button Hierarchy**
```html
<!-- Primary Actions -->
<button class="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90">Primary Action</button>
<button class="inline-flex items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground">Secondary Action</button>

<!-- Contextual Actions -->
<button class="inline-flex items-center justify-center rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white shadow transition-colors hover:bg-green-600/90">Success Action</button>
<button class="inline-flex items-center justify-center rounded-md border border-green-200 bg-background px-4 py-2 text-sm font-medium text-green-700 shadow-sm transition-colors hover:bg-green-50">Success Secondary</button>

<!-- Sizes -->
<button class="inline-flex items-center justify-center rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90">Small Button</button>
<button class="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90">Default Button</button>
<button class="inline-flex items-center justify-center rounded-md bg-primary px-8 py-3 text-base font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90">Large Button</button>
```

### **Bootstrap Integration with shadcn/ui Tokens**
```css
/* Button using shadcn/ui design tokens */
.btn {
  border-radius: var(--radius);
  font-weight: 500;
  transition: all 0.15s ease-in-out;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  border: 1px solid hsl(var(--primary));
}

.btn-primary:hover {
  background-color: hsl(var(--primary) / 0.9);
}

.btn-secondary {
  background-color: hsl(var(--secondary));
  color: hsl(var(--secondary-foreground));
  border: 1px solid hsl(var(--border));
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

.btn-lg {
  padding: 0.75rem 2rem;
  font-size: 1rem;
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

### **shadcn/ui Form Components**
```html
<!-- Form Field using shadcn/ui tokens -->
<div class="grid w-full max-w-sm items-center gap-1.5">
  <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70" for="input1">Label</label>
  <input class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" type="text" id="input1" placeholder="Enter text...">
</div>

<!-- Form Layout with Bootstrap Grid -->
<div class="row g-3">
  <div class="col-md-6">
    <label for="input1" class="form-label text-sm font-medium">Label</label>
    <input type="text" class="form-control rounded-md border-input bg-background text-sm focus:ring-2 focus:ring-ring focus:ring-offset-2" id="input1">
  </div>
  <div class="col-md-6">
    <label for="input2" class="form-label text-sm font-medium">Label</label>
    <input type="text" class="form-control rounded-md border-input bg-background text-sm focus:ring-2 focus:ring-ring focus:ring-offset-2" id="input2">
  </div>
</div>
```

### **Form Error Handling with shadcn/ui**
```html
<!-- Field with Error State -->
<div class="grid w-full max-w-sm items-center gap-1.5">
  <label class="text-sm font-medium leading-none" for="email">Email</label>
  <input class="flex h-10 w-full rounded-md border border-destructive bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-destructive focus-visible:ring-offset-2" type="email" id="email" placeholder="Email">
  <p class="text-sm text-destructive">Email is required.</p>
</div>

<!-- Success State -->
<div class="grid w-full max-w-sm items-center gap-1.5">
  <label class="text-sm font-medium leading-none" for="email-success">Email</label>
  <input class="flex h-10 w-full rounded-md border border-green-200 bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-500 focus-visible:ring-offset-2" type="email" id="email-success" placeholder="Email">
  <p class="text-sm text-green-600">Email is valid.</p>
</div>
```

## 🎨 Implementation Checklist

### **shadcn/ui Integration Standards**
- [ ] Use shadcn/ui design tokens (--primary, --border, --radius)
- [ ] Apply HSL color values with CSS custom properties
- [ ] Implement focus-visible states with ring utilities
- [ ] Use semantic color naming (primary, secondary, destructive)
- [ ] Follow Tailwind CSS utility patterns
- [ ] Maintain Bootstrap grid system compatibility

### For New Pages/Components:
- [ ] Use consistent shadcn/ui color system
- [ ] Apply proper spacing using Tailwind scale
- [ ] Use var(--shadow) for card elevation
- [ ] Apply hover states with proper transitions
- [ ] Use proper typography hierarchy (text-sm, text-base, text-lg)
- [ ] Implement consistent table styling with shadcn/ui tokens
- [ ] Use status badge system with semantic colors
- [ ] Apply var(--radius) consistently for border-radius
- [ ] Use SVG icons with proper sizing (w-4 h-4, w-6 h-6)
- [ ] Implement empty states with proper messaging

### **shadcn/ui Code Review Points:**
- [ ] Colors use HSL values with CSS custom properties
- [ ] Spacing follows Tailwind CSS scale
- [ ] Cards use var(--shadow) and var(--radius)
- [ ] Forms implement focus-visible ring states
- [ ] Typography uses shadcn/ui text classes
- [ ] Components are accessible with proper ARIA
- [ ] Animations use transition-colors and transition-all
- [ ] Mobile responsiveness maintained with responsive utilities

### **Design Token Usage:**
```css
/* Core shadcn/ui tokens to use */
--background: 0 0% 100%;        /* Page background */
--foreground: 222.2 84% 4.9%;   /* Primary text */
--card: 0 0% 100%;              /* Card background */
--card-foreground: 222.2 84% 4.9%; /* Card text */
--primary: 221.2 83.2% 53.3%;   /* Primary brand color */
--primary-foreground: 210 40% 98%; /* Primary text color */
--secondary: 210 40% 96%;       /* Secondary background */
--secondary-foreground: 222.2 84% 4.9%; /* Secondary text */
--muted: 210 40% 96%;          /* Muted background */
--muted-foreground: 215.4 16.3% 46.9%; /* Muted text */
--border: 214.3 31.8% 91.4%;   /* Border color */
--input: 214.3 31.8% 91.4%;    /* Input border */
--ring: 221.2 83.2% 53.3%;     /* Focus ring */
--radius: 0.5rem;              /* Border radius */
```

This design system integrates shadcn/ui patterns with Bootstrap components, ensuring modern, accessible, and consistent UI development across the Smart MCQ Platform.