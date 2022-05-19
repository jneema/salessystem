from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)
# Connecting to an existing database
conn = psycopg2.connect("dbname='dfntbcsr0kcm65' user='yoipryjxqdmhbj' host='ec2-63-32-248-14.eu-west-1.compute.amazonaws.com' password='62a8b9ece3038c57667a7045892820cc274c257349c1b4c1e6b411ea898b2ed1' port='5432'")
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS Products(id serial,name varchar(255),bp int,SP int,serial_no varchar(255))')
cur.execute('CREATE TABLE IF NOT EXISTS Sales(id serial,product_id serial,quantity int,created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW())')
conn.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/inventories', methods=['GET', 'POST'])
def inventories():
    cur = conn.cursor()
    if request.method == 'POST':
        query = ('INSERT INTO products(name, bp, sp, serial_no) VALUES(%s, %s, %s, %s)')
        row = (request.form['name'], request.form['bp'], request.form['sp'], request.form['serial_no'])
        cur.execute(query,row)
        conn.commit()
        # print(row)
        return redirect(url_for('inventories'))
    else:    
        # Query Execution
        cur.execute('SELECT * FROM products')
        # List Variable to put your results in
        list_prods = cur.fetchall()
        # print(list_prods)
        return render_template('inventories.html', x=list_prods)
@app.route('/sales/<string:pid>')
def sales(pid):
    cur = conn.cursor()
    cur.execute('SELECT products.name, SUM(sales.quantity) as Quantity, SUM((products.sp-products.bp)*sales.quantity) as Profit FROM sales INNER JOIN products ON products.id = sales.product_id WHERE product_id=%s GROUP BY products.name', [pid])
    # cur.execute('SELECT * FROM sales  WHERE product_id=%s;' ,[pid])

    list_sales = cur.fetchall()
    # print(list_sales)
    return render_template('sales.html', y=list_sales)

@app.route('/sales')
def total_sales():
    cur = conn.cursor()
    cur.execute('SELECT products.name, SUM(sales.quantity) as Quantity, SUM((products.sp-products.bp)*sales.quantity) as Profit FROM sales INNER JOIN products ON products.id = sales.product_id GROUP BY products.name')
    # cur.execute('SELECT * FROM sales  WHERE product_id=%s;' ,[pid])

    list_sales = cur.fetchall()
    # print(list_sales)
    return render_template('sales.html', y=list_sales)
        
@app.route('/makesale', methods = ['POST'])
def makesale():
    cur = conn.cursor()
    query = ('INSERT INTO sales(product_id, quantity, created_at) VALUES(%s, %s, %s)')
    row = (request.form['pid'], request.form['quantity'], 'NOW()')
    cur.execute(query,row)
    conn.commit()
    return redirect(url_for('inventories'))

@app.route('/editsale', methods=['POST'])
def editsale():
    cur = conn.cursor()
    query = ('update products set name =%s, bp =%s, sp=%s, serial_no=%s where id = %s')
    row = (request.form['name'], request.form['bp'], request.form['sp'], request.form['serial_no'], request.form['id'])
    print(row)
    cur.execute(query,row)
    conn.commit()
    return redirect(url_for('inventories'))

@app.route('/dashboard')
def dashboard():
    cur = conn.cursor()
    
    cur.execute("SELECT  extract(year from sl.created_at) || '-' || extract(month from sl.created_at) || '-' || extract(day from sl.created_at)as date, sum((pr.sp-pr.bp)* sl.quantity) as totalprofit FROM public.sales as sl join products as pr on pr.id=sl.product_id  group by sl.created_at order by sl.created_at ASC")
    x = cur.fetchall()
    # print(x)
    labels = []
    data = []
    for i in x:
        labels.append(i[0])
        data.append(int(i[1]))
        print(data,labels)
    return render_template('dashboard.html', labels= labels, data = data)



if __name__ == "__main__":
    app.run(debug=True)