import frappe
from frappe.model.document import Document
import pandas as pd


def delete_si():
    lst = frappe.get_all("Sales Invoice", filters={'docstatus':1})
    for row in lst:
        Doc = frappe.get_doc("Sales Invoice", row.name)
        Doc.cancel()
        print(row.name)
        frappe.db.commit()

def enqueue_j():
    frappe.enqueue(
            import_si_from_xls, # python function or a module path as string
            queue="long", # one of short, default, long
            timeout=3000000, # pass timeout manually
            is_async=True, # if this is True, method is run in worker
            now=False, # if this is True, method is run directly (not in a worker) 
            job_name="Sales Invoice Import", # specify a job name
            enqueue_after_commit=False, # enqueue the job after the database commit is done at the end of the request
            at_front=False, # put the job at the front of the queue
            file_path="/home/frappe/frappe-bench/apps/import_tool/import_tool/Sales_Stores.xlsx"
        )

def import_si_from_xls(file_path):
    # print(file_path)
    # print(type(file_path))
    # df = pd.read_excel("/home/midocean/Project/f14/apps/pic_custom/pic_custom/Sales.xlsx")
    df = pd.read_excel(str(file_path))
    df1 = df.fillna("-")
    dataDict = df1.to_dict(orient='records')
    doc = None
    for data in dataDict:
        print(data)
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
                doc.submit()
                frappe.db.commit()
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

            salesinvoiceDoc.append("payments",{
                'mode_of_payment': data.get("Mode of Payment (Sales Invoice Payment)"),
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
            


        
