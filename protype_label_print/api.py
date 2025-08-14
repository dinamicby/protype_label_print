import frappe, io, base64
from frappe.utils.pdf import get_pdf
from frappe.utils import now_datetime
from markupsafe import escape

try:
    import qrcode
except Exception:
    qrcode = None

@frappe.whitelist()
def generate_labels_pdf(item_codes, options=None):
    import json
    if isinstance(item_codes, str):
        item_codes = json.loads(item_codes)
    if isinstance(options, str):
        options = json.loads(options)

    if not item_codes:
        frappe.throw("Нет выбранных товаров")

    items = frappe.get_all("Item",
        filters={"name": ["in", item_codes]},
        fields=["name as item_code", "item_name", "storage_position"])

    labels = []
    per_item_qty = int(options.get("per_item_qty") or 1)

    for it in items:
        repeat = per_item_qty
        if repeat <= 0:
            continue
        labels.extend([{
            "item_code": it.item_code,
            "item_name": it.item_name,
            "position": it.storage_position or "",
            "qr_url": build_item_url(options, it.item_code) if options.get("show_qr") else None
        }] * repeat)

    if not labels:
        frappe.throw("Нет ярлыков для печати")

    # enrich with qr images
    for l in labels:
        if l.get("qr_url"):
            l["qr_png"] = make_qr_base64(l["qr_url"], box_size=8, border=1)

    html_template = load_template_by_name(options.get("template_name") or "default")
    css = load_default_css()
    grid_css = build_grid_css(options)

    cards_html = [render_label(html_template, lbl, options) for lbl in labels]
    body = f"""
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        {css}
        {grid_css}
      </style>
    </head>
    <body>
      <div class="sheet a4">
        <div class="labels-grid">
          {''.join(cards_html)}
        </div>
      </div>
    </body>
    </html>
    """
    pdf = get_pdf(body)
    file_name = f"labels_{now_datetime().strftime('%Y%m%d_%H%M%S')}.pdf"
    filedoc = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "content": pdf,
        "is_private": 1
    }).insert(ignore_permissions=True)
    return {"file_url": filedoc.file_url}

def build_item_url(options, item_code):
    base = (options.get("qr_url_base") or "").rstrip("/")
    if not base:
        return None
    return f"{base}/{escape(item_code)}"

def load_template_by_name(name):
    if name == "half_a4_2col_30mm":
        path = frappe.get_app_path("protype_label_print", "label_templates", "half_a4_2col_30mm.html")
    else:
        path = frappe.get_app_path("protype_label_print", "label_templates", "default_label.html")
    return frappe.read_file(path)

def load_default_css():
    path = frappe.get_app_path("protype_label_print", "label_templates", "default_label.css")
    return frappe.read_file(path)

def build_grid_css(options):
    cols = int(options.get("columns") or 2)
    rows = int(options.get("rows") or 0)
    w = int(options.get("label_width_mm") or 97)
    h = int(options.get("label_height_mm") or 30)
    hg = int(options.get("h_gap_mm") or 4)
    vg = int(options.get("v_gap_mm") or 2)
    m = int(options.get("page_margins_mm") or 6)

    rows_css = f"grid-auto-rows: {h}mm;" if rows == 0 else f"grid-template-rows: repeat({rows}, {h}mm);"

    return f"""
    @page {{
      size: A4;
      margin: {m}mm;
    }}
    .sheet.a4 {{
      width: 210mm;
      min-height: 297mm;
    }}
    .labels-grid {{
      display: grid;
      grid-template-columns: repeat({cols}, {w}mm);
      {rows_css}
      gap: {vg}mm {hg}mm;
    }}
    .label-card {{
      box-sizing: border-box;
      width: {w}mm;
      height: {h}mm;
      overflow: hidden;
      padding: 2mm 3mm;
      border: 0.2mm solid #bbb; /* отключите если не нужен контур */
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: flex-start;
    }}
    """

def render_label(tpl, lbl, options):
    html = tpl
    def esc(v): return escape(str(v)) if v is not None else ""
    mapping = {
        "{{ item_code }}": esc(lbl.get("item_code")),
        "{{ item_name }}": esc(lbl.get("item_name")),
        "{{ position }}": esc(lbl.get("position")),
        "{{ qr_png }}": esc(lbl.get("qr_png") or ""),
        "{{ qr_url }}": esc(lbl.get("qr_url") or ""),
    }
    for k, v in mapping.items():
        html = html.replace(k, v)

    # Прятать поля
    if not options.get("show_item_code"): html = hide_block(html, "item_code")
    if not options.get("show_item_name"): html = hide_block(html, "item_name")
    if not options.get("show_position"):  html = hide_block(html, "position")
    if not options.get("show_qr"):        html = hide_block(html, "qr")

    return f'<div class="label-card">{html}</div>'

def hide_block(html, block_name):
    return html.replace(f'data-field="{block_name}"', f'data-field="{block_name}" style="display:none"' )

def make_qr_base64(data, box_size=8, border=1):
    if not qrcode:
        return ""
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=box_size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    return base64.b64encode(bio.getvalue()).decode("ascii")
