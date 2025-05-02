#flask =create instance(use for making web application)
#render_templat=html code ko render kata hai
#request=http code ko request karta hai
#flash=used to show temporary messgaes
#these are necessary when we use flask for connectivity
from flask import Flask, render_template, request, redirect, flash
import mysql.connector
from db_config import get_connection

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Needed for flashing messages use when we use flask

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Route to add a customer
@app.route('/add_customer')
def add_customer():
    return render_template('add_customer.html')

# Route to submit customer details and add to the database
@app.route('/submit_customer', methods=['POST'])
def submit_customer():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')

        if not all([name, email, phone]):
            flash('All fields are required!', 'error')
            return redirect('/add_customer')
#cursor.execute mysql query run karne ke liye
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO customers (name, email, phone) VALUES (%s, %s, %s)",
                    (name, email, phone)
                )
                conn.commit()#data added in workbench 

        flash('Customer added successfully!', 'success')
        return redirect('/view_customer')  # ✅ Redirect to view all customers

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect('/add_customer')

# Route to view all customers
@app.route('/view_customer')
def view_customer():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers")
            rows = cursor.fetchall()

            columns = [col[0] for col in cursor.description]
            customers = [dict(zip(columns, row)) for row in rows]

        return render_template('view_customer.html', customers=customers)

    except Exception as e:
        flash(f'Failed to load customers: {str(e)}', 'error')
        return redirect('/')

@app.route('/delete_customer', methods=['POST'])
def delete_customer():
    try:
        customer_id = request.form.get('customer_id')

        if not customer_id:
            flash('Customer ID is required for deletion!', 'error')
            return redirect('/view_customer')

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
                conn.commit()

        flash('Customer deleted successfully!', 'success')
        return redirect('/view_customer')

    except Exception as e:
        flash(f'Failed to delete customer: {str(e)}', 'error')
        return redirect('/view_customer')

# Route to view all policies
@app.route('/policies')
def policies():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, c.name AS customer_name, p.policy_type, p.premium, p.start_date, p.end_date
                FROM policies p
                JOIN customers c ON p.customer_id = c.id
            """)
            columns = [col[0] for col in cursor.description]
            policies = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
        return render_template('policies.html', policies=policies)
    except Exception as e:
        flash(f'Failed to load policies: {str(e)}', 'error')
        return redirect('/')

# Route to add a policy (e.g., by filling out a form)
@app.route('/add_policy', methods=['POST'])
def add_policy():
    try:
        customer_id = request.form.get('customer_id')
        policy_type = request.form.get('policy_type')
        premium = request.form.get('premium')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        if not all([customer_id, policy_type, premium, start_date, end_date]):
            flash('All fields are required!', 'error')
            return redirect('/policies')

        # Insert new policy into the database
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO policies (customer_id, policy_type, premium, start_date, end_date) VALUES (%s, %s, %s, %s, %s)",
                    (customer_id, policy_type, premium, start_date, end_date)
                )
                conn.commit()

        flash('Policy added successfully!', 'success')
        return redirect('/policies')  # Redirect to view all policies

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect('/policies')

# Route to delete a policy by its ID
# Route to delete a policy by its ID
@app.route('/delete_policy', methods=['POST'])
def delete_policy():
    try:
        policy_id = request.form.get('policy_id')

        if not policy_id:
            flash('Policy ID is required to delete!', 'error')
            return redirect('/policies')

        # Connect to the database
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM policies WHERE id = %s", (policy_id,))#sql query run
                conn.commit()

        flash('Policy deleted successfully!', 'success')
        return redirect('/policies')  # Redirect back to the policies page

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect('/policies')

@app.route('/claims')
def claims():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, cu.name AS customer_name, c.claim_type, c.claim_status, c.claim_date
                FROM claims c
                JOIN customers cu ON c.customer_id = cu.id
            """)
            columns = [col[0] for col in cursor.description]
            claims = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return render_template('claims.html', claims=claims)
    except Exception as e:
        flash(f'Failed to load claims: {str(e)}', 'error')
        return redirect('/')

@app.route('/add_claim', methods=['POST'])
def add_claim():
    try:
        customer_id = request.form.get('customer_id')
        claim_type = request.form.get('claim_type')
        claim_status = request.form.get('claim_status')
        claim_date = request.form.get('claim_date')

        if not all([customer_id, claim_type, claim_status, claim_date]):
            flash('All fields are required!', 'error')
            return redirect('/view_claim')

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO claims (customer_id, claim_type, claim_status, claim_date)
                VALUES (%s, %s, %s, %s)
            """, (customer_id, claim_type, claim_status, claim_date))
            conn.commit()

        flash('Claim added successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect('/view_claim')


@app.route('/delete_claim', methods=['POST'])
def delete_claim():
    try:
        claim_id = request.form.get('claim_id')

        if not claim_id:
            flash('Claim ID is required to delete!', 'error')
            return redirect('/claims')

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM claims WHERE id = %s", (claim_id,))
                conn.commit()

        flash('Claim deleted successfully!', 'success')
        return redirect('/claims')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect('/claims')


@app.route('/product')
def product():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products")  # Fetching all data from the 'products' table
            rows = cursor.fetchall()  # Get all rows from the query result
            
            # Creating a list of dictionaries for easy usage in the template
            columns = [col[0] for col in cursor.description]  # Getting the column names
            products = [dict(zip(columns, row)) for row in rows]  # Creating a dictionary for each row
            
        return render_template('product.html', products=products)  # Passing the 'products' data to the template
    except Exception as e:
        flash(f'Error loading products: {str(e)}', 'error')
        return redirect('/')  # Redirect to the home page in case of an error

@app.route('/add_product', methods=['POST'])
def add_product():
    try:
        name = request.form.get('name')
        category = request.form.get('category')
        price = request.form.get('price')

        if not all([name, category, price]):
            flash('All fields are required!', 'error')
            return redirect('/product')

        # Insert into database
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO products (name, category, price) VALUES (%s, %s, %s)",
                    (name, category, price)
                )
                conn.commit()

        flash('Product added successfully!', 'success')
        return redirect('/product')

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect('/product')


@app.route('/delete_product', methods=['POST'])
def delete_product():
    try:
        product_id = request.form.get('product_id')

        if not product_id:
            flash('Product ID is required to delete!', 'error')
            return redirect('/product')

        # Delete product from the database
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
                conn.commit()

        flash('Product deleted successfully!', 'success')
        return redirect('/product')

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect('/product')

if __name__ == '__main__':
    app.run(debug=True)#flask application ko start karne ke liye
