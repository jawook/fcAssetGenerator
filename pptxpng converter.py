import os
import sys
from pathlib import Path

# ---- Dependencies:
# pip install pdf2image comtypes
# Also install Poppler and add its "bin" to PATH (Windows):
# https://github.com/oschwartz10612/poppler-windows/releases/

def main():
    folder = input("Enter the folder path containing the PPTX/PDF files: ").strip().strip('"')
    if not os.path.isdir(folder):
        print("❌ Invalid folder path. Please check and try again.")
        sys.exit(1)

    try:
        dpi_str = input("DPI for PNG export (default 300): ").strip()
        dpi = int(dpi_str) if dpi_str else 300
    except ValueError:
        print("⚠️ Invalid DPI; using 300.")
        dpi = 300

    folder_path = Path(folder)

    # Collect files
    pptx_files = sorted(p for p in folder_path.iterdir() if p.suffix.lower() == ".pptx")
    pdf_files  = sorted(p for p in folder_path.iterdir() if p.suffix.lower() == ".pdf")

    if not pptx_files and not pdf_files:
        print("ℹ️ No .pptx or .pdf files found in that folder.")
        return

    # Lazy import so script works even if PowerPoint/comtypes isn't installed
    ppt = None
    from pdf2image import convert_from_path

    # --- Handle PPTX -> PNG (FIRST SLIDE ONLY)
    if pptx_files:
        try:
            import comtypes.client
            print("📑 Initializing PowerPoint…")
            ppt = comtypes.client.CreateObject("PowerPoint.Application")
            ppt.Visible = 1
        except Exception as e:
            print("❌ Could not initialize PowerPoint/comtypes. "
                  "PPTX conversion will be skipped.\n   Details:", e)
            pptx_files = []

    try:
        for pptx in pptx_files:
            base = pptx.stem
            tmp_pdf = pptx.with_name(f"{base}__export_tmp.pdf")

            try:
                print(f"➡️ Converting PPTX to PDF: {pptx.name}")
                presentation = ppt.Presentations.Open(str(pptx))
                presentation.SaveAs(str(tmp_pdf), 32)  # 32 = PDF
                presentation.Close()

                print(f"   -> Exporting FIRST slide to PNG @ {dpi} DPI…")
                images = convert_from_path(
                    str(tmp_pdf), dpi=dpi, first_page=1, last_page=1
                )
                if images:
                    out_png = pptx.with_name(f"{base}.png")
                    images[0].save(str(out_png), "PNG")
                    print(f"      ✅ Saved {out_png.name}")
            finally:
                # Clean up temp PDF
                if tmp_pdf.exists():
                    try:
                        tmp_pdf.unlink()
                    except Exception:
                        pass
    finally:
        if ppt is not None:
            ppt.Quit()

    # --- Handle PDF -> PNG (FIRST PAGE ONLY)
    for pdf in pdf_files:
        base = pdf.stem
        print(f"➡️ Converting first page of PDF: {pdf.name} @ {dpi} DPI…")
        images = convert_from_path(str(pdf), dpi=dpi, first_page=1, last_page=1)
        if images:
            out_png = pdf.with_name(f"{base}.png")
            images[0].save(str(out_png), "PNG")
            print(f"   ✅ Saved {out_png.name}")

    print("🎉 Done!")

if __name__ == "__main__":
    main()
