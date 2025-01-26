from flask import Flask, render_template, request, send_file
import graphviz
import pandas as pd
from fpdf import FPDF

app = Flask(__name__)

def calculate_inheritance(spouse, children, parents, siblings):
    """
    Calculates inheritance distribution based on Florida intestate succession laws.
    """
    heirs = {}

    if spouse == "yes":
        if children == 0:
            heirs["Spouse"] = 100  # Spouse gets everything if no children
        elif children > 0:
            heirs["Spouse"] = 50
            share_per_child = 50 / children
            for i in range(children):
                heirs[f"Child {i+1}"] = round(share_per_child, 2)
    elif children > 0:
        share_per_child = 100 / children
        for i in range(children):
            heirs[f"Child {i+1}"] = round(share_per_child, 2)
    elif parents == "yes":
        heirs["Parents"] = 100  # Parents inherit if no spouse or children
    elif siblings > 0:
        share_per_sibling = 100 / siblings
        for i in range(siblings):
            heirs[f"Sibling {i+1}"] = round(share_per_sibling, 2)
    else:
        heirs["State of Florida"] = 100  # If no heirs, state takes the property

    return heirs

def generate_flowchart(heirs):
    """
    Generates a flowchart image of the inheritance breakdown.
    """
    graph = graphviz.Digraph(format="png")
    graph.node("Deceased")

    for heir, share in heirs.items():
        graph.node(heir, f"{heir}\n{share}%")
        graph.edge("Deceased", heir)

    graph_path = "static/heir_tree"
    graph.render(graph_path, format="png", cleanup=True)

    return f"{graph_path}.png"

def generate_pdf(heirs):
    """
    Generates a PDF report of the inheritance breakdown.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, "Intestate Succession Report", ln=True, align="C")

    pdf.ln(10)  # Line break
    pdf.set_font("Arial", size=12)

    for heir, share in heirs.items():
        pdf.cell(200, 10, f"{heir}: {share}%", ln=True, align="L")

    pdf_path = "static/inheritance_report.pdf"
    pdf.output(pdf_path)
    return pdf_path

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        spouse = request.form.get("spouse", "no")
        children = request.form.get("children", "0")
        parents = request.form.get("parents", "no")
        siblings = request.form.get("siblings", "0")

        # Convert numeric fields safely
        children = int(children) if children.isdigit() else 0
        siblings = int(siblings) if siblings.isdigit() else 0

        heirs = calculate_inheritance(spouse, children, parents, siblings)
        flowchart_path = generate_flowchart(heirs) if heirs else None
        pdf_path = generate_pdf(heirs) if heirs else None

        return render_template("index.html", heirs=heirs, flowchart_path=flowchart_path, pdf_path=pdf_path)

    return render_template("index.html", heirs=None, flowchart_path=None, pdf_path=None)

@app.route("/download_pdf")
def download_pdf():
    """
    Serves the generated PDF file for download.
    """
    return send_file("static/inheritance_report.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
