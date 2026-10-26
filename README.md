# se_tools

Custom tools for the Strategic Engagement ERPNext site.

## Additional Salary Tool

A single doctype that bulk-creates and submits Additional Salary records from an editable grid of
employees and salary components.

- One-time or recurring (From/To date range)
- Get Employees, Import/Export via .xlsx template, Save Draft
- Inline Base entry to create a Salary Structure Assignment for employees who have none
- Per-employee savepoints, so one failure does not stop the batch

Requires `frappe` and `hrms` (ERPNext HR and Payroll).

### Install

```bash
cd <frappe-bench>
bench get-app https://github.com/<owner>/se_tools.git
bench --site <site> install-app se_tools
bench --site <site> clear-cache
```

Then restart the web and worker processes and open `/app/additional-salary-tool`.

### Behaviour to be aware of

- A one-time run cancels any submitted one-time Additional Salary for the same employee and
  component in the same calendar month when the amount differs, then creates a new one.
- A recurring run shortens an overlapping recurring record's To Date, or cancels it if fully covered.
- There is no dry-run. "Create Additional Salaries" submits after a confirm dialog.

Originally built on the Titansoft ERPNext server (Feeds app) and ported here.
