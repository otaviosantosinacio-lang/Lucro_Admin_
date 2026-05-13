# Lucro Admin

Lucro Admin is a backend-oriented Python application designed to manage marketplace sales costs by consolidating taxes, commissions, freight, and ERP/order data into a structured workflow.

> **Project status:** currently under development.

## Overview

The main goal of this project is to centralize data from external platforms and transform raw sales information into structured business data that can be processed, analyzed, and persisted.

The application is focused on marketplace operations and cost visibility, helping organize data related to:

- taxes
- commissions
- freight costs
- order information
- ERP and marketplace synchronization

## Main Features

- Integration with external APIs
- Marketplace and ERP data synchronization
- Sales cost processing
- Business-rule validation and normalization
- Order and product data persistence
- Modular code organization for maintainability

## Current Integrations

- **Bling**
- **Mercado Livre**

## Project Structure

The project is organized into layers to separate responsibilities more clearly:

- `core/` → domain rules and abstractions
- `services/` → use case orchestration
- `adapters/` → external integrations
- `infra/` → repositories, logging, HTTP infrastructure
- `app/` → application-level organization
- `utils/` → helper utilities

This structure was designed to make the project easier to evolve and maintain over time.

## Business Flow

At a high level, the application follows this flow:

1. Validates and refreshes access credentials for external services
2. Retrieves order data from integrated platforms
3. Processes business rules related to costs and sales data
4. Extracts marketplace-related cost information
5. Persists processed orders and product data

## Technologies

- Python
- FastAPI
- REST API integrations
- Logging
- Repository-based persistence structure
- External service adapters

## Example Responsibilities Already Present in the Codebase

Some parts already represented in the project structure include:

- order processing
- sales synchronization
- credential providers
- external adapters
- repositories for orders and products

## Why This Project Matters

Lucro Admin was created to solve a real business problem: understanding the actual cost of marketplace sales by combining information that is usually spread across different systems.

Instead of working with isolated raw data, the application aims to deliver a more organized and reliable backend workflow for sales-cost management.

## Roadmap

Planned improvements include:

- API endpoint expansion
- stronger documentation
- test coverage
- infrastructure refinement
- improved deployment readiness

## Notes

This repository is still evolving, but it already reflects the architectural direction, integration approach, and business logic behind the solution.

## Author

**Otavio Santos Inacio**  
Backend-focused developer working with Python, FastAPI, API integrations, and business data processing.

- LinkedIn: https://linkedin.com/in/otavio-santos-inacio
- GitHub: https://github.com/otaviosantosinacio-lang