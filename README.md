# Daily Work Report (DWR)

## Overview
Daily Work Report (DWR) is an Odoo module that enables systematic tracking and management of employee daily activities, task progress, and workplace concerns. Designed to streamline the workflow between employees and management, it provides a structured way to report, review, and take action on daily work activities.

## Features

### Core Functionality
- **Daily Activity Reporting**: Employees can log their daily tasks, time spent, current status, and expected completion dates
- **Work Time Management**: Automatic calculation of total and actual work hours, with support for half-day leaves
- **Dual Reporting Structure**: Support for employees who report to multiple managers for different operations
  - Auto-selection of manager when employee has only one reporting manager
- **Task Status Tracking**: Monitor progress with customizable job status options (Completed, In Progress, etc.)
- **Approval Workflow**: Submit → Manager Approval → Director Review process
- **Concerns Management**: Record and track student, employee, or other concerns with ability to assign action items

### Key Components
- **Employee Reports**: Daily work logs submitted by employees
- **Job Status**: Customizable status options for tasks
- **Support Staff Reports**: Specialized reports for support staff
- **Concern Tracking**: System for recording and resolving workplace concerns

### Role-Based Access
- **User**: Regular employees who submit daily reports
- **Manager**: Can approve/reject reports from their team members (including additional reporting managers)
- **VP/Director**: Higher-level oversight and approval capabilities
- **Admin**: Full system access and configuration rights
- **Concern Managers**: Specialized access for handling reported concerns

## Technical Details

### Dependencies
- Odoo 17.0
- Required modules: base, web, mail, hr, tijus_custom_base

### Module Structure
- **Models**: Define the data structure and business logic
- **Views**: User interface components for data visualization and interaction
- **Security**: Access rights and record rules
- **Wizards**: Special forms for guided user actions like concern resolution

### Special Features
- **Time Format Validation**: Ensures consistent HH:MM format for time entries
- **Half-day Detection**: Automatically identifies half-day leaves and adjusts expected work hours
- **Work Hours Calculation**: Automatically calculates total work hours and actual recorded hours
- **First/Third Saturday Rules**: Special handling for half-day Saturdays (1st and 3rd of each month)
- **Multi-Manager Reporting**: Employees can submit separate daily reports to different reporting managers

## Usage

### Daily Reporting Workflow
1. **Create Report**: Employees create and fill their daily task report
2. **Select Manager** (optional): For employees with multiple reporting managers, select specific manager for this report
3. **Submit Report**: Once completed, employee submits for manager review
4. **Manager Review**: Manager approves or rejects with feedback
5. **Director Oversight**: Directors can review all reports in their area

### Concern Management
1. **Report Concern**: Employee logs a concern in their daily report
2. **Review**: Concern managers receive notifications about new concerns
3. **Action**: Create and assign action items for concern resolution
4. **Follow-up**: Track progress until resolution

## Configuration
- **Job Status**: Configure the available status options
- **User Access**: Assign users to appropriate security groups
- **Mail Activities**: Configure notification templates and activities
- **Additional Managers**: Configure additional reporting managers for employees who report to multiple managers

## Installation
Standard Odoo module installation process:
1. Place the module in the Odoo addons path
2. Update the module list in Odoo
3. Install the "Daily Report" module
4. Configure access rights for users

---

*Developed by Tijus Academy*