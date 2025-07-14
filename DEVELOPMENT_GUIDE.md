# Smart MCQ Platform - Development Guide

This guide provides practical instructions for developers to maintain design consistency across the Smart MCQ Platform using our established design system.

## 🚀 Quick Start

### 1. Include Design System
The design system CSS is automatically included in the base template. For new pages:

```html
{% extends 'base.html' %}
{% block title %}Page Title - Smart MCQ{% endblock %}
{% block content %}
<!-- Your content here -->
{% endblock %}
```

### 2. Page Structure Template
Use this standard structure for all pages:

```html
{% block content %}
<!-- Page Header -->
<div class="d-flex justify-content-between align-items-center mb-6">
    <div>
        <h1 class="h3 mb-0 text-gray-900">Page Title</h1>
        <p class="mb-0 text-muted">Page description</p>
    </div>
    <div class="d-flex align-items-center gap-3">
        <!-- Action buttons -->
        <a href="#" class="btn btn-primary">Primary Action</a>
    </div>
</div>

<!-- Main Content -->
<div class="row g-4 mb-6">
    <!-- Your content cards/components -->
</div>
{% endblock %}
```

## 📋 Component Templates

### Action Cards (Dashboard Style)
```html
<div class="col-lg-4 col-md-6">
    <div class="card border-0 shadow-sm h-100 hover-lift">
        <div class="card-body p-4">
            <div class="d-flex align-items-center mb-3">
                <div class="flex-shrink-0">
                    <div class="bg-primary bg-opacity-10 p-3 rounded-3">
                        <!-- SVG Icon -->
                        <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="24" height="24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="..."></path>
                        </svg>
                    </div>
                </div>
                <div class="flex-grow-1 ms-3">
                    <h5 class="mb-1">Card Title</h5>
                    <p class="text-muted mb-0 small">Card description</p>
                </div>
            </div>
            <div class="d-flex gap-2">
                <a href="#" class="btn btn-sm btn-outline-primary">View All</a>
                <a href="#" class="btn btn-sm btn-primary">Create New</a>
            </div>
        </div>
    </div>
</div>
```

### Data Table Card
```html
<div class="card border-0 shadow-sm">
    <div class="card-header bg-white py-3">
        <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Table Title</h5>
            <span class="text-muted small">{{ total_count }} total</span>
        </div>
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
                    {% for item in items %}
                    <tr>
                        <td class="ps-4">{{ item.field1 }}</td>
                        <td>{{ item.field2 }}</td>
                        <td class="pe-4">
                            <a href="#" class="btn btn-sm btn-outline-primary">Action</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- Pagination (if needed) -->
    {% if page_obj and page_obj.has_other_pages %}
    <div class="card-footer bg-white border-top">
        {% include 'components/pagination.html' with page_obj=page_obj %}
    </div>
    {% endif %}
</div>
```

### Status Badges
```html
<!-- Success/Active Status -->
<span class="badge bg-success bg-opacity-10 text-success border border-success">Active</span>

<!-- Warning/Pending Status -->
<span class="badge bg-warning bg-opacity-10 text-warning border border-warning">Pending</span>

<!-- Info/Scheduled Status -->
<span class="badge bg-info bg-opacity-10 text-info border border-info">Scheduled</span>

<!-- Code/Access Code Display -->
<span class="badge font-monospace">ABC123</span>
```

### Empty State
```html
<div class="card-body text-center py-5">
    <div class="mb-3">
        <svg class="w-12 h-12 text-muted mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="48" height="48">
            <!-- Relevant icon path -->
        </svg>
    </div>
    <h6 class="text-muted mb-2">No items yet</h6>
    <p class="text-muted mb-4">Descriptive message about the empty state</p>
    <a href="#" class="btn btn-primary">Primary Action</a>
</div>
```

### Form Layout
```html
<div class="card border-0 shadow-sm">
    <div class="card-header bg-white py-3">
        <h5 class="mb-0">Form Title</h5>
    </div>
    <div class="card-body p-4">
        <form method="post">
            {% csrf_token %}
            <div class="row g-3">
                <div class="col-md-6">
                    <label for="field1" class="form-label">Field Label</label>
                    <input type="text" class="form-control" id="field1" name="field1">
                </div>
                <div class="col-md-6">
                    <label for="field2" class="form-label">Field Label</label>
                    <input type="text" class="form-control" id="field2" name="field2">
                </div>
                <div class="col-12">
                    <div class="d-flex gap-2 justify-content-end">
                        <a href="#" class="btn btn-outline-secondary">Cancel</a>
                        <button type="submit" class="btn btn-primary">Save</button>
                    </div>
                </div>
            </div>
        </form>
    </div>
</div>
```

## 🎨 Color Usage Guide

### When to Use Each Color

**Primary (Blue)** - `btn-primary`, `text-primary`, `bg-primary`
- Main actions (Create, Save, Submit)
- Primary navigation items
- Key status indicators

**Success (Green)** - `btn-success`, `text-success`, `bg-success`
- Questions-related features
- Success states (completed, passed)
- Positive indicators

**Info (Cyan)** - `btn-info`, `text-info`, `bg-info`
- Sessions-related features
- Information states
- Neutral actions

**Warning (Orange)** - `btn-warning`, `text-warning`, `bg-warning`
- Pending states
- Upcoming items
- Caution indicators

**Danger (Red)** - `btn-danger`, `text-danger`, `bg-danger`
- Delete actions
- Error states
- Failed indicators

### Color Implementation Examples
```html
<!-- Primary Action Card (Questions) -->
<div class="bg-primary bg-opacity-10 p-3 rounded-3">
    <svg class="w-6 h-6 text-primary">...</svg>
</div>

<!-- Success Action Card (Tests) -->
<div class="bg-success bg-opacity-10 p-3 rounded-3">
    <svg class="w-6 h-6 text-success">...</svg>
</div>

<!-- Info Action Card (Sessions) -->
<div class="bg-info bg-opacity-10 p-3 rounded-3">
    <svg class="w-6 h-6 text-info">...</svg>
</div>
```

## 📏 Spacing Guidelines

### Section Spacing
- **Between major sections**: `mb-6` (48px)
- **Between cards in grid**: `g-4` (24px gap)
- **Between buttons**: `gap-2` (8px) or `gap-3` (16px)

### Card Padding
- **Standard card body**: `p-4` (24px)
- **Card header/footer**: `py-3` (16px vertical)
- **Table cells**: `ps-4` and `pe-4` for first/last columns

## 🔘 Button Guidelines

### Button Hierarchy
1. **Primary**: Main action on the page (`btn-primary`)
2. **Secondary**: Alternative action (`btn-outline-primary`)
3. **Contextual**: Color-coded actions (`btn-success`, `btn-info`)

### Button Combinations
```html
<!-- Action pairs -->
<div class="d-flex gap-2">
    <a href="#" class="btn btn-sm btn-outline-primary">View All</a>
    <a href="#" class="btn btn-sm btn-primary">Create New</a>
</div>

<!-- Form actions -->
<div class="d-flex gap-2 justify-content-end">
    <a href="#" class="btn btn-outline-secondary">Cancel</a>
    <button type="submit" class="btn btn-primary">Save</button>
</div>
```

## 🎯 Icon Guidelines

### Icon Sources
Use SVG icons from [Heroicons](https://heroicons.com/) or similar for consistency.

### Icon Sizing
- **Small icons**: 16px (w-4 h-4) - For buttons, inline text
- **Standard icons**: 24px (w-6 h-6) - For cards, navigation
- **Large icons**: 48px (w-12 h-12) - For empty states

### Icon Implementation
```html
<!-- Standard icon with background -->
<div class="bg-primary bg-opacity-10 p-3 rounded-3">
    <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="..."></path>
    </svg>
</div>

<!-- Inline icon -->
<svg class="w-4 h-4 me-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="..."></path>
</svg>
```

## 📱 Responsive Guidelines

### Grid Breakpoints
```html
<!-- Cards that stack on mobile -->
<div class="col-lg-4 col-md-6"><!-- Card --></div>

<!-- Full width on mobile, half on tablet, third on desktop -->
<div class="col-xl-4 col-lg-6 col-md-12"><!-- Card --></div>
```

### Mobile Considerations
- Use `mb-4` instead of `mb-6` on mobile (automatic in design system)
- Ensure buttons are touch-friendly (minimum 44px height)
- Stack form fields vertically on mobile

## 🔍 Common Patterns

### List Page Pattern
1. Page header with title and action button
2. Grid of action cards (if applicable)
3. Data table card with pagination

### Detail Page Pattern
1. Page header with breadcrumb and actions
2. Main content card
3. Related information cards

### Form Page Pattern
1. Page header with title
2. Form card with proper spacing
3. Action buttons aligned right

## ✅ Quality Checklist

Before marking a page/component as complete, verify:

- [ ] Uses design system colors consistently
- [ ] Proper spacing (mb-6, g-4, p-4) applied
- [ ] Cards have shadow-sm and hover-lift (if interactive)
- [ ] Tables follow borderless design pattern
- [ ] Buttons use proper hierarchy and colors
- [ ] Icons are consistent size and style
- [ ] Mobile responsive layout works
- [ ] Empty states have helpful messaging
- [ ] Status badges use opacity and border style
- [ ] Typography hierarchy is maintained

## 🚨 Common Mistakes to Avoid

1. **Don't** use Bootstrap's default card styling (has borders)
2. **Don't** mix button styles inconsistently
3. **Don't** use custom colors outside the design system
4. **Don't** forget hover states on interactive elements
5. **Don't** use different spacing patterns
6. **Don't** ignore mobile responsive behavior

## 📝 Code Review Checklist

When reviewing code, check for:

- [ ] Design system CSS classes used correctly
- [ ] No inline styles that override design system
- [ ] Consistent color usage throughout
- [ ] Proper component structure followed
- [ ] Responsive behavior maintained
- [ ] Accessibility considerations included

This guide ensures all developers can maintain consistency while building new features for the Smart MCQ Platform.