import sys,statistics as st
sys.path.insert(0,'out')
from analisis import *
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.chart import BarChart,ScatterChart,Reference,Series
from openpyxl.styles import Font,PatternFill
from docx import Document
from docx.shared import Pt,Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
L=kmeans()
NAMES={0:"Segmento A: jóvenes de tecnología",1:"Segmento B: adultos de ticket alto",2:"Segmento C: compradores frecuentes de ropa"}
def seg(j): return [r for r,l in zip(D,L) if l==j]
cop=lambda v:"$"+f"{v:,.0f}".replace(",",".")
# --- gráficos PNG
cnt={p:sum(1 for r in D if r[3]==p) for p in ("Tecnología","Ropa","Hogar")}
fig,ax=plt.subplots(figsize=(6,4)); b=ax.bar(list(cnt),list(cnt.values()),color=["#2b6cb0","#c05621","#2f855a"])
ax.bar_label(b); ax.set(title="Cantidad de compras por categoría de producto",xlabel="Categoría",ylabel="N.º de compras"); ax.set_ylim(0,6); ax.grid(axis="y",alpha=.3); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig("out/g1.png",dpi=150); plt.close()
fig,ax=plt.subplots(figsize=(6,4)); col=["#2b6cb0","#c05621","#2f855a"]
for j in range(3):
    m=seg(j); ax.scatter([r[4]/1000 for r in m],[r[5] for r in m],c=col[j],s=60,label=NAMES[j])
xs=[r[4]/1000 for r in D]; ys=[r[5] for r in D]; m=corr(xs,ys)*st.pstdev(ys)/st.pstdev(xs); c=st.mean(ys)-m*st.mean(xs)
ax.plot([min(xs),max(xs)],[m*min(xs)+c,m*max(xs)+c],"--",color="gray",label=f"Tendencia lineal (r = {corr(xs,ys):.2f})"); ax.grid(alpha=.3); ax.set_axisbelow(True)
ax.set(title="Valor de compra vs. frecuencia mensual",xlabel="Valor de compra (miles de COP)",ylabel="Compras mensuales"); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig("out/g2.png",dpi=150); plt.close()
# --- Excel
wb=Workbook(); ws=wb.active; ws.title="Datos"
ws.append(["ID de compra","Edad","Ciudad","Producto","Valor de compra (COP)","Compras mensuales","Grupo de edad","Categoría de compra","Segmento (K-means)"])
for r,l in zip(D,L): ws.append([*r,grupo(r[1]),cat(r[4]),NAMES[l]])
for c in ws[1]: c.font=Font(bold=True,color="FFFFFF"); c.fill=PatternFill("solid",fgColor="2B6CB0")
for row in ws.iter_rows(min_row=2,min_col=5,max_col=5): row[0].number_format='"$"#,##0'
for i,w in enumerate([14,8,12,13,22,18,14,18,40]): ws.column_dimensions["ABCDEFGHI"[i]].width=w
a=wb.create_sheet("Análisis")
a.append(["Categoría","N.º de compras","Valor total","Valor promedio","Frecuencia media"])
for i,p in enumerate(cnt,2):
    a.append([p,f'=COUNTIF(Datos!D:D,A{i})',f'=SUMIF(Datos!D:D,A{i},Datos!E:E)',f'=AVERAGEIF(Datos!D:D,A{i},Datos!E:E)',f'=AVERAGEIF(Datos!D:D,A{i},Datos!F:F)'])
    a.cell(i,3).number_format='"$"#,##0'; a.cell(i,4).number_format='"$"#,##0'
a.append([]); a.append(["Ciudad","N.º de compras"])
for i,c in enumerate(("Bogotá","Medellín","Cali"),7): a.append([c,f'=COUNTIF(Datos!C:C,A{i})'])
a.append([]); a.append(["Grupo de edad","N.º de compras","Valor promedio"])
for i,g in enumerate(("20-29","30-39","40+"),12):
    a.append([g,f'=COUNTIF(Datos!G:G,A{i})',f'=AVERAGEIF(Datos!G:G,A{i},Datos!E:E)']); a.cell(i,3).number_format='"$"#,##0'
a.append([]); a.append(["Categoría de compra","N.º de compras"])
for i,g in enumerate(("Baja","Media","Alta"),17): a.append([g,f'=COUNTIF(Datos!H:H,A{i})'])
a.append([])
a.append(["Valor promedio de compra","=AVERAGE(Datos!E2:E13)"]); a.append(["Mediana","=MEDIAN(Datos!E2:E13)"])
a.append(["Correlación valor-frecuencia","=CORREL(Datos!E2:E13,Datos!F2:F13)"]); a.append(["Correlación edad-valor","=CORREL(Datos!B2:B13,Datos!E2:E13)"])
a.append(["Reglas de categoría","Baja < $150.000 | Media $150.000–$299.999 | Alta ≥ $300.000"])
for row in (1,6,11,16):
    for c in a[row]: c.font=Font(bold=True)
a["B21"].number_format='"$"#,##0'; a["B22"].number_format='"$"#,##0'; a["B23"].number_format="0.00"; a["B24"].number_format="0.00"
a.column_dimensions["A"].width=30; a.column_dimensions["B"].width=18; a.column_dimensions["C"].width=14; a.column_dimensions["D"].width=16; a.column_dimensions["E"].width=16
bc=BarChart(); bc.title="Compras por categoría"; bc.add_data(Reference(a,min_col=2,min_row=1,max_row=4),titles_from_data=True); bc.set_categories(Reference(a,min_col=1,min_row=2,max_row=4)); bc.legend=None
bc.y_axis.title="N.º de compras"; bc.x_axis.title="Categoría"; bc.x_axis.delete=False; bc.y_axis.delete=False; a.add_chart(bc,"G2")
sc=ScatterChart(); sc.title="Valor de compra vs. frecuencia mensual"; sc.style=13
s=Series(Reference(ws,min_col=6,min_row=2,max_row=13),Reference(ws,min_col=5,min_row=2,max_row=13),title="Compras"); s.marker.symbol="circle"; s.graphicalProperties.line.noFill=True
sc.series.append(s); sc.x_axis.title="Valor de compra (COP)"; sc.y_axis.title="Compras mensuales"; sc.legend=None; sc.x_axis.delete=False; sc.y_axis.delete=False; a.add_chart(sc,"G20")
k=wb.create_sheet("Segmentos")
k.append(["Segmento","N.º compras","Edad media","Valor promedio","Frecuencia media","IDs"])
for j in range(3):
    m=seg(j)
    k.append([NAMES[j],len(m),round(st.mean(r[1] for r in m),1),st.mean(r[4] for r in m),st.mean(r[5] for r in m),", ".join(r[0] for r in m)])
    k.cell(j+2,4).number_format='"$"#,##0'
for c in k[1]: c.font=Font(bold=True)
k.column_dimensions["A"].width=42; k.column_dimensions["D"].width=16; k.column_dimensions["F"].width=28
k.append([]); k.append(["K-means (k=3) sobre edad, valor y frecuencia estandarizados (z-score); código en analisis.py."])
wb.save("out/Analisis_Datos_Comerciales.xlsx")
