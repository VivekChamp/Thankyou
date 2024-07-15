# Copyright (c) 2024, Vivek and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Consolidation(Document):
	def validate(self):

		if not self.item_log_fetched:

			outlet_name_list = frappe.get_all("Warehouse", {"custom_area": self.territory}, ["custom_outletname"], pluck = "custom_outletname")

			outlet_name_list = list(set(outlet_name_list))

			self.item_log_fetched = 1

			if len(outlet_name_list) == 1:
				condition = f"orl.territory = '{outlet_name_list[0]}' and orl.date = '{self.date}'"

			elif len(outlet_name_list) > 1:
				condition = f"orl.territory in {tuple(outlet_name_list)} and orl.date = '{self.date}'"

			else:
				condition = f"orl.territory = '{self.territory}' and orl.date = '{self.date}'"

			data_list = frappe.db.sql(f'''
				SELECT
					ti.uom,
					ti.item_code,
					ti.item_name,
					SUM(ti.required_qty) as reqd_qty
				
				FROM
					`tabOutlet Requirement Log` as orl,
					`tabThankyou Item` as ti        
				WHERE
					{condition} and orl.name = ti.parent and ti.parenttype = 'Outlet Requirement Log'
					
				GROUP BY
					ti.item_code
					
				ORDER BY
					ti.item_code
			''', as_dict = True)

			self.consolidation_table_data = []

			for data in data_list:
				self.append("consolidation_table_data", {
					"uom": data["uom"],
					"item_code": data["item_code"],
					"item_name": data["item_name"],
					"reqd_qty": data["reqd_qty"],
					"approved_qty": 0
				})

@frappe.whitelist()
def get_item_logs(item_code, date, territory):

	outlet_name_list = frappe.get_all("Warehouse", {"custom_area": territory}, ["custom_outletname"], pluck = "custom_outletname")

	outlet_name_list = list(set(outlet_name_list))

	if len(outlet_name_list) == 1:
		condition = f"ti.item_code = '{item_code}' and orl.date = '{date}' and orl.territory = '{outlet_name_list[0]}'"
	
	elif len(outlet_name_list) > 1:
		condition = f"ti.item_code = '{item_code}' and orl.date = '{date}' and orl.territory in {tuple(outlet_name_list)}"

	else:
		condition = f"ti.item_code = '{item_code}' and orl.date = '{date}'"

	data_list = frappe.db.sql(f'''
		SELECT
			ti.uom,
			ti.item_code,
			ti.item_name,
			ti.required_qty,
			orl.territory as custom_outletname
		
		FROM
			`tabOutlet Requirement Log` as orl,
			`tabThankyou Item` as ti      
		WHERE
			{condition} and orl.name = ti.parent and ti.parenttype = 'Outlet Requirement Log'
	''', as_dict = True)

	return data_list