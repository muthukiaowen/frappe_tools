"""Install and migrate hooks for se_tools.

HRMS owns the "Payroll" Workspace Sidebar and re-syncs it from its own files on every migrate, which
would drop a link added through the UI. So the link is (re)applied after each migrate, idempotently.
"""

import frappe

SIDEBAR = "Payroll"
ANCHOR_LINK = "Additional Salary"  # the new link goes directly below this one
TOOL = "Additional Salary Tool"
ICON = "calculator"


def after_install():
        ensure_payroll_sidebar_link()


def after_migrate():
        ensure_payroll_sidebar_link()


def ensure_payroll_sidebar_link():
        """Insert "Additional Salary Tool" into the Payroll sidebar, directly below "Additional Salary".

        Done with direct DB writes because the sidebar is a standard record owned by HRMS, which the
        document API refuses to edit outside developer mode. Safe to run repeatedly."""
        if not frappe.db.exists("Workspace Sidebar", SIDEBAR):
                return
        if not frappe.db.exists("DocType", TOOL):
                return

        parent = {"parent": SIDEBAR, "parenttype": "Workspace Sidebar", "parentfield": "items"}

        if frappe.db.exists("Workspace Sidebar Item", {**parent, "link_to": TOOL}):
                return  # already there

        anchor_idx = frappe.db.get_value(
                "Workspace Sidebar Item", {**parent, "type": "Link", "link_to": ANCHOR_LINK}, "idx"
        )
        if not anchor_idx:
                return  # HRMS layout changed; do nothing rather than guess a position

        # Make room for the new row right after the anchor.
        frappe.db.sql(
                """UPDATE `tabWorkspace Sidebar Item`
                SET idx = idx + 1
                WHERE parent = %s AND parenttype = %s AND parentfield = %s AND idx > %s""",
                (SIDEBAR, "Workspace Sidebar", "items", anchor_idx),
        )

        item = frappe.get_doc(
                {
                        "doctype": "Workspace Sidebar Item",
                        **parent,
                        "idx": anchor_idx + 1,
                        "label": TOOL,
                        "type": "Link",
                        "link_type": "DocType",
                        "link_to": TOOL,
                        "icon": ICON,
                        "child": 0,
                        "indent": 0,
                        "collapsible": 1,
                        "keep_closed": 0,
                        "show_arrow": 0,
                }
        )
        item.name = frappe.generate_hash(length=10)
        item.owner = item.modified_by = "Administrator"
        item.creation = item.modified = frappe.utils.now()
        item.db_insert()

        frappe.db.commit()
        frappe.clear_cache()
