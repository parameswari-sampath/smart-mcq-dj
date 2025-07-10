# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Smart MCQ Platform project currently in early development stage. The project is a Django-based web application for creating, managing, and taking multiple-choice question tests with role-based access control.

## Project Architecture

Based on the version roadmap in `version.yaml`, this will be a multi-tier application with:

- **Backend**: Django with PostgreSQL database
- **Authentication**: Role-based access control (Student & Teacher roles)
- **Core Features**: Question bank management, test creation, test sessions, and result tracking
- **Advanced Features**: Code execution sandbox, Redis caching, multi-organization support

## Development Phases

The project follows a structured versioning approach outlined in `version.yaml`:

- **v0.1-v0.7**: Core setup with PostgreSQL, Django, authentication, and basic CRUD operations
- **v1.0-v1.7**: Test execution engine with UI, timer, evaluation, and behavior tracking
- **v2.0-v2.8**: Enhanced features like navigation, notifications, export capabilities
- **v3.0-v3.9**: Advanced question types, randomization, Redis integration, code execution
- **v4.0+**: B2B features with multi-organization support and white-labeling

## Current Status

The project is in pre-development stage with only the version roadmap defined. No Django project structure, dependencies, or code has been implemented yet.

## Development Setup

This project uses **uv** for Python package management and virtual environment handling.

Setup steps:
1. uv is already initialized in this project
2. Use `uv sync` to install dependencies
3. Use `uv run` to execute Django commands
4. Set up PostgreSQL database
5. Configure Django settings

## Common Commands

**Package Management:**
- `uv sync` - Install/update dependencies
- `uv add <package>` - Add new dependency
- `uv remove <package>` - Remove dependency
- `uv lock` - Update lock file

**Django Commands (via uv):**
- `uv run python manage.py runserver` - Start development server
- `uv run python manage.py makemigrations` - Create database migrations
- `uv run python manage.py migrate` - Apply database migrations
- `uv run python manage.py createsuperuser` - Create admin user
- `uv run python manage.py test` - Run tests
- `uv run python manage.py collectstatic` - Collect static files

**Development Workflow:**
- Use `uv run` prefix for all Python/Django commands
- Dependencies are managed through `pyproject.toml`
- Virtual environment is automatically managed by uv

## Key Considerations

- Multi-role authentication system (Student/Teacher/Admin)
- Real-time test monitoring and behavior tracking
- Code execution sandbox for programming questions
- Scalability considerations with Redis and async handling
- Multi-tenant architecture for B2B deployment