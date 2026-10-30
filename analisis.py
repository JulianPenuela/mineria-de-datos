import statistics as st, math
D=[("C001",22,"Bogotá","Tecnología",250000,2),("C002",35,"Medellín","Ropa",120000,4),("C003",28,"Bogotá","Tecnología",320000,3),
("C004",42,"Cali","Hogar",180000,2),("C005",31,"Medellín","Ropa",150000,5),("C006",24,"Bogotá","Hogar",90000,1),
("C007",45,"Cali","Tecnología",450000,3),("C008",29,"Bogotá","Ropa",110000,4),("C009",38,"Medellín","Hogar",210000,2),
("C010",26,"Cali","Tecnología",280000,3),("C011",33,"Bogotá","Ropa",160000,5),("C012",41,"Medellín","Tecnología",390000,2)]
def cat(v): return "Baja" if v<150000 else ("Media" if v<300000 else "Alta")
def grupo(a): return "20-29" if a<30 else ("30-39" if a<40 else "40+")
def corr(x,y):
    mx,my=st.mean(x),st.mean(y)
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
def kmeans(k=3):
    cols=list(zip(*[(r[1],r[4],r[5]) for r in D]))
    mu=[st.mean(c) for c in cols]; sd=[st.pstdev(c) for c in cols]
    X=[[(v-m)/s for v,m,s in zip(p,mu,sd)] for p in zip(*cols)]
    d=lambda a,b:sum((i-j)**2 for i,j in zip(a,b))
    C=[X[0]]
    while len(C)<k: C.append(max(X,key=lambda p:min(d(p,c) for c in C)))
    for _ in range(100):
        L=[min(range(k),key=lambda j:d(p,C[j])) for p in X]
        N=[[sum(p[i] for p,l in zip(X,L) if l==j)/L.count(j) for i in range(3)] for j in range(k)]
        if N==C: break
        C=N
    return L
if __name__=="__main__":
    from collections import Counter
    v=[r[4] for r in D]; f=[r[5] for r in D]
    print(Counter(r[3] for r in D),Counter(r[2] for r in D),st.mean(v),st.median(v),corr(v,f),corr([r[1] for r in D],v))
    for g in ("20-29","30-39","40+"):
        s=[r[4] for r in D if grupo(r[1])==g]; print(g,len(s),st.mean(s),max(s))
    print(Counter(cat(x) for x in v))
    L=kmeans()
    for j in range(3):
        m=[r for r,l in zip(D,L) if l==j]; print(j,[r[0] for r in m],st.mean(r[1] for r in m),st.mean(r[4] for r in m),st.mean(r[5] for r in m),Counter(r[3] for r in m))
    for p in ("Tecnología","Ropa","Hogar"):
        s=[r for r in D if r[3]==p]; print(p,sum(r[4] for r in s),st.mean(r[4] for r in s),st.mean(r[5] for r in s))
