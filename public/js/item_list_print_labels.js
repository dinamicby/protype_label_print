frappe.listview_settings['Item'] = {
  onload(listview) {
    listview.page.add_actions_menu_item(__('Print Labels'), async () => {
      const checked = listview.get_checked_items();
      if (!checked.length) {
        frappe.msgprint(__('Выберите хотя бы один товар.'));
        return;
      }
      const d = new frappe.ui.Dialog({
        title: __('Печать этикеток'),
        fields: [
          {fieldtype:'Section Break', label: __('Поля на этикетке')},
          {fieldname:'show_item_code', label: __('Артикул (Item Code)'), fieldtype:'Check', default:1},
          {fieldname:'show_item_name', label: __('Название'), fieldtype:'Check', default:1},
          {fieldname:'show_position', label: __('Позиция на складе (Item.storage_position)'), fieldtype:'Check', default:1},
          {fieldname:'show_qr', label: __('QR с ссылкой на товар'), fieldtype:'Check', default:1},
          {fieldname:'qr_url_base', label: __('Base URL (например https://erp.company.com/app/item)'), fieldtype:'Data', depends_on:'eval:doc.show_qr', default: ''},

          {fieldtype:'Section Break', label: __('Шаблон и размеры')},
          {fieldname:'template_name', label: __('Шаблон'), fieldtype:'Select',
            options: 'half_a4_2col_30mm\ndefault',
            default: 'half_a4_2col_30mm'},
          {fieldname:'columns', label: __('Колонок'), fieldtype:'Int', default:2, reqd:1},
          {fieldname:'rows', label: __('Строк (авто)'), fieldtype:'Int', default:0, description:'0 = авто'},
          {fieldname:'label_width_mm', label: __('Ширина мм'), fieldtype:'Int', default:97},
          {fieldname:'label_height_mm', label: __('Высота мм'), fieldtype:'Int', default:30},
          {fieldname:'h_gap_mm', label: __('Гор. зазор мм'), fieldtype:'Int', default:4},
          {fieldname:'v_gap_mm', label: __('Вер. зазор мм'), fieldtype:'Int', default:2},
          {fieldname:'page_margins_mm', label: __('Поля страницы мм'), fieldtype:'Int', default:6},

          {fieldtype:'Section Break', label: __('Количество этикеток')},
          {fieldname:'per_item_qty', label: __('Штук на товар'), fieldtype:'Int', default:1, reqd:1},
        ],
        primary_action_label: __('Сгенерировать PDF'),
        primary_action: async (values) => {
          const item_codes = checked.map(c => c.name);
          try {
            const r = await frappe.call({
              method: "protype_label_print.api.generate_labels_pdf",
              type: "POST",
              args: { item_codes, options: values }
            });
            if (r.message && r.message.file_url) {
              window.open(r.message.file_url, "_blank");
            } else {
              frappe.msgprint(__('Не удалось получить файл.'));
            }
          } catch (e) {
            console.error(e);
            frappe.msgprint(__('Ошибка генерации PDF.'));
          } finally {
            d.hide();
          }
        }
      });
      d.show();
    });
  }
};
