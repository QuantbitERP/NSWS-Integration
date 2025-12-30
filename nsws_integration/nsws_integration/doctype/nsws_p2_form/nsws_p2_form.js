
frappe.ui.form.on("NSWS P2 Form", {
    refresh: function(frm) {
        // Check if the clipboard icon is already added to avoid duplicates
        if (!frm.fields_dict['nsws_p2_form_json'].$wrapper.find('.fa-clipboard').length) {
            // Add a custom button (clipboard icon) next to the FormField's label
            frm.fields_dict['nsws_p2_form_json'].$wrapper
                .find('.control-label') // Find the label for the field
                .append('<span class="fa fa-clipboard" title="Copy to Clipboard" style="cursor: pointer; margin-left: 10px;"></span>') // Add the clipboard icon
                .on('click', function() {
                    // Get the field value
                    const fieldValue = frm.doc.nsws_p2_form_json; // Retrieve the JSON field value
        
                    // Log the field value to check if it's defined
                    console.log("Field value:", fieldValue);
        
                    // Ensure the field value exists and is not empty
                    if (!fieldValue) {
                        frappe.show_alert({message: __('No data to copy!'), indicator: 'red'});
                        return;
                    }
        
                    // Use Clipboard API if supported
                    if (navigator.clipboard) {
                        navigator.clipboard.writeText(fieldValue).then(function() {
                            frappe.show_alert({message: __('Copied to clipboard!'), indicator: 'green'});
                        }).catch(function(error) {
                            console.error('Failed to copy:', error);
                            frappe.show_alert({message: __('Failed to copy!'), indicator: 'red'});
                        });
                    } else {
                        // Fallback to document.execCommand for older browsers (non-Clipboard API support)
                        const textarea = document.createElement('textarea');
                        textarea.value = fieldValue;
                        document.body.appendChild(textarea);
                        textarea.select();
                        try {
                            document.execCommand('copy');
                            frappe.show_alert({message: __('Copied to clipboard! (Fallback)'), indicator: 'green'});
                        } catch (error) {
                            console.error('Failed to copy (fallback):', error);
                            frappe.show_alert({message: __('Failed to copy!'), indicator: 'red'});
                        }
                        document.body.removeChild(textarea);
                    }
                });
        }
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Download JSON'), function() {
                var json_data = JSON.parse(frm.doc.nsws_p2_form_json);
                var filename = "NSWSP2 "+frm.doc.season_month+" "+frm.doc.sugar_season+".json";
                var text = JSON.stringify(json_data, null, 4);
                download(filename, text);
            }, 'fa fa-download'); // This adds the download symbol
        }
            if (frm.doc.docstatus == 1&& frm.doc.unique_id ==null) {
                frm.add_custom_button('Call API', () => {
                    // Create the API Request Dialog
                    const dialog = new frappe.ui.Dialog({
                        title: 'Submit Data to API',
                        fields: [
                            {
                                label: 'API URL',
                                fieldname: 'api_url',
                                fieldtype: 'Data',
                                reqd: true,
                                default: "https://api.nsws.gov.in/nsws_license/saveP2Data"
                            },
                            {
                                label: 'Access ID',
                                fieldname: 'access_id',
                                fieldtype: 'Data',
                                reqd: true,
                                default: "SaveP2Data"
                            },
                            {
                                label: 'Access Secret',
                                fieldname: 'access_secret',
                                fieldtype: 'Data',
                                reqd: true,
                                default: "SaveP2Data#0605_NSWS@1252"
                            },
                            {
                                label: 'API Key',
                                fieldname: 'api_key',
                                fieldtype: 'Data',
                                reqd: true,
                                default: "SaveP2Data#0605@AK1161"
                            }
                        ],
                        primary_action_label: 'Submit',
                        primary_action(values) {
                            console.log("Submitting API Request:", values);
                            console.log("Document ID:", frm.doc.name);
                            console.log("Payload:", frm.doc.nsws_p2_form_json);
    
                            let args = dialog.get_values();
                            if (!args) return;
    
                            frappe.call({
                                method: "sugar_mill.sugar_mill.doctype.nsws_p2_form.nsws_p2_form.call_api",
                                args: {
                                    api_url: args.api_url,
                                    access_id: args.access_id,
                                    access_secret: args.access_secret,
                                    api_key: args.api_key,
                                    payload: frm.doc.nsws_p2_form_json,
                                    id: frm.doc.name
                                },
                                freeze: true,
                                freeze_message: "Submitting data, please wait...",
                                callback: function (r) {
                                    dialog.hide();
                                    frm.refresh();
    
                                    if (r.message) {
                                        frappe.show_alert({
                                            message: `✅ Data submitted successfully! Unique ID: <b>${r.message}</b>`,
                                            indicator: 'green'
                                        });
                                    } else {
                                        frappe.show_alert({
                                            message: "❌ API submission failed. Please check the logs.",
                                            indicator: 'red'
                                        });
                                    }
                                }
                            });
                        }
                    });
    
                    dialog.show();
                });
            }
        },

    setup(frm) {
        set_filters(frm, 'production_multiselect', 'None', [['NSWS Options', 'options_type', '=', "Productions"]]);
        set_filters(frm, 'dispatch_multiselect', 'None', [['NSWS Options', 'options_type', '=', "Dispatches"]]);
        set_filters(frm, 'export_multiselect', 'None', [['NSWS Options', 'options_type', '=', "Export"]]);
    frm.refresh_fields()},


    copy_json: function(frm) {
        const fieldValue = frm.doc.nsws_p2_form_json; // Retrieve the JSON field value
        
        // Log the field value to check if it's defined
        console.log("Field value:", fieldValue);
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(fieldValue).then(function() {
                frappe.show_alert({message: __('Copied to clipboard!'), indicator: 'green'});
            }).catch(function(error) {
                console.error('Failed to copy:', error);
                frappe.show_alert({message: __('Failed to copy!'), indicator: 'red'});
            });
        } else {
            // Fallback to document.execCommand for older browsers (non-Clipboard API support)
            const textarea = document.createElement('textarea');
            textarea.value = fieldValue;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            frappe.show_alert({message: __('Copied to clipboard!'), indicator: 'green'});
        }
        
    },
    
    
    

    


    // Hide/Show the Production Section
    production_multiselect(frm) {

        if (frm.doc.production_multiselect) {
            let selectedValues = frm.doc.production_multiselect || [];
            make_hidden_true(frm, 'ns_2i_white__refined_sugar_section');
            make_hidden_true(frm, 'ns_2ii_raw_sugar_section');
            make_hidden_true(frm, 'ns_2iii_procured_sugar_section');
            make_hidden_true(frm, 'ns_31_title');
            make_hidden_true(frm, 'ns_32_ethanol_production_section');
            // make_hidden_true(frm, 'ns_4_recovery__age_section');

            


            // if (selectedValues.length > 0) {
            //     frm.toggle_display('ns_4_recovery__age_section', true);
            // }   
            selectedValues.forEach(value => {

                if (value.p2_form_production_select == "2(I) White / Refined Sugar") {
                    frm.set_df_property('ns_2i_a1', 'reqd', 1);
                    frm.set_df_property('ns_2i_b1', 'reqd', 1);
                    frm.set_df_property('ns_2i_c1', 'reqd', 1);
                    frm.set_df_property('ns_2i_c1_1', 'reqd', 1);
                    frm.set_df_property('ns_2i_c2_1', 'reqd', 1);
                    frm.set_df_property('ns_2i_c3_1', 'reqd', 1);
                    frm.set_df_property('ns_2i_c4_1', 'reqd', 1);
                    frm.set_df_property('ns_2i_a2', 'reqd', 1);
                    frm.set_df_property('ns_2i_b2', 'reqd', 1);
                    frm.set_df_property('ns_2i_c2', 'reqd', 1);
                    frm.set_df_property('ns_2i_c1_2', 'reqd', 1);
                    frm.set_df_property('ns_2i_c2_2', 'reqd', 1);
                    frm.set_df_property('ns_2i_c3_2', 'reqd', 1);
                    frm.set_df_property('ns_2i_c4_2', 'reqd', 1);
                    // frm.set_df_property('ns_2i_c4_2', 'reqd', 1);

                    frm.set_df_property('ns_4_i1', 'reqd', 1);
                    frm.set_df_property('ns_4_ii1', 'reqd', 1);
                    frm.set_df_property('ns_4_iii1', 'reqd', 1);
                    frm.set_df_property('ns_4_i2', 'reqd', 1);
                    frm.set_df_property('ns_4_ii2', 'reqd', 1);
                    frm.set_df_property('ns_4_iii2', 'reqd', 1);

                    frm.toggle_display('ns_2i_white__refined_sugar_section', true);
                }
                else if (value.p2_form_production_select == "2(II) Raw Sugar") {
                    frm.set_df_property('ns_2ii_a1', 'reqd', 1);
                    frm.set_df_property('ns_2ii_b1', 'reqd', 1);
                    frm.set_df_property('ns_2ii_c1', 'reqd', 1);
                    frm.set_df_property('ns_2ii_a2', 'reqd', 1);
                    frm.set_df_property('ns_2ii_b2', 'reqd', 1);
                    frm.set_df_property('ns_2ii_c2', 'reqd', 1);


                    frm.set_df_property('ns_4_i1', 'reqd', 1);
                    frm.set_df_property('ns_4_ii1', 'reqd', 1);
                    frm.set_df_property('ns_4_iii1', 'reqd', 1);
                    frm.set_df_property('ns_4_i2', 'reqd', 1);
                    frm.set_df_property('ns_4_ii2', 'reqd', 1);
                    frm.set_df_property('ns_4_iii2', 'reqd', 1);


                    frm.toggle_display('ns_2ii_raw_sugar_section', true);
                }
                else if (value.p2_form_production_select == "2(III) Procured sugar") {
                    frm.set_df_property('ns_2iii_a1', 'reqd', 1);
                    frm.set_df_property('ns_2iii_b1', 'reqd', 1);
                    frm.set_df_property('ns_2iii_c1', 'reqd', 1);
                    frm.set_df_property('ns_2iii_a2', 'reqd', 1);
                    frm.set_df_property('ns_2iii_b2', 'reqd', 1);
                    frm.set_df_property('ns_2iii_c2', 'reqd', 1);

                    frm.set_df_property('ns_4_i1', 'reqd', 1);
                    frm.set_df_property('ns_4_ii1', 'reqd', 1);
                    frm.set_df_property('ns_4_iii1', 'reqd', 1);
                    frm.set_df_property('ns_4_i2', 'reqd', 1);
                    frm.set_df_property('ns_4_ii2', 'reqd', 1);
                    frm.set_df_property('ns_4_iii2', 'reqd', 1);

                    frm.toggle_display('ns_2iii_procured_sugar_section', true);
                }
                else if (value.p2_form_production_select == "3(1) Diversion/sale of B-heavy/Syrup/sugarcane juice/sugar") {
                    frm.set_df_property('ns_31_i1', 'reqd', 1);
                    frm.set_df_property('ns_31_ii1', 'reqd', 1);
                    frm.set_df_property('ns_31_iii1', 'reqd', 1);
                    frm.set_df_property('ns_31_iv1', 'reqd', 1);
                    frm.set_df_property('ns_31_v1', 'reqd', 1);
                    frm.set_df_property('ns_31_vi1', 'reqd', 1);
                    frm.set_df_property('ns_31_i2', 'reqd', 1);
                    frm.set_df_property('ns_31_ii2', 'reqd', 1);
                    frm.set_df_property('ns_31_iii2', 'reqd', 1);
                    frm.set_df_property('ns_31_iv2', 'reqd', 1);
                    frm.set_df_property('ns_31_v2', 'reqd', 1);
                    frm.set_df_property('ns_31_vi2', 'reqd', 1);


                    frm.set_df_property('ns_4_i1', 'reqd', 1);
                    frm.set_df_property('ns_4_ii1', 'reqd', 1);
                    frm.set_df_property('ns_4_iii1', 'reqd', 1);
                    frm.set_df_property('ns_4_i2', 'reqd', 1);
                    frm.set_df_property('ns_4_ii2', 'reqd', 1);
                    frm.set_df_property('ns_4_iii2', 'reqd', 1);

                    frm.toggle_display('ns_31_title', true);
                }
                else if (value.p2_form_production_select == "3(2) Ethanol Production") {
                    frm.set_df_property('ns_32_i1', 'reqd', 1);
                    frm.set_df_property('ns_32_ii1', 'reqd', 1);
                    frm.set_df_property('ns_32_iii1', 'reqd', 1);
                    frm.set_df_property('ns_32_i2', 'reqd', 1);
                    frm.set_df_property('ns_32_ii2', 'reqd', 1);
                    frm.set_df_property('ns_32_iii2', 'reqd', 1);


                    frm.set_df_property('ns_4_i1', 'reqd', 1);
                    frm.set_df_property('ns_4_ii1', 'reqd', 1);
                    frm.set_df_property('ns_4_iii1', 'reqd', 1);
                    frm.set_df_property('ns_4_i2', 'reqd', 1);
                    frm.set_df_property('ns_4_ii2', 'reqd', 1);
                    frm.set_df_property('ns_4_iii2', 'reqd', 1);

                    frm.toggle_display('ns_32_ethanol_production_section', true);
                }
            });



            // logic starts here

            let field_list = {
                "2(I) White / Refined Sugar"                                :["ns_2i_a1","ns_2i_b1","ns_2i_c1","ns_2i_c1_1","ns_2i_c2_1","ns_2i_c3_1","ns_2i_c4_1","ns_2i_a2","ns_2i_b2","ns_2i_c2","ns_2i_c1_2","ns_2i_c2_2","ns_2i_c3_2","ns_2i_c4_2"],
                "2(II) Raw Sugar"                                           :["ns_2ii_a1","ns_2ii_b1","ns_2ii_c1","ns_2ii_a2","ns_2ii_b2","ns_2ii_c2"],
                "2(III) Procured sugar"                                     :["ns_2iii_a1","ns_2iii_internal1","ns_2iii_b1","ns_2iii_c1","ns_2iii_a2","ns_2iii_internal2","ns_2iii_b2","ns_2iii_c2"],
                "3(1) Diversion/sale of B-heavy/Syrup/sugarcane juice/sugar":["ns_31_i1","ns_31_ii1","ns_31_iii1","ns_31_iv1","ns_31_v1","ns_31_vi1","ns_31_i2","ns_31_ii2","ns_31_iii2","ns_31_iv2","ns_31_v2", "ns_31_vi2"],
                "3(2) Ethanol Production"                                   :["ns_32_i1","ns_32_ii1","ns_32_iii1","ns_32_i2","ns_32_ii2","ns_32_iii2"]
            }
            let production_options = ["2(I) White / Refined Sugar","2(II) Raw Sugar","2(III) Procured sugar","3(1) Diversion/sale of B-heavy/Syrup/sugarcane juice/sugar","3(2) Ethanol Production"]
            let unselected_options = []
            
            let selectedValues2 = []
            selectedValues.forEach(s=>selectedValues2.push(s.p2_form_production_select))
            production_options.forEach(ele=>{
                if(!selectedValues2.includes(ele)){
                    unselected_options.push(ele)
                }
            })
            
            function isDateField(field) {
                // Check if the field is a date field
                const field_meta = frm.fields_dict[field];
                return field_meta && field_meta.date_format == "YYYY-MM-DD";  // Checks the date_format is YYYY-MM-DD
            }
    
            unselected_options.forEach(option => {

                field_list[option].forEach(field=>{
                    
                    if (isDateField(field)) {
                        frm.doc[field] = ""
                    } else {
                        frm.doc[field]=0
                    }
                })

                // if (field_list[option]) {
                //     field_list[option].forEach(field=>{
                        
                //         frm.doc[field]=0
                //     })
                // }
            })





        }


        

        

    frm.refresh_fields()},



    



    // Hide/Show the Dispatches Section
    dispatch_multiselect(frm) {
        if (frm.doc.dispatch_multiselect) {
            let selectedValues = frm.doc.dispatch_multiselect || [];
            
            make_hidden_true(frm, 'ns_611_title');
            make_hidden_true(frm, 'ns_612_title');
            make_hidden_true(frm, 'ns_613_title');
            make_hidden_true(frm, 'ns_614_title');
            make_hidden_true(frm, 'ns_62_bisstitle');
            make_hidden_true(frm, 'ns_63_internaltitle');
            make_hidden_true(frm, 'ns_64_internaltitle');
            make_hidden_true(frm, 'ns_65_saletitle');
            // make_hidden_true(frm, 'hsn_code_and_related_details_section');



            // if (selectedValues.length > 0) {
            //     frm.toggle_display('hsn_code_and_related_details_section', true);
            // }
            selectedValues.forEach(value => {
                if (value.p2_form_dispatches_select === "6.1.1 Domestic Dispatch w.r.t. monthly release quantity") {
                    frm.set_df_property('ns_611_field1', 'reqd', 1);
                    frm.set_df_property('ns_611_field2', 'reqd', 1);
                    frm.set_df_property('ns_611_field3', 'reqd', 1);


                    frm.set_df_property('hsn_code_t1', 'reqd', 1);
                    frm.set_df_property('hsn_code_t2', 'reqd', 1);
                    frm.set_df_property('hsn_code_t3', 'reqd', 1);
                    frm.set_df_property('hsn_code_t4', 'reqd', 1);
                    // frm.set_df_property('upload_gstr_1', 'reqd', 1);

                    frm.toggle_display('ns_611_title', true);
                }
                else if (value.p2_form_dispatches_select === "6.1.2 Domestic Dispatch w.r.t. additional allotment, if any") {

                    frm.set_df_property('ns_612_field2', 'reqd', 1);
                    frm.set_df_property('ns_612_field3', 'reqd', 1);
                    frm.set_df_property('ns_612_field4', 'reqd', 1);

                    frm.set_df_property('hsn_code_t1', 'reqd', 1);
                    frm.set_df_property('hsn_code_t2', 'reqd', 1);
                    frm.set_df_property('hsn_code_t3', 'reqd', 1);
                    frm.set_df_property('hsn_code_t4', 'reqd', 1);
                    // frm.set_df_property('upload_gstr_1', 'reqd', 1);

                    frm.toggle_display('ns_612_title', true);
                }
                else if (value.p2_form_dispatches_select === "6.1.3 Domestic Dispatch w.r.t. extended quota") {

                    frm.set_df_property('ns_613_field2', 'reqd', 1);
                    frm.set_df_property('ns_613_field3', 'reqd', 1);
                    frm.set_df_property('ns_613_field4', 'reqd', 1);

                    frm.set_df_property('hsn_code_t1', 'reqd', 1);
                    frm.set_df_property('hsn_code_t2', 'reqd', 1);
                    frm.set_df_property('hsn_code_t3', 'reqd', 1);
                    frm.set_df_property('hsn_code_t4', 'reqd', 1);
                    // frm.set_df_property('upload_gstr_1', 'reqd', 1);

                    frm.toggle_display('ns_613_title', true);
                }
                else if (value.p2_form_dispatches_select === "6.1.4 Any other domestic Dispatch") {

                    frm.set_df_property('ns_614_field2', 'reqd', 1);
                    frm.set_df_property('ns_614_field3', 'reqd', 1);
                    frm.set_df_property('ns_614_field4', 'reqd', 1);

                    frm.set_df_property('hsn_code_t1', 'reqd', 1);
                    frm.set_df_property('hsn_code_t2', 'reqd', 1);
                    frm.set_df_property('hsn_code_t3', 'reqd', 1);
                    frm.set_df_property('hsn_code_t4', 'reqd', 1);
                    // frm.set_df_property('upload_gstr_1', 'reqd', 1);

                    frm.toggle_display('ns_614_title', true);
                }
                else if (value.p2_form_dispatches_select === "6.2 BISS Dispatch of unmarketable old Sugar for further processing") {

                    frm.set_df_property('ns_62_bissfield2', 'reqd', 1);
                    frm.set_df_property('ns_62_bissfield3', 'reqd', 1);

                    frm.set_df_property('hsn_code_t1', 'reqd', 1);
                    frm.set_df_property('hsn_code_t2', 'reqd', 1);
                    frm.set_df_property('hsn_code_t3', 'reqd', 1);
                    frm.set_df_property('hsn_code_t4', 'reqd', 1);
                    // frm.set_df_property('upload_gstr_1', 'reqd', 1);

                    frm.toggle_display('ns_62_bisstitle', true);
                }
                else if (value.p2_form_dispatches_select === "6.3 Internal transfer of raw sugar within a group") {

                    frm.set_df_property('ns_63_internalfield1', 'reqd', 1);
                    frm.set_df_property('ns_63_internalfield2', 'reqd', 1);
                    frm.set_df_property('ns_63_internalfield3', 'reqd', 1);
                    frm.set_df_property('ns_63_internalfield4', 'reqd', 1);

                    frm.set_df_property('hsn_code_t1', 'reqd', 1);
                    frm.set_df_property('hsn_code_t2', 'reqd', 1);
                    frm.set_df_property('hsn_code_t3', 'reqd', 1);
                    frm.set_df_property('hsn_code_t4', 'reqd', 1);
                    // frm.set_df_property('upload_gstr_1', 'reqd', 1);

                    frm.toggle_display('ns_63_internaltitle', true);
                }
                else if (value.p2_form_dispatches_select === "6.4 Internal transfer of white sugar within a group") {

                    frm.set_df_property('ns_64_internalfield1', 'reqd', 1);
                    frm.set_df_property('ns_64_internalfield2', 'reqd', 1);
                    frm.set_df_property('ns_64_internalfield3', 'reqd', 1);
                    frm.set_df_property('ns_64_internalfield4', 'reqd', 1);

                    frm.set_df_property('hsn_code_t1', 'reqd', 1);
                    frm.set_df_property('hsn_code_t2', 'reqd', 1);
                    frm.set_df_property('hsn_code_t3', 'reqd', 1);
                    frm.set_df_property('hsn_code_t4', 'reqd', 1);
                    // frm.set_df_property('upload_gstr_1', 'reqd', 1);

                    frm.toggle_display('ns_64_internaltitle', true);
                }
                else if (value.p2_form_dispatches_select === "6.5 Sale of raw sugar to other sugar mills for domestic purpose") {

                    frm.set_df_property('ns_65_salefield2', 'reqd', 1);
                    frm.set_df_property('ns_65_salefield3', 'reqd', 1);
                    frm.set_df_property('ns_65_salefield4', 'reqd', 1);

                    frm.set_df_property('hsn_code_t1', 'reqd', 1);
                    frm.set_df_property('hsn_code_t2', 'reqd', 1);
                    frm.set_df_property('hsn_code_t3', 'reqd', 1);
                    frm.set_df_property('hsn_code_t4', 'reqd', 1);
                    // frm.set_df_property('upload_gstr_1', 'reqd', 1);

                    frm.toggle_display('ns_65_saletitle', true);
                }
            });




            
            let field_list = {
                "6.1.1 Domestic Dispatch w.r.t. monthly release quantity"           :["release_order_date","ns_611_field1","ns_611_field2","ns_611_field3","ns_611_field4"],
                "6.1.2 Domestic Dispatch w.r.t. additional allotment, if any"       :["ns_612_field1","ns_612_field2","ns_612_field3","ns_612_field4","ns_612_field5"],
                "6.1.3 Domestic Dispatch w.r.t. extended quota"                     :["ns_613_field1","ns_613_field2","ns_613_field3","ns_613_field4","ns_613_field5"],
                "6.1.4 Any other domestic Dispatch"                                 :["ns_614_field1","ns_614_field2","ns_614_field3","ns_614_field4","ns_614_field5"],
                "6.2 BISS Dispatch of unmarketable old Sugar for further processing":["ns_62_bissfield1","ns_62_bissfield2","ns_62_bissfield3"],
                "6.3 Internal transfer of raw sugar within a group"                 :["ns_63_internalfield1","ns_63_internalfield2","ns_63_internalfield3","ns_63_internalfield4"],
                "6.4 Internal transfer of white sugar within a group"               :["ns_64_internalfield1","ns_64_internalfield2","ns_64_internalfield3","ns_64_internalfield4"],
                "6.5 Sale of raw sugar to other sugar mills for domestic purpose"   :["ns_65_salefield1","ns_65_salefield2","ns_65_salefield3","ns_65_salefield4"]
            }
    
            let dispatch_options = ["6.1.1 Domestic Dispatch w.r.t. monthly release quantity", "6.1.2 Domestic Dispatch w.r.t. additional allotment, if any", "6.1.3 Domestic Dispatch w.r.t. extended quota", "6.1.4 Any other domestic Dispatch","6.2 BISS Dispatch of unmarketable old Sugar for further processing","6.3 Internal transfer of raw sugar within a group","6.4 Internal transfer of white sugar within a group","6.5 Sale of raw sugar to other sugar mills for domestic purpose"]
    
            let unselected_options = []
            
            let selectedValues1 = []
            selectedValues.forEach(s=>selectedValues1.push(s.p2_form_dispatches_select))
            dispatch_options.forEach(ele=>{
                if(!selectedValues1.includes(ele)){
                    unselected_options.push(ele)
                }
            })

            function isDateField(field) {
                // Check if the field is a date field
                const field_meta = frm.fields_dict[field];
                return field_meta && field_meta.date_format == "YYYY-MM-DD";  // Checks the date_format is YYYY-MM-DD
            }
            

            unselected_options.forEach(option => {

                field_list[option].forEach(field=>{
                    
                    if (isDateField(field)) {
                        frm.doc[field] = ""
                    } else {
                        frm.doc[field]=0
                    }
                })

                // if (field_list[option]) {
                //     field_list[option].forEach(field=>{
                        
                //         frm.doc[field]=0
                //     })
                // }
            })






        }



        

        




    frm.refresh_fields()},




    // Hide/Show the Export Section
    export_multiselect(frm) {
        if (frm.doc.export_multiselect) {
            let selectedValues = frm.doc.export_multiselect || [];
            make_hidden_true(frm, 'ns_66a_exportrefinedtitle');
            make_hidden_true(frm, 'ns_66a_exportrawtitle');
            make_hidden_true(frm, 'ns_66a_exportinvoicetitle');
            make_hidden_true(frm, 'ns_66b_exportaastitle');


            selectedValues.forEach(value => {

                if (value.p2_form_export_select === "6.6 (a) Export under OGL/Export Quota- (i) White/ refined Sugar") {
                    frm.set_df_property('ns_66a_exportrefinedfield6', 'reqd', 1);
                    frm.set_df_property('ns_66a_exportrefinedfield7', 'reqd', 1);

                    frm.toggle_display('ns_66a_exportrefinedtitle', true);
                }
                else if (value.p2_form_export_select === "6.6 (a) Export under OGL- (ii) Raw Sugar (including SEZ refinery)") {
                    frm.set_df_property('ns_66a_exportrawfield4', 'reqd', 1);
                    frm.set_df_property('ns_66a_exportrawfield5', 'reqd', 1);

                    frm.toggle_display('ns_66a_exportrawtitle', true);
                }
                else if (value.p2_form_export_select === "6.6 (a) Export under OGL- (iii) Raw Sugar Sold to Refineries for Export by Invoice") {
                    frm.set_df_property('ns_66a_exportinvoicefield3', 'reqd', 1);
                    frm.set_df_property('ns_66a_exportinvoicefield4', 'reqd', 1);

                    frm.toggle_display('ns_66a_exportinvoicetitle', true);
                }
                else if (value.p2_form_export_select === "6.6 (b) Export under AAS (White Sugar)") {
                    frm.set_df_property('ns_66b_exportaasfield4', 'reqd', 1);
                    frm.set_df_property('ns_66b_exportaasfield5', 'reqd', 1);

                    frm.toggle_display('ns_66b_exportaastitle', true);
                }
            });



            let field_list = {
                "6.6 (a) Export under OGL/Export Quota- (i) White/ refined Sugar"                   :["ns_66a_exportrefinedfield3","ns_66a_exportrefinedfield4","ns_66a_exportrefinedfield5","ns_66a_exportrefinedfield6","ns_66a_exportrefinedfield7"],
                "6.6 (a) Export under OGL- (ii) Raw Sugar (including SEZ refinery)"                 :["ns_66a_exportrawfield1","ns_66a_exportrawfield2","ns_66a_exportrawfield3","ns_66a_exportrawfield4","ns_66a_exportrawfield5"],
                "6.6 (a) Export under OGL- (iii) Raw Sugar Sold to Refineries for Export by Invoice":["ns_66a_exportinvoicefield1","ns_66a_exportinvoicefield2","ns_66a_exportinvoicefield3", "ns_66a_exportinvoicefield4", "ns_66a_exportinvoicefield5"],
                "6.6 (b) Export under AAS (White Sugar)"                                            :["ns_66b_exportaasfield1","ns_66b_exportaasfield2","ns_66b_exportaasfield3","ns_66b_exportaasfield4","ns_66b_exportaasfield5"]
                
            }
            let export_options = ["6.6 (a) Export under OGL/Export Quota- (i) White/ refined Sugar","6.6 (a) Export under OGL- (ii) Raw Sugar (including SEZ refinery)","6.6 (a) Export under OGL- (iii) Raw Sugar Sold to Refineries for Export by Invoice","6.6 (b) Export under AAS (White Sugar)"]
            let unselected_options = []

            let selectedValues3 = []
            selectedValues.forEach(s=>selectedValues3.push(s.p2_form_export_select))
            export_options.forEach(ele=>{
                if(!selectedValues3.includes(ele)){
                    unselected_options.push(ele)
                }
            })
            
    
            function isDateField(field) {
                // Check if the field is a date field
                const field_meta = frm.fields_dict[field];
                return field_meta && field_meta.date_format == "YYYY-MM-DD";  // Checks the date_format is YYYY-MM-DD
            }

            unselected_options.forEach(option => {

                field_list[option].forEach(field=>{
                    
                    if (isDateField(field)) {
                        frm.doc[field] = ""
                    } else {
                        frm.doc[field]=0
                    }
                })

                // if (field_list[option]) {
                //     field_list[option].forEach(field=>{
                        
                //         frm.doc[field]=0
                //     })
                // }
            })








        }


        

        

    frm.refresh_fields()},



    isimport_yes: (frm) => {
        if (frm.doc.isimport_yes) {
            frm.set_value('isimport_no', 0);
            frm.refresh_fields("isimport_no");
        }
    frm.refresh_fields()},

    isimport_no: (frm) => {
        if (frm.doc.isimport_no) {
            frm.set_value('isimport_yes', 0);
            frm.refresh_fields("isimport_yes");
        }
    },
    // before_save:function(frm) {
        
    //     frm.clear_table("cane_dues_5_year_data")
    //     frm.refresh_fields("cane_dues_5_year_data");
    //     frm.call({
    //         method: 'get_cane_dues_data',//function name defined in python
    //         doc: frm.doc, //current document
    //     });
        
    // }




});

// Function to hide sections
function make_hidden_true(frm, field_name) {
    frm.toggle_display(field_name, false); // Hides the specified field
}



function download(file, text) {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', file);
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}


function set_filters(frm, DocTypeFieldName, DocTypeField, filters) {
    if (DocTypeField !== 'None') {
        frm.set_query(DocTypeFieldName, DocTypeField, function (doc, cdt, cdn) {
            return {
                filters: filters
            };
        });
    } else {
        frm.set_query(DocTypeFieldName, function (doc) {
            return {
                filters: filters,
            };
        });
    }
}

frappe.ui.form.on('NSWS cane dues data', {
	cane_price_paid: function(frm) {
		frm.call({
			method: 'cane_dues_data_caclculation',//function name defined in python
			doc: frm.doc, //current document
		});
	}
});