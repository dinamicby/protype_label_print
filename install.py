import frappe

def after_install():
    # Добавим кастомное поле 'Storage Position' к Item, если его нет
    try:
        if not frappe.db.exists("Custom Field", {"dt":"Item","fieldname":"storage_position"}):
            cf = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "Item",
                "fieldname": "storage_position",
                "label": "Storage Position",
                "fieldtype": "Data",
                "insert_after": "item_group",
                "fetch_from": "",
                "translatable": 0
            })
            cf.insert(ignore_permissions=True)
            frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Label Print after_install error: {e}")
