// Copyright (c) 2024, Vivek and contributors
// For license information, please see license.txt

frappe.ui.form.on('Outlet Requirements', {

	refresh: async function(frm){

		frm.disable_save()

		frm.add_custom_button(__('Update'), function() {
			frappe.call({
				method: 'thankyou.thankyou.doctype.outlet_requirements.outlet_requirements.on_update',
				args: {
					'data': frm.doc
				},
				callback: function(r) {
					if (r.message[0]){
						frappe.show_alert({message: r.message[1], indicator: 'green'});
					}
					else{
						frappe.show_alert({message: r.message[1], indicator: 'orange'});
					}
				}
			});
		});

		frm.set_query('territory', function(){
			return {
				filters: {
					is_group: 0
				}
			};
		});

		var item_group_list = []

		if(frm.doc.warehouse){

			await frappe.call({
				method: 'thankyou.thankyou.doctype.outlet_requirements.outlet_requirements.get_item_group',
				args: {
					'warehouse': frm.doc.warehouse
				},
				callback: function(r) {
					item_group_list = r.message
				}
			});

		}

		frm.set_query('category', function(){
			return {
				filters: {
					name: ["in", item_group_list]
				}
			};
		});
	},

	warehouse: async function(frm){

		frm.set_value("category", "")
		
		var item_group_list = []

		if(frm.doc.warehouse){

			await frappe.call({
				method: 'thankyou.thankyou.doctype.outlet_requirements.outlet_requirements.get_item_group',
				args: {
					'warehouse': frm.doc.warehouse
				},
				callback: function(r) {
					item_group_list = r.message
				}
			});

		}

		frm.set_query('category', function(){
			return {
				filters: {
					name: ["in", item_group_list]
				}
			};
		});
	},

	category: function(frm) {

		frappe.model.clear_table(frm.doc, 'item_details');

		if(frm.doc.territory && frm.doc.category && frm.doc.warehouse){
			
			frappe.call({
				method: 'thankyou.thankyou.doctype.outlet_requirements.outlet_requirements.get_exists_doc',
				args: {
					'territory': frm.doc.territory,
					'category': frm.doc.category,
					'date': frm.doc.date,
					'warehouse': frm.doc.warehouse
				},
				callback: function(r) {
					if (r.message) {

						$.each(r.message, function(i, d) {
							var row = frm.add_child('item_details');
							row.item_code = d.item_code;
							row.item_name = d.item_name;
							row.uom = d.uom;
							row.item_group = d.item_group;
							row.custom_suggested_qty = d.custom_suggested_qty;
							row.required_qty = d.required_qty;
						});
						frm.refresh_field('item_details');
					}
				}
			});
		}
		else{
			frm.refresh_field('item_details');
		}
	}
});
