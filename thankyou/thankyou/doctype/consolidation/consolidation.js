// Copyright (c) 2024, Vivek and contributors
// For license information, please see license.txt

frappe.ui.form.on('Consolidation', {
	// refresh: function(frm) {

	// }
});


frappe.ui.form.on('Consolidation Table', {
	view: async function(frm, cdt, cdn) {

		var row = locals[cdt][cdn]

		var data_list = []

		await frappe.call({
			method: "thankyou.thankyou.doctype.consolidation.consolidation.get_item_logs",
			args: {
				item_code: row.item_code,
				date: frm.doc.date,
				territory: frm.doc.territory
			},
			callback(r){
				data_list = r.message
			}
		})

		var dialog = new frappe.ui.Dialog({
			title: __("Items"),
			size: "extra-large",
			fields: [

				{
					fieldname: 'items', fieldtype: 'Table',
					fields: [
						{
							fieldtype:'Link',
							fieldname:'item_code',
							label: __('Item'),
							read_only:1,
							in_list_view:1,
							columns: 1
						},
						{
							fieldtype:'Data',
							fieldname:'item_name',
							label: __('Item Name'),
							read_only:1,
							in_list_view:1,
							columns: 2
						},
						{
							fieldtype:'Link',
							read_only:1,
							fieldname:'uom',
							label: __('UOM'),
							in_list_view:1,
							columns: 1
						},
						{
							fieldtype:'Link',
							read_only:1,
							fieldname:'custom_outletname',
							label: __('Outlet Name'),
							in_list_view:1,
							columns: 2
						},
						{
							fieldtype:'Float',
							fieldname:'required_qty',
							label: __('Required Qty'),
							read_only: 1,
							in_list_view:1,
							columns: 2
						},
						{
							fieldtype:'Float',
							fieldname:'approved_qty',
							label: __('Approved Qty'),
							in_list_view:1,
							columns: 2
						},
					],
					data: data_list,
				}
			],
			primary_action_label: 'Update',
			async primary_action (args) {
				var update_datas = dialog.get_values();

				var approved_qty_total = 0

				await update_datas.items.forEach(update_data => {
					approved_qty_total = approved_qty_total + update_data.approved_qty

				})

				frappe.model.set_value(cdt, cdn, "approved_qty", approved_qty_total)
				
				dialog.hide();
			}
		});
		dialog.show();
	}
});
