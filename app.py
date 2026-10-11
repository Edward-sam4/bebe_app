
import sqlite3, os
from flask import Flask, render_template, request, redirect, session
app = Flask(__name__)
app.secret_key = "bebe-bro-2024"

def get_db():
    conn = sqlite3.connect("bebe.db")
    conn.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, quantity INTEGER, price INTEGER, cost INTEGER)")
    conn.execute("CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY, product TEXT, qty INTEGER, total INTEGER, seller TEXT, date TEXT, time TEXT)")
    return conn

@app.route("/")
def home():
    if "user" not in session: return redirect("/login")
    db=get_db();
    cur=db.cursor()
    cur.execute("SELECT SUM(total) FROM sales WHERE date=date('now')")
    total=cur.fetchone()[0] or 0
    cur.execute("SELECT * FROM products WHERE quantity<5")
    low=cur.fetchall()
    db.close()
    return render_template("dashboard.html", total_sales=total, low_stock=low, role=session.get("role"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"]; p=request.form["password"]
        users={"admin":"admin123","boss":"boss123","bebe":"bebe123","manager":"manager123"}
        if u in users and users[u]==p:
            session["user"]=u; session["role"]="Boss" if u=="boss" or u=="admin" else "Sales"
            return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear(); return redirect("/login")

@app.route("/products")
def products():
    if "user" not in session: return redirect("/login")
    db=get_db(); cur=db.cursor(); cur.execute("SELECT * FROM products"); prods=cur.fetchall(); db.close()
    return render_template("products.html", products=prods)

@app.route("/add_product", methods=["GET","POST"])
def add_product():
    if "user" not in session: return redirect("/login")
    if request.method=="POST":
        db=get_db(); db.execute("INSERT INTO products (name,category,quantity,price,cost) VALUES (?,?,?,?,?)",
        (request.form["name"],request.form["category"],request.form["quantity"],request.form["price"],request.form["cost"])); db.commit(); db.close()
        return redirect("/products")
    return render_template("add_product.html")

@app.route("/edit_product/<int:id>", methods=["GET","POST"])
def edit_product(id):
    db=get_db(); cur=db.cursor()
    if request.method=="POST":
        cur.execute("UPDATE products SET name=?,category=?,quantity=?,price=?,cost=? WHERE id=?",
        (request.form["name"],request.form["category"],request.form["quantity"],request.form["price"],request.form["cost"],id)); db.commit(); db.close()
        return redirect("/products")
    cur.execute("SELECT * FROM products WHERE id=?",(id,)); prod=cur.fetchone(); db.close()
    return render_template("edit_product.html", product=prod)

@app.route("/sell", methods=["GET","POST"])
def sell():
    if "user" not in session: return redirect("/login")
    db=get_db(); cur=db.cursor()
    if request.method=="POST":
        pid=request.form["product_id"]; qty=int(request.form["quantity"])
        cur.execute("SELECT * FROM products WHERE id=?",(pid,)); p=cur.fetchone()
        if p and p[3]>=qty:
            cur.execute("UPDATE products SET quantity=? WHERE id=?",(p[3]-qty,pid))
            cur.execute("INSERT INTO sales (product,qty,total,seller,date,time) VALUES (?,?,?,?,date('now'),time('now'))",(p[1],qty,p[4]*qty,session["user"]))
            db.commit()
        db.close(); return redirect("/sales")
    cur.execute("SELECT * FROM products"); prods=cur.fetchall(); db.close()
    return render_template("sell.html", products=prods)

@app.route("/sales")
def sales():
    if "user" not in session: return redirect("/login")
    db=get_db(); cur=db.cursor(); cur.execute("SELECT * FROM sales ORDER BY id DESC"); s=cur.fetchall(); db.close()
    return render_template("sales.html", sales=s)

if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port, debug=True)
