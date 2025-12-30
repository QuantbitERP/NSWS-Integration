import frappe

def execute():
    # Define roles and permissions
    roles_permissions = {
        "NSWS User": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "submit": 0,
            "cancel": 0
        },
        "NSWS Manager": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 1,
            "cancel": 1
        }
    }

    # List of DocTypes to apply permissions to
    doctypes = ["NSWS Options", "NSWS P2 Form", "NSWS Season"]

    for doctype_name in doctypes:
        doc = frappe.get_doc("DocType", doctype_name)

        for role, perms in roles_permissions.items():
            # Remove existing permissions for this role to avoid duplicates
            doc.permissions = [p for p in doc.permissions if p.role != role]

            # Add new permissions for this role
            doc.append("permissions", {"role": role, **perms})

        # Save DocType with updated permissions
        doc.save(ignore_permissions=True)
        print(f"Permissions updated on '{doctype_name}' for roles: {', '.join(roles_permissions.keys())}")
