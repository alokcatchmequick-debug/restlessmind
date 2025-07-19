import fitz  # PyMuPDF
import os

pdf_folder = 'Traffic Rule'  # do not change the folder name unless your folder is different
output_file = 'combined_traffic_rules.txt'

pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]

with open(output_file, 'w', encoding='utf-8') as out_f:
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        doc = fitz.open(pdf_path)
        out_f.write(f'--- Start of {pdf_file} ---\n')
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            out_f.write(f'\n[Page {page_num}]\n{text}\n')
        out_f.write(f'--- End of {pdf_file} ---\n\n')

print(f"Extraction complete! All text saved to {output_file}")

