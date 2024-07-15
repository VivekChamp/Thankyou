# Copyright (c) 2024, Vivek and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class OutletRequirements(Document):
	pass

@frappe.whitelist()
def on_update(data):

	self = json.loads(data)

	if not self.get("territory"):
		return False, "Territory is Mandatory..."

	if not self.get("warehouse"):
		return False, "Warehouse is Mandatory..."

	if not self.get("category"):
		return False, "Category is Mandatory..."
	
	exists_log_doc_name = frappe.db.exists("Outlet Requirement Log", {"date": self["date"], "territory": self["territory"], "category": self["category"], "warehouse": self["warehouse"]})

	if not exists_log_doc_name:

		new_log_doc = frappe.new_doc("Outlet Requirement Log")

		new_log_doc.date = self["date"]
		new_log_doc.territory = self["territory"]
		new_log_doc.category = self["category"]
		new_log_doc.warehouse = self["warehouse"]
		
		for item_row in self["item_details"]:
			
			new_log_doc.append("item_details", {
				"item_code": item_row["item_code"],
				"item_name": item_row["item_name"],
				"uom": item_row["uom"],
				"item_group": item_row["item_group"],
				"date": item_row["date"],
				"available_qty": item_row["available_qty"],
				"suggested_qty": item_row["suggested_qty"],
				"required_qty": item_row["required_qty"]
			})
		
		new_log_doc.save()

	else:

		exists_log_doc = frappe.get_doc("Outlet Requirement Log", exists_log_doc_name)

		exists_log_doc.item_details = []

		for item_row in self["item_details"]:
			
			exists_log_doc.append("item_details", {
				"item_code": item_row["item_code"],
				"item_name": item_row["item_name"],
				"uom": item_row["uom"],
				"item_group": item_row["item_group"],
				"date": item_row["date"],
				"available_qty": item_row["available_qty"],
				"suggested_qty": item_row["suggested_qty"],
				"required_qty": item_row["required_qty"]
			})
		
		exists_log_doc.save()

	frappe.db.commit()

	return True, "Updated Successfully..."

@frappe.whitelist()
def get_exists_doc(warehouse, territory, category, date):

	exists_log_doc = frappe.db.exists("Outlet Requirement Log", {"date": date, "territory": territory, "category": category, "warehouse": warehouse})

	if exists_log_doc:

		item_list = frappe.get_all("Thankyou Item", {"parent": exists_log_doc}, ["item_code", "item_name", "uom", "item_group", "suggested_qty", "required_qty"], order_by = "idx")

	else:

		item_list = frappe.get_all("Item", {"item_group": category}, ["item_code", "item_name", "stock_uom as uom", "item_group", "custom_suggested_qty"])

	return item_list

@frappe.whitelist()
def get_item_group(warehouse):

	item_list = frappe.get_list("Bin", {"warehouse": warehouse}, ["item_code"], pluck = "item_code")

	item_group_list = list(set(frappe.get_list("Item", {"name": ["in", item_list]}, ["item_group"], pluck = "item_group")))

	return item_group_list