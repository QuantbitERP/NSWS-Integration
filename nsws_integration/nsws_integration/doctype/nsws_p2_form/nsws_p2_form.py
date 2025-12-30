# Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
# For license information, please see license.txt

from datetime import datetime
import json
import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate, formatdate
from dateutil.relativedelta import relativedelta
from datetime import datetime
import calendar
import requests

@frappe.whitelist()
def getval(value):
    return value if value else 0


def get_previous_month_name(current_month_name):
    months = list(calendar.month_name[1:])
    return months[(months.index(current_month_name) - 1) % 12]


def get_field_lable(field_name):
    return frappe.get_value(
        "DocField", {"parent": "NSWS P2 Form", "fieldname": field_name}, "label"
    )
    
@frappe.whitelist()
def format_precision(value, precision=2):
    try:
        # Check if value is None or null
        if value in [None, "None", "null"]:
            return f"{0:.{precision}f}"
        return f"{float(value):.{precision}f}"
    except (ValueError, TypeError):
        return f"{0:.{precision}f}"  # Return 0.00 if there's a ValueError or TypeError


@frappe.whitelist()
def get_opening_value(sugar_season, month=None):

    filters = {"sugar_season": sugar_season, "docstatus": 1}
    if month:
        data = get_all_previous_months(month)
        filters = {
            "sugar_season": sugar_season,
            "docstatus": 1,
            "season_month": ["in", data],
        }
    value = 0
    cane_value = getval(
        frappe.get_value(
            "NSWS P2 Form", filters, "sum(cane_crushed__during_the_month_mt)"
        )
    )
    if cane_value > 0:
        value = cane_value
        return value, False

    else:
        year_start_date = frappe.get_value(
            "NSWS Season", {"name": sugar_season}, "year_start_date"
        )
        last_season_data = frappe.get_all(
            "NSWS Season",
            filters={
                "year_end_date": ["<=", year_start_date],
                "disabled": 0,
                "name": ["!=", sugar_season],
            },
            limit=1,
        )
        last_season = None
        for l in last_season_data:
            last_season = l.name

        if not last_season:
            # frappe.msgprint('Please set "Cane Crushed Cumulative figures upto the Month end (MT)" value manualy')
            pass
        last_season_cane_value = getval(
            frappe.get_value(
                "NSWS P2 Form",
                {"sugar_season": last_season, "docstatus": 1},
                "sum(cane_crushed__during_the_month_mt)",
            )
        )
        if last_season_cane_value > 0:
            value = last_season_cane_value
        else:
            # frappe.msgprint('Please set "Cane Crushed Cumulative figures upto the Month end (MT)" value manualy')
            pass

        return value, True


@frappe.whitelist()
def get_due_payable(season_month, sugar_season):
    season_month_date = getdate(season_month)
    previous_month_date = season_month_date - relativedelta(months=1)
    previous_month_name = previous_month_date.strftime("%B")
    cane_dues_payable_cumulative = getval(
        frappe.get_value(
            "NSWS P2 Form",
            {
                "sugar_season": sugar_season,
                "season_month": ["=", previous_month_name],
                "docstatus": 1,
            },
            "sum(ss_24_25_field3)",
        )
    )
    cane_dues_paid_cumulative = getval(
        frappe.get_value(
            "NSWS P2 Form",
            {
                "sugar_season": sugar_season,
                "season_month": ["=", previous_month_name],
                "docstatus": 1,
            },
            "sum(ss_24_25_field4)",
        )
    )
    cane_price_arrears_cumulative = getval(
        frappe.get_value(
            "NSWS P2 Form",
            {
                "sugar_season": sugar_season,
                "season_month": ["=", previous_month_name],
                "docstatus": 1,
            },
            "sum(ss_24_25_field9)",
        )
    )

    if not cane_dues_payable_cumulative:
        cane_dues_payable_cumulative = 0

    if not cane_dues_paid_cumulative:
        cane_dues_paid_cumulative = 0

    if not cane_price_arrears_cumulative:
        cane_price_arrears_cumulative = 0

    return (
        cane_dues_payable_cumulative,
        cane_dues_paid_cumulative,
        cane_price_arrears_cumulative,
    )


@frappe.whitelist()
def get_opening_stock_white_sugar(season_month, sugar_season):
    season_month_date = getdate(season_month)
    previous_month_date = season_month_date - relativedelta(months=1)
    previous_month_name = previous_month_date.strftime("%B")
    opening_stock_white_sugar = getval(
        frappe.get_value(
            "NSWS P2 Form",
            {
                "sugar_season": sugar_season,
                "season_month": ["=", previous_month_name],
                "docstatus": 1,
            },
            "sum(white_sugar_closing_stock)",
        )
    )
    if not opening_stock_white_sugar:
        opening_stock_white_sugar = 0

    return opening_stock_white_sugar


@frappe.whitelist()
def get_opening_stock_biss_brown_sugar(season_month, sugar_season):
    season_month_date = getdate(season_month)
    previous_month_date = season_month_date - relativedelta(months=1)
    previous_month_name = previous_month_date.strftime("%B")
    opening_stock_biss_brown_sugar = getval(
        frappe.get_value(
            "NSWS P2 Form",
            {
                "sugar_season": sugar_season,
                "season_month": ["=", previous_month_name],
                "docstatus": 1,
            },
            "sum(biss_brown_sugar_closing_stock)",
        )
    )
    if not opening_stock_biss_brown_sugar:
        opening_stock_biss_brown_sugar = 0

    return opening_stock_biss_brown_sugar


@frappe.whitelist()
def get_opening_stock_raw_sugar(season_month, sugar_season):
    season_month_date = getdate(season_month)
    previous_month_date = season_month_date - relativedelta(months=1)
    previous_month_name = previous_month_date.strftime("%B")
    opening_stock_raw_sugar = getval(
        frappe.get_value(
            "NSWS P2 Form",
            {
                "sugar_season": sugar_season,
                "season_month": ["=", previous_month_name],
                "docstatus": 1,
            },
            "sum(raw_sugar_closing_stock)",
        )
    )
    if not opening_stock_raw_sugar:
        opening_stock_raw_sugar = 0

    return opening_stock_raw_sugar


@frappe.whitelist()
def get_opening_stock_outside_godown_white_sugar(season_month, sugar_season):
    season_month_date = getdate(season_month)
    previous_month_date = season_month_date - relativedelta(months=1)
    previous_month_name = previous_month_date.strftime("%B")
    opening_stock_outside_godown_white_sugar = getval(
        frappe.get_value(
            "NSWS P2 Form",
            {
                "sugar_season": sugar_season,
                "season_month": ["=", previous_month_name],
                "docstatus": 1,
            },
            "sum(outside_white_sugar_closing_stock)",
        )
    )
    if not opening_stock_outside_godown_white_sugar:
        opening_stock_outside_godown_white_sugar = 0

    return opening_stock_outside_godown_white_sugar


@frappe.whitelist()
def get_opening_stock_outside_godown_biss_brown_sugar(season_month, sugar_season):
    season_month_date = getdate(season_month)
    previous_month_date = season_month_date - relativedelta(months=1)
    previous_month_name = previous_month_date.strftime("%B")
    opening_stock_outside_godown_biss_brown_sugar = getval(
        frappe.get_value(
            "NSWS P2 Form",
            {
                "sugar_season": sugar_season,
                "season_month": ["=", previous_month_name],
                "docstatus": 1,
            },
            "sum(outside_biss_brown_sugar_closing_stock)",
        )
    )
    if not opening_stock_outside_godown_biss_brown_sugar:
        opening_stock_outside_godown_biss_brown_sugar = 0

    return opening_stock_outside_godown_biss_brown_sugar


@frappe.whitelist()
def get_opening_stock_outside_godown_raw_sugar(season_month, sugar_season):
    season_month_date = getdate(season_month)
    previous_month_date = season_month_date - relativedelta(months=1)
    previous_month_name = previous_month_date.strftime("%B")
    opening_stock_outside_godown_raw_sugar = getval(
        frappe.get_value(
            "NSWS P2 Form",
            {
                "sugar_season": sugar_season,
                "season_month": ["=", previous_month_name],
                "docstatus": 1,
            },
            "sum(outside_raw_sugar_closing_stock)",
        )
    )
    if not opening_stock_outside_godown_raw_sugar:
        opening_stock_outside_godown_raw_sugar = 0

    return opening_stock_outside_godown_raw_sugar


# Get all previous months
def get_all_previous_months(current_month_name: str):
    month_names = [
      
        "October",
        "November",
        "December",
        "January",
        "February",
        "March",
        "April",
        "May",
          "June",
        "July",
        "August",
        "September",
    ]
    month_index = {month: i for i, month in enumerate(month_names)}
    if current_month_name not in month_index:
        raise ValueError(f"'{current_month_name}' is not a valid month name.")

    current_month_idx = month_index[current_month_name]
    previous_months = []
    for i in range(current_month_idx - 1, -1, -1):
        previous_months.append(month_names[i])

    return previous_months


# Get only previous month
def get_previous_month(current_month_name: str):
    month_names = [
        
        "October",
        "November",
        "December",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
    ]
    month_index = {month: i for i, month in enumerate(month_names)}
    if current_month_name not in month_index:
        raise ValueError(f"'{current_month_name}' is not a valid month name.")

    current_month_idx = month_index[current_month_name]
    # Calculate the previous month index using modulo to handle wrapping
    previous_month_idx = (current_month_idx - 1) % len(month_names)
    previous_month = month_names[previous_month_idx]

    return previous_month


class NSWSP2Form(Document):       
        
    # def before_submit(self):
        # if not self.upload_gstr_1 and self.dispatch_multiselect:
        # if not self.upload_gstr_1:
        #     frappe.throw("GSTR is Mandatory")

    # New code logic starts here

    @frappe.whitelist()
    def get_cumulative_value(self, season_month, season=None, date=None):

        season_start_date = frappe.get_value("NSWS Season", season, "year_start_date")
        month_name = season_start_date.strftime("%B")
        season_end_date_obj = datetime.strptime(date, "%Y-%m-%d")
        start_year = season_start_date.year
        end_year = season_end_date_obj.year
        start_date = datetime.strptime(f"{month_name} {start_year}", "%B %Y")
        end_date = datetime.strptime(f"{season_month} {end_year}", "%B %Y")

        month_list = get_all_previous_months(season_month)
        # frappe.throw(f"{start_date} {end_date}")
        # Only push the previous month into month_list
        # current_date = end_date - relativedelta(months=1)

        # while current_date >= start_date:
        #     # Get the full month name (e.g., "January", "February")
        #     month_name = current_date.strftime('%B')

        #     # Check if the document exists for the current month (month name)
        #     is_exists = frappe.db.exists("NSWS P2 Form", {"sugar_season": season, "season_month": month_name, "docstatus": 1})

        #     if is_exists:
        #         # If document exists, append the month name to month_list
        #         month_list.append(month_name)
        #         break
        #     else:
        #         # If document doesn't exist, move to the previous month
        #         current_date -= relativedelta(months=1)

        # while current_date <= end_date:
        #     month_list.append(current_date.strftime('%B'))
        #     current_date += relativedelta(months=1)

        field_list = [
            "ns_2i_a2",
            "ns_2i_b2",
            "ns_2i_c2",
            "ns_2i_c1_2",
            "ns_2i_c2_2",
            "ns_2i_c3_2",
            "ns_2ii_a2",
            "ns_2ii_b2",
            "ns_2ii_c2",
            "ns_2iii_a2",
            "ns_2iii_b2",
            "ns_31_i2",
            "ns_31_ii2",
            "ns_31_iii2",
            "ns_31_iv2",
            "ns_31_v2",
            "ns_31_vi2",
            "ns_32_i2",
            "ns_32_ii2",
            "ns_32_iii2",
            "ns_611_field2",
            "ns_612_field3",
            "ns_613_field3",
            "ns_614_field3",
            "ns_62_bissfield3",
            "ns_63_internalfield4",
            "ns_64_internalfield4",
            "ns_65_salefield4",
            "ns_66a_exportrefinedfield7",
            "ns_66a_exportrawfield5",
            "ns_66a_exportinvoicefield4",
            "ns_66b_exportaasfield5",
        ]

        field_list2 = [
            "ns_2i_a1",
            "ns_2i_b1",
            "ns_2i_c1",
            "ns_2i_c1_1",
            "ns_2i_c2_1",
            "ns_2i_c3_1",
            "ns_2ii_a1",
            "ns_2ii_b1",
            "ns_2ii_c1",
            "ns_2iii_a1",
            "ns_2iii_b1",
            "ns_31_i1",
            "ns_31_ii1",
            "ns_31_iii1",
            "ns_31_iv1",
            "ns_31_v1",
            "ns_31_vi1",
            "ns_32_i1",
            "ns_32_ii1",
            "ns_32_iii1",
            "ns_611_field3",
            "ns_612_field4",
            "ns_613_field4",
            "ns_614_field4",
            "ns_62_bissfield2",
            "ns_63_internalfield3",
            "ns_64_internalfield3",
            "ns_65_salefield3",
            "ns_66a_exportrefinedfield6",
            "ns_66a_exportrawfield4",
            "ns_66a_exportinvoicefield3",
            "ns_66b_exportaasfield4",
        ]

        for i in range(0, len(field_list)):
            self.set(field_list[i], 0)
            # temp = frappe.get_all("NSWS P2 Form",{"season_month":["in",month_list],"name":["!=",self.name],'docstatus': 1},f"sum({field_list[i]}) as sum")
            temp = frappe.get_all(
                "NSWS P2 Form",
                {
                    "sugar_season": self.sugar_season,
                    "season_month": ["in", month_list],
                    "name": ["!=", self.name],
                    "docstatus": 1,
                },
                f"sum({field_list2[i]}) as sum",
            )
            # frappe.throw(f'{float(temp[0]["sum"] or 0)}====={float((getattr(self,field_list2[i])) or 0)}')
            self.set(
                field_list[i],
                float(temp[0]["sum"] or 0)
                + float((getattr(self, field_list2[i])) or 0),
            )

        # frappe.throw(f"{month_list} ==== {temp}")

    # New code logic ends here

    # @frappe.whitelist()
    # def set_data_in_cane_crushed(self):
    #     self.cane_crushed_cumulative_figures_upto_the_month_end_mt = (get_opening_value(self.sugar_season) or 0) + (self.cane_crushed__during_the_month_mt or 0)

    @frappe.whitelist()
    def get_stock_of_sugar(self):

        # For White Sugar
        white_sugar_opening_stock = get_opening_stock_white_sugar(
            self.season_month, self.sugar_season
        )
        self.white_sugar_opening_stock = (
            white_sugar_opening_stock
            if white_sugar_opening_stock > 0
            else self.white_sugar_opening_stock
        )

        if not self.outside_white_sugar_closing_stock:
            self.outside_white_sugar_closing_stock = (
                self.outside_white_sugar_opening_stock
            )

        self.white_sugar_closing_stock = (
            (self.white_sugar_opening_stock or 0)
            + (
                (self.ns_2i_c4_1 or 0)
                - (
                    (self.ns_611_field3 or 0)
                    + (self.ns_612_field4 or 0)
                    + (self.ns_613_field4 or 0)
                    + (self.ns_614_field4 or 0)
                    + (self.ns_64_internalfield3 or 0)
                    + (self.ns_66a_exportrefinedfield6 or 0)
                    + (self.ns_66b_exportaasfield4 or 0)
                )
            )
            - (self.initial_value_of_outside_godown_white_sugar_closing_stock)
        )
        self.outside_white_sugar_closing_stock = (
            self.initial_value_of_outside_godown_white_sugar_closing_stock
            + self.outside_white_sugar_opening_stock
            - (self.duty_paid_sale_during_the_month_o_g_white_sugar)
        )

        dummy_outside_white_sugar_closing_stock = (
            self.initial_value_of_outside_godown_white_sugar_closing_stock
            + self.outside_white_sugar_opening_stock
        )

        if (
            self.duty_paid_sale_during_the_month_o_g_white_sugar
            > dummy_outside_white_sugar_closing_stock
        ):
            self.outside_white_sugar_closing_stock = (
                self.initial_value_of_outside_godown_white_sugar_closing_stock
                + self.outside_white_sugar_opening_stock
            )
            self.duty_paid_sale_during_the_month_o_g_white_sugar = 0
            frappe.msgprint(
                "Value of 'Duty paid sale during the month' is greater than Final Closing Stock"
            )

        temp_white_sugar_closing_stock = (self.white_sugar_opening_stock or 0) + (
            (self.ns_2i_c4_1 or 0)
            - (
                (self.ns_611_field3 or 0)
                + (self.ns_612_field4 or 0)
                + (self.ns_613_field4 or 0)
                + (self.ns_614_field4 or 0)
                + (self.ns_64_internalfield3 or 0)
                + (self.ns_66a_exportrefinedfield6 or 0)
                + (self.ns_66b_exportaasfield4 or 0)
            )
        )

        if temp_white_sugar_closing_stock < 0:
            temp_white_sugar_closing_stock = 0

        if (
            self.initial_value_of_outside_godown_white_sugar_closing_stock
            > temp_white_sugar_closing_stock
        ):
            self.outside_white_sugar_closing_stock = (
                self.outside_white_sugar_opening_stock
            )
            self.white_sugar_closing_stock = (self.white_sugar_opening_stock or 0) + (
                (self.ns_2i_c4_1 or 0)
                - (
                    (self.ns_611_field3 or 0)
                    + (self.ns_612_field4 or 0)
                    + (self.ns_613_field4 or 0)
                    + (self.ns_614_field4 or 0)
                    + (self.ns_64_internalfield3 or 0)
                    + (self.ns_66a_exportrefinedfield6 or 0)
                    + (self.ns_66b_exportaasfield4 or 0)
                )
            )

            self.initial_value_of_outside_godown_white_sugar_closing_stock = 0

            if self.white_sugar_closing_stock < 0:
                frappe.msgprint(
                    f'{get_field_lable("white_sugar_closing_stock")} is Negative'
                )
            frappe.msgprint(
                "Invalid Entry: Outside godown White Sugar Closing Stock is greater than Factory Premises White Sugar Closing Stock"
            )

        if self.white_sugar_closing_stock < 0:
            frappe.msgprint(
                f'{get_field_lable("white_sugar_closing_stock")} is Negative'
            )

        # For BISS / Brown Sugar
        biss_brown_sugar_opening_stock = get_opening_stock_biss_brown_sugar(
            self.season_month, self.sugar_season
        )
        self.biss_brown_sugar_opening_stock = (
            biss_brown_sugar_opening_stock
            if biss_brown_sugar_opening_stock > 0
            else self.biss_brown_sugar_opening_stock
        )

        if not self.outside_biss_brown_sugar_closing_stock:
            self.outside_biss_brown_sugar_closing_stock = (
                self.outside_biss_brown_sugar_opening_stock
            )

        self.biss_brown_sugar_closing_stock = (
            (
                self.biss_brown_sugar_opening_stock
                + self.biss__brown_sugar_produced_during_the_month
            )
            - self.ns_62_bissfield2
            - (self.initial_value_of_outside_godown_biss_brown_sugar_closing_stock)
        )
        self.outside_biss_brown_sugar_closing_stock = (
            self.initial_value_of_outside_godown_biss_brown_sugar_closing_stock
            + self.outside_biss_brown_sugar_opening_stock
            - (self.duty_paid_sale_during_the_month_o_g_biss_brown_sugar)
        )

        dummy_outside_biss_brown_sugar_closing_stock = (
            self.initial_value_of_outside_godown_biss_brown_sugar_closing_stock
            + self.outside_biss_brown_sugar_opening_stock
        )

        if (
            self.duty_paid_sale_during_the_month_o_g_biss_brown_sugar
            > dummy_outside_biss_brown_sugar_closing_stock
        ):
            self.outside_biss_brown_sugar_closing_stock = (
                self.initial_value_of_outside_godown_biss_brown_sugar_closing_stock
                + self.outside_biss_brown_sugar_opening_stock
            )
            self.duty_paid_sale_during_the_month_o_g_biss_brown_sugar = 0
            frappe.msgprint(
                "Value of 'Duty paid sale during the month' is greater than Final Closing Stock"
            )

        temp_biss_brown_sugar_closing_stock = (
            self.biss_brown_sugar_opening_stock
            + self.biss__brown_sugar_produced_during_the_month
        ) - self.ns_62_bissfield2

        if temp_biss_brown_sugar_closing_stock < 0:
            temp_biss_brown_sugar_closing_stock = 0

        if (
            self.initial_value_of_outside_godown_biss_brown_sugar_closing_stock
            > temp_biss_brown_sugar_closing_stock
        ):
            self.outside_biss_brown_sugar_closing_stock = (
                self.outside_biss_brown_sugar_opening_stock
            )
            self.biss_brown_sugar_closing_stock = (
                self.biss_brown_sugar_opening_stock
                + self.biss__brown_sugar_produced_during_the_month
            ) - self.ns_62_bissfield2

            self.initial_value_of_outside_godown_biss_brown_sugar_closing_stock = 0

            if self.biss_brown_sugar_closing_stock < 0:
                frappe.msgprint(
                    f'{get_field_lable("biss_brown_sugar_closing_stock")} is Negative'
                )
            frappe.msgprint(
                "Invalid Entry: Outside godown BISS / Brown Sugar Closing Stock is greater than Factory Premises BISS / Brown Sugar Closing Stock"
            )

        if self.biss_brown_sugar_closing_stock < 0:
            frappe.msgprint(
                f'{get_field_lable("biss_brown_sugar_closing_stock")} is Negative'
            )

        # For Raw Sugar
        raw_sugar_opening_stock = get_opening_stock_raw_sugar(
            self.season_month, self.sugar_season
        )
        self.raw_sugar_opening_stock = (
            raw_sugar_opening_stock
            if raw_sugar_opening_stock > 0
            else self.raw_sugar_opening_stock
        )

        if not self.outside_raw_sugar_closing_stock:
            self.outside_raw_sugar_closing_stock = self.outside_raw_sugar_opening_stock

        # self.raw_sugar_closing_stock = (
        #     self.raw_sugar_opening_stock
        #     + (self.ns_2ii_a1 + self.ns_2ii_b1 + self.ns_2ii_c1 + self.ns_2iii_c1)
        #     - (
        #         self.ns_63_internalfield3
        #         + self.ns_65_salefield3
        #         + self.ns_66a_exportrawfield4
        #         + self.ns_66a_exportinvoicefield3
        #     )
        #     - (self.initial_value_of_outside_godown_raw_sugar_closing_stock)
        # )
        self.raw_sugar_closing_stock = (
            self.raw_sugar_opening_stock
            + (self.ns_2ii_a1 + self.ns_2ii_b1)
            + (self.ns_2ii_c1 + self.ns_2iii_c1)
            - self.ns_2i_c2_1
            - (self.ns_63_internalfield2 + self.ns_65_salefield2)
            - (self.ns_66a_exportrawfield4 + self.ns_66a_exportinvoicefield3)
        )
         
        self.outside_raw_sugar_closing_stock = (
            self.initial_value_of_outside_godown_raw_sugar_closing_stock
            + self.outside_raw_sugar_opening_stock
            - (self.duty_paid_sale_during_the_month_o_g_raw_sugar)
        )

        dummy_outside_raw_sugar_closing_stock = (
            self.initial_value_of_outside_godown_raw_sugar_closing_stock
            + self.outside_raw_sugar_opening_stock
        )

        if (
            self.duty_paid_sale_during_the_month_o_g_raw_sugar
            > dummy_outside_raw_sugar_closing_stock
        ):
            self.outside_raw_sugar_closing_stock = (
                self.initial_value_of_outside_godown_raw_sugar_closing_stock
                + self.outside_raw_sugar_opening_stock
            )
            self.duty_paid_sale_during_the_month_o_g_raw_sugar = 0
            frappe.msgprint(
                "Value of 'Duty paid sale during the month' is greater than Final Closing Stock"
            )

        temp_raw_sugar_closing_stock = (
            self.raw_sugar_opening_stock
            + (self.ns_2ii_a1 + self.ns_2ii_b1 + self.ns_2ii_c1 + self.ns_2iii_c1)
            - (
                self.ns_63_internalfield3
                + self.ns_65_salefield3
                + self.ns_66a_exportrawfield4
                + self.ns_66a_exportinvoicefield3
            )
        )

        if temp_raw_sugar_closing_stock < 0:
            temp_raw_sugar_closing_stock = 0

        if (
            self.initial_value_of_outside_godown_raw_sugar_closing_stock
            > temp_raw_sugar_closing_stock
        ):
            self.outside_raw_sugar_closing_stock = self.outside_raw_sugar_opening_stock
            self.raw_sugar_closing_stock = (
                self.raw_sugar_opening_stock
                + (self.ns_2ii_a1 + self.ns_2ii_b1 + self.ns_2ii_c1 + self.ns_2iii_c1)
                - (
                    self.ns_63_internalfield3
                    + self.ns_65_salefield3
                    + self.ns_66a_exportrawfield4
                    + self.ns_66a_exportinvoicefield3
                )
            )

            self.initial_value_of_outside_godown_raw_sugar_closing_stock = 0

            if self.raw_sugar_closing_stock < 0:
                frappe.msgprint(
                    f'{get_field_lable("raw_sugar_closing_stock")} is Negative'
                )
            frappe.msgprint(
                "Invalid Entry: Outside godown Raw Sugar Closing Stock is greater than Factory Premises Raw Sugar Closing Stock"
            )

        if self.raw_sugar_closing_stock < 0:
            frappe.msgprint(f'{get_field_lable("raw_sugar_closing_stock")} is Negative')

        self.outside_white_sugar_opening_stock = (
            get_opening_stock_outside_godown_white_sugar(
                self.season_month, self.sugar_season
            )
        )
        self.outside_biss_brown_sugar_opening_stock = (
            get_opening_stock_outside_godown_biss_brown_sugar(
                self.season_month, self.sugar_season
            )
        )
        self.outside_raw_sugar_opening_stock = (
            get_opening_stock_outside_godown_raw_sugar(
                self.season_month, self.sugar_season
            )
        )

    def get_packing_details_of_sugar(self):
        # Packing details of sugar (In MT)
        self.pdosim_field3 = self.pdosim_field1 + self.pdosim_field6
        self.pdosim_field4 = self.pdosim_field2 + self.pdosim_field7
        # self.pdosim_field5 = self.pdosim_field3 + self.pdosim_field4
        self.pdosim_field5=self.pdosim_field1 + self.pdosim_field6 + self.pdosim_field2 +self.pdosim_field7
        if self.pdosim_field5 != 0:
            self.pdosim_field8 = (self.pdosim_field3) / (self.pdosim_field5) * 100
        else:
            self.pdosim_field8 = 0

        if self.pdosim_field5 != 0:
            self.pdosim_field9 = (self.pdosim_field4) / (self.pdosim_field5) * 100
        else:
            self.pdosim_field9 = 0

    @frappe.whitelist()
    def get_cane_dues_data(self):
        # self.get('cane_dues_5_year_data').clear()
        month = get_previous_month_name(self.season_month)
        start_year, end_year = map(int, self.sugar_season.split("-"))
        previous_seasons = []
        for i in range(1, 5):
            previous_start_year = start_year - i
            previous_end_year = end_year - i
            previous_seasons.append(f"{previous_start_year}-{previous_end_year}")
        
        for season in previous_seasons:
            docs = frappe.get_list(
                "NSWS P2 Form",
                filters={"sugar_season": season, "docstatus": 1, "season_month": month},
                fields=[
                    "ss_24_25_field1 as cane_crushed",
                    "ss_24_25_field2 as sugar_recovery",
                    "ss_24_25_field9 as cane_price_arrears",
                    "ss_24_25_field6 as sugar_production",
                    "ss_24_25_field3 as cane_price_payable",
                    "ss_24_25_field4 as cane_dues_paid",
                    "ss_24_25_field5 as number_of_farmers",
                ],
            )
            for record in docs:
                
                self.append(
                    "cane_dues_5_year_data",
                    {
                        "child_season": season,
                        "cane_crushed": record.cane_crushed,
                        "sugar_recovery": record.sugar_recovery,
                        "cane_price_paid": record.cane_price_paid,
                        "cane_price_arrears": record.cane_price_arrears,
                        "sugar_production": record.sugar_production,
                        "cane_price_payable": record.cane_price_payable,
                        "cane_dues_paid": record.cane_dues_paid,
                        "number_of_farmers": record.number_of_farmers,
                    },
                )
        # # Cane Dues 24-25
        self.ss_24_25_field1 = (
            self.cane_crushed_cumulative_figures_upto_the_month_end_mt
        )
        self.ss_24_25_field6 = (
            self.total_sugar_produced_cumulative_figures_upto_the_month_end_mt
        )
        self.ss_24_25_field2 = self.ns_4_iii2
        self.ss_24_25_field3, self.ss_24_25_field4, self.ss_24_25_field9 = (
            get_due_payable(self.season_month, self.sugar_season)
        )

        self.ss_24_25_field3 += self.ss_24_25_field7
        self.ss_24_25_field4 += self.ss_24_25_field8
        sub = self.ss_24_25_field3 - self.ss_24_25_field4
        self.ss_24_25_field9 = sub if sub > 0 else 0

        # Get cane dues last month data
        prev_months_list = get_all_previous_months(self.season_month)

        # No. of farmers from which cane procured - During the Month retrieval
        prev_month_for_number_of_farmers = get_previous_month(self.season_month)

        actual_value_of_ss_24_25_field5 = frappe.get_value(
            "NSWS P2 Form",
            {
                "sugar_season": self.sugar_season,
                "season_month": ["in", self.season_month],
                "docstatus": 1,
            },
            "sum(ss_24_25_field5)",
        )
        # actual_value_of_ss_23_24_field5 = frappe.get_value(
        #     "NSWS P2 Form",
        #     {
        #         "sugar_season": "2023-2024",
        #         "season_month": ["in", prev_month_for_number_of_farmers],
        #         "docstatus": 1,
        #     },
        #     "sum(ss_23_24_field5)",
        # )
        # actual_value_of_ss_22_23_field8 = frappe.get_value(
        #     "NSWS P2 Form",
        #     {
        #         "sugar_season": "2022-2023",
        #         "season_month": ["in", prev_month_for_number_of_farmers],
        #         "docstatus": 1,
        #     },
        #     "sum(ss_22_23_field8)",
        # )
        # actual_value_of_ss_21_22_field8 = frappe.get_value(
        #     "NSWS P2 Form",
        #     {
        #         "sugar_season": "2021-2022",
        #         "season_month": ["in", prev_month_for_number_of_farmers],
        #         "docstatus": 1,
        #     },
        #     "sum(ss_21_22_field8)",
        # )
        # actual_value_of_ss_20_21_field8 = frappe.get_value(
        #     "NSWS P2 Form",
        #     {
        #         "sugar_season": "2020-2021",
        #         "season_month": ["in", prev_month_for_number_of_farmers],
        #         "docstatus": 1,
        #     },
        #     "sum(ss_20_21_field8)",
        # )
        # actual_value_of_ss_19_20_field8 = frappe.get_value(
        #     "NSWS P2 Form",
        #     {
        #         "sugar_season": "2019-2020",
        #         "season_month": ["in", prev_month_for_number_of_farmers],
        #         "docstatus": 1,
        #     },
        #     "sum(ss_19_20_field8)",
        # )

        self.ss_24_25_field5 = (
            actual_value_of_ss_24_25_field5
            if actual_value_of_ss_24_25_field5
            else self.ss_24_25_field5
        )
        # self.ss_23_24_field5 = (
        #     actual_value_of_ss_23_24_field5
        #     if actual_value_of_ss_23_24_field5
        #     else self.ss_23_24_field5
        # )
        # self.ss_22_23_field8 = (
        #     actual_value_of_ss_22_23_field8
        #     if actual_value_of_ss_22_23_field8
        #     else self.ss_22_23_field8
        # )
        # self.ss_21_22_field8 = (
        #     actual_value_of_ss_21_22_field8
        #     if actual_value_of_ss_21_22_field8
        #     else self.ss_21_22_field8
        # )
        # self.ss_20_21_field8 = (
        #     actual_value_of_ss_20_21_field8
        #     if actual_value_of_ss_20_21_field8
        #     else self.ss_20_21_field8
        # )
        # self.ss_19_20_field8 = (
        #     actual_value_of_ss_19_20_field8
        #     if actual_value_of_ss_19_20_field8
        #     else self.ss_19_20_field8
        # )

        # # Sugar Season - 2023-24
        # self.ss_23_24_field1 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2023-2024",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(cane_crushed__during_the_month_mt)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2023-2024",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(cane_crushed__during_the_month_mt)",
        #     )
        #     else self.ss_23_24_field1
        # )
        # self.ss_23_24_field2 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2023-2024",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ns_4_iii1)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2023-2024",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ns_4_iii1)",
        #     )
        #     else self.ss_23_24_field2
        # )
        # self.ss_23_24_field6 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2023-2024",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(total_sugar_produced__during_the_month_mt)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2023-2024",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(total_sugar_produced__during_the_month_mt)",
        #     )
        #     else self.ss_23_24_field6
        # )

        # # Sugar Season - 2022-23
        # self.ss_22_23_field1 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2022-2023",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(cane_crushed__during_the_month_mt)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2022-2023",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(cane_crushed__during_the_month_mt)",
        #     )
        #     else self.ss_22_23_field1
        # )
        # self.ss_22_23_field2 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2022-2023",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ns_4_iii1)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2022-2023",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ns_4_iii1)",
        #     )
        #     else self.ss_22_23_field2
        # )
        # self.ss_22_23_field5 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2022-2023",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(total_sugar_produced__during_the_month_mt)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2022-2023",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(total_sugar_produced__during_the_month_mt)",
        #     )
        #     else self.ss_22_23_field5
        # )

        # # Sugar Season - 2021-22
        # self.ss_21_22_field1 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2021-2022",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(cane_crushed__during_the_month_mt)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2021-2022",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(cane_crushed__during_the_month_mt)",
        #     )
        #     else self.ss_21_22_field1
        # )
        # self.ss_21_22_field2 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2021-2022",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ns_4_iii1)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2021-2022",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ns_4_iii1)",
        #     )
        #     else self.ss_21_22_field2
        # )
        # self.ss_21_22_field5 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2021-2022",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(total_sugar_produced__during_the_month_mt)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2021-2022",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(total_sugar_produced__during_the_month_mt)",
        #     )
        #     else self.ss_21_22_field5
        # )

        # # Sugar Season - 2020-21
        # self.ss_20_21_field1 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2020-2021",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(cane_crushed__during_the_month_mt)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2020-2021",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(cane_crushed__during_the_month_mt)",
        #     )
        #     else self.ss_20_21_field1
        # )
        # self.ss_20_21_field2 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2020-2021",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ns_4_iii1)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2020-2021",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ns_4_iii1)",
        #     )
        #     else self.ss_20_21_field2
        # )
        # self.ss_20_21_field5 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2020-2021",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(total_sugar_produced__during_the_month_mt)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2020-2021",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(total_sugar_produced__during_the_month_mt)",
        #     )
        #     else self.ss_20_21_field5
        # )

        # # Sugar Season - 2019-20
        # self.ss_19_20_field1 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2019-2020",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(cane_crushed__during_the_month_mt)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2019-2020",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(cane_crushed__during_the_month_mt)",
        #     )
        #     else self.ss_19_20_field1
        # )
        # self.ss_19_20_field2 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2019-2020",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ns_4_iii1)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2019-2020",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ns_4_iii1)",
        #     )
        #     else self.ss_19_20_field2
        # )
        # self.ss_19_20_field5 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2019-2020",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(total_sugar_produced__during_the_month_mt)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2019-2020",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(total_sugar_produced__during_the_month_mt)",
        #     )
        #     else self.ss_19_20_field5
        # )

        # # calculation for Sugar Season - 2023-24
        # self.ss_23_24_field7 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2023-2024",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field7)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2023-2024",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field7)",
        #     )
        #     else self.ss_23_24_field7
        # )
        # self.ss_23_24_field4 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2023-2024",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field8)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2023-2024",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field8)",
        #     )
        #     else self.ss_23_24_field4
        # )
        # self.ss_23_24_field9 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2023-2024",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field3 - ss_24_25_field4) as sumcanearrears",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2023-2024",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field3 - ss_24_25_field4) as sumcanearrears",
        #     )
        #     else self.ss_23_24_field9
        # )

        # self.ss_23_24_field4 += self.ss_23_24_field8
        # self.ss_23_24_field9 = self.ss_23_24_field7 - self.ss_23_24_field4

        # if self.ss_23_24_field9 < 0:
        #     self.ss_23_24_field8 = 0
        #     self.ss_23_24_field4 = (
        #         frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2023-2024",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_23_24_field4)",
        #         )
        #         if frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2023-2024",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_23_24_field4)",
        #         )
        #         else self.ss_23_24_field4
        #     )
        #     self.ss_23_24_field9 = (
        #         frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2023-2024",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_23_24_field9)",
        #         )
        #         if frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2023-2024",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_23_24_field9)",
        #         )
        #         else self.ss_23_24_field9
        #     )
        #     frappe.msgprint(
        #         "Value of 'Cane Price Paid (in Rs Cr) - During the Month' is invalid"
        #     )

        # # calculation for Sugar Season - 2022-23
        # self.ss_22_23_field7 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2022-2023",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field8)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2022-2023",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field8)",
        #     )
        #     else self.ss_22_23_field7
        # )
        # self.ss_22_23_field4 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2022-2023",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field3 - ss_24_25_field4) as sumcanearrears",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2022-2023",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field3 - ss_24_25_field4) as sumcanearrears",
        #     )
        #     else self.ss_22_23_field4
        # )
        # self.ss_22_23_field6 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2022-2023",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field7)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2022-2023",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field7)",
        #     )
        #     else self.ss_22_23_field6
        # )

        # self.ss_22_23_field7 += self.ss_22_23_field3
        # self.ss_22_23_field4 = self.ss_22_23_field6 - self.ss_22_23_field7

        # if self.ss_22_23_field4 < 0:
        #     self.ss_22_23_field3 = 0
        #     self.ss_22_23_field7 = (
        #         frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2022-2023",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_22_23_field7)",
        #         )
        #         if frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2022-2023",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_22_23_field7)",
        #         )
        #         else self.ss_22_23_field7
        #     )
        #     self.ss_22_23_field4 = (
        #         frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2022-2023",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_22_23_field4)",
        #         )
        #         if frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2022-2023",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_22_23_field4)",
        #         )
        #         else self.ss_22_23_field4
        #     )
        #     frappe.msgprint(
        #         "Value of 'Cane Price Paid (in Rs Cr) - During the Month' is invalid"
        #     )

        # # calculation for Sugar Season - 2021-22
        # self.ss_21_22_field7 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2021-2022",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field8)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2021-2022",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field8)",
        #     )
        #     else self.ss_21_22_field7
        # )
        # self.ss_21_22_field4 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2021-2022",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field3 - ss_24_25_field4) as sumcanearrears",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2021-2022",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field3 - ss_24_25_field4) as sumcanearrears",
        #     )
        #     else self.ss_21_22_field4
        # )
        # self.ss_21_22_field6 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2021-2022",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field7)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2021-2022",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field7)",
        #     )
        #     else self.ss_21_22_field6
        # )

        # self.ss_21_22_field7 += self.ss_21_22_field3
        # self.ss_21_22_field4 = self.ss_21_22_field6 - self.ss_21_22_field7

        # if self.ss_21_22_field4 < 0:
        #     self.ss_21_22_field3 = 0
        #     self.ss_21_22_field7 = (
        #         frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2021-2022",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_21_22_field7)",
        #         )
        #         if frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2021-2022",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_21_22_field7)",
        #         )
        #         else self.ss_21_22_field7
        #     )
        #     self.ss_21_22_field4 = (
        #         frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2021-2022",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_21_22_field4)",
        #         )
        #         if frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2021-2022",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_21_22_field4)",
        #         )
        #         else self.ss_21_22_field4
        #     )
        #     frappe.msgprint(
        #         "Value of 'Cane Price Paid (in Rs Cr) - During the Month' is invalid"
        #     )

        # # calculation for Sugar Season - 2020-21
        # self.ss_20_21_field7 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2020-2021",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field8)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2020-2021",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field8)",
        #     )
        #     else self.ss_20_21_field7
        # )
        # self.ss_20_21_field4 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2020-2021",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field3 - ss_24_25_field4) as sumcanearrears",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2020-2021",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field3 - ss_24_25_field4) as sumcanearrears",
        #     )
        #     else self.ss_20_21_field4
        # )
        # self.ss_20_21_field6 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2020-2021",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field7)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2020-2021",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field7)",
        #     )
        #     else self.ss_20_21_field6
        # )

        # self.ss_20_21_field7 += self.ss_20_21_field3
        # self.ss_20_21_field4 = self.ss_20_21_field6 - self.ss_20_21_field7

        # if self.ss_20_21_field4 < 0:
        #     self.ss_20_21_field3 = 0
        #     self.ss_20_21_field7 = (
        #         frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2020-2021",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_20_21_field7)",
        #         )
        #         if frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2020-2021",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_20_21_field7)",
        #         )
        #         else self.ss_20_21_field7
        #     )
        #     self.ss_20_21_field4 = (
        #         frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2020-2021",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_20_21_field4)",
        #         )
        #         if frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2020-2021",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_20_21_field4)",
        #         )
        #         else self.ss_20_21_field4
        #     )
        #     frappe.msgprint(
        #         "Value of 'Cane Price Paid (in Rs Cr) - During the Month' is invalid"
        #     )

        # # calculation for Sugar Season - 2019-20
        # self.ss_19_20_field7 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2019-2020",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field8)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2019-2020",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field8)",
        #     )
        #     else self.ss_19_20_field7
        # )
        # self.ss_19_20_field4 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2019-2020",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field3 - ss_24_25_field4) as sumcanearrears",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2019-2020",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field3 - ss_24_25_field4) as sumcanearrears",
        #     )
        #     else self.ss_19_20_field4
        # )
        # self.ss_19_20_field6 = (
        #     frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2019-2020",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field7)",
        #     )
        #     if frappe.get_value(
        #         "NSWS P2 Form",
        #         {
        #             "sugar_season": "2019-2020",
        #             "season_month": ["in", prev_months_list],
        #             "docstatus": 1,
        #         },
        #         "sum(ss_24_25_field7)",
        #     )
        #     else self.ss_19_20_field6
        # )

        # self.ss_19_20_field7 += self.ss_19_20_field3
        # self.ss_19_20_field4 = self.ss_19_20_field6 - self.ss_19_20_field7

        # if self.ss_19_20_field4 < 0:
        #     self.ss_19_20_field3 = 0
        #     self.ss_19_20_field7 = (
        #         frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2019-2020",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_19_20_field7)",
        #         )
        #         if frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2019-2020",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_19_20_field7)",
        #         )
        #         else self.ss_19_20_field7
        #     )
        #     self.ss_19_20_field4 = (
        #         frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2019-2020",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_19_20_field4)",
        #         )
        #         if frappe.get_value(
        #             "NSWS P2 Form",
        #             {
        #                 "sugar_season": "2019-2020",
        #                 "season_month": ["in", prev_months_list],
        #                 "docstatus": 1,
        #             },
        #             "sum(ss_19_20_field4)",
        #         )
        #         else self.ss_19_20_field4
        #     )
        #     frappe.msgprint(
        #         "Value of 'Cane Price Paid (in Rs Cr) - During the Month' is invalid"
        #     )

        # child table append
        # prev_season_list = [{'2024-2025':{"season":}},'2024-2025','2024-2025','2024-2025','2024-2025','2024-2025']
        # for i in prev_season_list:
        #     self.append("cane_dues_5_year_data",{
        #         ""
        #     })
        # self.append('cane_dues_5_year_data', {'cane_crushed':})

    def get_json_data(self):
        sections = [
                        {
                            "sectionName": "Form applied for -",
                            "fieldResponses": [
                                {
                                    "fieldName": "Sugar Season",
                                    "inputValue": f"{self.sugar_season.split('-')[0]}-{self.sugar_season.split('-')[1][-2:]}",
                                },
                                {
                                    "fieldName": "Month",
                                    "inputValue": f"{self.season_month}",
                                },
                            ],
                        },
                        {
                            "sectionName": "Sugar Mill Details",
                            "fieldResponses": [
                                {
                                    "fieldName": "Name of the Undertaking/Group",
                                    "inputValue": f"{self.name_of_the_undertakinggroup}",
                                },
                                {
                                    "fieldName": "Plant Name",
                                    "inputValue": f"{self.plant_name}",
                                },
                                {
                                    "fieldName": "Plant Code",
                                    "inputValue": f"{self.plant_code}",
                                },
                                {"fieldName": "State", "inputValue": f"{self.state}"},
                            ],
                        },
                        {
                            "sectionName": "Cane Crushed",
                            "fieldResponses": [
                                {
                                    "fieldName": "Capacity (In TCD for sugar mills/Tons Per Day (TPD) for refineries)",
                                    "inputValue": f"{self.capacity_in_tcd_for_sugar_millstons_per_day_tpd_for_refineries}",
                                },
                                {
                                    "fieldName": "Cane Crushed - During the Month (MT)",
                                    "inputValue": f"{self.cane_crushed__during_the_month_mt}",
                                },
                            ],
                        },
                        
      
                    ]
        fieldResponses = [
            # {
            #     "fieldName": f"Sugar Season - {self.sugar_season.split('-')[0]}-{self.sugar_season.split('-')[1][-2:]}",
            #     "subFields": [
            #         {
            #             "fieldName": "Cane Price Payable (in Rs Cr) - During the Month",
            #             "inputValue": f"{self.ss_24_25_field7}",
            #         },
            #         {
            #             "fieldName": "Cane Price Paid (in Rs Cr) - During the Month",
            #             "inputValue": f"{self.ss_24_25_field8}",
            #         },
            #         {
            #             "fieldName": "No. of farmers from which cane procured - During the Month",
            #             "inputValue": f"{self.ss_24_25_field5}",
            #         },
            #     ],
            # },
            
           {
    "fieldName": f"Sugar Season - {self.sugar_season.split('-')[0]}-{self.sugar_season.split('-')[1][-2:]}",
    "subFields": [
        # {
        #     "fieldName": "Cane Crushed",
        #     "inputValue": f"{format_precision(self.ss_24_25_field1)}",
        # },
        # {
        #     "fieldName": "Sugar Production (in MT)",
        #     "inputValue": f"{format_precision(self.ss_24_25_field6)}",
        # },
        # {
        #     "fieldName": "Sugar Recovery",
        #     "inputValue": f"{format_precision(self.ss_24_25_field2)}",
        # },
        {
            "fieldName": "Cane Price Payable (in Rs Cr) - During the Month",
            "inputValue": f"{format_precision(self.ss_24_25_field7)}",
        },
        {
            "fieldName": "Cane Price Paid (in Rs Cr) - During the Month",
            "inputValue": f"{format_precision(self.ss_24_25_field8)}",
        },
        # {
        #     "fieldName": "Cane Dues Payable (in Rs Cr) - Cumulative",
        #     "inputValue": f"{format_precision(self.ss_24_25_field3)}",
        # },
        # {
        #     "fieldName": "Cane Dues Paid (in Rs Cr) - Cumulative",
        #     "inputValue": f"{format_precision(self.ss_24_25_field4)}",
        # },
        # {
        #     "fieldName": "Cane Price Arrears (in Rs Cr) - Cumulative",
        #     "inputValue": f"{format_precision(self.ss_24_25_field9)}",
        # },
        {
            "fieldName": "No. of farmers from which cane procured",
            "inputValue": f"{format_precision(self.ss_24_25_field5)}",
        },
    ],
}
        ]
        for i in self.get("cane_dues_5_year_data"):
            if i.idx == 1 or i.idx==2:  # For the first season
                farmers_field_name = "No. of farmers from which cane procured - During the Month"
            else:  # For subsequent seasons
                farmers_field_name = "No. of farmers from which cane procured"
            fieldResponses.append({
            "fieldName": f"Sugar Season - {i.child_season.split('-')[0]}-{i.child_season.split('-')[1][-2:]}",
            "subFields": [
                {
                    "fieldName": "Cane Crushed",
                    "inputValue": f"{format_precision(i.cane_crushed)}",
                },
                {
                    "fieldName": "Sugar Production (in MT)",
                    "inputValue": f"{format_precision(i.sugar_production)}",
                },
                {
                    "fieldName": "Sugar Recovery",
                    "inputValue": f"{format_precision(i.sugar_recovery)}",
                },
                {
                    "fieldName": "Cane Price Payable (in Rs Cr) - During the Sugar Season",
                    "inputValue": f"{format_precision(i.cane_price_payable)}",
                },
                {
                    "fieldName": "Cane Price Paid (in Rs Cr) - During the Month",
                    "inputValue": f"{format_precision(i.cane_price_paid)}",
                },
                # {
                #     "fieldName": "Cane Dues Paid (in Rs Cr) - Cumulative",
                #     "inputValue": f"{format_precision(i.cane_dues_paid)}",
                # },
                # {
                #     "fieldName": "Cane Price Arrears (in Rs Cr) - Cumulative",
                #     "inputValue": f"{format_precision(i.cane_price_arrears)}",
                # },
                {
                    "fieldName": farmers_field_name,
                    "inputValue": f"{i.number_of_farmers}",
                },
            ],
        })
            
        # if self.get("production_multiselect"):
        production_items = [item.p2_form_production_select for item in self.get("production_multiselect")]

        # Check if the list is not empty and then format it as a JSON array string
        if production_items:
            production_selections = "[" + ",".join([f"\"{item}\"" for item in production_items]) + "]"
        else:
            production_selections = "[]"

# The dispatch_selections variable will now contain a properly formatted JSON array string

        # Define dispatch sections that should be included, structured with their corresponding data
        production_sections = [
                            {
                                "fieldName": "2(I) White / Refined Sugar",
                                "subFields": [
                                    {
                                        "fieldName": "a) From Cane - During the Month (MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_2i_a1'))}",
                                    },
                                    {
                                        "fieldName": "b) From Reprocessing unmarketable old Sugar - During the Month (MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_2i_b1'))}",
                                    },
                                    {
                                        "fieldName": "c) From raw procured from other domestic sugar mills - During the Month (MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_2i_c1'))}",
                                    },
                                    {
                                        "fieldName": "c(1) From transferred white sugar from other domestic sugar mills - During the Month (MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_2i_c1_1'))}",
                                    },
                                    {
                                        "fieldName": "c(2) From Raw Sugar used from own Stock - During the Month (MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_2i_c2_1'))}",
                                    },
                                    {
                                        "fieldName": "c(3) White sugar produced from own stock of raw sugar - During the Month (MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_2i_c3_1'))}",
                                    },
                                ],
                            },
                            {
                                "fieldName": "2(II) Raw Sugar",
                                "subFields": [
                                    {
                                        "fieldName": "a) From Cane - During the Month (MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_2ii_a1'))}",
                                    },
                                    {
                                        "fieldName": "b) From Reprocessing unmarketable old Sugar - During the Month (MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_2ii_b1'))}",
                                    },
                                    {
                                        "fieldName": "c) Raw sugar procured from other domestic sugar mills",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_2ii_c1'))}",
                                    },
                                ],
                            },
                            {
                                "fieldName": "2(III) Procured sugar",
                                "subFields": [
                                    {
                                        "fieldName": "a) Raw Sugar - Internal transfer from other group sugar mills - During the Month (MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_2iii_a1'))}",
                                    },
                                    {
                                        "fieldName": "Internal transfer - Plant Code",
                                        "inputValue": f"{getattr(self, 'ns_2iii_internal1')}",
                                    },
                                    {
                                        "fieldName": "Internal transfer - Plant Name",
                                        "inputValue": f"{getattr(self, 'ns_2iii_internal2')}",
                                    },
                                    {
                                        "fieldName": "b) From Imported Raw Sugar - During the Month (MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_2iii_b1'))}",
                                    },
                                ],
                            },
                            {
                                "fieldName": "3(1) Diversion/sale of B-heavy/Syrup/sugarcane juice/sugar",
                                "subFields": [
                                    {
                                        "fieldName": "(i).a. Qty of Syrup/Sugarcane Juice/Sugar diverted for ethanol - During the Month (in MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_31_i1'))}",
                                    },
                                    {
                                        "fieldName": "(ii).a. Qty of B-Heavy diverted for ethanol - During the Month (MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_31_ii1'))}",
                                    },
                                    {
                                        "fieldName": "(iii).a. Qty of C-Heavy diverted for ethanol - During the Month (MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_31_iii1'))}",
                                    },
                                    {
                                        "fieldName": "(iv) Sale of B-Heavy - During the Month (MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_31_iv1'))}",
                                    },
                                    {
                                        "fieldName": "(v) Sale of Syrup/Sugarcane Juice/Sugar - During the Month (MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_31_v1'))}",
                                    },
                                    {
                                        "fieldName": "(vi) Sale of C-Heavy - During the Month (MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_31_vi1'))}",
                                    },
                                ],
                            },
                            {
                                "fieldName": "3(2) Ethanol Production",
                                "subFields": [
                                    {
                                        "fieldName": "(i).b. Ethanol Production from In-house Syrup/Sugarcane Juice/Sugar - During the Month (in KL)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_32_i1'))}",
                                    },
                                    {
                                        "fieldName": "(ii).b. Ethanol Production from In-house B-Heavy - During the Month (in KL)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_32_ii1'))}",
                                    },
                                    {
                                        "fieldName": "(iii).b. Ethanol Production from In-house C-Heavy - During the Month (in KL)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_32_iii1'))}",
                                    },
                                ],
                            },
                            
                        ]
        production_response=[
                {
                    "fieldName": "Select",
                    "inputValue": production_selections
                }
            ]
        # Loop through each dispatch section and add it to 'fieldResponses' if it's selected
        for section in production_sections:
            if section["fieldName"] in production_selections:  # Check if the dispatch section is selected
                production_response.append(section)
        if production_selections!="[]":
            production_response.append({
                                "fieldName": "4. Recovery % age",
                                "subFields": [
                                    {
                                        "fieldName": "4 (i) Purity of Mixed Juice (Monthly Average) - During Month (in MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_4_i1'))}",
                                    },
                                    {
                                        "fieldName": "4 (ii) Pol in Mixed Juice % Cane (Monthly Average) - During the Month (in MT)",
                                        "inputValue": f"{format_precision(getattr(self, 'ns_4_ii1'))}",
                                    },
                                ],
                            },)
        sections.append({
            "sectionName":  "Production of white / refined / Raw Sugar from Domestic sources",
            "fieldResponses": production_response
        })
       # Create a list of dispatch selections
        # if self.get("dispatch_multiselect"):
        dispatch_items = [item.p2_form_dispatches_select for item in self.get("dispatch_multiselect")]

        # Check if the list is not empty and then format it as a JSON array string
        if dispatch_items:
            dispatch_selections = "[" + ",".join([f"\"{item}\"" for item in dispatch_items]) + "]"
        else:
            dispatch_selections = "[]"

# The dispatch_selections variable will now contain a properly formatted JSON array string

        # Define dispatch sections that should be included, structured with their corresponding data
        dispatch_sections = [
            {
                "fieldName": "6.1.1 Domestic Dispatch w.r.t. monthly release quantity",
                "subFields": [
                    {"fieldName": "Release Order - Date", "inputValue": f"{datetime.strptime(getattr(self, 'release_order_date'), '%Y-%m-%d').strftime('%d/%m/%Y') if self.release_order_date else None}"},
                    {"fieldName": "Release order - Qty Released (MT)", "inputValue": f"{format_precision(getattr(self, 'ns_611_field1'))}"},
                    {"fieldName": "Qty Dispatched - During the Month (MT)", "inputValue": f"{format_precision(getattr(self, 'ns_611_field3'))}"},
                    {"fieldName": "Remarks", "inputValue": f"{getattr(self, 'ns_611_field4')}"}
                ]
            },
            {
                "fieldName": "6.1.2 Domestic Dispatch w.r.t. additional allotment, if any",
                "subFields": [
                    {"fieldName": "Release Order - Date", "inputValue": f"{datetime.strptime(getattr(self, 'ns_612_field1'), '%Y-%m-%d').strftime('%d/%m/%Y') if self.ns_612_field1 else None}"},
                    {"fieldName": "Release order - Qty Released (MT)", "inputValue": f"{format_precision(getattr(self, 'ns_612_field2'))}"},
                    {"fieldName": "Qty Dispatched - During the Month (MT)", "inputValue": f"{format_precision(getattr(self, 'ns_612_field4'))}"},
                    {"fieldName": "Remarks", "inputValue": f"{getattr(self, 'ns_612_field5')}"}
                ]
            },
            {
                "fieldName": "6.1.3 Domestic Dispatch w.r.t. extended quota",
                "subFields": [
                    {"fieldName": "Release Order - Date", "inputValue": f"{datetime.strptime(getattr(self, 'ns_613_field1'), '%Y-%m-%d').strftime('%d/%m/%Y') if self.ns_613_field1 else None}"},
                    {"fieldName": "Release order - Qty Released (MT)", "inputValue": f"{format_precision(getattr(self, 'ns_613_field2'))}"},
                    {"fieldName": "Qty Dispatched - During the Month (MT)", "inputValue": f"{format_precision(getattr(self, 'ns_613_field4'))}"},
                    {"fieldName": "Remarks", "inputValue": f"{getattr(self, 'ns_613_field5')}"}
                ]
            },
            {
                "fieldName": "6.1.4 Any other domestic Dispatch",
                "subFields": [
                    {"fieldName": "Release Order - Date", "inputValue": f"{datetime.strptime(getattr(self, 'ns_614_field1'), '%Y-%m-%d').strftime('%d/%m/%Y') if self.ns_614_field1 else None}"},
                    {"fieldName": "Release order - Qty Released (MT)", "inputValue": f"{format_precision(getattr(self, 'ns_614_field2'))}"},
                    {"fieldName": "Qty Dispatched - During the Month (MT)", "inputValue": f"{format_precision(getattr(self, 'ns_614_field4'))}"},
                    {"fieldName": "Remarks", "inputValue": f"{getattr(self, 'ns_614_field5')}"}
                ]
            },
            {
                "fieldName": "6.2 BISS Dispatch of unmarketable old Sugar for further processing",
                "subFields": [
                    {"fieldName": "Release Order - Date", "inputValue": f"{datetime.strptime(getattr(self, 'ns_62_bissfield1'), '%Y-%m-%d').strftime('%d/%m/%Y') if self.ns_62_bissfield1 else None}"},
                    {"fieldName": "Qty Used for reprocessing - During the Month (MT)", "inputValue": f"{format_precision(getattr(self, 'ns_62_bissfield2'))}"}
                ]
            },
            {
                "fieldName": "6.3 Internal transfer of raw sugar within a group",
                "serialNumber": "1",
                "subFields": [
                    {"fieldName": "Plant code of sugar mill to which sugar transferred", "inputValue": f"{getattr(self, 'ns_63_internalfield1')}"},
                    {"fieldName": "Qty Transferred to other mills - During the Month (MT)", "inputValue": f"{format_precision(getattr(self, 'ns_63_internalfield3'))}"}
                ]
            },
            {
                "fieldName": "6.4 Internal transfer of white sugar within a group",
                "serialNumber": "1",
                "subFields": [
                    {"fieldName": "Plant code of sugar mill to which sugar transferred", "inputValue": f"{getattr(self, 'ns_64_internalfield1')}"},
                    {"fieldName": "Qty Transferred to other mills - During the Month (MT)", "inputValue": f"{format_precision(getattr(self, 'ns_64_internalfield3'))}"}
                ]
            },
            {
                "fieldName": "6.5 Sale of raw sugar to other sugar mills for domestic purpose",
                "serialNumber": "1",
                "subFields": [
                    {"fieldName": "Plant code of sugar mill to which sugar transferred", "inputValue": f"{getattr(self, 'ns_65_salefield1')}"},
                    {"fieldName": "Qty Transferred to other mills - During the Month (MT)", "inputValue": f"{format_precision(getattr(self, 'ns_65_salefield3'))}"}
                ]
            }
        ]

        dispatch_response = [
            {
                "fieldName": "Select",
                "inputValue": dispatch_selections
            },
            {
                "fieldName": "HSN code and related details",
                "subFields": [
                    {"fieldName": "Total Quantity of Sales (in MT) for HSN Code - 17011490", "inputValue": f"{format_precision(self.hsn_code_t1)}"},
                    {"fieldName": "Total Quantity of Sales (in MT) for HSN Code - 17019990", "inputValue": f"{format_precision(self.hsn_code_t2)}"},
                    {"fieldName": "Total Quantity of Sales (in MT) for HSN Code - Others", "inputValue": f"{format_precision(self.hsn_code_t3)}"}
                ]
            }
        ]
        # Loop through each dispatch section and add it to 'fieldResponses' if it's selected
        for section in dispatch_sections:
            if section["fieldName"] in dispatch_selections:  # Check if the dispatch section is selected
                dispatch_response.append(section)

        sections.append({
            "sectionName": "Dispatches",
            "fieldResponses": dispatch_response
        })
            
        # if self.get("export_multiselect"):
        export_items = [item.p2_form_export_select for item in self.get("export_multiselect")]

        # Check if the list is not empty and then format it as a JSON array string
        if export_items:
            export_selections = "[" + ",".join([f"\"{item}\"" for item in export_items]) + "]"
        else:
            export_selections = "[]"

        # The dispatch_selections variable will now contain a properly formatted JSON array string

        # Define dispatch sections that should be included, structured with their corresponding data
        export_sections = [
                        {
                            "fieldName": "6.6 (a) Export under OGL/Export Quota- (i) White/ refined Sugar",
                            "subFields": [
                                {
                                    "fieldName": "Release Order (if applicable) - No.",
                                    "inputValue": f"{getattr(self,'ns_66a_exportrefinedfield3')}",
                                },
                                {
                                    "fieldName": "Release Order (if applicable) - Date",
                                    "inputValue": f"{datetime.strptime(getattr(self, 'ns_66a_exportrefinedfield4'), '%Y-%m-%d').strftime('%d/%m/%Y') if self.ns_66a_exportrefinedfield4 else None}",
                                },
                                {
                                    "fieldName": "Release Order (if applicable) - Qty released (MT)",
                                    "inputValue": f"{format_precision(getattr(self,'ns_66a_exportrefinedfield5'))}",
                                },
                                {
                                    "fieldName": "Qty Dispatched - During the Month (MT)",
                                    "inputValue": f"{format_precision(getattr(self,'ns_66a_exportrefinedfield6'))}",
                                },
                            ],
                        },
                        {
                            "fieldName": "6.6 (a) Export under OGL- (ii) Raw Sugar (including SEZ refinery)",
                            "subFields": [
                                {
                                    "fieldName": "Release Order (if applicable) - No.",
                                    "inputValue": f"{getattr(self,'ns_66a_exportrawfield1')}",
                                },
                                {
                                    "fieldName": "Release Order (if applicable) - Date",
                                    "inputValue": f"{datetime.strptime(getattr(self, 'ns_66a_exportrawfield2'), '%Y-%m-%d').strftime('%d/%m/%Y') if self.ns_66a_exportrawfield2 else None}",
                                },
                                {
                                    "fieldName": "Release Order (if applicable) - Qty released (MT)",
                                    "inputValue": f"{format_precision(getattr(self,'ns_66a_exportrawfield3'))}",
                                },
                                {
                                    "fieldName": "Qty Dispatched - During the Month (MT)",
                                    "inputValue": f"{format_precision(getattr(self,'ns_66a_exportrawfield4'))}",
                                },
                            ],
                        },
                        {
                            "fieldName": "6.6 (a) Export under OGL- (iii) Raw Sugar Sold to Refineries for Export by Invoice",
                            "subFields": [
                                {
                                    "fieldName": "Release Order (if applicable) - No.",
                                    "inputValue": f"{getattr(self,'ns_66a_exportinvoicefield1')}",
                                },
                                {
                                    "fieldName": "Release Order (if applicable) - Date",
                                    "inputValue": f"{datetime.strptime(getattr(self, 'ns_66a_exportinvoicefield2'), '%Y-%m-%d').strftime('%d/%m/%Y') if self.ns_66a_exportinvoicefield2 else None}",
                                },
                                {
                                    "fieldName": "Qty Dispatched - During the Month (MT)",
                                    "inputValue": f"{format_precision(getattr(self,'ns_66a_exportinvoicefield3'))}",
                                },
                                {
                                    "fieldName": "Name of mill/refinery to whom sold",
                                    "inputValue": f"{getattr(self,'ns_66a_exportinvoicefield5')}",
                                },
                            ],
                        },
                        {
                            "fieldName": "6.6 (b) Export under AAS (White Sugar)",
                            "subFields": [
                                {
                                    "fieldName": "Export Order (if applicable) - No.",
                                    "inputValue": f"{getattr(self,'ns_66b_exportaasfield1')}",
                                },
                                {
                                    "fieldName": "Export Order (if applicable) - Date",
                                    "inputValue": f"{datetime.strptime(getattr(self, 'ns_66b_exportaasfield2'), '%Y-%m-%d').strftime('%d/%m/%Y') if self.ns_66b_exportaasfield2 else None}",
                                },
                                {
                                    "fieldName": "Export Order (if applicable) - Qty released",
                                    "inputValue": f"{format_precision(getattr(self,'ns_66b_exportaasfield3'))}",
                                },
                                {
                                    "fieldName": "Qty Received - During the Month (MT)",
                                    "inputValue": f"{format_precision(getattr(self,'ns_66b_exportaasfield4'))}",
                                },
                            ],
                        },
                    ]
        export_response=[
                {
                    "fieldName": "Select",
                    "inputValue": export_selections
                },
                
            
            ]
        
        for section in export_sections:
            if section["fieldName"] in export_selections:  # Check if the dispatch section is selected
                export_response.append(section)

        sections.append({
            "sectionName": "Export",
            "fieldResponses": export_response
        })
        sections.append({
        "sectionName": "Import",
        "fieldResponses": [
            {
                "fieldName": "Is there any import applicable?",
                "inputValue": f"{getattr(self, 'is_there_any_import_applicable')}",
            },
            {
                "fieldName": "6.7 (a) Import under OGL – (i) White/refined Sugar - Qty Received - During the Month (MT)",
                "inputValue": f"{format_precision(getattr(self, 'ns_67a_importfield1'))}",
            },
            {
                "fieldName": "6.7 (a) Import under OGL – (ii) Raw Sugar - Qty Received - During the Month (MT)",
                "inputValue": f"{format_precision(getattr(self, 'ns_67a_importfield2'))}",
            },
            {
                "fieldName": "6.7 (b) Import under AAS - Qty Received - During the Month (MT)",
                "inputValue": f"{format_precision(getattr(self, 'ns_67b_importfield'))}",
            },
        ],
    },)
        sections.append(
            {
        "sectionName": "Stock of Sugar (In MT)",
        "fieldResponses": [
            {
                "fieldName": "Factory Premises - White Sugar",
                "subFields": [
                    {
                        "fieldName": "Opening Stock",
                        "inputValue": f"{format_precision(self.white_sugar_opening_stock)}",
                    }
                ],
            },
            {
                "fieldName": "Factory Premises - BISS / Brown Sugar, If any",
                "subFields": [
                    {
                        "fieldName": "Opening Stock",
                        "inputValue": f"{format_precision(self.biss_brown_sugar_opening_stock)}",
                    },
                    {
                        "fieldName": "Closing Stock",
                        "inputValue": f"{format_precision(self.biss_brown_sugar_closing_stock)}",
                    },
                ],
            },
            {
                "fieldName": "Factory Premises - Raw Sugar",
                "subFields": [
                    {
                        "fieldName": "Opening Stock",
                        "inputValue": f"{format_precision(self.raw_sugar_opening_stock)}",
                    }
                ],
            },
            {
                "fieldName": "Outside Godown (Duty paid) - White Sugar",
                "subFields": [
                    {
                        "fieldName": "Opening Stock",
                        "inputValue": f"{format_precision(self.outside_white_sugar_opening_stock)}",
                    },
                    {
                        "fieldName": "Closing Stock",
                        "inputValue": f"{format_precision(self.outside_white_sugar_closing_stock)}",
                    },
                ],
            },
            {
                "fieldName": "Outside Godown (Duty paid) - BISS / Brown Sugar, If any",
                "subFields": [
                    {
                        "fieldName": "Opening Stock",
                        "inputValue": f"{format_precision(self.outside_biss_brown_sugar_opening_stock)}",
                    },
                    {
                        "fieldName": "Closing Stock",
                        "inputValue": f"{format_precision(self.outside_biss_brown_sugar_closing_stock)}",
                    },
                ],
            },
            {
                "fieldName": "Outside Godown (Duty paid) - Raw Sugar",
                "subFields": [
                    {
                        "fieldName": "Opening Stock",
                        "inputValue": f"{format_precision(self.outside_raw_sugar_opening_stock)}",
                    },
                    {
                        "fieldName": "Closing Stock",
                        "inputValue": f"{format_precision(self.outside_raw_sugar_closing_stock)}",
                    },
                ],
            },
        ],
    },
        )
        sections.append(
            
        {
            "sectionName": "Packing details of Sugar (In MT)",
            "fieldResponses": [
                {
                    "fieldName": "50 Kg Jute Bag - Qty in MT",
                    "inputValue": f"{format_precision(self.pdosim_field1)}",
                },
                {
                    "fieldName": "100 Kg Jute Bag - Qty in MT",
                    "inputValue": f"{format_precision(self.pdosim_field6)}",
                },
                {
                    "fieldName": "50 Kg PP/HDPE Bag - Qty in MT",
                    "inputValue": f"{format_precision(self.pdosim_field2)}",
                },
                {
                    "fieldName": "Other Retail Bags (<= 25 Kg and > 100 Kg)/ Loose Sugar - Qty in MT",
                    "inputValue": f"{format_precision(self.pdosim_field7)}",
                },
            ],
        },
            ) 
            
        sections.append({
            "sectionName": "Cane Dues Data",
            "fieldResponses": fieldResponses
        })
        person_data = [
            {
            "approvalId": f"{self.approval_id}",
            "swsId": f"{self.sws_id}",
            "projectNumber": f"{self.project_number}",
            "forms": [
                {
                    "name": "P2 Form (Directorate of Sugar)",
                    "sections": sections
                }
            ],
        }
                       ]
        
        self.nsws_p2_form_json = ""
        json_data = json.dumps(person_data, indent=4)
        self.nsws_p2_form_json = json_data

    def get_cane_crushed(self):
        self.cane_crushed_cumulative_figures_upto_the_month_end_mt, if_last_season = (
            get_opening_value(self.sugar_season, self.season_month)
        )
        if if_last_season:
            self.cane_crushed_cumulative_figures_upto_the_month_end_mt = (
                self.cane_crushed__during_the_month_mt
            )
        else:
            self.cane_crushed_cumulative_figures_upto_the_month_end_mt += (
                self.cane_crushed__during_the_month_mt
            )

    @frappe.whitelist()
    def get_field_cumulative_value(self, season_month, set_field, cumulative_value, season=None, date=None):

        season_start_date = frappe.get_value("NSWS Season", season, "year_start_date")
        month_name = season_start_date.strftime("%B")
        season_end_date_obj = datetime.strptime(date, "%Y-%m-%d")
        start_year = season_start_date.year
        end_year = season_end_date_obj.year
        start_date = datetime.strptime(f"{month_name} {start_year}", "%B %Y")
        end_date = datetime.strptime(f"{season_month} {end_year}", "%B %Y")

        month_list = get_all_previous_months(season_month)
        self.set(set_field, 0)
        # temp = frappe.get_all("NSWS P2 Form",{"season_month":["in",month_list],"name":["!=",self.name],'docstatus': 1},f"sum({field_list[i]}) as sum")
        temp = frappe.get_all(
            "NSWS P2 Form",
            {
                "sugar_season": self.sugar_season,
                "season_month": ["in", month_list],
                "name": ["!=", self.name],
                "docstatus": 1,
            },
            f"sum({cumulative_value}) as sum",
        )
        self.set(
            set_field,
            float(temp[0]["sum"] or 0),
        )
    
    def on_validate(self):
        self.validation()
        
        
    @frappe.whitelist()
    def get_recovery_age(self, set_field, cumulative_value):
        # for the first submission, set the field to 0
        self.set(set_field, 0)

        # Fetch sum of cumulative_value from all relevant records
        sum_value = frappe.get_all(
            "NSWS P2 Form",
            filters={
                "sugar_season": self.sugar_season,
                "name": ["!=", self.name],
                "docstatus": 1,
                "cane_crushed__during_the_month_mt":[">",0]
            },
            fields=["sum(" + cumulative_value + ") as sum"],
        )

        # Ensure sum_value is a valid float
        sum_value = float(sum_value[0]["sum"] or 0)

        # Now, if cumulative_value is a field name (like 'ns_4_i1'), fetch its value for the current record
        field_value = getattr(self, cumulative_value, 0)  # Get the field value from the current record

        # Add the field value to sum
        sum_value += float(field_value)

        # Get the count of records
        count_value = frappe.get_all(
            "NSWS P2 Form",
            filters={
                "sugar_season": self.sugar_season,
                "name": ["!=", self.name],
                "docstatus": 1,
                "cane_crushed__during_the_month_mt":[">",0]

            },
            fields=["count(" + cumulative_value + ") as count"],
        )

        # Get count value
        count_value = int(count_value[0]["count"] or 0)
        if self.cane_crushed__during_the_month_mt >0:
            count_value += 1  # Add 1 to count to include the current record

        # Calculate the value
        if count_value > 0:
            value = sum_value / count_value
        else:
            value = 0
        # frappe.msgprint(f"sum {sum_value} and count {count_value}")
        # Set the calculated value to the given field
        self.set(set_field, float(value))

        
    
    def before_save(self):
        
        # formatted_string = '"' + '","'.join([item.p2_form_dispatches_select for item in self.get("dispatch_multiselect")]) + '"'
        # frappe.throw(str(formatted_string))
        date_string = self.date
        date_object = datetime.strptime(date_string, "%Y-%m-%d")
        self.year = date_object.year

        self.get_cane_crushed()

        self.ns_2i_a2 = self.ns_2i_b2 = self.ns_2i_c2 = self.ns_2i_c1_2 = (
            self.ns_2i_c2_2
        ) = self.ns_2i_c3_2 = 0  # white/refined sugar
        self.ns_2ii_a2 = self.ns_2ii_b2 = self.ns_2ii_c2 = 0  # Raw sugar
        self.ns_2iii_a2 = self.ns_2iii_b2 = self.ns_2iii_c2 = 0  # procured sugar
        self.ns_31_i2 = self.ns_31_ii2 = self.ns_31_iii2 = self.ns_31_iv2 = (
            self.ns_31_v2
        ) = self.ns_31_vi2 = 0  # diversion juice sugar
        self.ns_32_i2 = self.ns_32_ii2 = self.ns_32_iii2 = 0  # ethanol production

        self.get_cumulative_value(self.season_month, self.sugar_season, self.date)
        
        # production
        self.ns_2i_c4_1 = (
            self.ns_2i_a1
            + self.ns_2i_b1
            + self.ns_2i_c1
            + self.ns_2i_c1_1
            # + self.ns_2i_c2_1
            + self.ns_2i_c3_1
        )  # left section
        # white/refined sugar
        self.ns_2i_c4_2 = (
            self.ns_2i_a2
            + self.ns_2i_b2
            + self.ns_2i_c2
            + self.ns_2i_c1_2
            + self.ns_2i_c2_2
            + self.ns_2i_c3_2
        )  # Right section # white/refined sugar
        self.ns_2iii_c1 = (
            self.ns_2iii_a1 + self.ns_2iii_b1
        )  # left section  procured sugar
        self.ns_2iii_c2 = (
            self.ns_2iii_a2 + self.ns_2iii_b2
        )  # right section procure sugar
        self.total_sugar_produced__during_the_month_mt = (
            self.ns_2i_c4_1 + self.ns_2ii_a1 + self.ns_2ii_b1 + self.ns_2ii_c1
        )  # left section - 2id + 2iic
        self.total_sugar_produced_cumulative_figures_upto_the_month_end_mt = (
            self.ns_2i_c4_2 + self.ns_2ii_a2 + self.ns_2ii_b2 + self.ns_2ii_c2
        )  # right section - 2id + 2iic
        self.get_recovery_age("ns_4_i2","ns_4_i1")
        self.get_recovery_age("ns_4_ii2","ns_4_ii1")
        if self.ns_4_ii1 > 0 and self.ns_4_i1 > 0:
            self.ns_4_iii1 = ((self.ns_4_ii1 or 0) * ((self.ns_4_i1 or 0) - 35.60) * 1.002) / (0.644 * (self.ns_4_i1 or 0))
        self.get_recovery_age("ns_4_iii2","ns_4_iii1")
        # hsn code
        self.hsn_code_t4 = self.hsn_code_t1 + self.hsn_code_t2 + self.hsn_code_t3
        self.get_field_cumulative_value(self.season_month, "ns_63_internalfield2","ns_63_internalfield3",self.sugar_season, self.date)
        self.get_field_cumulative_value(self.season_month,"ns_64_internalfield2","ns_64_internalfield3" ,self.sugar_season, self.date)
        self.get_field_cumulative_value(self.season_month,"ns_65_salefield2","ns_65_salefield3", self.sugar_season, self.date)
        self.domestic_mt = (
            (self.ns_611_field3 or 0)
            + (self.ns_612_field4 or 0)
            + (self.ns_613_field4 or 0)
            + (self.ns_614_field4 or 0)
            + (self.ns_62_bissfield2)
            + (self.ns_63_internalfield3)
            + (self.ns_64_internalfield3)
            + (self.ns_65_salefield3)
        )
        self.export_mt = (
            (self.ns_66a_exportrefinedfield6)
            + (self.ns_66a_exportrawfield4)
            + (self.ns_66a_exportinvoicefield3)
            + (self.ns_66b_exportaasfield4)
        )

        self.get_stock_of_sugar()
        self.get_packing_details_of_sugar()
        # self.get_cane_dues_data()
        # self.cane_dues_data_caclculation()
        self.get_json_data()

    @frappe.whitelist()
    def cane_dues_data_caclculation(self):
        month = get_previous_month_name(self.season_month)
        data = self.get("cane_dues_5_year_data")
        for d in data:
            d.cane_dues_paid = getval(d.cane_price_paid) + getval(
                frappe.get_value(
                    "NSWS P2 Form",
                    {
                        "sugar_season": d.child_season,
                        "docstatus": 1,
                        "season_month": month,
                    },
                    "ss_24_25_field4",
                )
            )
            d.cane_price_arrears = getval(d.cane_price_payable) - getval(
                d.cane_dues_paid
            )
            
            
    @frappe.whitelist()
    def validation(self):
        if self.ns_2i_a1:
            if self.ns_2i_a1+self.ns_2ii_a1<=(14/100*self.cane_crushed__during_the_month_mt):
                frappe.throw("In From Cane - During the Month (MT) of 2(I) White / Refined Sugar, Sum of 'From cane' in 2(I)a) and 2(II)a) should be less than or equal to 14% of [Cane Crushed - During the Month (MT)]")
        if self.ns_2ii_a1:
            if self.ns_2i_a1+self.ns_2ii_a1<=(14/100*self.cane_crushed__during_the_month_mt):
                frappe.throw("In From Cane - During the Month (MT) of 2(II) Raw Sugar, Sum of 'From cane' in 2(I)a) and 2(II)a) should be less than or equal to 14% of [Cane Crushed - During the Month (MT)]")
        if self.ns_2ii_c1>=(95/100)*(self.ns_2ii_a1 + self.ns_2ii_b1):
            frappe.throw("In Raw sugar procured from other domestic sugar mills - During the Month (MT), This value should be greater than or equal to 95% of during the month value of  [2(II).a + 2(II).b]")
        if self.pdosim_field5 ==(self.white_sugar_closing_stock + self.biss_brown_sugar_closing_stock +
self.raw_sugar_closing_stock + self.outside_white_sugar_closing_stock + 
self.outside_biss_brown_sugar_closing_stock +
self.outside_raw_sugar_closing_stock) :
            frappe.throw("In total quantity of Packing details of sugar (In MT),This value should be equal to sum of 'Factory Premises - White Sugar Closing Stock' + 'Factory Premises - BISS / Brown Sugar, If any Closing Stock'+ 'Factory Premises - Raw Sugar Closing Stock' + 'Outside Godown (Duty paid) - White Sugar Closing Stock' + 'Outside Godown (Duty paid) - BISS / Brown Sugar, If any Closing Stock' + 'Outside Godown (Duty paid) - Raw Sugar Closing Stock'")
            
        # Sum of 'From cane' in 2(I)a) and 2(II)a) should be less than or equal to 14% of [Cane Crushed - During the Month (MT)]
        

import json
import requests
import frappe

@frappe.whitelist()
def call_api(api_url, access_id, access_secret, api_key, payload, id):
    # Ensure payload is a valid JSON string
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)  
        except json.JSONDecodeError:
            frappe.throw("Invalid JSON format in payload")

    # Convert dict back to JSON string for API call
    payload = json.dumps(payload)

    headers = {
        'access-id': access_id,
        'access-secret': access_secret,
        'api-key': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(api_url, headers=headers, data=payload)

        try:
            response_data = response.json()  # Parse JSON response
        except json.JSONDecodeError:
            frappe.throw(f"Invalid response received: {response.text}")

        unique_id = response_data.get("uniqueId")

        # Save API response
        frappe.db.set_value("NSWS P2 Form", id, 'api_response', json.dumps(response_data, indent=2))

        if response.status_code == 200:
            response_data = response.json()
            status = response_data.get("status")
            message = response_data.get("message")
            unique_id = response_data.get("uniqueId")

            if int(status) == 200 and message == "Success" and unique_id:
                frappe.db.set_value("NSWS P2 Form", id, 'unique_id', str(unique_id))
                frappe.db.set_value("NSWS P2 Form", id, 'api_response', json.dumps(response_data, indent=2))

                frappe.msgprint(
                    msg=f"""
                    <div style="color: green; font-weight: bold; font-size: 14px;">
                        ✅ <b>Data Submitted Successfully!</b>
                    </div>
                    <br>
                    <b>Unique ID:</b> {unique_id}
                    <br>
                    <b>Response:</b> <pre>{json.dumps(response_data, indent=2)}</pre>
                    """,
                    title="Success",
                    indicator="green"
                )

                return unique_id
            else:
                # If message or status is not expected
                frappe.msgprint(
                    msg=f"""
                    <div style="color: red; font-weight: bold; font-size: 14px;">
                        ❌ <b>API Response Missing Expected Fields!</b>
                    </div>
                    <br>
                    <b>Status Code:</b> {response.status_code}
                    <br>
                    <b>Response:</b> <pre>{json.dumps(response_data, indent=2)}</pre>
                    """,
                    title="Failed",
                    indicator="red"
                )
                return None
        else:
            frappe.msgprint(
                msg=f"""
                <div style="color: red; font-weight: bold; font-size: 14px;">
                    ❌ <b>API Request Failed!</b>
                </div>
                <br>
                <b>Status Code:</b> {response.status_code}
                <br>
                <b>Response:</b> <pre>{response.text}</pre>
                """,
                title="Failed",
                indicator="red"
            )
            return None

    except requests.RequestException as e:
        frappe.throw(f"API Request failed: {str(e)}")
