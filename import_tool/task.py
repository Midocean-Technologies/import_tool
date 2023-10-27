import frappe

import pandas as pd
import frappe
from frappe.model.rename_doc import bulk_rename


def delete_si():
	lst = frappe.get_all("Sales Invoice", filters={'docstatus':1})
	for row in lst:
		Doc = frappe.get_doc("Sales Invoice", row.name)
		Doc.cancel()
		print(row.name)
		frappe.db.commit()

def delete_sii():
	lst = frappe.get_all("Sales Invoice", filters={'docstatus':0})
	for row in lst:
		frappe.delete_doc("Sales Invoice", row.name)
		frappe.db.commit()
		print(row)

def submit_invoice():
	lst = frappe.get_all("Sales Invoice", filters={'docstatus':0})
	for row in lst:
		doc = frappe.get_doc('Sales Invoice', row.name)
		doc.submit()
		frappe.db.commit()

def submit_invoice_new():
	lst = frappe.get_all("Sales Invoice", filters={'docstatus':0}, page_length=10, order_by='modified asc')
	for row in lst:
		doc = frappe.get_doc('Sales Invoice', row.name)
		doc.submit()
		frappe.db.commit()


def submit_invoice_nq():
	frappe.enqueue(
			submit_invoice, 
			queue= "long",
			timeout= 3000000, 
			is_async= True, 
			now= False, 
			job_name= "Sales Invoice Submit", 
			enqueue_after_commit= False, 
			at_front= False
		)



def enq_rename():
	frappe.enqueue(
			rename, 
			queue= "long",
			timeout= 3000000, 
			is_async= True, 
			now= False, 
			job_name= "Sales Invoice Rename", 
			enqueue_after_commit= False, 
			at_front= False
		)


def rename():
	from frappe.utils.csvutils import read_csv_content_from_attached_file
	rows = read_csv_content_from_attached_file(frappe.get_doc("Rename Tool", "Rename Tool"))
	return bulk_rename('Sales Invoice', rows=rows, via_console=True)

def enqueue_j():
	frappe.enqueue(
			import_si_from_xls, 
			queue= "long",
			timeout= 3000000, 
			is_async= True, 
			now= False, 
			job_name= "Sales Invoice Import", 
			enqueue_after_commit= False, 
			at_front= False,
			file_path= "/Users/sagarbhogayata/Sales_Stores.xlsx"
		)

def import_si_from_xls(file_path="/Users/sagarbhogayata/Sales_Stores.xlsx"):
	# print(file_path)
	# print(type(file_path))
	# df = pd.read_excel("/home/midocean/Project/f14/apps/pic_custom/pic_custom/Sales.xlsx")
	df = pd.read_excel(str(file_path))
	df1 = df.fillna("-")
	dataDict = df1.to_dict(orient='records')
	doc = None
	i = 1
	for data in dataDict:
		
		if not frappe.db.exists("Company", data.get("Company")):
			if data.get("Company") != "-":
				companyDoc = frappe.new_doc("Company")
				companyDoc.company_name = data.get("Company")
				x = data.get("Company").split(" ")
				abbr = str(x[0][0])+str(x[1][0])
				companyDoc.abbr = abbr
				companyDoc.default_currency = "AED"
				companyDoc.country = "United Arab Emirates"
				companyDoc.save()

		if not frappe.db.exists("Customer", data.get("Customer")):
			if data.get("Customer") != "-":
				custDoc = frappe.new_doc("Customer")
				custDoc.customer_name = data.get("Customer")
				custDoc.customer_type = "Individual"
				custDoc.save()

		if not frappe.db.exists("Customer", data.get("Customer")):
			if data.get("Customer") != "-":
				custDoc = frappe.new_doc("Customer")
				custDoc.customer_name = data.get("Customer")
				custDoc.customer_type = "Individual"
				custDoc.save()

		if not frappe.db.exists("UOM", data.get("UOM (Items)")):
			if data.get("UOM (Items)") != "-":
				uomDoc = frappe.new_doc("UOM")
				uomDoc.uom_name = data.get("UOM (Items)")
				uomDoc.enabled = 1
				uomDoc.save()

		if not frappe.db.exists("Item", data.get("Item (Items)")):
			if data.get("Item (Items)") != "-":
				itemDoc = frappe.new_doc("Item")
				itemDoc.item_code = str(data.get("Item (Items)"))
				itemDoc.item_name = data.get("Item Name (Items)")
				itemDoc.description = data.get("Description (Items)")
				itemDoc.stock_uom = data.get("UOM (Items)")
				itemDoc.item_group = "Products"
				itemDoc.save()
		
		if data.get("Company") != "-":
			if doc:
				doc.save()
				doc.append("payments",{
					'mode_of_payment': data.get("Mode of Payment (Sales Invoice Payment)"),
					'amount': doc.base_grand_total,
				})
				doc.save()
				# doc.submit()
				frappe.db.commit()
				print(i)
				i = i + 1
				doc = None
			salesinvoiceDoc = frappe.new_doc("Sales Invoice")
			salesinvoiceDoc.customer = data.get("Customer")
			salesinvoiceDoc.company = data.get("Company")
			salesinvoiceDoc.posting_date = data.get("Date")
			salesinvoiceDoc.set_posting_time = 1
			salesinvoiceDoc.due_date = data.get("Payment Due Date")
			salesinvoiceDoc.is_pos = data.get("Include Payment (POS)")
			salesinvoiceDoc.remarks = data.get("Remarks")
			salesinvoiceDoc.update_stock = data.get("Update Stock")
			salesinvoiceDoc.taxes_and_charges = data.get("Sales Taxes and Charges Template")
			salesinvoiceDoc.against_income_account = data.get("Sales Taxes and Charges Template")
			salesinvoiceDoc.currency = frappe.get_value("Company", data.get("Company"), "default_currency") 
			salesinvoiceDoc.conversion_rate = 1
			salesinvoiceDoc.append("items",{
				'item_code': data.get("Item (Items)"),
				'item_name': data.get("Item Name (Items)"),
				'description': data.get("Description (Items)"),
				'uom': data.get("UOM (Items)"),
				'rate': data.get("Rate (Items)"),
				'qty': data.get("Quantity (Items)"),
				'amount': data.get("Amount (Items)"),
				'warehouse': data.get("Warehouse (Items)"),
			})

			
		
			salesinvoiceDoc.append("taxes",{
				'charge_type': data.get("Type (Sales Taxes and Charges)"),
				'rate': data.get("Rate (Sales Taxes and Charges)"),
				'account_head': data.get("Account Head (Sales Taxes and Charges)"),
				'description': data.get("Description (Sales Taxes and Charges)")
			})

			# salesinvoiceDoc.save()
			doc = salesinvoiceDoc
			continue

		if doc:
			doc.append("items",{
				'item_code': data.get("Item (Items)"),
				'item_name': data.get("Item Name (Items)"),
				'description': data.get("Description (Items)"),
				'uom': data.get("UOM (Items)"),
				'rate': data.get("Rate (Items)"),
				'qty': data.get("Quantity (Items)"),
				'amount': data.get("Amount (Items)"),
				'warehouse': data.get("Warehouse (Items)"),
			})
			# doc.save()
		

		
			


		
