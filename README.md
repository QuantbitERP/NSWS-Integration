# NSWS Integration – Frappe App

A Frappe application to integrate ERPNext with the **National Single Window System (NSWS)** for managing **P2 Form** submissions.  
This app provides custom DocTypes, roles, permissions, and a scalable foundation for NSWS API integration.

---

## Overview

The **NSWS Integration** app is designed to:
- Manage NSWS P2 Form data inside ERPNext
- Control access using dedicated roles
- Apply permissions programmatically (no manual Role Permission Manager dependency)
- Support multi-site and production deployments

---

## Features

- ✅ NSWS P2 Form management
- ✅ Custom DocTypes for NSWS workflow
- ✅ Role-based access control
- ✅ Patch-based permission management
- ✅ Fixture support for app installation
- ✅ Production-safe and version controlled

---

## Custom DocTypes

| DocType Name | Description |
|-------------|------------|
| **NSWS Options** | Stores NSWS configuration and options |
| **NSWS P2 Form** | Stores NSWS P2 Form application data |
| **NSWS Season** | Stores seasonal data related to NSWS |

---

## Roles

| Role Name | Description |
|---------|------------|
| **NSWS User** | User responsible for creating and updating NSWS data |
| **NSWS Manager** | Manager role with higher-level permissions |

---

## Role Permissions

Permissions are applied using **patches**, not manually via Role Permission Manager.

### Permission Matrix

| DocType | Role | Read | Write | Create | Delete | Submit | Cancel |
|-------|------|------|------|--------|--------|--------|--------|
| NSWS Options | NSWS User | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| NSWS P2 Form | NSWS User | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| NSWS Season | NSWS User | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| NSWS Options | NSWS Manager | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| NSWS P2 Form | NSWS Manager | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| NSWS Season | NSWS Manager | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Permission Management (Important)

> ⚠️ Permissions are **not stored in Role** in Frappe.  
> They are stored inside the **DocType (DocPerm)**.

This app uses a **patch-based approach** to:
- Automatically add permissions
- Avoid manual Role Permission Manager steps
- Ensure permissions are applied consistently on all sites

### Patch Used
